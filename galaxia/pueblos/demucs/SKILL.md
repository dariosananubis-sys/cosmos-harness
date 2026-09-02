---
cosmos: pueblo
nombre: demucs
padre: audiovisual/voz
resumen: Separa la voz de la musica y del ambiente en una grabacion ya mezclada, sin perfil de ruido.
---

https://github.com/adefossez/demucs · MIT · 3.148★ · último push 2026-08-31 (comprobado por API de
GitHub el 2026-09-01).

**Ojo con la URL, que es lo primero**: el repositorio de Meta, `facebookresearch/demucs` (10.358★, el
que sale primero al buscar), está **archivado** desde 2024-04-24 — código congelado. El que sigue vivo
es el del autor original, el de arriba.

```bash
pip install demucs      # arrastra PyTorch
```

```bash
# dos pistas: voz y todo lo demas. Es lo que hace falta el 90 % de las veces
python -m demucs --two-stems=vocals -n htdemucs entrada.wav -o salida/

# con memoria justa, trocear para no llenar la memoria
python -m demucs --two-stems=vocals --segment 10 -d cpu entrada.wav -o salida/
```

Gana a `Rikorose/DeepFilterNet`, que es el reductor de ruido que se cita siempre para esto, por vida:
aquel no recibe un empujón desde octubre de 2024. Y gana al filtro `afftdn` de `ffmpeg` en el caso que
importa de verdad: `afftdn` resta un **perfil de ruido estacionario**, así que sirve para un zumbido
constante y no para una canción con letra o una cafetería de fondo. Esto separa fuentes, no resta un
perfil, y por eso quita lo que cambia.

Encadena con los vecinos: la voz aislada entra mucho mejor en `whisper-cpp` y en `whisperx` que la
mezcla original, y es la salida que hace que `auto-editor` encuentre silencios donde antes había
música.

Y lo que no hace bien:

- **Sin gráfica dedicada es lento**: del orden de minutos de proceso por minuto de audio, y
  sin `--segment` el consumo crece con la duración de la pista hasta llenar la memoria. Con
  `--segment 10` va, a costa de más tiempo. Estos números no se han medido en esta máquina: son la
  guía del propio proyecto y hay que comprobarlos antes de prometer un plazo.
- **La voz separada NO es una grabación limpia.** Deja artefactos metálicos y se come consonantes;
  para transcribir eso da igual y ayuda mucho, para una entrega final puede sonar peor que el
  original. Se escucha antes de entregar, siempre.
- **Está entrenado con música**, no con entrevistas. Sobre una grabación de voz con ruido de sala hace
  cosas raras: el modelo intenta encontrar batería y bajo donde no los hay.
- No hace diarización ni transcripción: solo separa. Quién habla lo dice `whisperx`.
