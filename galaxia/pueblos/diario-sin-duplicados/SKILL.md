---
cosmos: pueblo
nombre: diario-sin-duplicados
padre: agentes-ia/memoria
resumen: Quita los bloques que un enganche roto repitio, y prueba antes de escribir que lo escrito a mano sigue intacto.
origen: propio
---

`scripts/dedupe-daily-autocapture.py` — herramienta propia, no de GitHub. Por defecto **no escribe**.

```bash
python3 scripts/dedupe-daily-autocapture.py notes/daily/2026-09-01.md        # dry-run
python3 scripts/dedupe-daily-autocapture.py --apply notes/daily/2026-09-01.md
```

Cuando un enganche de captura automática deja de reconocer su propio marcador, en vez de actualizar su
bloque lo vuelve a añadir entero: el mismo día acaba con la sesión repetida tantas veces como se
guardó. Esto deja **uno por identificador de sesión**, el más completo según su propio metadato de
tamaño (`Transcript: N KB`).

Lo que lo hace fiable no es el deduplicado sino la guarda: antes de escribir comprueba que todo lo que
NO es bloque generado —las notas a mano, los cierres escritos por una persona— sigue siendo **byte por
byte lo mismo**, y aborta si no. Una limpieza destructiva que no demuestra lo que ha conservado es una
pérdida de datos que todavía no se ha notado.

Gana a un `sort -u` o a un dedup por hash del bloque entero: los bloques repetidos **no son idénticos**
(cada uno se escribió con un transcript más largo), así que un dedup exacto no quita ninguno.

Ojo: las tres expresiones (`OPEN`/`CLOSE`/`SID`) están escritas para un formato concreto de enganche —
encabezado `## Auto-capture` y pie «Generado automáticamente por…». Con otro formato **no encuentra
nada y sale limpio**: falso verde. Comprobar primero que el dry-run enumera bloques.
