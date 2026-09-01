---
cosmos: pueblo
nombre: freertos
padre: embebidos
resumen: El nucleo mas pequeno y mas desplegado: planificador, colas y semaforos, y nada mas alrededor.
---

Empata a proposito con `zephyr`, y el criterio de eleccion es este: aqui cuando hace falta el nucleo
minimo, cuando la placa apenas tiene memoria o cuando ya existe codigo escrito sobre el; alli cuando
el proyecto es nuevo y quiere de fabrica soporte de cientos de placas, controladores, radio, sistema
de ficheros y arranque firmado.

Dicho de otro modo: este es un planificador, aquel es un sistema operativo con su ecosistema. Elegir
el segundo por costumbre en una placa diminuta se paga en memoria.
