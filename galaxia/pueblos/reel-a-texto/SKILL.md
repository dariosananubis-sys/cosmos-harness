---
cosmos: pueblo
nombre: reel-a-texto
padre: audiovisual/video
resumen: Deja un video publicado en transcripcion mas fotogramas clave, que es lo unico de un video que un modelo lee.
---

Herramienta propia, no publica. Tres guiones en la cosecha de este arbol:

- `scripts/analyze-reel.sh` — la tuberia entera: descarga, extrae el audio, transcribe en la propia
  maquina y saca cinco fotogramas repartidos por la duracion.
- `scripts/extract_frames.py` — solo los fotogramas equiespaciados, cuando ya hay transcripcion.
- `scripts/ig-dl.sh` — descarga en cascada para las redes que no dejan bajar sin sesion: cookie del
  navegador, luego dos descargadores, y raspado como ultimo recurso.

```bash
brew install yt-dlp ffmpeg gallery-dl
pip install mlx-whisper            # transcripcion por Metal, en Apple Silicon
```

```bash
scripts/analyze-reel.sh "<url-del-video>" /tmp/reel-analysis
scripts/analyze-reel.sh "<url-del-video>" /tmp/reel-analysis --high-precision
```

Deja en `/tmp/reel-analysis/<hash-de-la-url>/`: `video.mp4`, `audio.mp3`, `transcript.txt`,
`frame_01.jpg` … `frame_05.jpg`, `meta.txt` y `description.txt`.

```bash
scripts/extract_frames.py --auto --min-chars 300      # solo los videos con transcripcion pobre
scripts/ig-dl.sh "<url-del-post>" ~/media
```

No sustituye a `ffmpeg` ni a `whisper-cpp`: los llama. Existe porque la pregunta real casi nunca es
"convierte este video", sino "dime que dice y que se ve en el", y esa respuesta son dos artefactos,
no uno. Frente a montar la cascada a mano cada vez, el aporte es el orden, el muestreo de fotogramas
y el tratamiento de los casos que rompen: carrusel sin video (extrae solo el texto y sale con 0),
sesion caducada (sale con codigo 2 y un mensaje que dice que hacer). Frente a un servicio de
transcripcion en la nube, gana en que no sale nada de la maquina y no cuesta dinero.

Y lo que no hace bien:

- **Exige sesion iniciada en el navegador** para las redes cerradas: lee la cookie de Firefox o
  Chrome. Sin ella devuelve `LOGIN_REQUIRED` y codigo 2. No pide credenciales ni las guarda, y no
  debe hacerlo.
- **Transcribe con `whisper-base` por defecto**, que alucina sobre audio con musica o silencios. El
  propio guion documenta como detectarlo (bigrama repetido mas de cinco veces, o proporcion de
  palabras unicas por debajo de 0,15) y `--high-precision` sube a `large-v3`: tres veces mas lento y
  unos 3 GB de pesos, que en 8 GB va justo.
- **Cinco fotogramas equiespaciados no son cinco fotogramas representativos.** Si el video tiene el
  texto en pantalla dos segundos, el muestreo lo pierde. Es un resumen, no una lectura.
- Depende de `yt-dlp`, que se rompe cada vez que una red cambia su web: `brew upgrade yt-dlp` es
  parte del procedimiento, no una excepcion.
