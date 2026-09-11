---
cosmos: pueblo
nombre: ripwire
padre: agentes-ia/instrumentacion
resumen: Contexto de codigo desde la consola: quien llama a que, impacto y traza, sin cargar ficheros enteros ni MCP.
---

https://github.com/redhat-et/ripwire · Apache-2.0 · 1.894★ · último push 2026-09-11 (comprobado 2026-09-11; v0.5.0 del 2026-09-08, C++23)

```bash
RIPWIRE_REPO=redhat-et/ripwire bash -c "$(curl -fsSL https://raw.githubusercontent.com/redhat-et/ripwire/main/scripts/install.sh)"
ripwire . --for="cambiar como se calcula el precio medio"   # los ficheros y símbolos que tocan eso, recortados a un presupuesto
ripwire . --callers=calcular_precio                        # quién lo llama
ripwire . --impact=calcular_precio                         # qué se rompe si cambia
ripwire . --from-trace=traza.txt                           # de un stack trace a los ficheros que importan
```

Un binario, sin servidor. El camino principal es la **consola**, así que no mete ni una definición
de herramienta en el contexto; el servidor MCP existe pero el propio README desaconseja empezar por
él («its verb schemas sit in your agent's context every session, whether or not it calls them»).
Ataca la partida que la documentación oficial de costes señala como la mayor: «file reads dominate
context usage».

Gana a `serena` en dos cosas medibles: cuesta ~1.700 tokens por sesión (el frontmatter de sus 17
skills, medido) frente a ~6.600 de las ~20 herramientas MCP de aquella, y **publica sus derrotas**:
en `docs/EVALS.md`, contra un grafo de código por MCP ganó 27, perdió 7 y empató 14 en 48 preguntas
gastando ~77K tokens frente a ~486K; y el titular «5 % del gasto ingenuo» viene con «satisfizo 5
preguntas frente a 11». Frontera con `codigo-al-modelo`: aquel empaqueta el repo para pegarlo; este
elige qué parte hace falta.

Ojo: instalar las 17 skills cuesta 1.721 tokens por sesión; instala cuatro o seis. El riesgo real es
el contrario del que promete: que el agente lo use para preguntas que `grep` ya respondía en una
línea. Y está a versión 0.5: la interfaz de línea de comandos puede cambiar entre releases.
