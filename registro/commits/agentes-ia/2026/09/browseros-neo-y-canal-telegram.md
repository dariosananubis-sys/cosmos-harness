---
cosmos: lluvia
nombre: browseros-neo-y-canal-telegram
moja: []
resumen: Neo instalado y verificado con llamada real por MCP; pueblo nuevo; Telegram y servidor Oracle preparados.
---

# BrowserOS Neo dentro del arnés y el camino a Telegram

**Fecha:** 2026-09-03 · **Encargo:** hablar con el agente desde el móvil por Telegram, montar el
navegador de agentes del kit `browseros-neo-vision-kit` dentro del harness y dejar preparado un
servidor de 0 € para que todo corra sin el Mac encendido. · **Escribe:** `galaxia/pueblos/browseros-neo/`,
`docs/SERVIDOR-ORACLE.md`, `docs/servidor-oracle/bootstrap.sh` y este parte.

## Lo que se instaló y cómo se comprobó

- **BrowserOS neo 0.49.3.1** (release `browserclaw/v0.49.3`, DMG arm64, sha256
  `a5c8e4bf…c6b93`). `codesign --deep --strict` falló en el DMG por metadatos de Finder en un
  subcomponente de Sparkle; Gatekeeper lo aceptó como *Notarized Developer ID* (equipo `8YMKWU47S5`).
  Tras copiar a `/Applications` y limpiar los atributos extendidos, la verificación estricta pasó.
- Al abrirlo por primera vez Neo **registró él solo** `browseros-neo` en la configuración de usuario
  de Claude Code. El `preflight.py` del kit descubrió la misma URL loopback (`http://127.0.0.1:9010/mcp`,
  CDP en 9110, servidor en 9210) y `install-claude.sh --check/--apply` la dio por coincidente sin
  tocar nada.
- **Llamada real**, como exige el contrato: `name_session` → `tabs new https://example.com` →
  `evaluate document.title` = «Example Domain» → `tabs close` solo de esa pestaña. Hecha dos veces por
  JSON-RPC directo contra el endpoint (el servidor devuelve SSE con una primera línea `data:` vacía
  que hay que saltar). 20 herramientas expuestas, servidor `browseros-neo 0.0.50`.
- Los 30 tests del kit pasan desde el directorio del pueblo; `cosmos validar` verde tras `compilar`.

## Lo que quedó abierto, y es de seguridad

Los puertos **9010 y 9011 escuchan en todas las interfaces** (`*:9010`), igual que en el equipo de
origen, y **el cortafuegos de macOS está desactivado**. Con `allow_remote_in_mcp` sin definir, el MCP
del navegador con los logins del dueño es alcanzable desde la LAN. No se cambió el cortafuegos (es
ajuste de sistema del dueño); hay que decidirlo antes de llevar el portátil a una red ajena.

## Telegram y el servidor

- Canal de Telegram de Claude Code (research preview): Bun 1.4.0 y el plugin `telegram@claude-plugins-official`
  0.0.7 instalados a nivel usuario. Falta el token de BotFather y arrancar con `--channels`.
- Descartados Render, Hermes y «Claw Army»: otro agente, otro coste, sin repo ni cuenta. Lo que hace
  falta es un Linux con root: Oracle Always Free (2 OCPU, 12 GB ARM) o Hetzner CX32. Clave SSH
  dedicada generada (`~/.ssh/id_ed25519_cosmos_oracle`), guion idempotente en `docs/servidor-oracle/`.
  Neo no va al servidor: es de escritorio; allí el navegador es `agent-browser` o `playwright`.

## Lo aprendido

- El guardarraíl G03 del propio harness deniega escrituras con ruta calculada (`$P/scripts/`): las
  rutas literales no son manía, son la única forma de que el gate sepa qué se escribe.
- Las releases «latest» de `browseros-ai/BrowserOS` son extensiones y recursos del servidor; el
  navegador entero solo aparece en tags `browserclaw/vX` y en los antiguos `vX`. Buscar por nombre de
  asset, no por fecha.
