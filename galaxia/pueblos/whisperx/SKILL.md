---
cosmos: pueblo
nombre: whisperx
padre: audiovisual/voz
resumen: Marcas de tiempo por palabra y separacion de hablantes sobre una transcripcion ya hecha.
---

https://github.com/m-bain/whisperX · BSD-2-Clause · 23.837★ · último push 2026-08-30 (comprobado por
API de GitHub el 2026-09-01)

```bash
pip install whisperx
```

```bash
# transcribir y alinear palabra a palabra: nada sale de la maquina, no hace falta cuenta
whisperx entrada.wav --language es --model small --output_format srt --output_dir salida/

# con separacion de hablantes. Exige aceptar los terminos de los modelos de pyannote en
# huggingface.co con un token de lectura propio (gratis, sin tarjeta) que NUNCA se escribe aqui:
export HF_TOKEN="$(security find-generic-password -s <SERVICIO_EN_EL_LLAVERO> -w)"
whisperx entrada.wav --language es --diarize --min_speakers 2 --max_speakers 4 \
  --hf_token "$HF_TOKEN" --output_format srt --output_dir salida/
```

Entra porque su vecino lo declara: `whisper-cpp` transcribe y exporta subtítulos, pero no marca la
palabra ni dice quién habla. Este cose las tres piezas —transcripción, alineación forzada contra el
audio y diarización— en una sola pasada, y el SRT sale ya con hablante.

Gana a encadenar a mano `SYSTRAN/faster-whisper` (25.243★) con `pyannote/pyannote-audio`, que es la
alternativa real: ahí hay que casar dos ejes de tiempo distintos y el error de un segundo aparece al
final, cuando ya se maquetó el subtítulo. Aquí la alineación es el paso intermedio, no un apaño
posterior. Para transcribir y nada más sigue ganando `whisper-cpp`: es un binario y esto arrastra
Python con PyTorch.

Y lo que no hace bien:

- **En 8 GB aprieta.** Instala PyTorch (2-3 GB en disco) y carga dos modelos a la vez —el de
  reconocimiento y el de alineación— más un tercero si se pide diarización. Con `--model small` y
  `--batch_size 4` va; con `large-v3` y el navegador abierto, intercambia.
- **La alineación en castellano es peor que en inglés.** El modelo de alineación por defecto para
  español es más flojo, y las palabras que no consigue alinear salen con marca de tiempo vacía y
  **se descartan en silencio**: el subtítulo queda correcto a la vista y con palabras de menos.
  Comparar el número de palabras del `.srt` con el del `.txt` antes de dar por bueno el resultado.
- **La diarización es una estimación, no una verdad.** Con voces solapadas o parecidas, cambia de
  etiqueta a mitad de frase; `--min_speakers`/`--max_speakers` ayudan solo si de verdad se sabe
  cuántos hay.
- Hereda la alucinación del modelo base: sobre silencio o música devuelve texto plausible que nadie
  dijo, y aquí encima llega con marca de tiempo y hablante, que es lo que lo hace creíble.
