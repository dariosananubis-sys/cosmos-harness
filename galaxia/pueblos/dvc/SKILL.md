---
cosmos: pueblo
nombre: dvc
padre: cientifico/reproducible
resumen: Versiona datos y pesos fuera del repositorio y reejecuta solo la etapa que cambio.
---

https://github.com/treeverse/dvc · Apache-2.0 · 15.855★ · último push 2026-08-31 (comprobado 2026-09-01)
(comprobado por API de GitHub el 2026-09-01). El repositorio cambio de organizacion: el antiguo
`iterative/dvc` redirige aqui.

```bash
pipx install "dvc[s3]"      # o dvc[gs], dvc[azure], dvc a secas para remoto local
```

```bash
dvc init
dvc remote add -d almacen /Volumes/<tu-disco>/dvc-store   # o s3://<tu-bucket>/dvc
dvc add datos/crudo.parquet          # el fichero sale de Git; entra datos/crudo.parquet.dvc
git add datos/crudo.parquet.dvc datos/.gitignore .dvc/config && git commit -m "datos v1"
dvc push
```

```yaml
# dvc.yaml — la tuberia: cada etapa declara sus dependencias exactas
stages:
  limpiar:
    cmd: python src/limpiar.py
    deps: [src/limpiar.py, datos/crudo.parquet]
    outs: [datos/limpio.parquet]
  entrenar:
    cmd: python src/entrenar.py
    deps: [src/entrenar.py, datos/limpio.parquet]
    outs: [modelos/pesos.pkl]
    metrics: [metricas.json]
```

```bash
dvc repro          # reejecuta SOLO lo que cambio, por hash del dato, no por fecha
dvc metrics diff
```

Es lo que falta entre tener el codigo versionado y poder demostrar de que datos salio un resultado.
Gana a `git-lfs` —la alternativa que la gente prueba primero— porque LFS solo guarda ficheros
grandes: no sabe que etapa depende de que dato, no reejecuta nada y no compara metricas entre
ramas. Y no sustituye a la copia de seguridad: aquella protege de la perdida, este de la duda.

Y lo que no hace bien: `dvc repro` decide por hash del contenido de las dependencias declaradas. Si
una etapa lee un fichero que no esta en `deps`, o depende de una variable de entorno, o usa la hora
del sistema, DVC dara "todo al dia" mientras el resultado cambia. El falso verde vive ahi: en el
`deps` incompleto.

Aviso de dinero: los remotos de nube (S3, GCS) se pagan por almacenamiento y por trafico de salida.
Un remoto en disco local o en un NAS es coste cero y cubre el caso de un portatil.
