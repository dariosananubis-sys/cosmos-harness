---
cosmos: pueblo
nombre: backtesting-py
padre: trading/backtesting
resumen: Bucle vela a vela de un solo activo: el modelo mental donde cuesta mas hacerse trampa sin verlo.
---

https://github.com/kernc/backtesting.py · AGPL-3.0 · 8.923★ · último push 2026-08-05 (comprobado 2026-09-01)

```bash
pip install backtesting
```

```python
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG          # datos de ejemplo que trae la librería

class Cruce(Strategy):
    n1, n2 = 10, 20
    def init(self):
        self.r = self.I(SMA, self.data.Close, self.n1)
        self.l = self.I(SMA, self.data.Close, self.n2)
    def next(self):                              # se ejecuta vela a vela
        if crossover(self.r, self.l): self.buy()
        elif crossover(self.l, self.r): self.position.close()

bt = Backtest(GOOG, Cruce, commission=.002, cash=10_000)
print(bt.run())        # la métrica que vale es la que EMPEORA al subir 'commission'
```

El contrapeso del barrido masivo. Como itera en el tiempo, cada decisión solo puede usar lo que ya
había ocurrido: el sesgo de anticipación no entra por descuido, tiene que escribirse a propósito.
Frente a `vectorbt`, que descarta mil combinaciones rápido pero trabaja sobre matrices ya
calculadas, este obliga a razonar «qué sé en el instante t».

**Modela**: comisión por operación y relleno dentro del rango de la vela, con órdenes de mercado,
límite y stop. **No modela**: cartera de varios instrumentos, libro de órdenes, latencia ni liquidez
— si tu tamaño mueve el precio, este motor no lo sabe. Regla que sale de ahí: el único número que
vale es el que empeora al añadir costes; una curva que solo sube cuando se quitan las comisiones no
es una estrategia.

Ojo con la licencia: **AGPL-3.0**. Libre para un bot propio o de cliente; obliga a liberar el código
si se ofrece como servicio de red a terceros.
