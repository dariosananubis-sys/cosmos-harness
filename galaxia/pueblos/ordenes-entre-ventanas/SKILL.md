---
cosmos: pueblo
nombre: ordenes-entre-ventanas
padre: agentes-ia/herramientas
resumen: Entrega ordenes de la interfaz interactiva a las OTRAS ventanas abiertas; la propia va siempre la ultima.
---

`cosecha/mandar-a-terminales.py` — herramienta propia, no de GitHub. macOS + VS Code, por AppleScript.

```bash
python3 cosecha/mandar-a-terminales.py --listar
python3 cosecha/mandar-a-terminales.py --calibrar                       # 1 vez por sesión
python3 cosecha/mandar-a-terminales.py --enviar "/pre-compact" --mi-posicion 3 --dry-run
python3 cosecha/mandar-a-terminales.py --enviar "/pre-compact" --mi-posicion 3
```

Hay órdenes que **solo existen dentro de la sesión interactiva** (`/compact`, `/clear`, `/resume`,
`/pre-compact`): no tienen API, así que ningún canal automático puede lanzarlas. Esto las entrega
tecleándolas en las demás ventanas, con la regla dura de no escribir nunca en la terminal desde la que
corre — y si se pide incluirla, va la última.

Su valor real es el registro de lo que NO funciona, comprobado y no supuesto: escribir al dispositivo
de terminal va a su **salida** y no a la entrada del proceso; `TIOCSTI`, el mecanismo del sistema
diseñado para inyectar teclas, está **denegado en macOS** (`EPERM`); y el árbol de accesibilidad de
Electron devuelve `missing value` al preguntar qué terminal tiene el foco, así que hay que calibrar
ciclando una vuelta entera y leyendo la cabecera. Sin eso se pierde una tarde para llegar aquí.

Gana a repartir trabajo por este canal solo en ese hueco: para dar trabajo está el demonio que habla
por API y no depende de teclazos. Esto es únicamente para lo que vive dentro de la interfaz de texto.

Ojo: `--calibrar` caduca en cuanto se abre o cierra una pestaña — el ciclo cambia y sin recalibrar se
escribe en la ventana equivocada. El título de la pestaña no sirve para apuntar: Claude Code lo
reescribe con el resumen de su tarea.
