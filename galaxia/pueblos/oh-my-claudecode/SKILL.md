---
cosmos: pueblo
nombre: oh-my-claudecode
padre: agentes-ia/instrumentacion
resumen: Un SubagentStop que comprueba que el subagente dejo los ficheros que dijo; la cobertura de eventos mas completa.
---

https://github.com/Yeachan-Heo/oh-my-claudecode · MIT · 39.103★ · último push 2026-09-11 (comprobado 2026-09-11; v5.4.0, 39 skills, 25 hooks en 11 eventos)

```
/plugin marketplace add Yeachan-Heo/oh-my-claudecode
/plugin install oh-my-claudecode@oh-my-claudecode
```

El fichero que importa es `scripts/verify-deliverables.mjs`, registrado en `hooks/hooks.json` bajo
`SubagentStop`: «a task can be marked "completed" with **zero output files**». Lee los ficheros que
el subagente debía producir de `.omc/deliverables.json` y comprueba **existencia y contenido
mínimo**. Es verificación por artefacto, no por narración, y comprobar que un fichero existe cuesta
cero tokens. Lleva `sanitizePath()` contra `..` y rutas absolutas, y una lección cara: en
`SubagentStop` no se emite `additionalContext`, porque se reinyecta en el subagente que termina
(regresiones #3209/#3233); devuelve siempre `{continue:true}`.

```json
// .omc/deliverables.json — lo que el subagente tiene que dejar escrito
{ "deliverables": [ { "path": "informe.md", "minBytes": 200 } ] }
```

Lo demás que enseña su `hooks.json`: enganchar `UserPromptSubmit` (cargar skills por disparador en
el prompt, no al arrancar), `PermissionRequest`, `PostToolUseFailure` y `SubagentStart`, eventos que
un arnés que solo mira `PreToolUse`/`PostToolUse`/`Stop` deja sin vigilar.

Frontera con `cwc-long-running-agents`: aquel verifica con un evaluador que lee; este verifica que
el artefacto exista antes de que nadie lo lea. Gana a `ruvnet/ruflo` (72.000★) en que sus hooks
deniegan de verdad: los de ruflo terminan todos en `|| true`.

Ojo: 39 skills con nombres de marca (`harbor`, `drydock`, `loft`, `ultragoal`) que hay que
aprenderse, tres hooks de `SessionStart` (memoria de proyecto y wiki) cuya inyección **no está
medida** y no es auditable sin instalar, y `dist/` entero versionado. Para COSMOS lo instalable es
la forma de `verify-deliverables.mjs`, no el plugin.
