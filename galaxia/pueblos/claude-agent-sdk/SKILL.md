---
cosmos: pueblo
nombre: claude-agent-sdk
padre: agentes-ia/construccion
resumen: SDK oficial para montar agentes propios con herramientas, permisos y bucle de ejecucion completo.
---

https://github.com/anthropics/claude-agent-sdk-python · MIT · 8.014★ · último push 2026-08-31 (comprobado 2026-09-01)
Gemelo TypeScript: https://github.com/anthropics/claude-agent-sdk-typescript · 1.723★ · sin SPDX declarado · mismo push.

```bash
pip install claude-agent-sdk          # Python 3.10+; trae el CLI de Claude Code embebido
npm install @anthropic-ai/claude-agent-sdk   # TypeScript
```

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    opciones = ClaudeAgentOptions(system_prompt="Responde en una linea", max_turns=1)
    async for mensaje in query(prompt="Cuenta los ficheros .md de este directorio", options=opciones):
        print(mensaje)

anyio.run(main)
```

Gana a `langchain-ai/langgraph` (40.847★) y a `crewAIInc/crewAI` (57.935★) por no añadir vocabulario:
los dos ponen un modelo de grafos o de roles ENCIMA del mismo bucle de herramientas, así que hay que
mantener dos modelos mentales y traducir entre ellos. Aquí las herramientas, los enganches y los
subagentes son los mismos que ya usa el arnés. `microsoft/autogen` (60.733★) queda como legado: sin
commits desde 2026-04-15 y con el propio Microsoft moviendo el foco a `microsoft/agent-framework`
(13.264★, activo hoy).

Ojo, dos cosas que sorprenden: `allowed_tools` **no quita herramientas**, solo auto-aprueba las que
lista — lo que bloquea de verdad es `disallowed_tools`; creer lo contrario deja al agente con Bash y
Write disponibles. Y el paquete es el bucle, no el modelo: según cómo se autentique consume la cuota
de la suscripción o **factura por API**. Comprobar cuál antes de dejar un agente corriendo solo.
