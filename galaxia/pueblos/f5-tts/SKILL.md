---
cosmos: pueblo
nombre: f5-tts
padre: audiovisual/voz
resumen: Clona una voz a partir de un audio de referencia de segundos; ni kokoro ni piper clonan.
---

https://github.com/SWivid/F5-TTS · MIT · 15.188★ · último push 2026-07-23 (comprobado 2026-09-03)

```bash
pip install f5-tts        # solo inferencia; requiere PyTorch instalado antes segun el dispositivo (CPU/CUDA/MPS)
```

```bash
f5-tts_infer-cli --model F5TTS_v1_Base \
  --ref_audio "VOZ-DE-REFERENCIA.wav" \
  --ref_text "Transcripcion exacta de lo que se dice en ese audio de referencia." \
  --gen_text "Texto nuevo que se quiere generar con esa misma voz."

f5-tts_infer-gradio --port 7860   # interfaz web local, mismo motor
```

Llena el hueco que sus dos vecinos de este mismo país declaran explícitamente que no cubren: la
ficha de `kokoro` dice «no clona voces» y la de `piper` hereda el mismo límite — ambos generan con un
catálogo fijo de voces entrenadas. `f5-tts` genera con **cualquier** voz a partir de unos segundos de
audio de referencia y su transcripción exacta (`--ref_audio` + `--ref_text`), con un transformador de
difusión (Diffusion Transformer + ConvNeXt V2) en vez de un modelo de voces cerradas.

Gana a `coqui-ai/TTS` — la referencia histórica de clonación, citada y descartada ya en la ficha de
`kokoro` por no tener commits desde agosto de 2024 y la empresa cerrada — por estar vivo: `f5-tts`
tuvo push en julio de 2026. Frente a `kokoro`/`piper`, la contrapartida es el coste: aquellos corren
en CPU en minutos; este es un modelo de difusión que quiere GPU (CUDA o ROCm) o Apple Silicon con
MPS para no ser lentísimo, y el propio proyecto publica sus benchmarks sobre una GPU de centro de
datos, no sobre un portátil.

Ojo: la transcripción del audio de referencia (`--ref_text`) tiene que ser **exacta** — un error ahí
contamina el timbre y la prosodia de todo lo generado, y el fallo no avisa, solo suena raro. Y el uso
de voz clonada trae encima la pregunta de consentimiento: clonar la voz de alguien sin su permiso es
la misma familia de riesgo que un deepfake, y no se hace sin que quien presta la voz lo sepa y lo
autorice. En memoria: sin GPU, cada generación corta puede tardar varios segundos a varios minutos
según el hardware — no es para uso en tiempo real como sí lo es `piper` con su servidor HTTP.
