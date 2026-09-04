---
cosmos: lluvia
nombre: obsidian
moja: []
resumen: Obsidian 1.13.7 instalado, skills oficiales como plugin y pueblo nuevo en agentes-ia/memoria; el CLI lo activa el dueno.
---

# Obsidian, de la mejor manera que existe hoy

**Fecha:** 2026-09-04 · **Encargo:** «implementa de la mejor manera existente Obsidian». · **Escribe:**
`galaxia/pueblos/obsidian/SKILL.md` y este parte.

## Lo elegido y por qué

La vía oficial es doble: el **CLI de Obsidian** (en la app desde la 1.12.4, febrero de 2026, ~115
comandos por IPC) y las **skills de `kepano/obsidian-skills`** (47.848★, MIT, del creador de
Obsidian), que siguen la especificación Agent Skills y se instalan como plugin de Claude Code.
Descartado `mcp-obsidian` sobre Local REST API: servidor residente, plugin de terceros y clave de
API para algo que es una carpeta de `.md`.

## Lo que se hizo en esta máquina

- **Obsidian 1.13.7** desde `obsidianmd/obsidian-releases` (la 1.13.8 solo trae el `.apk`). DMG
  sha256 `05daa54f…99bce`; `codesign --verify --deep --strict` y Gatekeeper «Notarized Developer ID»
  de Dynalist Inc. (`6JSW4SJWN9`). Copiada a `/Applications`.
- **Plugin** `obsidian@obsidian-skills` 1.0.1 en ámbito usuario (marketplace `kepano/obsidian-skills`):
  cinco skills (`obsidian-markdown`, `obsidian-bases`, `json-canvas`, `obsidian-cli`, `defuddle`).
  Coste medido por el propio CLI: **~606 tokens siempre encendidos** por sesión; se apaga con
  `claude plugin disable obsidian@obsidian-skills`.
- **Bóveda** `~/Obsidian/cuaderno` con una nota `Inicio.md`, abierta por URI.
- **Pueblo** `obsidian` bajo `agentes-ia/memoria`, con instalación, uso del CLI, rival nombrado y
  avisos; `cosmos validar` verde tras compilar.

## Lo que queda del dueño

- Activar el CLI dentro de la app (Ajustes → General → Command line interface): pide contraseña de
  administrador para el enlace `/usr/local/bin/obsidian`, y eso no se hace desde fuera.
- Decidir si los 606 tokens del plugin valen en todas las sesiones o solo cuando se trabaja en la
  bóveda (entonces: `--scope project` dentro de `~/Obsidian/cuaderno`).
