---
cosmos: pueblo
nombre: py-spy
padre: rendimiento/perfilado
resumen: Se engancha a un proceso de Python ya en marcha y lo perfila sin reiniciarlo ni tocar su codigo.
---

Es lo que `samply` no puede hacer: mirar dentro de un servicio que ya esta corriendo en produccion,
leyendo la memoria del proceso, sin instrumentar nada ni pedir una parada.

Ese es exactamente el caso en el que el perfilado importa —el proceso que va lento ahora y que nadie
puede reiniciar para investigarlo— y lo que ningun analisis estatico puede deducir sin medir.
