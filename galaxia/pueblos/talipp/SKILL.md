---
cosmos: pueblo
nombre: talipp
padre: trading/mercado/investigacion
resumen: Recalcula solo el ultimo valor al llegar un precio nuevo, sin rehacer la serie en cada tick.
---

https://github.com/nardew/talipp · MIT · 536★ · último push 2025-09-09 (comprobado 2026-09-01)

```bash
pip install talipp
```

```python
from talipp.indicators import SMA

sma = SMA(period=20, input_values=[1.0, 2.0, 3.0])   # arranque con lo que ya había
sma.add(4.0)      # llega un precio nuevo: recalcula SOLO el último valor
print(sma[-1])    # no rehace toda la serie

# la comprobación obligatoria: mismo resultado que el cálculo en lote
```

Es la diferencia entre un bot que aguanta el ritmo del mercado y uno que se atasca cuando hay que
mantener cincuenta indicadores sobre veinte pares. Frente a `ta-lib`, que recalcula la serie entera,
este actualiza solo el último valor al llegar el tick — para operar en vivo, no para estudiar.

Ojo, la comprobación obligatoria al usarlo: pasar la misma serie por el cálculo en lote (`ta-lib`) y
por el incremental y **exigir que coincidan**. Si no coinciden, el bot en vivo está operando con
números que el backtest nunca vio, y ese descuadre no da error, da pérdidas. Segundo aviso: es el
pueblo **menos activo** del país (último push 2025-09-09) y de comunidad pequeña — si algún día se
detiene, la salida es reimplementar el puñado de indicadores que uses en incremental sobre `ta-lib`,
no cambiar de librería.
