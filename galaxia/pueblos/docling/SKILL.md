---
cosmos: pueblo
nombre: docling
padre: extraccion/documentos
resumen: Convierte PDF, textos de oficina y hojas a Markdown o JSON conservando tablas, orden y jerarquia.
---

https://github.com/docling-project/docling · MIT · 65.840★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
pip install docling
docling entrada.pdf --to md --output /tmp/salida
```

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import ConversionStatus

r = DocumentConverter().convert("entrada.pdf")
if r.status is ConversionStatus.SUCCESS:
    print(r.document.export_to_markdown())
else:
    print("no fiable:", r.status)      # PARTIAL_SUCCESS o FAILURE
```

Gana a `datalab-to/marker` (39.452★), `Unstructured-IO/unstructured` (15.376★) y
`microsoft/markitdown` (177.500★) en el punto que decide: devuelve un `ConversionStatus` **de tres
valores** (`SUCCESS` / `PARTIAL_SUCCESS` / `FAILURE`), no un booleano. Una página que no se pudo leer
se sabe; no se confunde con una página vacía. Es el patrón trivalente que exige el revisor adversarial
—nunca colapsar «no lo sé» en el valor tranquilizador— y ninguno de los tres rivales lo trae.
`marker` afina mejor las fórmulas en PDF académico y pesa más; `markitdown` es más simple y pierde
estructura de tablas.

Ojo: `PARTIAL_SUCCESS` es el estado que se ignora en la práctica, y es justo el peligroso — devuelve
Markdown que parece completo. Hay que ramificar por él, no por «hay texto o no». Y el modelo de layout
se descarga en la primera ejecución: la primera conversión no es representativa del tiempo ni sirve
para medir en un entorno sin red.
