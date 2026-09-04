---
cosmos: pueblo
nombre: delegar-generacion
padre: agentes-ia/construccion
resumen: Un modelo redacta el encargo y otro teclea el fichero; el prompt se ve antes de correr y la cuota agotada reintenta.
origen: propio
---

`scripts/codex-delegate.sh` y `scripts/codex-handler.sh` — herramientas propias, no de GitHub.
Requieren `claude` y `codex` en el PATH; los dos ficheros van en el mismo directorio.

```bash
chmod +x scripts/codex-delegate.sh scripts/codex-handler.sh
scripts/codex-delegate.sh src/utilidades/normalizar.py \
  "Funcion normalizar(texto) que quite acentos, pase a minusculas y colapse espacios. Sin dependencias externas. Con doctests."
scripts/codex-delegate.sh src/utilidades/normalizar.py "<descripcion>" --self-review   # si el output sale con avisos
```

El reparto es el que justifica el guion: `codex-delegate.sh` hace que un modelo redacte el encargo
autocontenido **y lo enseñe antes de ejecutarlo** — ahí se ve si el prompt está mal, en vez de
descubrirlo en el resultado; `codex-handler.sh` es la llamada real (`codex exec -s workspace-write`),
resuelve la ruta absoluta de salida y distingue por el texto del error una **cuota agotada** de un
fallo de código, para reintentar en vez de abortar un trabajo largo.

Gana a llamar a `codex exec` a pelo justo por esas dos cosas: a pelo no hay revisión del prompt y un
límite temporal de cuota se ve igual que un error de generación, así que se repite el trabajo entero.

Ojo: por debajo de unas 30 líneas delegar cuesta más que escribirlo. Y `--full-auto` ya no existe en
codex-cli (0.147.0+): un guion viejo que lo use falla con «unexpected argument», que parece un
problema de permisos y no lo es.
