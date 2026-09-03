---
cosmos: pueblo
nombre: ta-lib
padre: trading/mercado/investigacion
resumen: El vocabulario comun: nucleo en C, decadas de uso y el mismo resultado que espera todo el mundo.
---

https://github.com/TA-Lib/ta-lib-python · BSD-2-Clause · 12.222★ · último push 2026-08-29 (comprobado 2026-09-01)

```bash
brew install ta-lib      # la librería de C por debajo, el roce real de la instalación
pip install TA-Lib       # el enlace de Python
```

```python
import numpy as np, talib

cierre = np.random.random(200)              # en real: la serie de cierres
sma = talib.SMA(cierre, timeperiod=20)      # calcula sobre la serie ENTERA
rsi = talib.RSI(cierre, timeperiod=14)
macd, senal, hist = talib.MACD(cierre)
```

Entra porque es la **referencia contra la que se comparan las demás**: cuando dos librerías
discrepan en una media móvil, la que suele tener razón es esta. Su único roce real es la instalación,
que exige la librería de C por debajo (de ahí el `brew install` antes del `pip`). Calcula sobre la
serie entera, que es lo que hace falta al estudiar y lo que sobra en el bucle en vivo — para eso
está `talipp`: lote para estudiar, incremental para operar.

Ojo, caso raro comprobado que ahorra buscar un 404: la librería de indicadores sobre dataframes más
citada durante años, `pandas-ta`, **ya no existe en su dirección original** (`twopirllc/pandas-ta`
da 404). Si un tutorial o un cliente pide `pandas-ta`, hoy el que vive es el mantenido por la
comunidad, `xgboosted/pandas-ta-classic` (427★, activo).
