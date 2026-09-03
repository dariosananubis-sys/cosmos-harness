---
cosmos: pueblo
nombre: vectorbt
padre: trading/estrategia/backtesting
resumen: Miles de combinaciones de parametros en el tiempo que un motor evento a evento tarda en una.
---

https://github.com/polakowo/vectorbt · Apache-2.0 con Commons Clause (leído en su `LICENSE.md`; la API de GitHub la reporta como `NOASSERTION`) · 8.945★ · último push 2026-08-02 (comprobado 2026-09-01)

```bash
pip install vectorbt
```

```python
import vectorbt as vbt

precio = vbt.YFData.download("BTC-USD").get("Close")   # solo para prototipar

# barrer TODAS las combinaciones de dos medias a la vez, no una por una
rapida, lenta = vbt.MA.run_combs(precio, window=range(5, 50), r=2)
entra = rapida.ma_crossed_above(lenta)
sale  = rapida.ma_crossed_below(lenta)

pf = vbt.Portfolio.from_signals(precio, entra, sale, fees=0.001, slippage=0.001)
print(pf.total_return().sort_values(ascending=False).head())
```

Sirve para **descartar rápido, no para decidir**. Modela comisiones y deslizamiento por operación y
trae validación hacia delante por ventanas. Ocupa un hueco que ningún otro cubre gratis: probar
miles de combinaciones en el tiempo que un motor evento a evento tarda en una.

Ojo, y es lo importante: al trabajar sobre **matrices de señales ya calculadas**, nada te obliga a
preguntarte qué sabías en el instante t, así que un `shift` mal puesto mete sesgo de anticipación
**sin que salte ningún error**. Regla del país: lo que sobreviva al barrido se vuelve a correr en un
motor evento a evento (`backtesting-py`, `nautilus-trader`) antes de creérselo. Y la licencia lleva
**Commons Clause**: usarlo y modificarlo es libre, venderlo o alquilarlo como servicio de
backtesting no — para montar bots propios o de cliente no estorba, para un producto sí.
