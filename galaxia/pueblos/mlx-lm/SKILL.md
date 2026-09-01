---
cosmos: pueblo
nombre: mlx-lm
padre: modelos-locales/servir
resumen: Inferencia y adaptadores nativos de Apple Silicon, exprimiendo la memoria unificada del portatil.
---

https://github.com/ml-explore/mlx-lm · MIT · 6.853★ · último push 2026-09-01 (comprobado 2026-09-01).
Sobre https://github.com/ml-explore/mlx · MIT · 28.251★ · mismo push. Solo Apple Silicon.

```bash
pip install mlx-lm
mlx_lm.generate --model mlx-community/Qwen3-4B-Instruct-4bit \
  --prompt "Resume en tres lineas que hace este repositorio" --max-tokens 200
mlx_lm.lora --model mlx-community/Qwen3-4B-Instruct-4bit --train --data ./datos --iters 200
```

**En 8 GB, con cuantización 4-bit**: un modelo de ~3B en 4 bits corre con soltura; uno de **7-8B en
4 bits (~4-4,5 GB) es factible pero deja poco margen** para el sistema — con el editor y el navegador
abiertos, empieza el intercambio. Por encima de ~13B cuantizado **no entra**, y no hay truco que lo
arregle. `mlx-community` en HuggingFace trae miles de modelos ya convertidos, así que casi nunca hay
que cuantizar a mano.

Gana en esta máquina concreta a `ggml-org/llama.cpp` (126.621★, el estándar de facto) por la memoria
unificada: no hay copia entre procesador y gráfica, que es justo donde se cae todo lo demás con 8 GB.
La señal de madurez más fuerte es que el propio Ollama lo adoptó como backend en Apple Silicon.

Es además **la única vía real de ajuste fino aquí**: `mlx_lm.lora` hace LoRA/QLoRA sobre esa base.
Los entrenadores del ecosistema NVIDIA quedan descartados por hardware, `unslothai/unsloth` (75.414★)
incluido: exige CUDA y no corre en este Mac.

Ojo: cuantizar no es gratis. Un 4-bit pierde calidad de forma que no se ve en una prueba corta y sí en
una tarea larga, así que comparar modelos a ojo entre cuantizaciones distintas no vale — para eso está
`lm-evaluation-harness`. Y el ajuste fino LoRA compite por la misma RAM: entrenar y servir a la vez no
cabe.
