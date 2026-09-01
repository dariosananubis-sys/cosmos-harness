---
cosmos: pueblo
nombre: claude-mem
padre: agentes-ia/memoria
resumen: Comprime y recupera lo hablado en sesiones anteriores del propio asistente de consola.
---

Especifico del asistente de consola, que es donde de verdad se pierde el hilo entre ventanas.
Mecanismo propio de compresion y recuperacion, no un fichero de notas.

Se acompana de `cosecha/patch-claude-mem-hooks.sh`, que corrige tres fallos documentados de sus
enganches. No es un pueblo aparte: es el parche de este, y vive con el.
