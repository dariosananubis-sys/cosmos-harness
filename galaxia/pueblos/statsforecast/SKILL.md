---
cosmos: pueblo
nombre: statsforecast
padre: analitica
resumen: Prevision con modelos estadisticos clasicos, rapidos y explicables, sin redes neuronales.
---

https://github.com/Nixtla/statsforecast · Apache-2.0 · 4.892★ · último push 2026-09-01 (comprobado 2026-09-01)
(comprobado por API de GitHub el 2026-09-01).

```bash
pip install statsforecast
```

```python
import pandas as pd
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, AutoETS, SeasonalNaive

# el formato es fijo: unique_id (la serie), ds (la fecha), y (el valor)
df = pd.read_parquet("datos/serie.parquet")[["unique_id", "ds", "y"]]

sf = StatsForecast(
    models=[AutoARIMA(season_length=12), AutoETS(season_length=12), SeasonalNaive(season_length=12)],
    freq="MS", n_jobs=-1,
)
pred = sf.forecast(df=df, h=12, level=[80, 95])     # con intervalos, no solo el punto
print(pred.head())

# y la comprobacion que de verdad importa: validacion cruzada temporal
cv = sf.cross_validation(df=df, h=12, step_size=12, n_windows=3)
```

En una maquina de ocho gigas los modelos estadisticos ganan por goleada a cualquier red neuronal: se
ajustan en segundos, no necesitan GPU ni un tiempo de ejecucion de aprendizaje profundo cargado en
memoria, y se puede explicar por que dan lo que dan. Descartado `facebook/prophet` —el modelo de
prevision mas famoso del sector, y el rival real—: arrastra un motor de inferencia bayesiana pesado,
tarda mucho mas en ajustar y se comporta peor en series cortas.

Y lo que no hace bien, que es donde se falsea una prevision:

- **`SeasonalNaive` esta en el ejemplo a proposito.** Es la referencia contra la que hay que medir:
  una prevision que no bate a "repite lo del ano pasado" no vale nada, aunque el grafico quede
  bonito. Sin esa comparacion, cualquier numero parece bueno.
- **El punto sin intervalo es un numero inventado.** Por eso `level=[80, 95]` va en el ejemplo: la
  incertidumbre se publica junto a la prediccion, no se omite.
- **Un ajuste sobre todo el historico no dice nada sobre el futuro.** Lo que mide de verdad es
  `cross_validation` con ventanas moviles. Un error de entrenamiento bajo es el falso verde clasico
  de este pueblo.
- Espera series regulares y sin huecos. Si faltan periodos, hay que rellenarlos antes; no avisa.
