---
cosmos: pueblo
nombre: uptime-kuma
padre: infraestructura/vigilancia
resumen: Comprueba desde fuera que los servicios responden y avisa cuando dejan de hacerlo.
---

Comprobacion externa, que es la unica que detecta la caida entera. Tiene ademas monitores de
empuje, asi que cubre tambien el interruptor de hombre muerto de una tarea programada.

Por eso queda fuera la herramienta dedicada solo a vigilar tareas programadas: se solapa.
