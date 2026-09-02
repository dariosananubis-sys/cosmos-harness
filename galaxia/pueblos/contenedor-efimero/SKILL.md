---
cosmos: pueblo
nombre: contenedor-efimero
padre: infraestructura
resumen: Un trabajo es un contenedor que nace y muere: espera con limite, registro antes del borrado y progreso en vivo.
---

`scripts/docker-ephemeral-runner.js`, `docker-wait-with-timeout.js`, `docker-job-log-markers.js`,
`docker-orphan-container-cleanup.js` y `pg-secret-file-connection.js` — herramientas propias, no hay
repositorio público. Las rutas SON la referencia. Node 18+, sin dependencias salvo `dockerode` en el
primero.

```bash
npm install dockerode

node --input-type=module -e "
import { dockerClient, runEphemeralContainer } from './scripts/docker-ephemeral-runner.js';
const docker = dockerClient({ host: '127.0.0.1', port: 2375 });   // socket-proxy, no el socket real
const r = await runEphemeralContainer(docker,
  { Image: 'alpine:3', Cmd: ['sh','-c','echo ::JOB_STEP::{\"paso\":1}; echo hecho'] },
  { timeoutMs: 60000, label: 'demo', onStep: (s) => console.log('paso', s) });
console.log(r);"
```

Nada de esto compite con un orquestador de cientos de nodos: es el trozo que hace falta cuando **un
trabajo por contenedor se resuelve en una máquina** y montar Kubernetes o Nomad sería más caro que el
problema. Lo que se prefiere de aquí frente a llamar a `docker run` desde el código es el orden, que
es donde están los cuatro fallos que ya costaron una noche:

1. `AutoRemove:false` y borrado manual **después** de leer el registro. Con borrado automático el
   contenedor desaparece antes de que nadie lea los logs y el fallo queda sin explicación.
2. `waitWithTimeout` — la espera siempre con límite duro; al vencer, mata el contenedor. Sin esto un
   contenedor colgado congela la cola entera y nadie se entera hasta que alguien pregunta.
3. `parseStepLine` / `demuxLogs` — protocolo mínimo de progreso por la salida estándar
   (`::JOB_STEP::{json}`), en vez de montar una API o un socket aparte solo para saber por qué paso
   va el trabajo.
4. `planOrphanCleanup` — al arrancar, decide qué contenedores del proceso anterior muerto hay que
   parar **antes** de reconciliar filas en la base de datos, para que lo que se persiste sea cierto.

`pg-secret-file-connection.js` arma la cadena de conexión desde un fichero de secreto, con la
variable de entorno solo como sustitución explícita para pruebas: una variable con la contraseña
queda visible en `docker inspect`, un fichero montado en `/run/secrets` no.

Ojo: el módulo **no impone allowlist de imágenes**. Aceptar el nombre de la imagen desde un payload
externo es dar ejecución arbitraria a quien controle ese payload; la lista blanca la pone quien
llama. Y todo esto habla con un socket-proxy con permisos mínimos, no con `/var/run/docker.sock`
montado a pelo — montarlo equivale a dar root de la máquina.
