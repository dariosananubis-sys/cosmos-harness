---
cosmos: pueblo
nombre: lancedb
padre: modelos-locales/recuperacion
resumen: Base vectorial embebida que lee de disco y no pelea por la RAM del proceso que la usa.
---

https://github.com/lancedb/lancedb · Apache-2.0 · 11.326★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
pip install lancedb
```

```python
import lancedb
db = lancedb.connect("/tmp/indice-lance")
tabla = db.create_table("notas", data=[
    {"vector": [0.1, 0.2, 0.3], "texto": "primera nota"},
    {"vector": [0.9, 0.8, 0.7], "texto": "segunda nota"},
])
print(tabla.search([0.1, 0.2, 0.25]).limit(2).to_list())
```

**Cabe donde otros ni arrancan, y es la razón de que gane**: corre dentro del proceso, con formato columnar
propio y acceso directo a disco, así que **no mantiene el índice entero en memoria** por diseño —
soporta conjuntos más grandes que la RAM disponible. No hay ningún servicio adicional compitiendo por
la RAM residente.

Gana a `qdrant/qdrant` (34.313★) y a `chroma-core/chroma` (29.196★) exactamente en este entorno: los
dos son mejores a escala real (filtrado complejo, miles de millones de vectores) pero piden un proceso
servidor permanente con su propia porción de RAM. En una máquina justa de memoria con el editor y el navegador
abiertos, ese proceso es el que provoca el intercambio. No es sustituto en todos los escenarios: es el
mejor **para esta máquina**.

Ojo: al vivir en el proceso, **no hay control de concurrencia entre escritores**. Dos guiones
escribiendo a la vez sobre el mismo directorio no dan un error claro. Y la búsqueda por fuerza bruta
sobre unas pocas miles de filas va bien sin índice; crear el índice ANN cambia el resultado
—recuperación aproximada— y eso no se ve, solo se mide.
