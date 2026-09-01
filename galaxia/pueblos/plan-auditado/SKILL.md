---
cosmos: pueblo
nombre: plan-auditado
padre: agentes-ia/construccion
resumen: Audita el plan antes de creerselo: campos, tipos, dependencias que existen y rastro de lo que dice estar hecho.
---

`cosecha/audit-harness.sh` — recorre la lista de tareas de cada proyecto y la valida como un
contrato: campos obligatorios presentes, tipos correctos, estado dentro de los permitidos, criterios
de aceptacion con su prefijo numerado, y **dependencias que apuntan a identificadores que existen de
verdad**. Ese ultimo es el que se cuela siempre: un plan con una dependencia fantasma parece
completo y bloquea en silencio.

La segunda mitad separa lo declarado de lo demostrado: si una tarea dice estar terminada, exige su
registro con la linea que lo acredita; si dice llevar diseno previo, exige el documento. Un estado
terminado sin rastro es la forma mas comun de mentira en un plan, y casi nunca es deliberada.

Funciona con o sin analizador de JSON instalado: si no lo hay, usa un lector propio en vez de
saltarse la comprobacion. Una validacion que se desactiva sola cuando falta una dependencia es peor
que no tenerla, porque pasa en verde.
