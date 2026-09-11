---
cosmos: pueblo
nombre: claude-plugins-official
padre: agentes-ia/instrumentacion
resumen: El mercado oficial: hooks condicionales y en segundo plano, bucle Ralph, revisor con filtro de confianza, evals.
---

https://github.com/anthropics/claude-plugins-official · Apache-2.0 · 36.141★ · último push 2026-09-11 (comprobado 2026-09-11; 25 plugins propios y 14 externos)

```
/plugin marketplace add anthropics/claude-plugins-official     # Claude Code lo añade solo la primera vez
/plugin install security-guidance@claude-plugins-official
/plugin install skill-creator@claude-plugins-official
```

Lo que merece leerse aunque no se instale nada, con el fichero exacto:

- `plugins/security-guidance/hooks/hooks.json`: dos campos del manifiesto de hooks que un arnés
  propio puede usar tal cual. `"if": "Bash(git commit:*)"` hace que el hook **no arranque** si la
  orden no encaja (coste cero, no «arranca y sale pronto»); `"asyncRewake": true` con
  `rewakeMessage` lo corre en segundo plano y solo despierta al agente **si hay hallazgo**. Es la
  única forma conocida de verificar en cada commit sin pagar contexto en el camino feliz.
- `plugins/ralph-loop/hooks/stop-hook.sh`: el bucle «hasta que esté hecho» con freno por estructura
  —`max_iterations` y una frase de terminación comparada literalmente— aislado por `session_id`.
- `plugins/code-review/commands/code-review.md`: cinco revisores en paralelo y, por cada hallazgo,
  un juez aparte que puntúa la confianza 0-100; **por debajo de 80 no se emite**. Es lo que convierte
  una revisión adversarial en algo que no ahoga en ruido.
- `plugins/skill-creator/`: `run_eval.py` lanza `claude -p` de verdad y mide si la descripción de
  una skill hace que se dispare; el brazo sin skill dice si el modelo ya lo hacía solo.
- `plugins/hookify/`: reglas de bloqueo en markdown con frontmatter, evaluadas por un motor.
- Los plugins `*-lsp` (`pyright-lsp`, `typescript-lsp`…): navegación por símbolos y diagnóstico
  tras cada edición, que es lo que la documentación de costes recomienda frente a grep y leer
  ficheros enteros.

Gana a `davila7/claude-code-templates` en criterio: 25 plugins con dueño frente a 5.660 ficheros
sin filtro. Frontera con `revision-cruzada`: aquel es el revisor de COSMOS por otro modelo; el
filtro de confianza de `code-review` es la pieza que le falta.

Ojo: `security-guidance` llama a un modelo desde el hook (`security_reminder_hook.py`, 116 KB): no
cuesta contexto en el camino feliz pero sí dinero en cada commit. La regla de ejemplo de `hookify`
(`require-tests-stop`) comprueba que la palabra `pytest` **aparezca** en el transcript, no que la
suite saliera en verde: un `pytest` que falló la satisface. Y `ralph-loop` reinyecta el prompt
entero en cada vuelta: con 50 iteraciones son decenas de miles de tokens solo de realimentación.
