---
cosmos: pueblo
nombre: sanitizers
padre: rendimiento/depuracion
resumen: Detectan en ejecucion el desbordamiento, el uso despues de liberar y la carrera que ningun test ve.
---

No tienen competidor real: son la implementacion de referencia y estan integrados en los dos
compiladores mayores, asi que se activan con una bandera.

Se usan antes que `rr`: primero se compila con ellos y se corre la suite, porque la mayoria de los
fallos de memoria y de concurrencia salen ahi solos y con el sitio exacto. `rr` es para el que
sobrevive a esto y solo aparece una vez de cada cien.
