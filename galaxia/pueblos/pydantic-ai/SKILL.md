---
cosmos: pueblo
nombre: pydantic-ai
padre: agentes-ia/construccion
resumen: Agentes tipados con Pydantic; misma API para Anthropic, OpenAI, Gemini y otros, sin atarse a uno.
---

https://github.com/pydantic/pydantic-ai · MIT · 19.693★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
pip install pydantic-ai
```

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class Respuesta(BaseModel):
    resumen: str
    confianza: float

agente = Agent("anthropic:claude-sonnet-4-5", output_type=Respuesta, system_prompt="Responde breve")
resultado = agente.run_sync("Resume en una frase que hace este repositorio")
print(resultado.output.resumen, resultado.output.confianza)
```

Gana a `claude-agent-sdk` (el pueblo que empaqueta `anthropics/claude-agent-sdk-python`, su vecino
más cercano en este mismo país) en una cosa concreta: el mismo código de agente corre contra
Anthropic, OpenAI, Gemini, Groq o Mistral cambiando un string, porque valida la salida con un
`BaseModel` de Pydantic en vez de con el formato propio de un proveedor. Rompe el monocultivo del
país: hasta esta ficha, todo lo que construye un agente aquí asumía un solo fabricante. Pierde
frente a él cuando el agente vive dentro de Claude Code y ya hereda sus herramientas, permisos y
subagentes sin escribir nada.

Ojo: la salida tipada no es gratis — un modelo que no sigue bien el function calling reintenta o
falla la validación, y ese reintento es una llamada de pago más. Y `output_type` fuerza al modelo
a rellenar un esquema; para una respuesta abierta de texto largo, forzar un `BaseModel` reduce la
calidad de la prosa en vez de mejorarla.
