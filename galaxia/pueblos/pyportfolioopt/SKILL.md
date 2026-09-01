---
cosmos: pueblo
nombre: pyportfolioopt
padre: trading/riesgo
resumen: Reparte capital entre activos con frontera eficiente, CVaR y paridad de riesgo jerarquica.
---

https://github.com/PyPortfolio/PyPortfolioOpt · MIT · 6.002★ · último push 2026-07-07 (comprobado 2026-09-01)

```bash
pip install PyPortfolioOpt
```

```python
from pypfopt import EfficientFrontier, expected_returns, risk_models
import pandas as pd

precios = pd.read_parquet("precios.parquet")     # columnas = activos
mu = expected_returns.mean_historical_return(precios)
S  = risk_models.sample_cov(precios)

ef = EfficientFrontier(mu, S)
pesos = ef.max_sharpe()                          # cuánto va a CADA activo
print(ef.clean_weights())
```

Resuelve **cuánto va a cada activo** con frontera eficiente, CVaR y paridad de riesgo jerárquica. Se
apoya en `cientifico/scipy`, que es el sustrato de la optimización.

Ojo, lo que **no** resuelve y hay que escribir a mano: cuánto se arriesga en **una entrada concreta**
— la fracción fija y el criterio de Kelly no tienen librería madura en ningún sitio, y hoy se
escriben dentro del bot. Es de las pocas piezas de este nicho que hay que programar en vez de
instalar, y es de las primeras que Darío necesita para un bot que arriesga por operación. Segundo
aviso, el clásico de la optimización de cartera: los pesos que salen dependen por completo de `mu` y
`S` estimados del pasado — la media histórica de rentabilidad es un estimador ruidoso, y una frontera
eficiente sobre datos ruidosos reparte con falsa precisión. Los métodos robustos (Ledoit-Wolf para la
covarianza, paridad de riesgo) existen aquí justo por eso.
