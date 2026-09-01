---
cosmos: pueblo
nombre: osv-scanner
padre: ciberseguridad/analisis/cadena-de-suministro
resumen: Compara los ficheros de bloqueo contra la base publica y devuelve poco ruido para revisar.
---

https://github.com/google/osv-scanner · Apache-2.0 · 10.950★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install osv-scanner
# o, sin Homebrew:
go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest
```

```bash
# escaneo recursivo del árbol de un proyecto
osv-scanner scan source -r .

# solo un lockfile concreto, con salida legible por máquina
osv-scanner scan source --lockfile=poetry.lock --format=json

# sin red, contra la base descargada antes
osv-scanner scan source --offline --download-offline-databases -r .
```

Gana a `anchore/grype` (12.816★) en ruido: su base viene deduplicada desde OSV.dev y da la versión
afectada exacta en lugar de un listado de CVE por paquete de sistema. Para imágenes de contenedor y
configuración de infraestructura no compite — ahí manda su vecino `trivy`.

Ojo, el falso verde clásico: `scan source` lee **ficheros de bloqueo**. Si el proyecto no tiene
lockfile (o lo tiene sin commitear), no ve las dependencias transitivas y sale verde sin haber
mirado nada. Comprobar siempre que la salida dice cuántos ficheros parseó, y no solo cuántos
hallazgos hubo. En modo `--offline` la base es la del último `--download-offline-databases`: una
base de hace un mes es una base que no conoce lo de este mes.
