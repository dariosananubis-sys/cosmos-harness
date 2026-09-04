---
cosmos: pueblo
nombre: langgraph
padre: agentes-ia/construccion
resumen: Orquesta agentes como grafo de estados con checkpoints; retoma un fallo desde el ultimo nodo, no desde cero.
---

https://github.com/langchain-ai/langgraph · MIT · 40.976★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
pip install langgraph
```

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class Estado(TypedDict):
    contador: int

def sumar(estado: Estado) -> Estado:
    return {"contador": estado["contador"] + 1}

grafo = StateGraph(Estado)
grafo.add_node("sumar", sumar)
grafo.set_entry_point("sumar")
grafo.add_conditional_edges("sumar", lambda e: END if e["contador"] >= 3 else "sumar")
app = grafo.compile()
print(app.invoke({"contador": 0}))
```

Gana a `claude-agent-sdk` cuando el flujo necesita **ramas explícitas, bucles con condición y
checkpoints persistentes** (retomar un agente parado a mitad, con su estado, tras un reinicio):
aquí el grafo se declara y se inspecciona como dato, no como código de control disperso entre
condicionales. Pierde frente a él en simplicidad para un agente de un solo bucle con
herramientas — ahí el SDK no obliga a aprender el vocabulario de nodos y aristas. Frontera con
`pydantic-ai`: aquel valida el contrato de entrada/salida de cada paso; esto orquesta el paso
entre pasos.

Ojo: el vocabulario de grafo es una capa mental extra sobre el mismo bucle de llamadas a
herramientas — para un agente de una sola tarea lineal es sobreingeniería. Y los checkpoints
persistentes (`MemorySaver`, `SqliteSaver`) guardan el estado completo en cada paso: en un grafo
con muchos nodos y estado grande, eso es I/O que crece con cada ejecución, no solo memoria de
proceso.
