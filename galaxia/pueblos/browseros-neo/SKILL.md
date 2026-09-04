---
cosmos: pueblo
nombre: browseros-neo
padre: agentes-ia/herramientas
resumen: Navegador persistente con tus logins y MCP nativo en loopback: el agente actua en sesiones ya iniciadas.
---

https://github.com/browseros-ai/BrowserOS · AGPL-3.0 · 13.533★ · último push 2026-09-03 (comprobado 2026-09-03).
Kit de instalación propio: https://github.com/dariosananubis-sys/browseros-neo-vision-kit (copiado aquí en
`scripts/`, `tests/`, `CONTRATO.md`, `INSTALACION.md` y `PLAN-MEJORA-TOTAL.md`). Instalador de escritorio:
release `browserclaw/v0.49.3` (2026-08-06), DMG `arm64`, `universal` y `x64` más `.exe`; el nombre
anterior de la app era BrowserClaw y el bundle sigue siendo `com.browseros.BrowserClaw`.

```bash
# 1. Navegador (macOS Apple Silicon); verificar firma antes de abrir
curl -L -o /tmp/neo.dmg https://github.com/browseros-ai/BrowserOS/releases/download/browserclaw/v0.49.3/BrowserOS_neo_v0.49.3.1_arm64.dmg
hdiutil attach -nobrowse -mountpoint /tmp/neo /tmp/neo.dmg
codesign --verify --deep --strict /tmp/neo/*.app && cp -R /tmp/neo/*.app /Applications/ && hdiutil detach /tmp/neo
open -a "BrowserOS neo"        # abrirlo una vez para que escriba su config.json
# 2. Conectar Claude Code (descubre la URL loopback real, no la fija a mano)
python3 scripts/preflight.py --json
./scripts/install-claude.sh --check && ./scripts/install-claude.sh --apply
# 3. Sesión nueva de Claude y prueba real:
#    "Usa BrowserOS Neo. Nombra la sesión neo-smoke, abre una pestaña propia con https://example.com,
#     confirma que el título es Example Domain y cierra únicamente esa pestaña."
```

Gana a `agent-browser` (pueblo vecino) en una cosa que aquel no puede dar: **el perfil persistente con
las sesiones iniciadas**. Gmail, GitHub, el panel de un cliente: Neo ya está dentro, y el agente hereda
la sesión sin tocar cookies ni contraseñas. Gana a `microsoft/playwright-mcp` en ruido de herramientas
(20 nativas frente a 71) y a `ChromeDevTools/chrome-devtools-mcp` en puesta en marcha: no hay que
lanzar otro Chromium con perfil de depuración, el MCP viene dentro. Pierde contra `agent-browser` en
coste por tarea de QA sin login: ahí sobra un navegador persistente y bastan una CLI y cero
herramientas residentes. Regla de reparto: **con login, Neo; sin login, agent-browser.**

Flujo fiable, en este orden: nombrar la sesión, abrir pestaña propia, `snapshot` o `grep` para obtener
referencias frescas, actuar, verificar el `diff` que devuelve la acción, captura solo si hay que
juzgar algo visual, cerrar únicamente las pestañas propias. `CONTRATO.md` es el contrato completo que
sigue Claude al instalar; `PLAN-MEJORA-TOTAL.md`, la capa de inspección DevTools de solo lectura que
está diseñada y **no implementada**: no instalar `chrome-devtools-mcp` como herramienta con escritura
hasta que exista el proxy con allowlist que describe.

Ojo, cuatro falsos verdes. La **URL del MCP cambia por máquina** (9010 en un equipo, 9200 o 9239 en la
documentación oficial) y **el puerto CDP cambia en cada arranque**: `preflight.py` los lee de la
configuración de Neo y `install-claude.sh` se niega a registrar nada que no sea loopback; nunca
copiar el puerto de otro ordenador. Las referencias del `snapshot` **caducan** tras navegar o
re-renderizar: repetir el snapshot antes de actuar. `fill` puede **concatenar** en inputs React que ya
tenían texto. Y en una máquina justa de RAM, un render con swap saturado devuelve `about:blank` o
componentes a medias y parece un fallo de la web: máximo tres sesiones de navegador simultáneas y
comprobar viewport y URL antes de medir. En el equipo de origen se vieron los puertos 9010 y 9011
escuchando en todas las interfaces aunque el acceso remoto estaba desactivado: auditar con
`lsof -nP -iTCP -sTCP:LISTEN` antes de dar por cerrada la seguridad de red.

Para Claude Desktop y Cowork existe una extensión aparte, https://github.com/browseros-ai/browserclaw-claude-desktop
(release `v0.5.0`, fichero `.mcpb` que se instala desde Ajustes → Extensiones); solo reenvía al mismo
MCP local y **Claude Code no la necesita**: se conecta al endpoint directamente.

Es un navegador de escritorio (macOS y Windows): **no corre en un servidor sin pantalla**. En un VPS el
navegador del agente es `agent-browser` o `playwright` en modo headless; Neo se queda en el equipo con
el perfil. Los tests del kit se corren desde este directorio: `python3 -m unittest discover -s tests`.
