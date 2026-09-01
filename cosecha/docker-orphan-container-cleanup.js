// docker-orphan-container-cleanup.js — decisión pura sobre contenedores "de job" huérfanos
// encontrados al arrancar un control-plane. Dep-free a propósito (no importa dockerode):
// el caller hace el listContainers/stop/remove real, esto solo decide QUÉ hacer con cada uno.
//
// Por qué existe: al arrancar (o recrear) el proceso que orquesta jobs efímeros, ANTES de
// registrar workers no hay nadie esperando a ningún contenedor: todo contenedor etiquetado
// como job que siga 'running' quedó huérfano del proceso anterior (murió/se recreó a mitad
// de ejecución). Si no se paran primero, siguen trabajando (y escribiendo resultados) sin que
// nadie lea su exit code, mientras su fila en la base de datos se marca 'failed' — un job
// fantasma hasta el siguiente arranque. Pararlos ANTES de reconciliar filas hace que el estado
// que se persiste sea cierto.

/**
 * @param {Array<{Id?:string, State?:string}>} containers salida de docker.listContainers
 * @returns {{toStop:string[], toRemove:string[]}} ids; toStop ⊆ toRemove, en ese orden
 */
export function planOrphanCleanup(containers = []) {
  const toStop = [];
  const toRemove = [];
  for (const c of containers) {
    if (!c?.Id) continue;
    if (c.State === 'running') toStop.push(c.Id);
    toRemove.push(c.Id);
  }
  return { toStop, toRemove };
}
