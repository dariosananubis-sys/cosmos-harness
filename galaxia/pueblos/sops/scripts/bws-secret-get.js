import { spawn } from 'node:child_process';

// Bitwarden Secrets Manager (bws): busca un secreto por su `key` en uno o varios proyectos.
// Útil cuando las credenciales están repartidas en más de un proyecto BWS (p.ej. credenciales
// por-sitio en un proyecto y claves de servicios externos compartidos en otro) y quieres una
// sola función que mire en todos sin tener que saber de antemano en cuál vive cada secreto.
//
// Requiere BWS_ACCESS_TOKEN y BWS_PROJECT_IDS (uno o varios project-id BWS, separados por coma)
// en el entorno.
const PROJECT_IDS = (process.env.BWS_PROJECT_IDS || '').split(',').map((s) => s.trim()).filter(Boolean);

let cache = null;

function runBws(args) {
  return new Promise((resolve, reject) => {
    const child = spawn('bws', args, { env: process.env });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', reject);
    child.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`bws: exit ${code}: ${stderr.slice(0, 200)}`));
      } else {
        resolve(stdout);
      }
    });
  });
}

export async function getSecret(key) {
  if (!process.env.BWS_ACCESS_TOKEN) {
    throw new Error('bws: falta BWS_ACCESS_TOKEN en el entorno');
  }
  if (!PROJECT_IDS.length) {
    throw new Error('bws: falta BWS_PROJECT_IDS en el entorno (uno o más project-id, separados por coma)');
  }
  if (!cache) {
    const lists = await Promise.all(
      PROJECT_IDS.map((pid) => runBws(['secret', 'list', pid, '--output', 'json']).then(JSON.parse)),
    );
    cache = lists.flat();
  }
  const hit = cache.find((s) => s.key === key);
  if (!hit) {
    throw new Error(`bws: secreto no encontrado: ${key}`);
  }
  return hit.value;
}
