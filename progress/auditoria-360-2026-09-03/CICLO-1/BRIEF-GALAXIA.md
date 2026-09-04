# Brief para los agentes de la galaxia (auditoría 360, ciclo 1)

Repo: `~/cosmos` (rama `arreglos-2026-09-03`, ya creada; NO cambies de rama, NO hagas commit, NO push).
Todo se hace con `cd ~/cosmos` y `python3` del sistema (`/usr/local/bin/python3`, sin venv).
`trash` no está en el PATH: para retirar algo usa `mv <fichero> ~/.Trash/`, NUNCA `rm`.

## Qué es un pueblo y cómo se escribe

Lee ENTERO `spec/PUEBLO.md` (normativo) y copia la forma de `galaxia/pueblos/nuclei/SKILL.md`
(una herramienta ofensiva) y `galaxia/pueblos/osv-scanner/SKILL.md`. Un pueblo es
`galaxia/pueblos/<nombre>/SKILL.md`:

```markdown
---
cosmos: pueblo
nombre: <nombre>                 # ^[a-z0-9-]+$, ÚNICO en toda la galaxia (ls galaxia/pueblos)
padre: <ruta existente>          # una de PADRES.txt (pais o provincia), nunca inventada
resumen: <≤120 caracteres, sin acentos, dice en qué se distingue de su vecino, no qué categoría es>
---

https://github.com/<org>/<repo> · <licencia leída en su LICENSE> · <N>★ · último push <YYYY-MM-DD> (comprobado 2026-09-03)

```bash
<instalación real: brew/pip/pipx/npm/cargo/go/docker>
```

```bash
# <uso mínimo, copiable, con marcadores explícitos (OBJETIVO-DEL-ALCANCE, RUTA/AL/PROYECTO)>
```

<Por qué este y no otro: «Gana a `rival` en ...». Nombra al rival con su backtick. Frontera con el
vecino del mismo nicho si lo hay.>

Ojo: <lo que no hace bien, falsos verdes, coste de máquina si lo tiene (RAM/GPU), y para las
ofensivas la frase de alcance autorizado>. Las IP de ejemplo son de la RFC 5737 (198.51.100.0/24,
203.0.113.0/24). Cero valores reales, cero rutas de máquina, cero dominios de nadie.
```

Reglas duras (spec/PUEBLO.md «Reglas que no se negocian» + GOAL.md):

1. **Verifica viva cada herramienta ANTES de escribirla**, con estos comandos y pega lo medido en tu
   informe: `curl -sI https://github.com/<slug> | head -1` (200; si 301, usa la URL canónica de
   `Location`), `curl -s https://github.com/<slug>/commits/HEAD.atom | grep -m1 -oE '<updated>[^<]+'`
   (último commit; si es anterior a 2026-03-01, NO la añadas y dilo), y estrellas con
   `curl -s https://api.github.com/repos/<slug> | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['stargazers_count'],d['license'] and d['license']['spdx_id'],d['archived'])"`
   (la API sin token da 60 llamadas/hora entre todos: si devuelve rate limit, saca las estrellas del
   HTML `curl -sL https://github.com/<slug> | grep -oE 'aria-label="[0-9,]+ users starred' | head -1`).
   Una herramienta archivada no entra.
2. **Cero repetidos**: antes de crear, `grep -rl "github.com/<slug>" galaxia/` y `ls galaxia/pueblos | grep <nombre>`.
   Si ya existe en otro sitio, no la dupliques: dilo en el informe.
3. **El resumen es lo que cuesta** (entra en el contexto de cada sesión de ese nicho). ≤120 caracteres,
   concreto, sin acentos. El cuerpo no cuesta: escríbelo completo.
4. No toques el `resumen` de ningún pueblo existente. No ejecutes `cosmos generar`. No edites `spec/`
   ni `README.md` ni `GOAL.md`. No toques `cosmos/` ni `puente/` ni `tests/` (código).
5. Al terminar cada tanda: `python3 -m cosmos validar` tiene que decir `verde 0 errores` (E00 dice la
   línea exacta si el frontmatter está mal; E18 si el nombre se repite; E02 si el padre no existe).
   Y `python3 -m cosmos medir`: pega la salida en el informe. Si el veredicto se pone ROJO, retira la
   última que añadiste al nicho culpable y dilo.

## Informe (anti-teléfono-descompuesto)

Escribe `progress/auditoria-360-2026-09-03/CICLO-1/galaxia-<TU-ID>.md` con: tabla
`herramienta | padre | URL | último commit | estrellas | licencia | añadida/omitida y por qué`, la
salida literal de `cosmos validar` y `cosmos medir` al final, y la lista de ficheros tocados.
Responde en el chat UNA sola línea: `done -> <ruta del informe> | N añadidas, M omitidas` o
`blocked -> <ruta>`.
