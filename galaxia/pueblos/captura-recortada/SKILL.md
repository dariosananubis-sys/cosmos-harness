---
cosmos: pueblo
nombre: captura-recortada
padre: agentes-ia/coste
resumen: Captura solo la ventana o la region que hace falta; una pantalla entera es la imagen mas cara que se puede meter.
origen: propio
---

`scripts/captura-ventana.py` — herramienta propia, no de GitHub. macOS, requiere `pyobjc` (Quartz) y
permiso de Grabación de pantalla.

```bash
python3 scripts/captura-ventana.py --listar              # ver qué ventanas hay
python3 scripts/captura-ventana.py "code" /tmp/v.png     # captura esa ventana, aunque esté tapada
screencapture -R 100,200,800,400 /tmp/region.png         # una región exacta, nativo, sin dependencias
```

`screencapture -l <windowid>` fotografía el contenido de la ventana **sin traerla al frente**, así que
se puede seguir trabajando encima mientras se captura la de atrás. El guion resuelve el `windowid` por
substring de «app  título» con `CGWindowListCopyWindowInfo`; sale 1 y lista las disponibles si no
encuentra ninguna.

Gana a `screencapture` a secas para el caso de ventana tapada, que es el único donde la región no
sirve: no se puede recortar lo que no se ve. Para todo lo demás, el `-R` nativo es más barato aún y no
pide dependencias — y en este arnés la pantalla entera está bloqueada por enganche.

Ojo: si sale negra no está rota — es TCC. Concederle Grabación de pantalla al proceso que la lanza
(Ajustes › Privacidad), no al guion. Y no confundirlo con `scripts/foto-cuadrar.py`, que es otra cosa:
re-encuadra fotos de producto a lienzo cuadrado, no recorta capturas.
