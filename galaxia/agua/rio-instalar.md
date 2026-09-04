---
cosmos: rio
nombre: instalar
moja: []
momento: mantenimiento
invoca: python3 -m cosmos instalar
resumen: Todo el alta de una maquina nueva en un comando: arrancar, configurar y el estado de la maquina.
---

`git clone` y luego esto. Encadena `arrancar` (vista plana e índice), `configurar` (oficios,
herramientas, credenciales) y, si se piden, `--autonomia auto|libre`, `--modelos` y `--lanzador`;
termina con `estado --maquina`, que es el inventario trivalente de lo que hay y lo que falta en
ese ordenador.

No hay `curl | bash`: lo que se ejecuta ya está en disco y ha pasado por el índice, el escáner de
secretos y el gate. Nada de red en el camino crítico. Con `--oficios`/`--herramientas` no pregunta
nada y no toca los ajustes de usuario sin una bandera explícita; sin ellas pregunta lo mismo que
`configurar`. `--seco` lo cuenta sin escribir.
