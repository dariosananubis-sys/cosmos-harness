---
cosmos: pueblo
nombre: py-spy
padre: rendimiento/perfilado
resumen: Se engancha a un proceso de Python ya en marcha y lo perfila sin reiniciarlo ni tocar su codigo.
---

https://github.com/benfred/py-spy · MIT · 15.463★ · push 2026-08-14 (comprobado 2026-09-01)

```bash
pip install py-spy

py-spy top --pid <PID>                                  # como 'top', pero por funcion de Python
py-spy record --pid <PID> --duration 30 -o perfil.svg   # grafico de llama
py-spy dump --pid <PID>                                 # pila de CADA hilo, ahora mismo
# en macOS y en un contenedor hace falta permiso: sudo, o --cap-add SYS_PTRACE
```

Es lo que `samply` no puede hacer: **mirar dentro de un servicio que ya está corriendo en producción**,
leyendo la memoria del proceso desde fuera, sin instrumentar nada, sin importar un módulo y sin pedir
una parada. Ese es exactamente el caso en el que el perfilado importa —el proceso que va lento ahora y
que nadie puede reiniciar para investigarlo— y lo que ningún análisis estático puede deducir sin
medir. Gana a `cProfile` por eso mismo: `cProfile` exige envolver el código y reiniciar, y su
sobrecoste distorsiona lo que mide.

`py-spy dump` es además la respuesta a un proceso **colgado**: enseña en qué línea está bloqueado cada
hilo sin tocarlo.

Ojo: es un perfilador de **muestreo**, así que una función muy corta llamada un millón de veces puede
no aparecer, y los números son proporciones, no cuentas exactas. No ve el tiempo pasado dentro de
código nativo (numpy, extensiones en C) más allá de la llamada que lo invoca. Y `--native` requiere
símbolos: sin ellos, la parte nativa sale como direcciones ilegibles.
