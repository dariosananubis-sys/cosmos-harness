---
cosmos: pueblo
nombre: cwc-long-running-agents
padre: agentes-ia/instrumentacion
resumen: Los hooks de Anthropic para sesiones largas: veredicto en rojo hasta ver evidencia y evaluador sin escritura.
---

https://github.com/anthropics/cwc-long-running-agents · Apache-2.0 · 676★ · último push 2026-05-13 (comprobado 2026-09-11; el propio README dice «example ingredients, not a turnkey harness», sin mantenimiento)

Son seis ficheros y se copian a mano, no se instalan: el valor está en leerlos.

```bash
git clone --depth 1 https://github.com/anthropics/cwc-long-running-agents /tmp/cwc
ls /tmp/cwc/claude-code-config/.claude/hooks/     # verify-gate.sh  track-read.sh  commit-on-stop.sh  kill-switch.sh  steer.sh
cat /tmp/cwc/claude-code-config/.claude/agents/evaluator.md
```

Los tres primitivos que nombra su README, y lo que hace cada fichero:

- **Veredicto en rojo por defecto** (`verify-gate.sh`, `PreToolUse` sobre `Write|Edit`): deniega
  escribir `test-results.json` si en esta sesión no se ha leído antes un fichero de evidencia
  (`track-read.sh` apunta las lecturas), y consume la evidencia al usarla.
- **Evaluador de contexto fresco** (`agents/evaluator.md`): un subagente con `tools: Read, Glob,
  Grep, Bash` y sin `Write`/`Edit`, que responde `PASS` o `NEEDS_WORK` en la primera línea para que
  un guion lo lea. El aislamiento por herramientas es lo que lo hace mecánico.
- **Traspaso entre sesiones**: `commit-on-stop.sh` hace un commit de punto de control en cada `Stop`.

```bash
# El bucle que publica el README: construir, evaluar con otro contexto, repetir.
while grep -q '"passes": false' test-results.json; do
  claude -p "Read PROGRESS.md and build the next unfinished feature per CLAUDE.md."
  VERDICT=$(claude --agent evaluator -p "Review the most recent commit against its spec.")
  [ "$(echo "$VERDICT" | head -1)" = "PASS" ] || echo "$VERDICT" > NEXT_FINDINGS.md
done
```

Frontera con `playbook-obligatorio` y con G04 de COSMOS: `track-read.sh` es la misma idea de
«lo he leído» convertida en hecho comprobable, pero más floja (no ata sesión ni SHA-256). Gana a
`superpowers` en que su «verificar antes de terminar» es un hook que deniega, no una skill que
exhorta.

Ojo: el propio `verify-gate.sh` declara sus huecos en los comentarios: solo engancha `Write|Edit`
(un `sed` o `jq` por `Bash` reescribe el fichero sin control), casa por nombre de fichero y
cualquier evidencia leída desbloquea cualquier fila. Y `kill-switch.sh` bloquea **toda** llamada
mientras exista `./AGENT_STOP`, sin válvula acotada: exactamente lo que la doctrina de COSMOS
convierte en `cosmos saltar`. Ninguno de los dos artículos de Anthropic que lo acompañan publica
una mejora de calidad medida; las únicas cifras son de coste (20 min / 9 USD frente a 6 h / 200 USD).
