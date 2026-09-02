// docker-ephemeral-runner.js — ciclo de vida completo de un contenedor efímero de job:
// create → start → wait (con timeout) → logs → demux → remove. Pensado para un control-plane
// que lanza contenedores cortos (un job = un contenedor) contra un socket-proxy de Docker
// (p.ej. tecnativa/docker-socket-proxy) con permisos mínimos.
//
// Por qué existe como función compartida: si cada tipo de job repite este ciclo copiado línea
// por línea, una corrección (p.ej. el timeout de F-1 más abajo) solo se aplica donde alguien
// se acuerde de pegarla — y el resto se queda con el bug.
//
// Dos decisiones de diseño que vale la pena conservar si copias este patrón:
// 1. AutoRemove:false + remove() manual DESPUÉS de leer los logs. Con AutoRemove:true el
//    contenedor puede desaparecer antes de poder leer sus logs (race condition real).
// 2. El wait() SIEMPRE lleva timeout (ver waitWithTimeout): sin límite, un contenedor colgado
//    (proceso zombie, red externa caída, un login que espera para siempre) deja la espera
//    congelada para siempre — si ese contenedor ocupa el único slot de una cola serial, la
//    cola entera queda bloqueada sin auto-recuperación.
//
// Seguridad: NUNCA aceptes el nombre de la imagen a lanzar desde un payload externo sin
// contrastarlo antes contra una allowlist fija en tu código (mitigación ante compromiso del
// socket-proxy o del propio control-plane). Este módulo no impone la allowlist — es
// responsabilidad del caller, que sí conoce qué imágenes son válidas para tu caso.
import Dockerode from 'dockerode';
import { waitWithTimeout } from './docker-wait-with-timeout.js';
import { demuxLogs, parseStepLine } from './docker-job-log-markers.js';

/**
 * @param {object} [opts]
 * @param {string} [opts.host] host del socket-proxy (default: env DOCKER_PROXY_HOST o 'localhost')
 * @param {number} [opts.port] puerto del socket-proxy (default: env DOCKER_PROXY_PORT o 2375)
 * @returns {import('dockerode')}
 */
export function dockerClient({ host, port } = {}) {
  return new Dockerode({
    host: host || process.env.DOCKER_PROXY_HOST || 'localhost',
    port: port || Number(process.env.DOCKER_PROXY_PORT || 2375),
  });
}

/**
 * @param {import('dockerode')} docker
 * @param {object} spec  config de docker.createContainer (Image, Cmd, Env, HostConfig...)
 * @param {{timeoutMs:number, label:string, onStep?:Function}} opts
 * @returns {Promise<{exitCode:number, logs:string}>}
 */
export async function runEphemeralContainer(docker, spec, { timeoutMs, label, onStep } = {}) {
  const container = await docker.createContainer(spec);
  await container.start();

  // Progreso en vivo: stream paralelo solo para parsear los marcadores ::PREFIX::{json} del
  // protocolo de docker-job-log-markers.js. Aditivo — no toca la lectura final de logs.
  const stopFollow = onStep ? followStepMarkers(container, onStep) : () => {};

  let exitCode;
  try {
    ({ StatusCode: exitCode } = await waitWithTimeout(container, timeoutMs, label));
  } finally {
    stopFollow();
  }

  let logs = '';
  try {
    const buf = await container.logs({ follow: false, stdout: true, stderr: true, timestamps: false });
    logs = demuxLogs(buf);
  } catch (err) {
    console.warn(`[docker-ephemeral-runner] ${label} logs warn:`, err.message);
  }

  await container.remove({ force: true }).catch((err) => {
    console.warn(`[docker-ephemeral-runner] ${label} remove warn:`, err.message);
  });

  return { exitCode, logs };
}

/**
 * Sigue el stream de logs del contenedor EN VIVO y emite cada marcador `::PREFIX::{json}` a
 * `onStep`. Desmultiplexa frames Docker (8B de header) acumulando entre chunks. Fire-and-forget;
 * devuelve un stop() idempotente. No interfiere con la lectura final de logs (follow:false).
 * @param {import('dockerode').Container} container
 * @param {(marker:object)=>void} [onStep]
 * @returns {()=>void} stop
 */
export function followStepMarkers(container, onStep) {
  if (typeof onStep !== 'function') return () => {};
  let stream = null;
  let carry = Buffer.alloc(0);
  let lineBuf = '';

  const onData = (chunk) => {
    carry = Buffer.concat([carry, chunk]);
    let off = 0;
    while (off + 8 <= carry.length) {
      const size = carry.readUInt32BE(off + 4);
      if (off + 8 + size > carry.length) break; // frame incompleto: esperar más datos
      lineBuf += carry.slice(off + 8, off + 8 + size).toString('utf8');
      off += 8 + size;
      let nl;
      while ((nl = lineBuf.indexOf('\n')) >= 0) {
        const line = lineBuf.slice(0, nl);
        lineBuf = lineBuf.slice(nl + 1);
        const step = parseStepLine(line);
        if (step) onStep(step);
      }
    }
    carry = carry.slice(off);
  };

  container.logs({ follow: true, stdout: true, stderr: true, timestamps: false })
    .then((s) => { stream = s; s.on('data', onData); s.on('error', () => {}); })
    .catch(() => { /* sin progreso en vivo, el job sigue normal */ });

  return () => { try { stream?.destroy(); } catch { /* noop */ } };
}

/**
 * Limpieza al arrancar: para y elimina los contenedores de job (por label) que sobrevivieron
 * a una caída/recreate del proceso anterior. Llamar ANTES de registrar workers: en ese
 * instante no hay ningún worker esperando a ningún contenedor, así que todo el que siga
 * 'running' es huérfano por definición.
 * @param {import('dockerode')} docker
 * @param {{key:string, value:string}} label filtro, p.ej. {key:'job', value:'true'}
 * @param {(containers:Array)=>{toStop:string[],toRemove:string[]}} planFn normalmente
 *   planOrphanCleanup de docker-orphan-container-cleanup.js
 * @returns {Promise<{removed:number, stopped:number}>}
 */
export async function cleanupOrphanJobContainers(docker, label, planFn) {
  let removed = 0;
  let stopped = 0;
  try {
    const list = await docker.listContainers({ all: true, filters: { label: [`${label.key}=${label.value}`] } });
    const { toStop, toRemove } = planFn(list);
    for (const id of toStop) {
      await docker.getContainer(id).stop({ t: 10 }).catch(() => {});
      stopped++;
    }
    for (const id of toRemove) {
      await docker.getContainer(id).remove({ force: true }).catch(() => {});
      removed++;
    }
  } catch (err) {
    console.warn('[docker-ephemeral-runner] cleanup orphans warn:', err.message);
  }
  return { removed, stopped };
}
