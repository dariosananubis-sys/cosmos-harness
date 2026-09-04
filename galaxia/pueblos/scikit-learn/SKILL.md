---
cosmos: pueblo
nombre: scikit-learn
padre: aprendizaje-automatico/entrenamiento
resumen: Los modelos clasicos con una sola interfaz y tuberias que impiden que el futuro se cuele en el entrenamiento.
---

https://github.com/scikit-learn/scikit-learn · BSD-3-Clause · 67.158★ · último push 2026-09-04
(comprobado 2026-09-04, API de GitHub y `commits/HEAD.atom`: HEAD 2026-09-04T06:13Z; no archivado)

```bash
pip install scikit-learn
```

```python
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)
X_ent, X_prueba, y_ent, y_prueba = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=0)          # stratify y semilla, siempre

tuberia = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
print(cross_val_score(tuberia, X_ent, y_ent, cv=5).mean())    # medida honesta, sin tocar la prueba
tuberia.fit(X_ent, y_ent)
print(tuberia.score(X_prueba, y_prueba))                      # el conjunto de prueba, una sola vez
```

Gana a `xgboost` y a `lightgbm` en lo que decide aquí, y conviene decirlo al revés de como suena:
**no gana en exactitud** —sobre datos tabulares el refuerzo por gradiente suele ganarle— sino en ser
la interfaz que habla todo el ecosistema. `fit`/`predict`/`score` es el contrato que implementan esos
dos, `optuna` y media docena más, así que empezar aquí no cierra ninguna puerta y cambiar el modelo
por uno de ellos es una línea.

Y la pieza que de verdad justifica el sitio es `Pipeline`: cualquier transformación que aprende algo
—escalar, imputar, codificar categorías— queda dentro, y la validación cruzada la reajusta en cada
pliegue. Escalar el conjunto entero antes de partirlo es la fuga de información más común del oficio
y aquí no se puede cometer sin salirse del camino marcado.

Ojo de máquina: no usa GPU y trabaja en un solo proceso con todo en memoria. En un M3 Pro de 18 GB
eso alcanza para tablas de millones de filas; a partir de ahí no es que vaya lento, es que el proceso
muere sin resultado. No hay modo de flujo salvo los pocos estimadores con `partial_fit`.

Ojo de medida: `score` devuelve el acierto medio, que con clases desiguales no informa —un 99 % con
un 1 % de positivos es contestar siempre que no—. Para eso están `f1`, `roc_auc` o
`average_precision` en `scoring=`, y elegirlos es parte del trabajo, no un detalle.
