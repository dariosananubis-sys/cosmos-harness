# Barrido del 2026-09-11 — harnesses, tokens, calidad y funciones nativas

Cuatro informes escritos por agentes de investigación en Opus el 2026-09-11, cada uno con
estrellas, licencia y último commit verificados ese día contra `api.github.com`, y las funciones
nativas contra `code.claude.com/docs` (Claude Code 2.1.268). Son la fuente de las seis fichas que
entraron en `agentes-ia/instrumentacion` ese día (`cwc-long-running-agents`,
`claude-plugins-official`, `superpowers`, `oh-my-claudecode`, `claude-code-hooks`, `ripwire`) y
de dos guardarraíles: la corrección de G05 (el runtime solo honra `updatedToolOutput` con el
esquema entero de la respuesta) y G06 (la verificación declarada al cerrar).

| Fichero | Pregunta |
|---|---|
| `harnesses.md` | Qué mecanismos tienen los harnesses de Claude Code más usados que COSMOS no tiene (13 repos) |
| `tokens.md` | Qué reduce de verdad el gasto de tokens: 13 funciones nativas y 16 herramientas, con lo medido y lo que es marketing |
| `calidad.md` | Qué mecanismos mejoran el resultado final y se pueden hacer hook (15 mecanismos, 5 guardarraíles propuestos) |
| `nativo.md` | Inventario de hooks (33 eventos), ajustes, comandos, skills, rules, subagentes y plugins a esa fecha |

Lo que estos informes dicen y todavía no se ha hecho vive en el informe de cierre de esa sesión y
en `PROGRESS.md`; las cifras de aquí son de su fecha y no se actualizan.
