---
cosmos: pueblo
nombre: lanzadores-de-modelo
padre: agentes-ia/coste
resumen: Arranca cada tarea con el modelo mas barato que la resuelve y con el perfil minimo de servidores externos.
---

`scripts/claude-code/` (5 lanzadores + 2 perfiles MCP + README) y `scripts/modelos-fijar.py` —
herramientas propias, no de GitHub.

```bash
chmod +x scripts/claude-code/*.sh
scripts/claude-code/run-balanced.sh sonnet          # diario
scripts/claude-code/run-strict.sh --task "revisar el diff"   # coste mínimo, clasifica la tarea
export SESIONES_GLOB="$HOME/.claude-accounts/sessions"       # si hay cuentas aisladas
python3 scripts/modelos-fijar.py                    # repone el menú de /model, idempotente
```

Dos perfiles de servidores MCP, `mcp-servers.min.json` (memoria + ficheros) y `mcp-servers.full.json`
(+ git), porque un servidor conectado y sin usar **se paga en cada sesión aunque no se invoque** — eso
importa tanto como elegir el modelo. `modelos-fijar.py` repone las entradas de
`additionalModelOptionsCache` que el CLI reescribe en cada arranque, y valida el identificador antes
de dejarlo puesto: un modelo mal escrito falla al arrancar, no a mitad de un trabajo largo.

Gana a bajar el esfuerzo de razonamiento, que es lo primero que la gente toca: medido aquí, eso apenas
ahorra. Lo que ahorra es decidir con el modelo caro, ejecutar con el barato y no arrastrar
herramientas.

Ojo: la lista de modelos del guion es un ejemplo y **envejece rápido** — hay que ajustarla a lo que
acepte el plan de la cuenta. Y `run-*.sh` no impide que una sesión ya abierta siga con el perfil
completo: el perfil se elige al arrancar.
