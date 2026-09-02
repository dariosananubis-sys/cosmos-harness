---
cosmos: pueblo
nombre: hypothesis
padre: trading/bots/codigo-de-bot
resumen: Genera las secuencias de eventos que nadie escribiria y comprueba que el invariante aguanta.
---

https://github.com/HypothesisWorks/hypothesis · MPL-2.0 (leído en su `LICENSE.txt`; la API de GitHub la reporta como `NOASSERTION`) · 8.930★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
pip install hypothesis
```

```python
from hypothesis import given, strategies as st

# no se prueba un ejemplo: se prueba un invariante contra miles de casos generados
@given(
    ejecuciones=st.lists(st.floats(min_value=0, max_value=100), max_size=50),
    pedido=st.floats(min_value=0, max_value=100),
)
def test_nunca_se_ejecuta_de_mas(ejecuciones, pedido):
    posicion = min(sum(ejecuciones), pedido)     # el código real del bot
    assert posicion <= pedido        # la suma de ejecuciones nunca supera lo pedido
```

Aquí no se prueban ejemplos, se prueban **invariantes**: el efectivo nunca queda negativo, la suma
de ejecuciones nunca supera lo pedido, el mismo aviso de ejecución dos veces no cuenta dos veces,
cerrar una posición que no existe no abre la contraria. Su modo de máquina de estados
(`RuleBasedStateMachine`) construye órdenes de llamadas que a nadie se le ocurren y, cuando rompe,
**reduce el fallo al caso mínimo** que lo reproduce — que es lo que convierte un fallo raro en un
test permanente.

Complementa al mar `pruebas` sin repetirlo: allí la mutación mide si un test afirma algo; aquí se
busca el contraejemplo. Ojo: encuentra el caso que rompe, no arregla el diseño — si el invariante
está mal escrito, pasará en verde mientras el bot pierde dinero. Y una suite con generación amplia
es **lenta**: se fija una semilla y un presupuesto de ejemplos para que sea determinista en
integración continua. Licencia MPL-2.0.
