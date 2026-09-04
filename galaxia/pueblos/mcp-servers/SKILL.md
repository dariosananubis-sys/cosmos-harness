---
cosmos: pueblo
nombre: mcp-servers
padre: agentes-ia/herramientas
resumen: Coleccion oficial de servidores MCP de referencia: filesystem, git, fetch, memoria, listos para usar.
---

https://github.com/modelcontextprotocol/servers · MIT/Apache-2.0 (en transición) · 90.045★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
npx -y @modelcontextprotocol/server-filesystem /RUTA/AL/PROYECTO
# o instalados uno a uno vía pip/npm según el servidor concreto del repo
```

```json
// claude_desktop_config.json — o el equivalente de configuracion MCP del cliente
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/RUTA/AL/PROYECTO"]
    }
  }
}
```

Gana a escribir un servidor propio para los casos comunes: filesystem, git, fetch de una URL,
memoria persistente y un puñado más ya están aquí, mantenidos por el propio proyecto MCP y
probados contra el protocolo que ellos mismos definen. Frontera con `fastmcp`: esto es el
**catálogo** de servidores ya hechos; aquel es la herramienta para escribir uno **nuevo** que no
esté en esta lista.

Ojo: el repo separó los servidores más usados a repos propios y dejó otros como referencia
histórica — antes de instalar uno de aquí, comprobar en su README si sigue siendo el canónico o
si se movió. Y `server-filesystem` da acceso de lectura/escritura a la ruta que se le pase: pasar
la raíz del disco es darle a esa herramienta las llaves de todo, no solo del proyecto.
