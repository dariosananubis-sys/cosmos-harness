---
cosmos: pueblo
nombre: trafilatura
padre: extraccion/fuentes-web
resumen: Se queda con el texto principal y sus metadatos, y devuelve vacio explicito si no puede.
---

https://github.com/adbar/trafilatura · Apache-2.0 · 6.748★ · último push 2026-08-28 (comprobado 2026-09-01)

```bash
pip install trafilatura
trafilatura -u "https://example.com/articulo" --json > /tmp/articulo.json
```

```python
import trafilatura
html = trafilatura.fetch_url("https://example.com/articulo")
texto = trafilatura.extract(html, include_comments=False, with_metadata=True)
if texto is None:
    print("no logro aislar contenido")     # ausencia explicita, no un fragmento disfrazado
```

Grado académico y **sin navegador**: quita menú, anuncio y pie sin cargar un motor de render entero.
Devuelve `None` explícito cuando no logra aislar el contenido con confianza suficiente, en vez de
entregar un trozo parcial que parece el artículo — que es lo que exige el agua de resistencia de este
árbol.

Gana a `mozilla/readability` (11.422★) y a `jina-ai/reader` (11.937★, último push 2026-05-22) en dos
cosas: publica benchmarks de precisión y exhaustividad contra los otros extractores —es transparente
sobre sus propios límites, raro en la categoría— y no depende de un servicio remoto con cuota, como sí
hace el prefijo público de Jina.

Ojo: no ejecuta JavaScript. En una página que pinta el contenido en el cliente devuelve `None` o
cuatro líneas de esqueleto, y eso **no significa que la página esté vacía** — significa que hace falta
render (`playwright`) antes. No confundir un `None` de «no pude» con un «no había».
