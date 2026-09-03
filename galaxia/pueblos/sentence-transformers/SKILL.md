---
cosmos: pueblo
nombre: sentence-transformers
padre: modelos-locales/recuperacion
resumen: Genera los vectores del texto con modelos pequenos que caben y corren en la propia maquina.
---

https://github.com/huggingface/sentence-transformers · Apache-2.0 · 19.055★ · último push 2026-09-01
(comprobado 2026-09-01). **El repositorio se movió de `UKPLab` a `huggingface`**: los enlaces viejos
redirigen, pero un `git clone` a la ruta antigua confunde a quien audite la procedencia.

```bash
pip install sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer
modelo = SentenceTransformer("all-MiniLM-L6-v2")     # 22M parametros, ~90 MB en disco
vectores = modelo.encode(["primera nota", "segunda nota"], normalize_embeddings=True)
print(vectores.shape)
```

**Memoria**: `all-MiniLM-L6-v2` es la opción segura y trivial —22M parámetros, unos 90 MB, cabe en
cualquier sitio y basta para casi todo. `BGE-M3` (~560M parámetros, ~2,2 GB en fp32,
https://github.com/FlagOpen/FlagEmbedding, 12.116★) **también cabe** pero se lleva más de una cuarta
parte de la RAM de la máquina: se reserva para cuando el idioma importa de verdad o hace falta
búsqueda híbrida. Regla: empezar por el pequeño y subir solo si la recuperación lo pide, medido.

Es la capa de entrada estándar de todo el nicho — no hay debate real sobre si usarla, solo sobre qué
modelo cargar encima. Frente a pedir embeddings a una API, gana en lo que manda aquí: cero coste por
llamada y nada sale de la máquina.

Ojo: la primera llamada **descarga el modelo de la red** a `~/.cache/huggingface`, así que la primera
medición no es representativa y en una máquina sin red falla donde no se espera. Y `encode` sin
`normalize_embeddings=True` devuelve vectores sin normalizar: la similitud coseno luego no cuadra con
lo que devuelve la base vectorial, y el fallo aparece como «los resultados son malos», no como error.
