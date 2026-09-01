---
cosmos: pueblo
nombre: auto-editor
padre: audiovisual/video
resumen: Elimina silencios y partes muertas de una grabacion y entrega el corte, o la lista de cortes.
---

https://github.com/WyattBlue/auto-editor · Unlicense (dominio público) · 5.126★ · último push
2026-08-25 (comprobado por API de GitHub el 2026-09-01)

```bash
pip install auto-editor
```

```bash
# corte por volumen: fuera lo que baje del umbral, con un margen para no comerse las consonantes
auto-editor entrada.mp4 --edit "audio:threshold=4%" --margin 0.2sec --output salida.mp4

# lo mismo pero SIN recodificar: solo la lista de cortes, para abrirla en el editor
auto-editor entrada.mp4 --export premiere        # tambien: final-cut-pro, shotcut, resolve

# lote
for f in origen/*.mp4; do auto-editor "$f" --margin 0.2sec --output "salida/$(basename "$f")"; done
```

Gana a encadenar `silencedetect` de `ffmpeg` a mano, que es lo que se hace si esto no existe: aquel
imprime pares de tiempos en el log y a partir de ahí hay que construir un `filter_complex` con
`trim`/`concat` de decenas de tramos, y un error de índice se ve al final. Aquí el corte se aplica, y
si no se quiere tocar el fichero se exporta la lista de cortes para el editor.

Y lo que no hace bien:

- **Recodifica por defecto**, así que hay pérdida de calidad y tiempo de proceso. Cuando el material
  se va a editar después, la forma correcta es `--export` a la lista de cortes y no tocar el vídeo.
- **El umbral es la trampa.** Subirlo se lleva el principio de las palabras y el final de las frases;
  por eso `--margin` va en el ejemplo y no es opcional. Un umbral mal puesto no falla: entrega un
  vídeo entero con el habla mutilada.
- **Con música de fondo continua no hay silencio y no corta nada.** Ahí la señal es el
  `--edit motion`, o separar la voz antes con `demucs`.
- Licencia **Unlicense**: dominio público, sin garantía y sin concesión expresa de patentes. Para uso
  interno da igual; si el resultado se empaqueta dentro de un producto que se distribuye, conviene
  saberlo antes y no después.
