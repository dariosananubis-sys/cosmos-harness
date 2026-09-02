#!/usr/bin/env bash
# Respalda un directorio de configuraciones (p.ej. fichas de cliente en YAML/JSON
# que están gitignored porque llevan credenciales) a un host remoto por rsync,
# solo-añadir (sin --delete): lo que se borre en local sobrevive en el backup.
#
# Por qué existe: un directorio con datos que NO están en git (gitignored porque
# llevan credenciales) es un punto único de fallo — si desaparece del disco local,
# no hay commit del que recuperarlo. Este script es la única red de seguridad.
#
# Uso: SRC=<ruta/local> REMOTE_HOST=<alias-ssh> REMOTE_DIR=<ruta/remota> backup-rsync-configs.sh
#   (o exporta las tres variables antes de llamarlo desde otro script/cron)
set -euo pipefail

SRC="${SRC:?define SRC=<ruta local a respaldar>}"
REMOTE_HOST="${REMOTE_HOST:?define REMOTE_HOST=<alias ssh o user@host>}"
REMOTE_DIR="${REMOTE_DIR:?define REMOTE_DIR=<ruta remota>}"
MIN_FILES="${MIN_FILES:-1}"   # sanity check: si hay menos de N ficheros en SRC, algo está mal — aborta
PATTERN="${PATTERN:-*.yaml}"  # patrón(es) a incluir; para varios, edita el rsync de abajo

n=$(find "$SRC" -maxdepth 1 -name "$PATTERN" | wc -l | tr -d ' ')
if [ "$n" -lt "$MIN_FILES" ]; then
  echo "solo $n fichero(s) '$PATTERN' en $SRC — ¿directorio vacío o ruta mal? aborto" >&2
  exit 1
fi

ssh "$REMOTE_HOST" "mkdir -p ~/$REMOTE_DIR"
# Sin --chmod (algunas versiones de rsync, p.ej. la 2.6.9 que trae macOS, no lo soportan).
rsync -az --include="$PATTERN" --include='*/' --exclude='*' "$SRC"/ "$REMOTE_HOST:~/$REMOTE_DIR/"

# chmod DESPUÉS del rsync, siempre: `rsync -a` implica -p y aplica al destino los permisos
# del directorio origen, pisando cualquier chmod previo. Con el chmod antes, el backup
# queda con permisos del origen (a menudo demasiado abiertos) en el remoto.
# Directorios y ficheros por separado: un `chmod 600 dir/*` a secas deja los subdirectorios
# sin permiso de entrada y el backup pasa a ser irrecorrible (ni el propio dueño puede
# hacer find sobre él).
ssh "$REMOTE_HOST" "find ~/$REMOTE_DIR -type d -exec chmod 700 {} + && find ~/$REMOTE_DIR -type f -exec chmod 600 {} +"

remoto=$(ssh "$REMOTE_HOST" "ls ~/$REMOTE_DIR/$PATTERN 2>/dev/null | wc -l" | tr -d ' ')
echo "OK: $n local(es) -> $remoto en $REMOTE_HOST:~/$REMOTE_DIR"
[ "$remoto" -ge "$n" ] || { echo "el remoto tiene MENOS ficheros que el origen: revisar" >&2; exit 1; }
