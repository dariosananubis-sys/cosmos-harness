---
cosmos: pueblo
nombre: browser-use
padre: agentes-ia/herramientas
resumen: Un modelo conduce el navegador por vision y DOM cuando la tarea no se puede describir con selectores.
---

https://github.com/browser-use/browser-use · MIT · 112.126★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
pip install browser-use
playwright install chromium
```

```python
import asyncio
from browser_use import Agent
from browser_use.llm import ChatAnthropic

async def main():
    agente = Agent(
        task="Busca en github.com el repositorio con mas estrellas de 'MCP server' y dime el nombre",
        llm=ChatAnthropic(model="claude-sonnet-4-5"),
    )
    resultado = await agente.run()
    print(resultado.final_result())

asyncio.run(main())
```

Gana a `agent-browser` cuando la tarea **no se puede describir con selectores por adelantado** —
un sitio nuevo cada vez, un flujo que cambia de forma, "encuentra la opción que sirva para X" sin
saber el DOM de antemano: aquí el modelo mira la página (accesibilidad + captura) y decide el
siguiente clic. Pierde frente a él en coste: cada paso es una llamada al modelo con imagen o árbol
de accesibilidad completo, así que un flujo ya conocido (login, rellenar un formulario fijo) sale
mucho más caro aquí que con un script de `agent-browser` de cuatro líneas.

Ojo: un agente que conduce solo el navegador puede aceptar un diálogo, enviar un formulario o
comprar algo que no debía — el `task` en lenguaje natural es también la única barrera, y una
instrucción ambigua o una página con contenido malicioso (inyección de prompt vía DOM) puede
desviarlo. Alcance autorizado siempre explícito en el `task`, nunca "navega y haz lo que haga
falta" sobre un sitio con sesión de cliente ya iniciada.
