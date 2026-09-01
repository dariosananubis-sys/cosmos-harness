---
cosmos: pueblo
nombre: ocrmypdf
padre: extraccion/documentos
resumen: Anade capa de texto buscable a un escaneado sin tocar el original, con codigos de salida claros.
---

https://github.com/ocrmypdf/OCRmyPDF · MPL-2.0 · 34.645★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install ocrmypdf tesseract-lang        # el paquete de idiomas va aparte
ocrmypdf -l spa escaneado.pdf buscable.pdf
echo $?    # 0 ok · 2 argumentos · 4 PDF cifrado · 6 ya tenia texto · 10 salida invalida ...
```

Añade una capa de texto buscable a un escaneado **sin destruir el original**. Lo que lo hace ganar es
la tabla de **códigos de salida distintos por modo de fallo** (ya tenía texto y no se fuerza, PDF
cifrado, prioridades en conflicto, Ghostscript ausente) en vez de un genérico «error»: es el mejor
ejemplo de fallo ruidoso de todo el barrido, y el antipatrón contrario —un fallo genérico que no
nombra al culpable— es el que hace perder tardes enteras.

Por debajo lleva `tesseract-ocr/tesseract` (76.288★), el motor canónico. Para imágenes sueltas con
maquetación compleja, `PaddlePaddle/PaddleOCR` (88.587★) acierta más en tablas y facturas; se anota
como alternativa y no como pueblo porque aquí casi todo llega en PDF.

Ojo, el falso verde: Tesseract puede devolver **cadena vacía sin lanzar excepción** ante una imagen
ilegible. Un pipeline serio lee la confianza por palabra (`image_to_data`, columna `conf`), no solo el
texto. Y sin el paquete del idioma correcto (`-l spa`) el reconocimiento sale plausible y mal, que es
peor que salir vacío.
