---
cosmos: pueblo
nombre: mutmut
padre: refactorizacion/mutacion
resumen: Rompe el codigo Python a proposito y mira si algun test se entera; el que sobrevive es una rama sin probar.
---

https://github.com/boxed/mutmut · BSD-3-Clause · 1.412★ · push 2026-08-17 (comprobado 2026-09-01, v3.7.0)

```bash
pip install mutmut

# en setup.cfg (o [tool.mutmut] en pyproject.toml) hay que decirle donde esta el codigo:
#   [mutmut]
#   source_paths=calc/

mutmut run                        # todo el codigo configurado
mutmut run "calc.nucleo*"         # solo un modulo: se filtra por nombre de mutante, con comodines
mutmut results                    # los supervivientes
mutmut show <mutante>             # el cambio exacto que nadie detecto
mutmut browse                     # interfaz de terminal, mutante a mutante
mutmut print-time-estimates       # cuanto va a tardar, ANTES de lanzarlo
```

Cambia un `>` por un `>=`, un `+` por un `-`, un `True` por un `False`, y vuelve a correr las pruebas.
Si siguen en verde, esa linea no estaba protegida por ninguna asercion aunque la cobertura dijera que
si. Es la unica medida objetiva de si una suite comprueba algo: la cobertura dice que la linea se
ejecuto, no que alguien mirara el resultado.

Probado el 2026-09-01 sobre un modulo de dos funciones con un test cada una: 2 mutantes, 1 muerto y 1
superviviente — `calc.nucleo.x_es_mayor__mutmut_1`, que convierte `a > b` en `a >= b`. El test decia
`assert es_mayor(3, 2)`, que vale igual con las dos versiones. Eso es exactamente el hallazgo que
ninguna otra herramienta da.

**El aviso importante es el coste, y es de otro orden de magnitud.** El tiempo sale de multiplicar
*numero de mutantes × duracion de las pruebas que tocan ese codigo*. Un modulo mediano genera de
cientos a un par de miles de mutantes; con una suite relevante de diez segundos, mil mutantes son del
orden de **horas**, no de minutos — frente a los segundos que cuesta un analizador estatico, dos o tres
ordenes de magnitud mas. Por eso existe `print-time-estimates`, y por eso se corre **sobre un modulo
concreto** y en integracion continua **de madrugada o a mano**, jamas en el gancho de cada commit.
Ayuda `max_stack_depth` en la configuracion: descarta como cobertura las funciones alcanzadas de rebote
desde muy arriba, que son las que disparan el numero de pruebas por mutante.

Ojo, y estos tres cuestan una tarde si no se saben de antemano:

- **Cualquier orden falla si no encuentra el codigo**, incluida `mutmut --help`: la configuracion se
  carga al importar, asi que sin `source_paths` la primera ejecucion muere con un `FileNotFoundError`
  que parece un fallo de instalacion y no lo es.
- **Copia el proyecto a `mutants/` y lo reimporta**, asi que el codigo tiene que ser importable por su
  propio nombre de paquete. Si las pruebas hacen `from src.calc import ...`, aborta con `Failed
  trampoline hit. Module name starts with 'src.'`. El arreglo es el propio paquete (`from calc.nucleo
  import ...`), no una opcion.
- **Necesita `fork`**, asi que en Windows solo corre dentro de WSL.

Y lo de siempre en mutacion: exige una suite **verde y determinista** —con un test intermitente cada
ejecucion mata y perdona mutantes distintos y el informe deja de significar nada— y existen los
**mutantes equivalentes**, cambios que no alteran el comportamiento y que ningun test puede detectar:
se marcan y se ignoran, perseguirlos es tiempo perdido. Con 1.412 estrellas no es un proyecto grande:
es la opcion mantenida de Python, no un estandar del sector.
