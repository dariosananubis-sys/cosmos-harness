---
cosmos: pueblo
nombre: superpowers
padre: agentes-ia/instrumentacion
resumen: Tres guiones que pasan tarea y diff entre agentes por fichero, nunca por el contexto del que coordina.
---

https://github.com/obra/superpowers · MIT · 285.219★ · último commit en `main` 2026-08-12 (comprobado 2026-09-11; el repo más estrellado del ecosistema)

Lo que vale son tres guiones de bash de menos de sesenta líneas, y se usan sin instalar el plugin:

```bash
git clone --depth 1 https://github.com/obra/superpowers /tmp/superpowers
S=/tmp/superpowers/skills/subagent-driven-development/scripts
$S/sdd-workspace  PLAN.md                 # un directorio por plan bajo .superpowers/sdd/<plan>/, que se auto-ignora en git
$S/task-brief     PLAN.md 3               # extrae SOLO la tarea 3 del plan a task-3-brief.md: el coordinador pasa la ruta, no el texto
$S/review-package PLAN.md BASE HEAD       # commits + --stat + `git diff -U10 BASE..HEAD` a un fichero nombrado por rango
```

El comentario de cabecera lo dice: el texto de la tarea «never has to be pasted through the
controller's context». Es carga perezosa **hacia fuera** —qué pasa entre agentes— y el revisor ve
el diff completo con contexto en vez de un resumen narrado por quien lo escribió. Es el mismo
contrato que `research/PATRONES-HARNESS.md` §10 («escribe a fichero, responde una línea»), ya
escrito y probado.

Frontera con `delegar-generacion`: aquel delega a otro modelo; estos guiones deciden **qué viaja**
en la delegación. Gana a `EveryInc/compound-engineering-plugin` en que su handoff (`ce-handoff`)
es una skill de prosa y esto son guiones.

Ojo: instalar el plugin entero cuesta lo contrario de lo que promete. Su único hook (`SessionStart`)
inyecta `skills/using-superpowers/SKILL.md` envuelto en `<EXTREMELY_IMPORTANT>`: 3.108 bytes,
unos 780 tokens fijos en cada arranque, cada `/clear` y cada compactación, más los ~100 por skill de
metadatos de sus 14 skills. Unos 2.200 tokens por sesión antes de disparar nada —más de la mitad del
presupuesto entero de COSMOS— y el texto es exhortación pura («YOU DO NOT HAVE A CHOICE», una tabla
de pensamientos prohibidos). `verification-before-completion` es una redacción excelente del
principio y **ningún hook la hace cumplir**. Y `main` lleva un mes sin commits aunque `pushed_at`
sea de hoy.
