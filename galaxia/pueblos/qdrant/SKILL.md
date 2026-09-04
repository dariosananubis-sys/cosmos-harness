---
cosmos: pueblo
nombre: qdrant
padre: modelos-locales/recuperacion
resumen: Base vectorial con servidor propio en Rust; filtrado complejo y escala real, con coste de proceso.
---

https://github.com/qdrant/qdrant · Apache-2.0 · 34.362★ · último push 2026-09-03 (comprobado 2026-09-03,
`.../commits/HEAD.atom`)

```bash
docker run -p 6333:6333 -v $(pwd)/datos-qdrant:/qdrant/storage qdrant/qdrant
```

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

cliente = QdrantClient(url="http://localhost:6333")
cliente.create_collection("notas", vectors_config=VectorParams(size=3, distance=Distance.COSINE))
cliente.upsert("notas", points=[
    PointStruct(id=1, vector=[0.1, 0.2, 0.3], payload={"texto": "primera nota", "categoria": "a"}),
])
resultado = cliente.query_points(
    "notas", query=[0.1, 0.2, 0.25],
    query_filter={"must": [{"key": "categoria", "match": {"value": "a"}}]}, limit=2,
)
print(resultado.points)
```

Gana a `lancedb` en filtrado complejo y en escala: un servidor dedicado en Rust con su propio
motor de índice HNSW aguanta millones de vectores con condiciones de filtro anidadas sin que el
proceso que lo consulta cargue nada en su propia memoria. Es el vecino natural de `lancedb`, que
gana justo en el caso contrario: cuando no hay presupuesto para un proceso servidor permanente y
el conjunto cabe embebido en el proceso que ya corre.

Ojo: es un **proceso servidor aparte** con su propia porción de RAM y de disco, que hay que
levantar, actualizar y vigilar — no es gratis frente a una librería embebida, y esa es
exactamente la razón por la que `lancedb` gana cuando el presupuesto de memoria del proceso
anfitrión está ajustado. Sin volumen persistente (`-v`), los datos desaparecen al reiniciar el
contenedor.
