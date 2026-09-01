---
cosmos: pueblo
nombre: trivy
padre: ciberseguridad/analisis/cadena-de-suministro
resumen: Un solo binario para dependencias, imagenes, configuracion de nube y secretos, tambien sin conexion.
---

https://github.com/aquasecurity/trivy · Apache-2.0 · 37.729★ · último push 2026-08-28 (comprobado 2026-09-01)

```bash
brew install trivy
```

```bash
# imagen de contenedor: paquetes de sistema + dependencias de aplicación
trivy image --severity HIGH,CRITICAL nginx:1.27-alpine

# árbol de ficheros: dependencias, configuración de infraestructura y secretos a la vez
trivy fs --scanners vuln,misconfig,secret .

# inventario de materiales en formato estándar
trivy image --format cyclonedx --output sbom.json nginx:1.27-alpine
```

Entra junto a `osv-scanner` por amplitud, no por duplicar: aquí la **imagen de contenedor** y la
**configuración de infraestructura** (Terraform, Kubernetes, Dockerfile), que el otro no mira. Y
gana a la pareja `anchore/syft` + `anchore/grype` (9.492★ / 12.816★) por número de piezas: el
inventario de materiales lo genera este mismo binario, sin encadenar dos herramientas.

Ojo: por defecto **descarga su base de datos de vulnerabilidades en cada ejecución**. En una tubería
de integración sin caché eso son minutos y un punto de fallo de red — usar `--cache-dir` persistente
o `trivy image --download-db-only` en un paso aparte. Y su escáner de secretos es por patrón, sin
verificar contra el proveedor: para saber si una credencial encontrada sigue viva, `trufflehog`.
