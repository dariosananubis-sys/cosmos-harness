---
cosmos: pueblo
nombre: obsidian
padre: agentes-ia/memoria
resumen: Boveda de notas Markdown que el agente lee y escribe con las skills oficiales de Obsidian y su CLI.
---

https://github.com/kepano/obsidian-skills · MIT · 47.848★ · último push 2026-06-08 (comprobado 2026-09-04).
Las skills las publica el propio creador de Obsidian y son la vía oficial para que un agente escriba
Markdown de Obsidian (wikilinks, callouts, propiedades, embeds), Bases (`.base`) y JSON Canvas
(`.canvas`) sin inventarse la sintaxis, y para manejar la bóveda por el CLI oficial de Obsidian
(≥ 1.12.4, https://obsidian.md/cli). Escritorio: https://github.com/obsidianmd/obsidian-releases,
release `v1.13.7` (2026-08-12; la `v1.13.8` solo trae el `.apk` de Android).

```bash
# 1. La aplicación (macOS; verificar la firma antes de abrir). Notarizada por Dynalist Inc. (6JSW4SJWN9)
curl -L -o /tmp/obsidian.dmg https://github.com/obsidianmd/obsidian-releases/releases/download/v1.13.7/Obsidian-1.13.7.dmg
hdiutil attach -nobrowse -mountpoint /tmp/obsidian /tmp/obsidian.dmg
codesign --verify --deep --strict /tmp/obsidian/Obsidian.app && cp -R /tmp/obsidian/Obsidian.app /Applications/ && hdiutil detach /tmp/obsidian
# 2. Las skills, como plugin de Claude Code (ámbito usuario: valen en cualquier carpeta, también dentro de la bóveda)
claude plugin marketplace add kepano/obsidian-skills
claude plugin install obsidian@obsidian-skills --scope user
# 3. Una bóveda es un directorio; se abre por URI y Obsidian la registra
mkdir -p ~/Obsidian/cuaderno && open -a Obsidian "obsidian://open?path=$HOME/Obsidian/cuaderno"
# 4. El CLI se activa DENTRO de la app (Ajustes → General → Command line interface; pide administrador
#    para el enlace /usr/local/bin/obsidian). Después, con Obsidian abierto:
obsidian vault="cuaderno" create name="Reunión con el cliente" content="# Reunión\n\n- [ ] enviar presupuesto"
obsidian vault="cuaderno" search query="presupuesto" format=json
obsidian vault="cuaderno" daily:append content="- [ ] revisar [[Reunión con el cliente]]"
```

Gana a `MarkusPfundstein/mcp-obsidian` (4.367★, MCP sobre el plugin comunitario Local REST API) en dos
cosas: no hay servidor MCP residente cobrando herramientas en cada sesión, y no depende de un plugin
de terceros con clave de API: el agente escribe los ficheros `.md` directamente (la bóveda es una
carpeta) y usa el CLI oficial para lo que exige la app abierta (búsqueda indexada, nota diaria,
propiedades, tareas). Frente a `claude-mem` (pueblo vecino) no compite: aquel recuerda las sesiones
del asistente; esto es el cuaderno del dueño, legible por una persona y por el agente.

Regla de uso: sin la app abierta, leer y escribir ficheros; con la app abierta, el CLI para buscar,
para la nota diaria y para lo que toque propiedades o tareas. `obsidian help` lista los ~115 comandos
y `obsidian <comando> help` la sintaxis de cada uno; los parámetros son `clave=valor`, con comillas si
hay espacios, y `vault=` elige la bóveda cuando hay más de una.

Ojo, cuatro cosas. El plugin cuesta **~606 tokens siempre encendidos** en toda sesión de Claude Code
(`claude plugin details obsidian@obsidian-skills`), que es justo lo que COSMOS vigila: si el cuaderno
no se usa a diario, `claude plugin disable obsidian@obsidian-skills` y este pueblo sigue explicando
cómo escribir en la bóveda. El CLI necesita Obsidian **en marcha**: en un servidor sin pantalla no
hay CLI, solo ficheros. La activación del CLI y el enlace en `/usr/local/bin` piden contraseña de
administrador y no se hacen desde fuera de la app. Y `obsidian-bases` carga ~5.200 tokens al
invocarse: no pedir Bases si basta una lista.
