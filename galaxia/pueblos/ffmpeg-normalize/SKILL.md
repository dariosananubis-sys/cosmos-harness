---
cosmos: pueblo
nombre: ffmpeg-normalize
padre: audiovisual/voz
resumen: Iguala el volumen percibido de muchos ficheros al estandar medido, en vez de al oido.
---

https://github.com/slhck/ffmpeg-normalize · **MIT**, leído en su `LICENSE.md` el 2026-09-01 (la API
de GitHub lo reporta como `NOASSERTION` porque el fichero lleva cabecera propia) · 1.530★ · último
push 2026-07-10 (misma comprobación)

```bash
pip install ffmpeg-normalize      # exige ffmpeg en el PATH
```

```bash
# EBU R128 a doble pasada sobre una carpeta entera: mide, y despues corrige
ffmpeg-normalize origen/*.mp4 -o salida/ -ext mp4 \
  -nt ebu -t -16 -lrt 11 -tp -1.5 -c:a aac -b:a 192k

# solo medir, sin escribir nada: para saber cuanto se desvia cada fichero
ffmpeg-normalize origen/*.mp4 --print-stats --dry-run
```

`-t -16` LUFS es el objetivo habitual de pódcast y plataformas de vídeo; `-t -23` es el de
radiodifusión europea. Se elige uno y se aplica a todo el lote: la queja de «un vídeo se oye y el
siguiente no» es siempre esto.

Gana a `ffmpeg -af loudnorm` a pelo, que es la alternativa real y ya está en la máquina: `loudnorm`
en una sola pasada estima mientras corrige y se desvía del objetivo varios decibelios. Esto hace la
**doble pasada** que la propia documentación del filtro recomienda —medir el fichero entero y luego
aplicar los valores medidos— y además recorre una carpeta sin escribir un bucle con veinte
parámetros.

Y lo que no hace bien:

- **`-nt peak` y `-nt rms` no son el estándar y engañan.** El pico no tiene relación con el volumen
  percibido: dos ficheros normalizados a pico pueden sonar distintísimos. El modo que resuelve el
  problema es `ebu`, que es el de por defecto y el que hay que dejar.
- **Recodifica el audio**, así que a un MP3 o un AAC se le añade una generación de pérdida más. Si el
  material se va a seguir editando, normalizar al final y no al principio.
- **Doble pasada es doble tiempo**, y sobre vídeo hay que decidir qué hacer con la imagen: sin
  `-c:v copy` puede recodificarla también.
- Lo que ya viene recortado (*clipping*) no se recupera: subir el nivel sube el ruido con él, y el
  informe dirá que el objetivo se cumplió.
