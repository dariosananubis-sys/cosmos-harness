---
cosmos: pueblo
nombre: unsloth
padre: modelos-locales/servir
resumen: Ajuste fino LoRA/QLoRA hasta 2x mas rapido y con menos VRAM sobre GPU NVIDIA.
---

https://github.com/unslothai/unsloth · Apache-2.0 · 75.532★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
pip install unsloth
```

```python
from unsloth import FastLanguageModel

modelo, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2.5-7B-Instruct-bnb-4bit", max_seq_length=2048, load_in_4bit=True,
)
modelo = FastLanguageModel.get_peft_model(modelo, r=16, lora_alpha=16)
# entrenamiento con trl.SFTTrainer sobre `modelo`, igual que con transformers normal
```

Gana a hacer el mismo LoRA con `transformers` + `peft` a pelo: kernels propios en Triton que
recortan memoria y tiempo de entrenamiento de forma medible (el propio proyecto publica
benchmarks por modelo), sin cambiar el bucle de entrenamiento que ya se conoce de `trl`. En este
país, hoy no hay ninguna vía real de ajuste fino documentada: `PADRES.txt` no tiene un nicho
`modelos-locales/entrenamiento` propio, así que se cataloga aquí, en `servir`, junto al resto de
lo que corre un modelo local.

Ojo: **exige GPU NVIDIA con CUDA** (o AMD con soporte experimental) — no corre en Apple Silicon
ni en CPU, así que en una máquina sin esa GPU esta ficha es para saber que existe, no para usar
hoy. Y "hasta 2x más rápido" es su propia cifra de marketing: varía mucho según modelo, tamaño de
contexto y el hardware exacto — medir en el caso propio antes de repetir el número.
