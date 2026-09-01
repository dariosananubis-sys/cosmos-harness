---
cosmos: pueblo
nombre: ffsubsync
padre: audiovisual/video
resumen: Cuadra un subtitulo descolocado con el audio real, corrigiendo desplazamiento y escala.
---

https://github.com/smacke/ffsubsync · MIT · 7.861★ · último push 2026-07-24 (comprobado por API de
GitHub el 2026-09-01)

```bash
pip install ffsubsync
```

```bash
# sincronizar contra el audio del video
ffs entrada.mp4 -i descolocado.srt -o sincronizado.srt

# sincronizar un subtitulo traducido contra otro que ya esta bien, sin tocar el video
ffs referencia.srt -i traducido.srt -o traducido-sincronizado.srt

# lote
for s in subtitulos/*.srt; do
  ffs "videos/$(basename "${s%.*}").mp4" -i "$s" -o "salida/$(basename "$s")"
done
```

Gana a desplazar el subtítulo con `ffmpeg -itsoffset` o con el editor de subtítulos, que es lo que se
hace a mano: aquellos aplican un **desplazamiento constante**, y el desajuste real casi nunca lo es —
viene de una diferencia de fotogramas por segundo (23,976 contra 25) o de un anuncio recortado, y
entonces el subtítulo empieza bien y termina un minuto tarde. Aquí se extrae la envolvente de voz del
audio con detección de actividad y se ajusta **desplazamiento y escala** por correlación, que es lo
que corrige ese caso.

Complementa a `whisperx`: aquel genera el subtítulo desde cero cuando no hay ninguno; esto arregla el
que ya venía con el material, que es el caso más frecuente en un encargo de cliente.

Y lo que no hace bien, y es su falso verde:

- **Siempre devuelve un fichero.** Si el ajuste no encaja, no da error: entrega el mejor resultado
  posible, que puede ser malo. Hay que mirar el desplazamiento y la puntuación que imprime, y abrir
  el vídeo por el minuto 1, por la mitad y por el final.
- **Necesita voz.** Sobre música, ambiente o una pista doblada muy comprimida, la detección de
  actividad falla y el ajuste es ruido.
- **Un montaje distinto no se arregla con un ajuste global.** Si al vídeo le faltan o le sobran
  escenas respecto al subtítulo, ninguna recta lo cuadra: hay que partir el subtítulo por tramos y
  sincronizar cada uno.
- Depende de `ffmpeg` en el `PATH` para leer el audio; sin él falla al arrancar.
