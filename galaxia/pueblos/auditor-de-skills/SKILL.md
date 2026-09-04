---
cosmos: pueblo
nombre: auditor-de-skills
padre: ciberseguridad/analisis/cadena-de-suministro
resumen: Audita el paquete de una skill antes de instalarla: guiones, inyeccion en su texto y fugas de carpeta.
---

https://github.com/alirezarezvani/claude-skills · MIT (leído en su LICENSE: «Copyright (c) 2025 Alireza Rezvani») · 25.450★ · último push 2026-08-26 (comprobado 2026-09-03, `.../commits/HEAD.atom`; la API de GitHub da `pushed_at` 2026-08-30, pero eso cuenta cualquier rama — el HEAD del repo, que es lo que se instala, es del 26)

Es la skill `skill-security-auditor` de ese repositorio, de Alireza Rezvani, licencia MIT. **El guion
no viaja con este pueblo**: se cataloga y se enlaza, como el resto del catálogo (retirado el
2026-09-03, ver `NOTICE`). Se instala desde su origen — la ruta de abajo está comprobada contra el
árbol del repositorio ese mismo día (1.066 líneas, solo biblioteca estándar). Comprobado el
2026-09-02 sobre dos skills reales.

```bash
git clone --depth 1 https://github.com/alirezarezvani/claude-skills /tmp/claude-skills
AUD=/tmp/claude-skills/engineering/skills/skill-security-auditor/scripts/skill_security_auditor.py
python3 "$AUD" /ruta/a/la-skill/
python3 "$AUD" https://github.com/usuario/repo --skill nombre --cleanup
python3 "$AUD" /ruta/a/la-skill/ --strict --json
```

Veredicto en el codigo de salida: `0` PASS, `2` WARN (revisar a mano), `1` FAIL (no instalar).
`--strict` convierte cualquier WARN en FAIL, que es lo que se pone en un enganche de pre-instalacion.

Por que existe teniendo `semgrep` y `trufflehog` al lado en este mismo continente: aquellos analizan
**codigo**, y una skill no es solo codigo. La mitad del riesgo esta en el `SKILL.md` —instrucciones
que secuestran al agente que la lee— y en la forma del paquete: guiones que salen de su carpeta,
dependencias que se instalan solas, red hacia un dominio que no viene a cuento. `scorecard` puntua la
higiene del repositorio, que es otra pregunta. Aqui la unidad auditada es el paquete de skill entero,
y por eso el resultado es una decision de instalar o no, en vez de una lista de hallazgos.

Ojo, y es el aviso serio: un PASS significa «no ha saltado ninguno de sus patrones», no «es
inofensiva». No ejecuta nada ni razona sobre intencion, asi que un guion malicioso escrito con
cuidado —ofuscado, o que descarga su carga en tiempo de ejecucion— sale limpio. Sirve para descartar
rapido lo evidente y para obligar a mirar lo dudoso; no sustituye leer los guiones de una skill que
va a correr con tus permisos. Y auditar una URL de git **clona el repositorio**: usa `--cleanup` o te
deja el arbol descargado en un temporal.
