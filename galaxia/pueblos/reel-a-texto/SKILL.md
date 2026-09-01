---
cosmos: pueblo
nombre: reel-a-texto
padre: audiovisual/video
resumen: Deja un video publicado en transcripcion mas fotogramas clave, que es lo unico de un video que un modelo lee.
---

`cosecha/analyze-reel.sh` — descarga, extrae el audio, transcribe en la propia maquina y saca cinco
fotogramas repartidos. El orden y el muestreo son el aporte; las piezas son las que ya estan en el
arbol.

`cosecha/extract_frames.py` — los fotogramas equiespaciados por separado, cuando solo hace falta eso.

`cosecha/ig-dl.sh` — descarga en cascada para las redes que no dejan bajar sin sesion: cookie del
navegador, luego dos descargadores, y raspado como ultimo recurso.

No sustituye a `ffmpeg` ni a `whisper-cpp`: los llama. Existe porque la pregunta real casi nunca es
"convierte este video", sino "dime que dice y que se ve en el", y esa respuesta son dos artefactos,
no uno.
