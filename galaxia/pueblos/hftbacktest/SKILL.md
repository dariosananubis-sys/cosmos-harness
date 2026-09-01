---
cosmos: pueblo
nombre: hftbacktest
padre: trading/backtesting
resumen: Simula posicion en cola y latencia sobre libro completo: el unico que no se engana solo.
---

https://github.com/nkaz001/hftbacktest · MIT · 4.574★ · último push 2025-12-23 (comprobado 2026-09-01 — es el menos activo del país, vigilar)

```bash
pip install hftbacktest
```

```python
import numpy as np
from hftbacktest import BacktestAsset, HashMapMarketDepthBacktest, GTX, LIMIT

# la latencia y las comisiones son parámetros explícitos, no supuestos ocultos
activo = (
    BacktestAsset()
      .data(["datos_l2_tick.npz"])          # exige libro nivel 2/3 reconstruido
      .linear_asset(1.0)
      .constant_latency(10_000_000, 10_000_000)   # 10 ms feed / 10 ms orden, en ns
      .maker_fee(-0.00005).taker_fee(0.0007)
)
hbt = HashMapMarketDepthBacktest([activo])
# dentro del bucle: hbt.submit_buy_order(0, id, precio, qty, GTX, LIMIT, ...)
```

Modela lo que los demás ignoran: **dónde queda tu orden en la cola del libro** y cuánto tarda en
llegar, con retardo de datos y de orden configurables por separado. Sin eso, cualquier estrategia
que ponga precio sale rentable en el papel. Frente a sus hermanos: `backtesting-py` no ve el libro,
`vectorbt` ni siquiera itera en el tiempo, y `quantconnect-lean` modela el coste pero no la cola.

Ojo, lo que exige a cambio: **datos de libro nivel 2 o 3 reconstruidos tick a tick**. Ese dato ni es
gratis ni es cómodo de conseguir, y es el motivo real por el que casi nadie backtestea así. Regla
del país: si la estrategia cruza el diferencial y aguanta horas, cualquier motor vale; si vive
dentro del diferencial, solo vale este. Y darle velas en vez de libro lo convierte en un motor peor
que los otros, sin avisar — es un mal uso, no un fallo suyo.
