---
cosmos: pueblo
nombre: bentoml
padre: aprendizaje-automatico
resumen: Empaqueta el modelo con su codigo de servicio y sus dependencias en una imagen que arranca igual en cualquier sitio.
---

https://github.com/bentoml/BentoML · Apache-2.0 · 8.820★ · último push 2026-08-28 (comprobado
2026-09-04, API de GitHub y `commits/HEAD.atom`: HEAD 2026-08-28T09:19Z; no archivado)

```bash
pip install bentoml
```

```python
# servicio.py
import bentoml
import joblib
import numpy as np


@bentoml.service(resources={"cpu": "1"}, traffic={"timeout": 10})
class Clasificador:
    def __init__(self) -> None:
        self.modelo = joblib.load("modelo.joblib")     # el artefacto que dejo el entrenamiento

    @bentoml.api
    def predecir(self, filas: list[list[float]]) -> list[int]:
        return self.modelo.predict(np.array(filas)).tolist()
```

```bash
bentoml serve servicio:Clasificador          # http://localhost:3000, con OpenAPI y pagina de prueba
curl -s -X POST http://localhost:3000/predecir \
  -H 'content-type: application/json' -d '{"filas": [[0.1, 2.4, 3.0]]}'

bentoml build                                 # empaqueta codigo + dependencias + modelo
bentoml containerize clasificador:latest      # y de ahi sale una imagen de contenedor
```

Gana a `mlflow models serve` —el otro camino corto, y `mlflow` está en el árbol, en
`agentes-ia/evaluacion`— en lo que separa una demostración de un servicio: aquel levanta un servidor
de conveniencia alrededor del artefacto registrado, con la firma que el artefacto tenga; este parte
del **código de servicio** que tú escribes, así que caben el preprocesado, varios modelos en la misma
clase, la validación de la entrada y el agrupado automático de peticiones.

Frontera con `infraestructura`, que es el vecino declarado del oficio: lo que sale de aquí es una
imagen de contenedor normal. Desplegarla, escalarla y vigilarla no es trabajo de este pueblo.

Ojo de tamaño: la imagen hereda todas las dependencias del entorno. Con `scikit-learn` ronda unos
cientos de megas; en cuanto entra `torch` con CUDA se va a varios gigas, y eso se paga en cada
despliegue y en cada arranque en frío.

Ojo de arquitectura, y muerde en un Mac: `bentoml containerize` en Apple Silicon produce una imagen
`arm64`. Subida a un servidor `amd64` no arranca, y el error llega en el despliegue, no aquí — hay
que construirla con `--platform linux/amd64` cuando el destino sea x86.

Ojo: `resources={"cpu": "1"}` es una **declaración** que leen los orquestadores, no un límite que
imponga nada en tu portátil. En local el servicio usará lo que le dé la gana.
