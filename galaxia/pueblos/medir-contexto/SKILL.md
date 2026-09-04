---
cosmos: pueblo
nombre: medir-contexto
padre: agentes-ia/coste
resumen: Lo que saben las transcripciones: cuanto costo la sesion, que entro de mas y que comandos se ejecutaron.
origen: propio
---

`scripts/medir-contexto-claude.py`, `scripts/barrido-transcripts.py` y `scripts/cc-history.sh` — tres
lecturas de la misma fuente (los `.jsonl` de `~/.claude/projects`). Herramientas propias, no de GitHub.

```bash
python3 scripts/medir-contexto-claude.py --json > antes.json   # báscula; repetir después del cambio
python3 scripts/barrido-transcripts.py /tmp/dias --proyecto <carpeta-del-proyecto> --dias 7
chmod +x scripts/cc-history.sh && scripts/cc-history.sh --global | grep rsync
```

El medidor deduplica por `requestId` (aparece 3-4 veces en el `.jsonl`) y separa **crear caché** de
**salida**, con la unidad comparable `cache_creation*1,25 + cache_read*0,10`. Da tres números: el
coste de arranque —system prompt + CLAUDE.md + catálogo de skills, que se paga entero en cada ventana
y en cada subagente—, el peso de cada sesión viva, y el total. Medido así, la mayor parte del gasto
suele ser material nuevo entrando, no razonamiento.

`cc-history.sh` es la tercera lectura y la que salva auditorías: los comandos de consola que se
ejecutaron de verdad, en orden. Es el rastro de lo que se tocó **fuera del repositorio** —un
despliegue, un borrado— cuando el resumen de la sesión ya no lo cuenta. Corre por `npx`, sin
instalación ni credenciales.

Gana a `/cost` y a la barra de la interfaz porque produce un JSON diffable: sin medir antes y después,
«he bajado el gasto» es una impresión, no un número.

Ojo: `--proyecto` es obligatorio en el barrido y no tiene valor por defecto sano — el nombre de la
carpeta lo deriva Claude Code de la ruta del repo con guiones, hay que listar `~/.claude/projects`
para verlo. Y los `.jsonl` **no dicen de qué cuenta salió** cada mensaje: con varias cuentas aisladas,
el total mezcla el consumo de todas.
