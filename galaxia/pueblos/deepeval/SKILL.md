---
cosmos: pueblo
nombre: deepeval
padre: agentes-ia/evaluacion
resumen: Evalua salidas de LLM con metricas tipo pytest: fidelidad, relevancia, alucinacion, en el propio CI.
---

https://github.com/confident-ai/deepeval · Apache-2.0 · 18.072★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
pip install deepeval
```

```python
from deepeval import assert_test
from deepeval.metrics import HallucinationMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

caso = LLMTestCase(
    input="Cual es la capital de Francia?",
    actual_output="La capital de Francia es Paris.",
    context=["Paris es la capital de Francia desde el siglo X."],
)
assert_test(caso, [HallucinationMetric(threshold=0.5), AnswerRelevancyMetric(threshold=0.7)])
```

```bash
deepeval test run test_agente.py     # codigo de salida != 0 si una metrica no pasa: rompe el CI
```

Gana a `promptfoo` cuando la evaluación vive **dentro del código Python del agente**, como un test
más de la suite (`pytest` lo descubre igual que cualquier otro `test_*.py`) y las métricas
(fidelidad, relevancia, alucinación, sesgo, toxicidad) se combinan por caso. Pierde frente a él
cuando lo que hace falta es una matriz declarativa de prompts × modelos × casos sin escribir
Python, o red teaming automatizado — eso lo cubre `promptfoo`.

Ojo: varias métricas (`HallucinationMetric`, `AnswerRelevancyMetric`) usan **otro LLM como juez**
por defecto — eso es una llamada de pago adicional por cada caso evaluado, y el juez también se
equivoca: calibrar el umbral con un conjunto de casos ya etiquetados a mano antes de fiarse del
número. Sin ese LLM juez bien configurado, cae a heurísticas más débiles sin avisar tan alto como
debería.
