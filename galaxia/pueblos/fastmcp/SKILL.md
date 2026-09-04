---
cosmos: pueblo
nombre: fastmcp
padre: agentes-ia/herramientas
resumen: Define un servidor MCP con decoradores Python; menos codigo que el SDK oficial para lo mismo.
---

https://github.com/PrefectHQ/fastmcp · Apache-2.0 · 27.498★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
pip install fastmcp
```

```python
# servidor.py
from fastmcp import FastMCP

mcp = FastMCP("Herramientas de proyecto")

@mcp.tool
def contar_lineas(ruta: str) -> int:
    """Cuenta las lineas de un fichero de texto."""
    with open(ruta) as f:
        return sum(1 for _ in f)

if __name__ == "__main__":
    mcp.run()   # stdio por defecto; mcp.run(transport="http", port=8000) para servirlo en red
```

```bash
fastmcp dev servidor.py     # inspector web para probar la tool a mano antes de conectarla
```

Gana al SDK oficial `modelcontextprotocol/python-sdk` en líneas: un `@mcp.tool` sobre una función
normal, con el esquema JSON derivado del type hint, donde el SDK de bajo nivel exige declarar a
mano el `Tool` y el manejador. Es además la base sobre la que ahora se construye la sección de
servidor del propio SDK oficial. Frontera con `mcp-servers`: aquí se **escribe** un servidor MCP
nuevo; allí hay una colección ya escrita de servidores de referencia para no reinventar los
comunes.

Ojo: `fastmcp run` sobre `stdio` asume que quien lo invoca controla el proceso padre — servido por
HTTP sin autenticación delante, cualquier cliente en la red ejecuta las tools tal cual estén
escritas. Igual que con cualquier tool expuesta a un LLM, validar los argumentos dentro de la
función: el esquema JSON no impide una ruta fuera del directorio esperado en `contar_lineas`.
