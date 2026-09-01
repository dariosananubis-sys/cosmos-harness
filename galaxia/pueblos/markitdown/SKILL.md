---
cosmos: pueblo
nombre: markitdown
padre: documentos/conversion
resumen: Deja en Markdown lo que entre, sea ofimatica, PDF, audio o web, para darselo a un modelo.
---

https://github.com/microsoft/markitdown · MIT · 177.500★ · push 2026-08-31 (comprobado 2026-09-01)

```bash
pip install 'markitdown[all]'

markitdown documento.pdf > documento.md
markitdown presentacion.pptx -o presentacion.md
cat hoja.xlsx | markitdown            # tambien lee de la entrada estandar
```

Sentido contrario a `pandoc`: aquí **todo converge a un solo formato de texto**. Se elige este cuando
el destinatario es un modelo y `pandoc` cuando el destinatario es una persona — porque lo que importa
aquí es que el texto llegue con su estructura de encabezados y tablas, no que el resultado quede
bonito. Gana a `unstructured` (el otro convertidor generalista para modelos) en coste de arranque:
una orden, sin servicio ni modelo local que descargar.

Frontera con el nicho de extracción: allí el PDF complejo con tablas anidadas y jerarquía; aquí la
conversión rápida y sin ceremonia.

Ojo: en un PDF **escaneado** no hay texto que extraer y devuelve prácticamente nada, sin error —un
falso verde de manual. Para eso hace falta `pip install markitdown-ocr` o una tubería de
reconocimiento óptico aparte. Y `[all]` arrastra bastante dependencia: si solo se convierten
documentos de ofimática, `pip install 'markitdown[docx,pptx,xlsx]'` deja el entorno mucho más
ligero.
