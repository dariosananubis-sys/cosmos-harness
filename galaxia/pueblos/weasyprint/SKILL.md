---
cosmos: pueblo
nombre: weasyprint
padre: documentos
resumen: Compone PDF a partir de HTML y CSS, asi que la plantilla se edita como una pagina cualquiera.
---

https://github.com/Kozea/WeasyPrint · BSD-3-Clause · 9.546★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install pango libffi && pip install weasyprint      # en macOS, Pango es obligatorio

weasyprint factura.html factura.pdf

python - <<'PY'
from weasyprint import HTML, CSS
HTML(string="<h1>Informe</h1><p>Contenido de ejemplo.</p>").write_pdf(
    "informe.pdf",
    stylesheets=[CSS(string="@page { size: A4; margin: 2cm } h1 { color: #333 }")])
PY
```

Entra porque **la plantilla la puede tocar quien sabe maquetar**, sin aprender un lenguaje de
composición: es HTML y CSS, con `@page`, saltos de página y contadores para «página X de Y».
Descartadas `reportlab` y `fpdf2`, que dibujan el PDF por coordenadas: ahí cambiar un margen obliga a
tocar código, y la plantilla deja de ser editable por nadie que no programe. Y gana a `wkhtmltopdf`,
que está sin mantenimiento desde 2023 y arrastra un WebKit antiguo.

Ojo: **no ejecuta JavaScript**. Una plantilla que pinta una tabla o un gráfico en el navegador sale
en blanco aquí, sin error; hay que generar el HTML ya resuelto en el servidor, o el SVG del gráfico.
Ese es el falso verde típico. Y el soporte de CSS es amplio pero no completo: `flexbox` y `grid`
funcionan, algunas propiedades modernas no — la plantilla se **mira en el PDF**, no en el navegador,
antes de darla por buena.
