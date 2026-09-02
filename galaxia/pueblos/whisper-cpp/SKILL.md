---
cosmos: pueblo
nombre: whisper-cpp
padre: audiovisual/voz
resumen: Transcribe audio a texto en la propia maquina, aprovechando la grafica integrada del portatil.
---

https://github.com/ggml-org/whisper.cpp · MIT · 53.345★ · último push 2026-08-31 (comprobado 2026-09-01)
(comprobado por API de GitHub el 2026-09-01). Del mismo equipo que el motor de modelos locales, con
el mismo formato de pesos.

```bash
brew install whisper-cpp
# los pesos van aparte, del mas pequeno (~75 MB) al mas grande (~3 GB):
curl -L -o ggml-small.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin
```

```bash
# el audio TIENE que ser WAV de 16 kHz mono: ese paso lo hace ffmpeg
ffmpeg -i entrada.mp4 -vn -ac 1 -ar 16000 audio.wav

whisper-cli -m ggml-small.bin -f audio.wav -l es -osrt -otxt
# deja audio.wav.srt y audio.wav.txt
```

Transcribe en la propia maquina, aprovechando la grafica integrada del portatil por Metal, y exporta
SRT y VTT directamente, asi que cubre transcripcion y subtitulos en el mismo paso. Gana a
`SYSTRAN/faster-whisper` (25,2k estrellas), que es mas rapido en cierto hardware, por dos motivos que
pesan aqui: aquel no recibe commits desde noviembre de 2025, y arrastra Python con CTranslate2
mientras esto es un binario. Descartados tambien los envoltorios en Python: mismo motor, mas
dependencias.

Y lo que no hace bien — el falso verde de este pueblo, y es serio: **alucina en silencio**. Sobre
audio con musica sin voz, silencios largos o ruido, devuelve texto plausible que nadie dijo, y a
veces entra en bucle repitiendo la misma frase. El modelo `base` lo hace mas que el `small` y mucho
mas que el `large-v3`. Se detecta a posteriori mirando si hay un bigrama repetido mas de cinco veces
seguidas o si la proporcion de palabras unicas cae por debajo de 0,15. Una transcripcion no revisada
no es una fuente.

Y no separa hablantes ni da marcas de tiempo por palabra: para eso, `m-bain/whisperX`, mas pesado.

Aviso de maquina: `large-v3` son unos 3 GB de pesos y en una maquina justa de memoria deja poco margen para nada
mas. `small` es el punto de equilibrio razonable aqui; `base` solo para material limpio.
