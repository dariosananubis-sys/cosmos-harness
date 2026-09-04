---
cosmos: pueblo
nombre: yt-dlp
padre: audiovisual/video
resumen: Descarga video de mas de mil sitios con seleccion de formato y subtitulos; ya en uso sin catalogar en reel-a-texto.
---

https://github.com/yt-dlp/yt-dlp · Unlicense (dominio público) · 188.643★ · último push 2026-08-30
(comprobado 2026-09-03)

```bash
brew install yt-dlp
```

```bash
yt-dlp -f "bv*[height<=1080]+ba/b" "<URL-DEL-VIDEO>" -o "%(title)s.%(ext)s"
yt-dlp --write-auto-sub --sub-lang es --skip-download "<URL-DEL-VIDEO>"   # solo subtitulos
yt-dlp --cookies-from-browser chrome "<URL-DEL-VIDEO>"                    # sitios con sesion
```

**Ya está en uso en esta galaxia sin catalogar**: `galaxia/pueblos/reel-a-texto/scripts/ig-dl.sh` lo
instala y lo llama como primer descargador de la cascada (`brew install yt-dlp ffmpeg gallery-dl`,
comentario propio: «yt-dlp para video»). Este pueblo lo nombra como lo que es, con su propia URL,
licencia y ficha — `reel-a-texto` sigue llamándolo igual, ahora contra un vecino que existe en el
catálogo.

Gana al fork del que nació, `youtube-dl/youtube-dl` (137k★, sin push reciente), en mantenimiento:
`yt-dlp` corrige la rotura semanal de extractores cuando un sitio cambia su web, que es la razón por
la que el original quedó atrás. Frente a `gallery-dl` (el otro descargador que usa `reel-a-texto` en
cascada), la frontera es el tipo de contenido: este resuelve video y audio; los carruseles de solo
imagen los ve como «0 items» y ahí gana `gallery-dl`.

Ojo: depende de que un sitio no le haya roto el extractor esa semana — `brew upgrade yt-dlp` antes de
un fallo raro, no después, es parte del procedimiento normal, no una excepción. Y `--cookies-from-browser`
lee la sesión real del navegador: sirve para contenido que exige sesión iniciada, pero es exactamente
la superficie que hay que declarar en cualquier informe que diga «medido sin credenciales».
