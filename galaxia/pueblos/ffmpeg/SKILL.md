---
cosmos: pueblo
nombre: ffmpeg
padre: audiovisual/video
resumen: Convierte, corta, escala y mezcla cualquier formato desde un solo comando reproducible.
---

https://github.com/FFmpeg/FFmpeg - licencia mixta LGPL-2.1+ o GPL-2+ **segun como se compile** (la
API de GitHub devuelve `NOASSERTION`; ver abajo) - 63.851 estrellas - ultimo push 2026-09-01
(comprobado por API de GitHub el 2026-09-01). Espejo oficial del repositorio canonico,
`git.ffmpeg.org`.

```bash
brew install ffmpeg
```

```bash
# recortar sin recodificar (instantaneo, sin perdida)
ffmpeg -ss 00:00:10 -to 00:00:40 -i entrada.mp4 -c copy recorte.mp4

# escalar a 720 de ancho manteniendo proporcion, calidad razonable
ffmpeg -i entrada.mp4 -vf "scale=720:-2" -c:v libx264 -crf 23 -preset medium salida.mp4

# extraer el audio a 16 kHz mono, que es lo que quiere whisper-cpp
ffmpeg -i entrada.mp4 -vn -ac 1 -ar 16000 audio.wav

# el lote, que es donde esta el valor: la misma orden sobre doscientos ficheros
for f in origen/*.mov; do
  ffmpeg -nostdin -i "$f" -vf "scale=1080:-2" -c:v libx264 -crf 23 "salida/$(basename "${f%.*}").mp4"
done
```

La base de todo el nicho: `whisper-cpp` y `reel-a-texto` lo llaman por debajo. Se usa siempre por
linea de comandos y con la orden guardada, porque el valor esta en poder repetirla identica sobre
doscientos ficheros. Descartados los envoltorios en Python (`kkroening/ffmpeg-python`, `Zulko/moviepy`):
anaden una capa que hay que traducir mentalmente cuando falla, y el error util lo imprime FFmpeg de
todas formas.

Ojo con la licencia, que aqui no es un detalle: el binario de Homebrew se compila con `--enable-gpl`
y componentes GPL (x264, x265), asi que **ese binario es GPL**. Distribuir un producto cerrado que
lo empaquete obliga a liberar el codigo. Para distribuir hace falta una compilacion LGPL sin esos
codificadores. Usarlo como herramienta en tu maquina no tiene ese problema.

Y lo que no hace bien — el falso verde de este pueblo: FFmpeg escribe el fichero de salida y
devuelve 0 aunque el resultado sea inservible. Un `-c copy` con corte a mitad de un grupo de
imagenes deja los primeros segundos congelados; un flujo de audio que no encaja en el contenedor se
descarta con un aviso que se pierde entre mil lineas de log. Verificar siempre la salida con
`ffprobe -v error -show_streams salida.mp4` y mirar el fichero, no solo el codigo de retorno.

En un `for` de shell, `-nostdin` es obligatorio: sin el, FFmpeg se come la entrada estandar y el
bucle procesa un solo fichero.
