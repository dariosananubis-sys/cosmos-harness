---
cosmos: pueblo
nombre: playbook-obligatorio
padre: agentes-ia
resumen: Deniega escribir hasta haber leido el manual en ESTA sesion; si lo editas, invalida las lecturas anteriores.
---

Destilado generico del mecanismo que hacia cumplir una skill obligatoria en un arnes propio (alli
eran dos enganches atados a una web de cliente; aqui no queda nada de eso). El guion viaja con el
pueblo: `scripts/playbook_gate.py`, solo biblioteca estandar.

```bash
export PLAYBOOK_OBLIGATORIO=docs/COMO-SE-HACE-AQUI.md
python3 scripts/playbook_gate.py autotest      # 8 casos, incluido verla denegar
```

Se engancha en tres sitios y ya no depende de la memoria de nadie:

```json
{"PostToolUse": [{"matcher": "Read",
   "hooks": [{"type": "command", "command": "python3 scripts/playbook_gate.py marca"}]}],
 "PreToolUse":  [{"matcher": "Edit|Write",
   "hooks": [{"type": "command", "command": "python3 scripts/playbook_gate.py guard"}]}],
 "PreCompact":  [{"matcher": "*",
   "hooks": [{"type": "command", "command": "python3 scripts/playbook_gate.py olvida"}]}]}
```

Gana a escribir «lee siempre X antes de tocar Y» en el fichero de contexto, que es la alternativa que
todo el mundo usa: aquella depende de que el modelo se acuerde, y no se entera nunca de cuando no se
acordo. Esta **deniega la llamada** (codigo 2) y dice por que. Tres detalles que son el pueblo entero:
la marca lleva el SHA-256 del playbook, asi que editarlo invalida todas las lecturas anteriores y
nadie trabaja con una version vieja; va indexada por `session_id`, asi que una ventana no le presta el
permiso a otra; y `PreCompact` la borra, porque si el playbook salio del contexto al compactar es como
no haberlo leido. Un `Read` con `offset` no cuenta: leer un trozo no es haber leido el manual.

Vecino, no rival: `alcance-y-excepcion` limita **donde** se puede escribir; esto limita **si** se
puede escribir todavia. Se usan juntos.

Ojo con tres cosas. Solo vigila las herramientas que le digas (`PLAYBOOK_HERRAMIENTAS`, por defecto
`Edit|Write|MultiEdit|NotebookEdit`): si el dano se puede hacer por consola, esa via queda abierta —
anadela al regex o acota con `PLAYBOOK_RUTAS`. La marca vive en disco (`PLAYBOOK_ESTADO`), asi que
borrar esa carpeta libera el freno. Y esto garantiza que el fichero **se leyo**, no que se entendiera:
es una precondicion, no una revision.
