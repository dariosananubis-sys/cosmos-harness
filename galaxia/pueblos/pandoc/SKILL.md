---
cosmos: pueblo
nombre: pandoc
padre: documentos/conversion
resumen: Traduce entre decenas de formatos de documento conservando notas, citas y referencias cruzadas.
---

https://github.com/jgm/pandoc · GPL-2.0 · 46.100★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install pandoc

pandoc informe.md -o informe.docx
pandoc informe.md --citeproc --bibliography=refs.bib --csl=apa.csl -o informe.pdf
pandoc --from=docx --to=gfm --wrap=none entrada.docx -o salida.md
```

Sentido documento a documento, con control fino del resultado: conserva notas al pie, citas
bibliográficas y referencias cruzadas, que es exactamente lo que pierden los convertidores rápidos.
Gana a `markitdown` cuando el destinatario es una persona y no un modelo, y no tiene rival real en su
hueco: es la implementación de referencia desde hace quince años y su modelo intermedio es lo que usa
media herramienta de documentación por debajo.

Ojo: la licencia es **GPL-2.0**, con copyleft. Se usa como herramienta que se invoca —eso no
contamina nada—, pero **no se empotra** como biblioteca dentro de un producto de cliente sin aceptar
la GPL. Y para salida PDF necesita un motor aparte (`brew install --cask basictex` o `weasyprint`):
sin él, la orden falla con un mensaje sobre `pdflatex` que no explica que falta una instalación
entera.
