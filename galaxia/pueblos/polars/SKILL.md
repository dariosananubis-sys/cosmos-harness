---
cosmos: pueblo
nombre: polars
padre: datos/motor-analitico
resumen: Marcos de datos en Rust con modo perezoso: planifica antes de leer y evita cargar de mas.
---

Entra junto al motor SQL y no en su lugar porque el modelo mental es distinto: aqui se encadenan
transformaciones tipadas, alli se escribe una consulta.

El esquema se fija al inferirse, asi que una columna con un valor raro falla en voz alta en vez de
convertirse en texto en silencio.
