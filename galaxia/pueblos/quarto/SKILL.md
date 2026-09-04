---
cosmos: pueblo
nombre: quarto
padre: documentos/publicacion
resumen: Renderiza el mismo cuaderno con codigo a PDF, web, Word o slides; ejecuta antes de publicar.
---

https://github.com/quarto-dev/quarto-cli · MIT · 5.980★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
brew install quarto
```

````markdown
---
title: "Informe de ventas"
format:
  html: default
  pdf: default
execute:
  echo: false
---

## Resumen del mes

```{python}
import pandas as pd
df = pd.read_csv("ventas.csv")
print(f"Total facturado: {df['importe'].sum():.2f} EUR")
```

```{python}
df.groupby("categoria")["importe"].sum().plot(kind="bar")
```
````

```bash
quarto render informe.qmd --to html,pdf
quarto preview informe.qmd     # recarga en vivo mientras se edita
```

Gana a un cuaderno Jupyter exportado a mano cuando el destino es **publicar**, no solo explorar:
el mismo `.qmd` se renderiza a HTML, PDF (vía LaTeX o Typst), Word o una presentación reveal.js
sin tocar el contenido, y el código se ejecuta de verdad en cada render — el número que sale en el
informe es el que acaba de calcular, no uno pegado a mano de una sesión anterior. Frontera con
`typst`: aquí el documento es sobre todo prosa con código incrustado y varios formatos de salida;
allí se escribe el documento entero en el lenguaje de composición, para quien controla cada
detalle tipográfico.

Ojo: renderizar ejecuta el código de cada bloque en cada pasada — un informe con una consulta
pesada o una descarga de red se vuelve lento de explorar en `quarto preview` salvo que se cachee
(`execute: cache: true`). Y la salida a PDF depende de tener LaTeX instalado (o Typst como motor
alternativo, más ligero) aparte del propio Quarto: sin uno de los dos, `--to pdf` falla con un
error que no siempre dice qué falta.
