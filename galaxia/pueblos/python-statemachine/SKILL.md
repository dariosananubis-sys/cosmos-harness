---
cosmos: pueblo
nombre: python-statemachine
padre: trading/bots/codigo-de-bot
resumen: El ciclo de vida de una orden como transiciones declaradas: lo prohibido falla al intentarlo.
---

https://github.com/fgmacedo/python-statemachine · MIT · 1.299★ · último push 2026-08-17 (comprobado 2026-09-01)

```bash
pip install python-statemachine
```

```python
from statemachine import StateMachine, State

class Orden(StateMachine):
    enviada   = State(initial=True)
    aceptada  = State()
    llena     = State(final=True)
    cancelada = State(final=True)

    aceptar  = enviada.to(aceptada)
    ejecutar = aceptada.to(llena)
    cancelar = enviada.to(cancelada) | aceptada.to(cancelada)

o = Orden()
o.aceptar()
# o.cancelar() ahora lanzaría TransitionNotAllowed: cancelada->llena no existe
```

Una orden pasa por enviada, aceptada, parcial, llena, cancelada y rechazada, y el mercado manda esos
avisos desordenados, repetidos y a veces después de haber cerrado. Escrito con condicionales
sueltos, la transición imposible se cuela y se descubre con dinero puesto. Declarada, el intento de
pasar de cancelada a llena **revienta en el sitio y con el nombre exacto** — la diferencia entre un
fallo ruidoso y un descuadre silencioso.

Gana a `pytransitions/transitions` (6.582★, último push 2025-09-11) pese a tener **cinco veces menos
estrellas**: la otra lleva un año sin publicar y esto es código que decide si una orden puede pasar
de cancelada a llena. Ojo: modela el ciclo de vida, no la idempotencia — que el mismo aviso de
ejecución llegue dos veces hay que resolverlo aparte (identificador de ejecución ya visto), la
máquina de estados sola no lo hace.
