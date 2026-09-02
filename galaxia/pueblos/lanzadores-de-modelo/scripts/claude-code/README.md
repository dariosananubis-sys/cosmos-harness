# Claude Code + MCP (Local)

Esta carpeta endurece Claude Code para trabajo local: MCPs minimos, cero dependencias remotas innecesarias y una politica de instalacion segura.

## Qué se incluye
- `mcp-servers.min.json`: memoria + filesystem (Node).
- `mcp-servers.full.json`: memoria + filesystem + git (requiere `uvx`).

Ambos siguen el formato `mcpServers` que usan los clientes MCP (ej. Claude Desktop).

## Cómo usar (Claude Desktop)
1. Abre el archivo de config de Claude Desktop:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Copia el contenido de `mcp-servers.min.json` (o `mcp-servers.full.json`) dentro del archivo.
3. Reinicia Claude Desktop.

## Servidores recomendados (local-first)
- **memory** (npx) para memoria persistente local.
- **filesystem** (npx) con acceso restringido solo al repo.
- **git** (uvx) para operaciones de repo si lo necesitas.

> Nota: los servidores MCP de referencia se usan con `npx` (TypeScript) o `uvx`/`pip` (Python).

## Perfiles de ejecucion

### Balanceado (recomendado diario)

```bash
tools/claude-code/run-balanced.sh sonnet
```

### Bajo coste (estricto)

```bash
tools/claude-code/run-strict.sh --task "tarea"
```

### Bajo coste (manual)

```bash
tools/claude-code/run-low.sh sonnet
```

### Pro (full MCP)

```bash
tools/claude-code/run-pro.sh --task "tarea compleja"
```

Todos los perfiles usan MCP minimo por defecto. Para full MCP:

```bash
tools/claude-code/run-smart.sh --full --task "tarea"
```

Esto aplica:
- `CLAUDE_CODE_MAX_OUTPUT_TOKENS=1024`
- `CLAUDE_CODE_EFFORT_LEVEL=low`
- `CLAUDE_CODE_DISABLE_THINKING=1`
- `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1`
- `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1`
- `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`

Puedes sobreescribir cualquiera exportandola antes del comando.

## Seleccion de modelo automatica
Si quieres que el launcher elija el modelo segun la tarea:

```bash
tools/claude-code/run-smart.sh --task "corrige un typo en README"
tools/claude-code/run-smart.sh --task "refactoriza el flujo de login" --low
```

Reglas (conservadoras):
- Solo tareas claramente triviales -> `haiku`
- Default diario -> `sonnet`
- Planificacion/arquitectura -> `opusplan`
- Riesgo alto o complejidad real -> `opus`

Puedes forzar modelo con `--haiku`, `--sonnet`, `--opus`, `--opusplan` o `--model`.

## Politica de instalacion (seguridad)
El registro oficial es **muy permisivo** y asume **moderacion minima**. Usa allowlist y valida origen antes de instalar nuevos MCPs.

Recomendado:
- Preferir servidores oficiales o de proveedores verificados.
- Limitar rutas (`filesystem`) y variables de entorno.
- Revisar dependencias y permisos antes de habilitar nuevos MCPs.
