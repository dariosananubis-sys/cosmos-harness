---
cosmos: pueblo
nombre: ta
padre: trading/mercado/investigacion
resumen: Los indicadores en Python puro sobre un DataFrame: sin compilar nada, al precio de ir mas lento que el C.
---

https://github.com/bukosabino/ta · MIT · 5.183★ · último push 2026-03-18 (comprobado 2026-09-03, API de GitHub y `commits/HEAD.atom`; cadencia lenta pero no parado: la alternativa habitual, `pandas-ta`, devuelve 404 ese mismo día)

```bash
pip install ta
```

```python
import pandas as pd, ta
df = pd.read_csv("ohlcv.csv")                       # columnas open, high, low, close, volume
df["rsi"]  = ta.momentum.rsi(df["close"], window=14)
df["macd"] = ta.trend.macd_diff(df["close"])
df = ta.add_all_ta_features(df, "open", "high", "low", "close", "volume")   # los ~90 de golpe
```

Por qué existe teniendo `ta-lib` al lado en este mismo país: aquél es un enlace a una biblioteca de
C que hay que **compilar o instalar con brew** —el roce real de su instalación—, y este es Python puro
sobre `pandas`, que se instala en cualquier sitio donde ya haya un DataFrame, incluido un cuaderno o
un contenedor mínimo. Para el estudio en lote de una serie, da los indicadores clásicos con nombres
legibles y una sola llamada que los añade todos como columnas.

Ojo, dos cosas que no hace. Es **solo lote**: no tiene modo incremental, así que la barra que llega
en vivo se recalcula sobre la ventana entera (para eso, la propia `ta-lib` trae `talib.stream`, que
es como este país garantiza que el vivo y el backtest den el mismo número). Y es más lento que el C
en órdenes de magnitud sobre series largas: si el cuello de botella es el cálculo y no la
instalación, se está en el pueblo equivocado.
