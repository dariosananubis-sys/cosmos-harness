---
cosmos: pueblo
nombre: d2
padre: documentos/diagramas
resumen: Para el diagrama de arquitectura que se mantiene aparte: mejor colocacion y sintaxis.
---

https://github.com/d2lang/d2 · MPL-2.0 · 25.110★ · push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install d2

cat > arquitectura.d2 <<'D2'
navegador -> proxy: HTTPS
proxy -> api: HTTP
api -> base_de_datos: SQL
api.shape: rectangle
base_de_datos.shape: cylinder
D2

d2 arquitectura.d2 arquitectura.svg
d2 --watch arquitectura.d2          # recarga en el navegador al guardar
```

Empata de verdad con `mermaid` y la frontera es **dónde vive el diagrama**: dentro del texto, aquel;
fichero propio que se mantiene años, este. Lo que gana aquí es la colocación automática —motores
`elk` y `dagre` seleccionables, y contenedores anidados que no se cruzan— y una sintaxis que aguanta
un diagrama de cincuenta nodos sin volverse ilegible, que es justo donde `mermaid` se rompe.

Ojo: no lo pinta ninguna plataforma de forma nativa. Un `.d2` en un repositorio es un fichero que hay
que **compilar y commitear el SVG** para que se vea en la web del repositorio o en la documentación —
si nadie automatiza ese paso, el diagrama publicado y el fuente divergen, que es el mismo problema
que el diagrama se supone que resuelve. Ponerlo en la tubería junto al resto de la documentación.
