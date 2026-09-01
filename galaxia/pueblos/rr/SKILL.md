---
cosmos: pueblo
nombre: rr
padre: rendimiento/velocidad/depuracion
resumen: Graba una ejecucion entera y la repite igual, hacia delante y hacia atras: la carrera se caza.
---

https://github.com/rr-debugger/rr · MIT (Mozilla) · 10.633★ · push 2026-08-16 (comprobado 2026-09-01)

```bash
# Linux, x86-64 o ARM64. En Debian/Ubuntu:
sudo apt install rr
sudo sysctl kernel.perf_event_paranoid=1     # requisito habitual

rr record ./mi-programa --argumentos
rr replay                                    # abre GDB sobre la grabacion
#   (rr) continue        avanzar
#   (rr) reverse-continue   ir HACIA ATRAS hasta el punto de ruptura anterior
#   (rr) watch -l variable ; reverse-continue   quien escribio ese valor
```

Convierte el fallo que no se repite en uno que sí: **graba una ejecución entera y la repite idéntica**,
las veces que haga falta, hacia delante y hacia atrás. No hay nada equivalente —razonar sobre el
código no reproduce una condición de carrera, y un `printf` la desplaza—; `gdb` solo va hacia delante
y su modo de grabación es tan lento que no sirve para un programa real.

Se usa **después** de `sanitizers`: primero se compila con ellos y se corre la suite, porque la
mayoría de los fallos de memoria y concurrencia salen ahí solos y con el sitio exacto. Esto es para el
que sobrevive a eso y solo aparece una vez de cada cien.

Ojo: **solo Linux**, y necesita contadores de rendimiento del procesador, así que en una máquina
virtual o en un contenedor de la nube muchas veces no arranca. Desde un portátil de otra familia se
usa contra una máquina o una máquina virtual Linux, no contra el propio sistema. Y la grabación
**serializa los hilos**: reproduce la carrera que grabó, pero al ralentizar el programa puede hacer
que la carrera no llegue a ocurrir durante la grabación — si no se caza a la primera, `rr record
--chaos` cambia la planificación para provocarla.
