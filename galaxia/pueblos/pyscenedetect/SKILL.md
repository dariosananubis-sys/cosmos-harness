---
cosmos: pueblo
nombre: pyscenedetect
padre: audiovisual/video
resumen: Encuentra los cortes de plano y trocea el video por escenas sin que nadie lo vea entero.
---

https://github.com/Breakthrough/PySceneDetect · BSD-3-Clause · 5.144★ · último push 2026-08-28
(comprobado por API de GitHub el 2026-09-01)

```bash
pip install "scenedetect[opencv]"
```

```bash
# listar los cortes y dejar el CSV con los tiempos
scenedetect -i entrada.mp4 detect-adaptive list-scenes

# el lote, que es donde esta el valor: trocear y sacar una miniatura por escena
for f in origen/*.mp4; do
  scenedetect -i "$f" -o "salida/$(basename "${f%.*}")" \
    detect-adaptive split-video save-images --num-images 1
done
```

Gana al filtro `select='gt(scene,0.4)'` de `ffmpeg`, que es la alternativa real y ya está instalada:
aquel devuelve una puntuación por fotograma y el umbral se acaba eligiendo a ojo, así que un fundido
o un cambio de luz se cuenta como corte. `detect-adaptive` compara cada fotograma con una ventana
móvil de vecinos, de modo que un cambio progresivo no dispara. Y `split-video` deja los ficheros ya
cortados, llamando a `ffmpeg` por debajo.

Es la pieza que le falta a `reel-a-texto` cuando el vídeo es largo: aquel muestrea cinco fotogramas
equiespaciados, que es un resumen; esto trocea por contenido, que es una lectura.

Y lo que no hace bien:

- **`split-video` copia el flujo por defecto y los cortes van a fotograma clave.** El resultado tiene
  los primeros fotogramas congelados o el corte movido hasta un segundo. Para corte exacto,
  `split-video --precise`, que recodifica y tarda.
- **Las disolvencias largas y los fundidos a negro se le escapan** con `detect-adaptive`: para eso
  está `detect-threshold`, que es otro detector y hay que elegirlo a propósito.
- **Decodifica el vídeo entero.** Una hora en 4K son minutos de proceso, y `--downscale` es la
  diferencia entre viable e inviable en un portátil.
- Cámara fija con mucho movimiento dentro del plano da cortes falsos; el número de escenas que
  devuelve **no es el número de planos** hasta que alguien lo mira.
