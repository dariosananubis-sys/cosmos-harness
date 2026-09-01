---
cosmos: pueblo
nombre: wordpress-skills
padre: web/construccion-de-sitios
resumen: Skills oficiales del proyecto con guiones que detectan y validan bloques, temas, REST y permisos.
---

https://github.com/WordPress/agent-skills · **licencia sin SPDX** · 2.090★ · último push 2026-08-24
(comprobado 2026-09-01). Oficial del proyecto WordPress.

```bash
npx skills add WordPress/agent-skills --list
npx skills add WordPress/agent-skills --skill wp-plugin-development wp-abilities-api wp-playground
npx skills add WordPress/agent-skills --skill wp-plugin-development --global
```

Catorce skills portables con documentación de referencia y **guiones JavaScript deterministas** de
detección y validación — no solo prosa. Cubre bloques (`block.json`, render, deprecación),
arquitectura de plugins, capacidades y permisos, REST e Interactivity API, WP-CLI, rendimiento,
WordPress Playground y las guías del directorio de plugins.

Gana a `Automattic/wordpress-agent-skills` (112★) por dos motivos medibles: aquel lleva **sin push
desde 2026-03-17**, más de cinco meses, y añade el ángulo propio de la plataforma comercial duplicando
lo demás. Se consulta si el encargo vive allí, y con la advertencia que el propio README de aquel trae:
sus temas generados **no son aptos para producción**. Frente a las colecciones de terceros con más
estrellas, la fuente canónica es la que se actualiza cuando la API cambia.

Ojo: `npx skills add` instala en el ámbito del proyecto por defecto, así que las skills acaban en
`.claude/skills/` y **se comitean con el repo** — decisión, no accidente. Y cada skill instalada se
paga en el catálogo que se inyecta en cada sesión: instalar las catorce «por tenerlas» es un impuesto
permanente; se instalan las que el encargo use.
