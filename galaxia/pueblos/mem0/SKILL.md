---
cosmos: pueblo
nombre: mem0
padre: agentes-ia/memoria
resumen: Capa de recuerdos con extraccion y busqueda, servible desde cualquier tiempo de ejecucion de agente.
---

https://github.com/mem0ai/mem0 · Apache-2.0 · 64.500★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
pip install mem0ai
```

```python
from mem0 import Memory
memoria = Memory()          # autoalojada: SQLite + almacén vectorial local
memoria.add("Prefiere los informes en castellano y en una sola pagina", user_id="<usuario>")
print(memoria.search(query="en que idioma escribo el informe", filters={"user_id": "<usuario>"}, top_k=3))
```

El genérico, para agentes propios construidos sobre un SDK: extrae hechos de la conversación y los
recupera por relevancia, sin atarse a un asistente concreto. Es la pieza que hace falta cuando la
memoria tiene que ser compartida entre tiempos de ejecución o modelos distintos.

Gana a `letta-ai/letta` (24.524★) para este caso porque `letta` monta un **servidor con estado** que se
solapa a la vez con esto y con la base vectorial: dos procesos permanentes donde bastaba una
biblioteca. `MemTensor/MemOS` (11.133★) resuelve lo mismo con menos adopción. Y frente a `claude-mem`,
la frontera es clara: aquel es para el asistente de consola, este para lo demás.

Ojo, y es el falso verde caro: `Memory()` **por defecto llama a un modelo para extraer y a otro para
embeber**, y la configuración de fábrica apunta a un proveedor de pago por uso. En un entorno de gasto
cero hay que configurarlo explícitamente contra el modelo servido en local antes de la primera
llamada. Sin eso, «funciona» y factura.
