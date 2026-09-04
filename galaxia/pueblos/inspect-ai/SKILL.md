---
cosmos: pueblo
nombre: inspect-ai
padre: agentes-ia/evaluacion
resumen: Framework de evals con log de traza completa por muestra; el usado por labs para evals de seguridad.
---

https://github.com/UKGovernmentBEIS/inspect_ai · MIT · 2.692★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
pip install inspect-ai
```

```python
# tarea.py
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import generate

@task
def suma_simple():
    return Task(
        dataset=[Sample(input="Cuanto es 12 + 30?", target="42")],
        solver=[generate()],
        scorer=match(numeric=True),
    )
```

```bash
inspect eval tarea.py --model anthropic/claude-sonnet-4-5
inspect view      # explorador web de la traza completa de cada muestra
```

Gana a `deepeval` y a `promptfoo` en **auditoría**: cada muestra guarda la traza completa
(prompt, herramientas invocadas, tokens, puntuación) en un log inspeccionable con `inspect view`,
el mismo formato que usan los propios evals de seguridad de los laboratorios que lo mantienen
(UK AI Security Institute). Pierde frente a ambos en arranque rápido: su vocabulario propio
(`Task`, `Solver`, `Scorer`) pide más código para el mismo caso simple que un YAML de `promptfoo`.

Ojo: pensado para evals de investigación y seguridad (razonamiento, uso de herramientas
peligrosas en sandbox), no para un pipeline de CI ligero — el sandbox de ejecución (`--sandbox
docker`) añade un contenedor por tarea, que es coste de máquina real si se corre en cada commit.
