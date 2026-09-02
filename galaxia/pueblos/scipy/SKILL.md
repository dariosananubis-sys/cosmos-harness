---
cosmos: pueblo
nombre: scipy
padre: cientifico
resumen: Optimizacion, integracion de ecuaciones y algebra dispersa sobre el array de referencia.
---

https://github.com/scipy/scipy · BSD-3-Clause · 14.976★ · último push 2026-09-01 (comprobado 2026-09-01)
(comprobado por API de GitHub el 2026-09-01).

```bash
pip install scipy
```

```python
import numpy as np
from scipy import optimize, integrate, sparse

# 1. ajustar una curva a datos con ruido
def modelo(x, a, b): return a * np.exp(-b * x)
x = np.linspace(0, 4, 50)
y = modelo(x, 2.5, 1.3) + np.random.default_rng(0).normal(0, 0.05, x.size)
parametros, covarianza = optimize.curve_fit(modelo, x, y)

# 2. integrar una ecuacion diferencial
sol = integrate.solve_ivp(lambda t, y: -0.5 * y, [0, 10], [1.0], dense_output=True)

# 3. algebra dispersa: una matriz de un millon de filas que cabe en memoria
M = sparse.random(1_000_000, 1_000_000, density=1e-7, format="csr", random_state=0)
```

Es donde se resuelve la mayor parte de "calculo numerico y algebra" sin salir de la pila cientifica
de facto. El array de `numpy` que tiene debajo no entra como pueblo propio: no es una eleccion, es
el sustrato de todo lo demas. Y `JuliaLang/julia` (49k estrellas, MIT), que resuelve el mismo
problema mas rapido y con bloqueo de dependencias de fabrica, queda citado y fuera: cambiar de
lenguaje es una decision de proyecto, no una herramienta que se anade.

Y lo que no hace bien, en clave de reproducibilidad —que es el criterio de este nicho: el resultado
depende de la BLAS que traiga la rueda instalada y del numero de hilos que decida en tiempo de
ejecucion. Dos maquinas con el mismo `scipy` pueden dar ultimos decimales distintos. Si el resultado
tiene que ser identico, se fija `OMP_NUM_THREADS=1` y se registra la version de BLAS
(`scipy.show_config()`) junto al resultado, no despues.

Y el falso verde clasico: `optimize.curve_fit` y `minimize` devuelven un resultado siempre. Hay que
mirar `sol.success` y la covarianza — un ajuste que no convergio se parece mucho a uno que si, hasta
que lo publicas.
