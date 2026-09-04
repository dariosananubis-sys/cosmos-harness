---
cosmos: pueblo
nombre: syft
padre: cumplimiento/licencias
resumen: Genera el SBOM del proyecto o de una imagen; hoy en este pais no habia ninguna herramienta que lo hiciera.
---

https://github.com/anchore/syft · Apache-2.0 · 9.510★ · último push 2026-09-02 (comprobado 2026-09-03)

```bash
brew install syft
```

```bash
# SBOM del arbol de un proyecto, formato estandar CycloneDX
syft dir:. -o cyclonedx-json=sbom.json

# de una imagen de contenedor, sin arrancarla
syft docker:mi-imagen:tag -o spdx-json=sbom-imagen.json

# formato de tabla legible, rapido, para revisar en el momento
syft dir:. -o table
```

Ningún pueblo de `cumplimiento/licencias` producía hoy un inventario de materiales — `fossology`,
`ort` y `reuse` auditan y clasifican licencias sobre dependencias ya declaradas o código ya escrito,
pero ninguno **emite el documento** (SBOM en CycloneDX o SPDX) que un cliente o una auditoría externa
pide como entregable. Ese es el hueco que llena `syft`.

Gana a `cyclonedx/cdxgen` (rival directo del mismo nicho) en cobertura de ecosistemas detectados sin
configuración —Python, Node, Go, Rust, Java, imágenes de contenedor, paquetes del sistema operativo—
y en que su formato de salida es el que después consume `grype` (de la misma casa, Anchore) para
cruzar contra vulnerabilidades. Frontera con `osv-scanner` y `trivy`: aquellos escanean y dan
veredicto de vulnerabilidad; `syft` solo **inventaría** lo que hay, sin opinar si es seguro.

Ojo: un SBOM es una foto del momento del build, no un vigilante. Generarlo una vez y archivarlo es
casi tan inútil como no tenerlo — hay que regenerarlo en cada release y versionarlo, porque un SBOM
de hace tres meses no sabe de la dependencia que se añadió la semana pasada. Y sobre imágenes
`docker:`, si la imagen usa una distribución poco común, el catálogo de paquetes de sistema puede
salir incompleto: revisar el recuento de paquetes contra lo esperado antes de firmar el documento
como completo.
