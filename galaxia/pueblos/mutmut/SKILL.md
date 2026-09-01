---
cosmos: pueblo
nombre: mutmut
padre: rendimiento/calidad
resumen: Rompe el codigo Python a proposito y mira si algun test se entera; el que sobrevive es una rama sin probar.
---

https://github.com/boxed/mutmut · BSD-3-Clause · 1.412★ · push 2026-08-17 (comprobado 2026-09-01, v3.7.0)

```bash
pip install mutmut

# se apunta a UN modulo, nunca al repositorio entero (ver el aviso de abajo)
mutmut run --paths-to-mutate src/facturacion/
mutmut results                 # resumen
mutmut browse                  # navegador de terminal: mutante por mutante
mutmut show <id>               # el diff exacto que sobrevivio
```

Cambia un `>` por un `>=`, un `+` por un `-`, un `True` por un `False`, y vuelve a correr las
pruebas. Si siguen en verde, esa linea no estaba protegida por ninguna asercion aunque la cobertura
dijera que si. Es la unica medida objetiva de si una suite comprueba algo: la cobertura dice que la
linea se ejecuto, no que alguien mirara el resultado.

**El aviso importante es el coste, y es de otro orden de magnitud.** El tiempo total sale de
multiplicar: *numero de mutantes × duracion de las pruebas que tocan ese codigo*. Un modulo mediano
genera de cientos a un par de miles de mutantes; con una suite relevante de diez segundos, mil
mutantes son del orden de **horas**, no de minutos. Frente a los segundos que cuesta un analizador
estatico, son dos o tres ordenes de magnitud. Consecuencia practica y no negociable: se corre
**sobre un modulo concreto**, y en integracion continua **de madrugada o a mano**, jamas en el gancho
de cada commit ni sobre todo el repositorio.

Ojo: la version 3 reescribio el motor y la linea de ordenes, asi que cualquier receta escrita para la
2 no vale. Exige una suite **verde y determinista**: con un test intermitente, cada ejecucion mata y
perdona mutantes distintos y el informe deja de significar nada. Y existen los **mutantes
equivalentes** —un cambio que no altera el comportamiento, asi que ningun test puede detectarlo—:
perseguirlos es tiempo perdido, se marcan y se ignoran. Con 1.412 estrellas no es un proyecto
grande; es la opcion mantenida de Python, no un estandar del sector, y eso hay que saberlo antes de
apoyar un proceso encima.
