#!/usr/bin/env bash
# El clon en frío de la auditoría E, reproducido con reloj sobre EL ÁRBOL DE TRABAJO (R-03: la
# versión anterior clonaba la rama, que no tiene commits, es decir `main`: medía el código viejo).
# Copia el árbol (sin .git ni artefactos), lo convierte en repo, lo clona en frío y corre los 8 pasos.
# Uso: bash progress/auditoria-360-2026-09-03/CICLO-1/clon-en-frio.sh
set -u
ORIGEN="$HOME/cosmos"
BASE="$(mktemp -d /tmp/cosmos-clon-frio.XXXXXX)"
PY=/usr/local/bin/python3
rsync -a --exclude='.git' --exclude='.cosmos' --exclude='__pycache__' --exclude='progress' "$ORIGEN/" "$BASE/trabajo/"
( cd "$BASE/trabajo" && git init -q && git add -A -f >/dev/null 2>&1 && git -c user.email=clon@ejemplo.test -c user.name=clon commit -q -m "arbol de trabajo" )
DESTINO="$BASE/cold-clone"
t0=$(python3 -c 'import time;print(time.time())')
paso() { n="$1"; shift; a=$(python3 -c 'import time;print(time.time())'); "$@" > "$BASE/paso$n.out" 2>&1; rc=$?; b=$(python3 -c 'import time;print(time.time())'); printf 'paso %-2s EXIT=%s %5.2fs  %s\n' "$n" "$rc" "$(python3 -c "print($b-$a)")" "$*"; return $rc; }
fallos=0
paso 0 git clone --quiet "$BASE/trabajo" "$DESTINO" || fallos=$((fallos+1))
cd "$DESTINO" || exit 1
paso 1 $PY -m cosmos arrancar || fallos=$((fallos+1))
paso 2 $PY -m cosmos --help || fallos=$((fallos+1))
paso 3 $PY -m cosmos validar || fallos=$((fallos+1))
paso 4 $PY -m cosmos medir || fallos=$((fallos+1))
paso 5 $PY -m cosmos buscar montar un bot de trading || fallos=$((fallos+1))
paso 6 $PY -m cosmos abrir trading/bots/codigo-de-bot/toxiproxy || fallos=$((fallos+1))
paso 7 $PY -m cosmos enganchar --sesion || fallos=$((fallos+1))
paso 8 env COSMOS_HOLDOUT=/no/existe $PY -m cosmos acertar || fallos=$((fallos+1))
t1=$(python3 -c 'import time;print(time.time())')
printf 'arrancar: %s lineas / %s bytes\n' "$(wc -l < "$BASE/paso1.out")" "$(wc -c < "$BASE/paso1.out")"
printf 'acertar sin holdout dice NO DISPONIBLE: %s\n' "$(grep -c 'NO DISPONIBLE' "$BASE/paso8.out")"
printf 'hooks portables (sin rutas de esta maquina): %s ocurrencias de /Users/ en settings.json\n' "$(grep -c '/Users/' .claude/settings.json)"
printf '%s/9 pasos en verde (clon + 8), %.2fs total\n' "$((9-fallos))" "$(python3 -c "print($t1-$t0)")"
echo "clon en $DESTINO"
