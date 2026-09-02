---
cosmos: pueblo
nombre: nautilus-trader
padre: trading/bots/motores
resumen: Motor de eventos con nucleo en Rust: el mismo codigo corre en simulacion y en vivo sin tocarlo.
---

https://github.com/nautechsystems/nautilus_trader · LGPL-3.0 · 28.248★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
pip install nautilus_trader
```

```python
# el backtest y el vivo comparten la MISMA clase de estrategia; cambia el adaptador
from nautilus_trader.trading.strategy import Strategy

class MiEstrategia(Strategy):
    def on_bar(self, bar):
        # esta lógica corre idéntica en simulación y en producción
        ...
# BacktestEngine para investigar → TradingNode para vivo, sin tocar la estrategia
```

Que la simulación y el vivo compartan la misma semántica de ejecución y el mismo reloj determinista
es lo que impide el fallo clásico: tener dos comportamientos y descubrirlo con dinero puesto. Guarda
el estado fuera del proceso (Redis), que es lo que permite reiniciar con posiciones abiertas sin
perderlas.

**Modela**: reloj de nanosegundos, cotizaciones y operaciones tick a tick, barras y libro real, con
comisiones y deslizamiento por adaptador. **No modela** por sí solo la posición en la cola del libro
— para eso, `hftbacktest`. Frente a `quantconnect-lean`, que ocupa el mismo hueco de motor completo:
aquel desmonta el realismo en modelos por mercado que se auditan uno a uno; este garantiza que lo que
probaste es literalmente lo que corre. Ojo: núcleo en Rust y modelo de eventos tienen **curva de
entrada** — es más motor del que necesita un primer bot de una estrategia sobre velas, ahí
`backtesting-py` o `freqtrade` llegan antes.
