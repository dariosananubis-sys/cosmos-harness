---
cosmos: pueblo
nombre: quantstats
padre: trading/estrategia/riesgo
resumen: Convierte una serie de resultados en Sharpe, caida maxima e informe comparado con una referencia.
---

https://github.com/ranaroussi/quantstats · Apache-2.0 · 7.601★ · último push 2026-07-20 (comprobado 2026-09-01)

```bash
pip install quantstats
```

```python
import quantstats as qs

retornos = qs.utils.download_returns("SPY")      # aquí: la serie de tu backtest

print(qs.stats.sharpe(retornos))
print(qs.stats.max_drawdown(retornos))
qs.reports.html(retornos, benchmark="SPY", output="informe.html")
```

Se enchufa a la salida de **cualquier** motor, así que la comparación entre dos backtests hechos con
motores distintos se hace aquí y no a ojo — misma vara para todos. Sustituye a la librería
equivalente del ecosistema que murió con Quantopian (`pyfolio`, sin publicar desde 2023). Aquí se
mide lo ya ocurrido; el cuadro de mando que mira otra persona es `analitica/cuadros-de-mando/evidence`.

Ojo: es una **capa de informe**, no de validación — calcula el Sharpe que le des de comer, y un
Sharpe altísimo suele ser la señal de un backtest con sesgo de anticipación, no de una buena
estrategia. El número bonito de aquí se cree solo después de que el motor evento a evento y los
comprobadores de sesgo (`freqtrade lookahead-analysis`) hayan dado su visto bueno. Y compara contra
la referencia que le pases: elegir un `benchmark` fácil de batir es engañarse con permiso.
