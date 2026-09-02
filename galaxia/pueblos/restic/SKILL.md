---
cosmos: pueblo
nombre: restic
padre: infraestructura/custodia
resumen: Copias cifradas, deduplicadas e incrementales, con verificacion y restauracion de prueba.
---

https://github.com/restic/restic · BSD-2-Clause · 35.812★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install restic

export RESTIC_REPOSITORY=/ruta/al/repositorio-de-copias
export RESTIC_PASSWORD_FILE=~/.secrets/restic.pass     # nunca la clave en la orden

restic init
restic backup ~/Documentos --exclude-caches
restic check --read-data-subset=5%      # verifica que lo guardado se puede leer de verdad
restic restore latest --target /tmp/prueba-restauracion --include ~/Documentos
restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune
```

**Una copia que nunca se ha restaurado no es una copia**, y esa es la razón de que gane a
`borgbackup`, `duplicity` y `kopia`. `restic check --read-data-subset` lee de verdad los datos del
repositorio y comprueba las sumas, no solo el índice, y se puede programar como cualquier otra
tarea; `restic restore` a un directorio temporal es la prueba de restauración completa en una línea,
no un proyecto. `borgbackup` tiene `check` pero su repositorio no admite dos clientes a la vez;
`duplicity` encadena incrementales sobre una copia completa, así que un eslabón roto invalida la
cadena entera.

Descartado también el respaldo propio por sincronización remota en modo solo añadir
(`scripts/backup-rsync-configs.sh`): resuelve el mismo problema sin cifrado, sin deduplicación y sin
comando de verificación. Conserva una idea que sí vale y queda recogida aquí: **los permisos se
aplican DESPUÉS de copiar**, porque copiar los reescribe.

Ojo: `restic check` sin `--read-data` o `--read-data-subset` solo mira la estructura — pasa en verde
con datos corruptos. Y perder el fichero de contraseña es perder el repositorio entero: no hay
recuperación, el cifrado es el punto. La contraseña va al vault, no junto a las copias.
