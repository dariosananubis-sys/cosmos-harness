---
cosmos: pueblo
nombre: mimalloc
padre: rendimiento
resumen: Reservador de memoria de sustitucion directa: se enlaza o se precarga y se nota, sin tocar el codigo.
---

Es de las pocas mejoras de rendimiento que no exige entender el programa: se cambia el reservador y se
mide con `hyperfine` antes y despues.

Gana a la alternativa clasica del hueco por facilidad de adopcion en un proyecto nuevo y por soporte
nativo de la arquitectura de los portatiles actuales. Como toda optimizacion, entra despues de medir:
si el programa no reserva memoria en el camino caliente, no cambia nada.
