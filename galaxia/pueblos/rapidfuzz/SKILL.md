---
cosmos: pueblo
nombre: rapidfuzz
padre: extraccion
resumen: Compara y agrupa cadenas parecidas a gran velocidad para unir registros que no coinciden exactos.
---

https://github.com/rapidfuzz/RapidFuzz · MIT · 4.106★ · último push 2026-08-30 (comprobado 2026-09-01)

```bash
pip install rapidfuzz
```

```python
from rapidfuzz import process, fuzz

catalogo = ["Camiseta algodon organico", "Camiseta algodon organica", "Pantalon vaquero"]
print(process.extractOne("camiseta algodon organico", catalogo, scorer=fuzz.WRatio))
print(process.cdist(catalogo, catalogo, scorer=fuzz.token_sort_ratio, workers=-1))
```

La primitiva de comparación de cadenas: unir registros que no coinciden exactos (dos veces el mismo
producto escrito distinto, un nombre con y sin tilde) a velocidad de C++, con `workers=-1` para la
matriz completa.

Gana a `dedupeio/dedupe` (4.510★) y a `moj-analytical-services/splink` (2.373★) por ser el peldaño
correcto hoy: los dos resuelven enlace de registros **probabilístico** —millones de filas, modelo
estadístico, aprendizaje activo— que aquí todavía no existe; y `dedupe` además lleva sin commits desde
2025-07-29, más de un año. De hecho los dos usan esta biblioteca por debajo como pieza de comparación.
Cuando el caso de millones de filas exista, suben.

Ojo: un porcentaje de parecido **no es una decisión**. Sin un umbral fijado con una muestra de control
y sin bloqueo previo por algún campo, `extractOne` siempre devuelve algo, y ese «algo» con 62 puntos
se cuela como coincidencia buena. El umbral se mide, no se opina.
