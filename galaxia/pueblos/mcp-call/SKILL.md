---
cosmos: pueblo
nombre: mcp-call
padre: agentes-ia/herramientas
resumen: Invoca una sola herramienta de un servidor externo desde la consola, sin levantar un anfitrion completo.
---

`scripts/mcp-call.py` — herramienta propia, no de GitHub. Cliente JSON-RPC por STDIN/STDOUT, sin
conexión persistente.

```bash
export MCP_BRIDGE_CMD="npx -y @ejemplo/mcp-servidor --config /ruta/config.json"
python3 scripts/mcp-call.py --list
python3 scripts/mcp-call.py --schema herramienta_a,herramienta_b
python3 scripts/mcp-call.py herramienta_a '{"ruta": "/tmp/entrada.txt"}'
```

Sirve para dos cosas que de otro modo cuestan una sesión entera: **comprobar que un servidor devuelve
lo que su documentación promete antes de conectarlo** —el número y la forma real de sus herramientas,
que es lo que se pagará en cada sesión—, y reproducir a mano el fallo de una llamada sin reconstruir
la conversación que la provocó.

Gana a conectar el servidor en el arnés «para probarlo»: eso ya cuesta contexto en todas las sesiones
siguientes, y desconectarlo se olvida. Aquí el coste es cero y el servidor muere al terminar el
comando.

Ojo: manda `initialize` y la llamada, y **descarta el stderr del puente** a propósito (si se mezcla
con stdout rompe el parseo del JSON). Es decir, un servidor que falle explicándose por stderr aquí se
ve como una respuesta vacía: si sale vacío, relanzar el `MCP_BRIDGE_CMD` a mano para leer su error.
Solo habla stdio; para uno remoto por HTTP hace falta un puente delante.
