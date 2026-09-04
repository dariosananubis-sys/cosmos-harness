---
cosmos: pueblo
nombre: llama-cpp
padre: modelos-locales/servir
resumen: Motor de inferencia en C/C++ que define GGUF; corre en cualquier CPU/GPU, el estandar de facto.
---

https://github.com/ggml-org/llama.cpp · MIT · 126.862★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
brew install llama.cpp
```

```bash
llama-server -hf bartowski/Qwen2.5-7B-Instruct-GGUF:Q4_K_M --port 8080
curl http://localhost:8080/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"local","messages":[{"role":"user","content":"hola"}]}'
```

Es la capa que hay debajo de `ollama` y de buena parte del ecosistema local: define el formato
**GGUF** que casi todo el mundo cuantiza y distribuye, y su motor (`llama-server`, API compatible
OpenAI) corre en CPU pura, Metal, CUDA o Vulkan sin recompilar nada del lado del usuario final —
solo elegir el binario. Gana a `ollama` en control fino: flags de cuantización, `--n-gpu-layers`
exacto, muestreo (`--top-k`, `--min-p`, gramáticas GBNF) que `ollama` esconde detrás de su propia
capa de conveniencia. Pierde frente a él en comodidad: `ollama pull` gestiona descarga y versión
de modelo solo, aquí hay que traer el `.gguf` de HuggingFace a mano. Frontera con `mlx-lm`: este
solo corre en Apple Silicon y explota su memoria unificada; esto corre en cualquier máquina,
incluida la misma Apple Silicon, aunque sin esa ventaja específica.

Ojo: sin GPU dedicada ni Apple Silicon, un modelo de 7B en CPU pura funciona pero a una fracción
de los tokens/segundo de cualquiera de las dos rutas aceleradas — usable para un lote sin prisa,
no para un chat interactivo. Y compilar desde fuente con soporte CUDA/HIP concreto pide las
dependencias del fabricante de la GPU instaladas antes: `brew install llama.cpp` trae un binario
genérico, no siempre con el backend de aceleración deseado.
