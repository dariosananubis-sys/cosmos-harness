---
cosmos: pueblo
nombre: optuna
padre: aprendizaje-automatico/entrenamiento
resumen: Busca hiperparametros cortando por lo sano el intento que ya va mal, en vez de recorrer la rejilla entera.
---

https://github.com/optuna/optuna · MIT · 14.744★ · último push 2026-09-04 (comprobado 2026-09-04,
API de GitHub y `commits/HEAD.atom`: HEAD 2026-09-04T06:25Z; no archivado)

```bash
pip install optuna
```

```python
import optuna
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

X, y = load_breast_cancer(return_X_y=True)

def objetivo(intento):
    modelo = RandomForestClassifier(
        n_estimators=intento.suggest_int("n_estimators", 50, 500),
        max_depth=intento.suggest_int("max_depth", 2, 16),
        min_samples_leaf=intento.suggest_int("min_samples_leaf", 1, 8),
        random_state=0,
    )
    return cross_val_score(modelo, X, y, cv=3, scoring="roc_auc").mean()

# storage= en fichero: si el proceso muere, la busqueda se reanuda donde iba
estudio = optuna.create_study(direction="maximize", study_name="bosque",
                              storage="sqlite:///estudio.db", load_if_exists=True)
estudio.optimize(objetivo, n_trials=30)
print(estudio.best_params, estudio.best_value)
```

Gana a `GridSearchCV` y a `RandomizedSearchCV` de `scikit-learn` en dos cosas medibles. Una, el
espacio se declara **dentro** de la función, así que puede ser condicional —los parámetros de un
árbol solo existen si el intento eligió árbol— y una rejilla no puede expresar eso. Dos, poda: con
un objetivo que reporta valores intermedios, corta el intento que ya va peor que la mediana en lugar
de terminarlo, y ahí es donde aparece el ahorro real de horas.

Frontera con `mlflow`, que vive en `agentes-ia/evaluacion`: `optuna` **busca** y guarda su propia
historia en su base de datos; aquel **registra** lo que pasó en cada ejecución para poder compararlo
meses después. Se usan juntos y no se solapan.

Ojo: la poda no funciona sola. Si el objetivo devuelve un único número al final —como el ejemplo de
arriba, que hace validación cruzada entera— no hay nada intermedio que podar y el ahorro es cero. Hay
que llamar a `intento.report(valor, paso)` y comprobar `intento.should_prune()` dentro del bucle de
entrenamiento; sin eso, la promesa de la ficha no se cumple y parece que sí.

Ojo de honestidad: probar trescientas combinaciones y quedarse con la mejor sobre la misma validación
es pescar ruido. El mejor valor que imprime `best_value` está optimizado contra esos pliegues y es
optimista; el número que se publica sale del conjunto de prueba apartado, que no ha entrado aquí.
