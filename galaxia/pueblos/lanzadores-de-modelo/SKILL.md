---
cosmos: pueblo
nombre: lanzadores-de-modelo
padre: agentes-ia/coste
resumen: Arranca cada tarea con el modelo mas barato que la resuelve y con el perfil minimo de servidores externos.
---

`cosecha/claude-code/` — familia de lanzadores con ajustes de coste y esfuerzo, un clasificador que
propone modelo segun la tarea, y dos perfiles de servidores externos: el minimo y el completo. Lo
segundo importa tanto como lo primero, porque un servidor conectado y sin usar se paga en cada
sesion aunque no se invoque.

`cosecha/modelos-fijar.py` — fija que modelo usa cada papel por variable de entorno y valida el
nombre antes de dejarlo puesto, para que un modelo mal escrito falle al arrancar y no a mitad de un
trabajo largo.

La regla que materializa: decidir con el modelo caro, ejecutar con el barato. Bajar el esfuerzo de
razonamiento apenas ahorra; elegir bien el modelo y no arrastrar herramientas, si.
