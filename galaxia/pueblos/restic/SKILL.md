---
cosmos: pueblo
nombre: restic
padre: infraestructura
resumen: Copias cifradas, deduplicadas e incrementales, con verificacion y restauracion de prueba.
---

Gana a los tres competidores por combinacion de actividad, licencia permisiva y un comando de
verificacion que se puede programar. Una copia que nunca se ha restaurado no es una copia: aqui la
restauracion de prueba es un comando, no un proyecto.

Descartado tambien el respaldo propio por sincronizacion remota en modo solo anadir
(`cosecha/backup-rsync-configs.sh`): resuelve el mismo problema sin cifrado, sin deduplicacion y sin
comando de verificacion. Conserva una idea que si vale y esta recogida aqui: los permisos se aplican
DESPUES de copiar, porque copiar los reescribe.
