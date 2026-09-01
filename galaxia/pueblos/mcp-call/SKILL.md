---
cosmos: pueblo
nombre: mcp-call
padre: agentes-ia/herramientas
resumen: Invoca una sola herramienta de un servidor externo desde la consola, sin levantar un anfitrion completo.
---

`cosecha/mcp-call.py` — cliente generico por entrada estandar o por HTTP para llamar a una
herramienta suelta y ver su respuesta cruda.

Sirve para dos cosas que de otro modo cuestan una sesion entera: comprobar que un servidor responde
lo que su documentacion promete antes de conectarlo, y reproducir a mano el fallo de una llamada sin
tener que reconstruir la conversacion que la provoco.
