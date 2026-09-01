---
cosmos: pueblo
nombre: dask
padre: cientifico
resumen: Paraleliza con la interfaz de siempre y no reserva memoria por adelantado al arrancar.
---

Escala el mismo codigo de un hilo a un grupo de maquinas sin reescribirlo, con la interfaz de los
arrays y las tablas que ya se usan.

Se prefiere a la alternativa mas popular por una razon medible en una maquina de memoria justa:
aquella aparta cerca de un tercio de la memoria para su almacen de objetos nada mas arrancar. Esta no
reserva nada por adelantado y baja de escala sin friccion. Para un grupo de maquinas de verdad, la
otra sigue siendo la correcta.
