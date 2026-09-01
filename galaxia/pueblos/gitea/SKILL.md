---
cosmos: pueblo
nombre: gitea
padre: infraestructura/servidores
resumen: Repositorio Git autoalojado con su propio motor de integracion continua y sus ejecutores.
---

https://github.com/go-gitea/gitea · MIT · 57.732★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
docker run -d --name gitea -p 3000:3000 -p 2222:22 \
  -v "$PWD/gitea-data:/data" \
  -e GITEA__server__ROOT_URL=http://localhost:3000/ \
  gitea/gitea:latest
# panel en http://localhost:3000 ; el primer usuario que se registra es el administrador

# ejecutor de integracion continua (Gitea Actions), token desde Ajustes > Actions > Runners
docker run -d --name gitea-runner \
  -e GITEA_INSTANCE_URL=http://localhost:3000 \
  -e GITEA_RUNNER_REGISTRATION_TOKEN=<TOKEN_REGISTRO> \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitea/act_runner:latest
```

Gana a `GitLab CE` en consumo —arranca en una máquina modesta donde GitLab necesita varios gigas
solo para el proceso— y a `Forgejo`, su bifurcación, por ecosistema de ejecutores maduro. Lo que lo
mete en el catálogo es **Gitea Actions**: acepta el mismo formato de fichero de flujo que el servicio
más extendido, así que una tubería se trae a casa sin reescribirla.

Ojo: compatible no es idéntico. Las acciones del mercado público que usan la API interna del
servicio original fallan aquí, y algunas se descargan de un registro que hay que configurar a mano.
Migrar una tubería es probarla, no copiarla. Y el `docker.sock` montado en el ejecutor da control
total de la máquina a cualquier trabajo que corra: en un servidor compartido, ejecutor en máquina
aparte.
