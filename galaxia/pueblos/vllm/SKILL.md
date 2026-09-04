---
cosmos: pueblo
nombre: vllm
padre: modelos-locales/servir
resumen: Motor de inferencia de alto rendimiento con PagedAttention; sirve muchas peticiones a la vez.
---

https://github.com/vllm-project/vllm · Apache-2.0 · 90.859★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
pip install vllm
```

```bash
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000
curl http://localhost:8000/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"Qwen/Qwen2.5-7B-Instruct","messages":[{"role":"user","content":"hola"}]}'
```

Gana a `ollama` y a `llama-cpp` en **throughput con muchas peticiones simultáneas**: su
`PagedAttention` gestiona la caché KV como memoria virtual paginada en vez de reservarla contigua
por petición, así que sirve decenas de usuarios a la vez sin que el rendimiento se desplome
linealmente. Es el motor que corre detrás de la mayoría de endpoints de inferencia propios en
producción a escala.

Ojo, y es lo que decide si entra o no: **necesita GPU dedicada** (NVIDIA con CUDA, o AMD con
ROCm) con VRAM suficiente para el modelo entero más la caché KV — no es una opción viable en una
máquina sin GPU discreta ni en Apple Silicon, donde ni siquiera arranca en su modo acelerado. El
aviso es la ficha: para servir un modelo en CPU o memoria unificada, la respuesta es `llama-cpp`,
`mlx-lm` o `ollama`, no esto.
