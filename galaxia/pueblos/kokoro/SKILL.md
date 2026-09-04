---
cosmos: pueblo
nombre: kokoro
padre: audiovisual/voz
resumen: Voz sintetica de calidad con un modelo de ochenta y dos millones de parametros que cabe en todo.
---

https://github.com/hexgrad/kokoro · Apache-2.0 · 8.648★ · **ultimo push
2025-08-06** (comprobado por API de GitHub el 2026-09-01), es decir, casi trece meses parado.

Lo que se ejecuta de verdad: https://github.com/thewh1teagle/kokoro-onnx - MIT - 2.694 estrellas -
ultimo push 2026-08-19 (misma comprobacion). Alternativa con servidor HTTP:
https://github.com/remsky/Kokoro-FastAPI · Apache-2.0 · 5.392★ · push 2026-09-01. (comprobado 2026-09-01)

```bash
pip install kokoro-onnx soundfile
curl -L -O https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -L -O https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

```python
import soundfile as sf
from kokoro_onnx import Kokoro

kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
audio, sr = kokoro.create("Texto de ejemplo para la locucion.", voice="ef_dora", speed=1.0, lang="es")
sf.write("salida.wav", audio, sr)
```

Ochenta y dos millones de parametros: consume dos o tres GB y corre en CPU sin grafica dedicada,
asi que sirve para sintesis de voz local en un portatil normal sin GPU — justo lo que este hueco
necesita. Gana a `rhasspy/piper` (11,3k estrellas, MIT), que era el sintetizador mas conocido del
hueco, por un motivo comprobable y no opinable: ese repositorio esta **archivado** y su ultimo push
es de 2025-08-26. Frente a `espeak-ng/espeak-ng`, que sigue vivo y pesa muchisimo menos, gana en
calidad — aquel suena robotico y no vale para una entrega final.

Y lo que no hace bien — con una advertencia sobre el propio criterio de admision de este catalogo:
**el repositorio del modelo tampoco esta vivo** (push 2025-08-06). Lo que esta vivo es el ejecutor
ONNX, que es el que se instala arriba. Si lo que se busca es un proyecto con desarrollo activo del
modelo, este pueblo no lo cumple y hay que revisarlo cada trimestre; entra porque no hay hoy una
alternativa local, gratis y de esta calidad que si lo cumpla.

Y lo demas que no hace: la calidad en castellano esta por debajo de la del ingles, no clona voces, y
la lista de voces es fija. Para clonacion la referencia era `coqui-ai/TTS`, sin commits desde agosto
de 2024 y con la empresa cerrada — o sea, tampoco.
