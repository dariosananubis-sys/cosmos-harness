---
cosmos: pueblo
nombre: ort
padre: cumplimiento/licencias
resumen: Pasa las dependencias por una politica de licencias y emite inventario y avisos en la tuberia.
---

https://github.com/oss-review-toolkit/ort · Apache-2.0 · 2.077★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
docker run --rm ghcr.io/oss-review-toolkit/ort --help

# el ciclo completo sobre un proyecto: resolver, escanear, evaluar politica, informar
docker run --rm -v "$PWD:/project" ghcr.io/oss-review-toolkit/ort \
  analyze -i /project -o /project/ort-salida
docker run --rm -v "$PWD:/project" ghcr.io/oss-review-toolkit/ort \
  evaluate -i /project/ort-salida/analyzer-result.yml \
           --rules-file /project/reglas.kts -o /project/ort-salida
docker run --rm -v "$PWD:/project" ghcr.io/oss-review-toolkit/ort \
  report -i /project/ort-salida/evaluation-result.yml -o /project/ort-salida -f SpdxDocument,WebApp
```

**Ejecuta** el cumplimiento en integración continua en vez de describirlo: `evaluate` corre una
política escrita en Kotlin sobre el árbol de dependencias resuelto y devuelve código de salida
distinto de cero cuando aparece una licencia prohibida. Es lo que `fossology` no hace —allí la
decisión la toma una persona en una interfaz— y por eso entran los dos.

El generador de inventario de materiales más citado (`syft`) no entra: el inventario ya lo produce el
escáner de imágenes del nicho de seguridad, y duplicarlo sería pagar dos líneas por lo mismo.

**Norma que cubre**: igual que su vecino, cumplimiento contractual de licencias, no norma legal.
Emite **SPDX 2.3 y CycloneDX**, y encaja con **OpenChain ISO/IEC 5230**. Sin territorio.

**Lo que NO comprueba**: patentes, marcas ni obligaciones de atribución que no estén declaradas en
los metadatos del paquete. Y como todo escáner, ve lo que el gestor de paquetes declara: una
dependencia copiada dentro del repositorio (código empotrado) no aparece.

Ojo: el ciclo completo es **lento** —el escaneo de fuentes de un proyecto grande son decenas de
minutos— y sin la caché de escaneo compartida se repite entero en cada ejecución. Ponerlo en la
tubería de cada `push` sin caché es garantizar que alguien lo desactive en un mes. Va en la nocturna,
o en la de la etiqueta de versión.
