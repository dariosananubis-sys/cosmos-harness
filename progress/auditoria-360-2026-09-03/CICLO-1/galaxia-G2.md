# Galaxia G2 — auditoría 360, ciclo 1

Repo: `~/cosmos`, rama `arreglos-2026-09-03` (sin commit, sin push, tal como pide el brief).
Pin de estado al escribir este informe: `HEAD b0c1ebdeb2d9bac7e068d10714213ff2f9eda926`,
`git status --porcelain` con 116 ficheros sin commitear (repo compartido por varios agentes de
galaxia trabajando en paralelo en este mismo ciclo).

## Tanda 1 — 21 pueblos nuevos

Verificación en vivo hecha con los tres comandos del brief (`curl -sI`, `.../commits/HEAD.atom`,
API de GitHub) el 2026-09-03. Todas vivas, ninguna archivada, ningún push anterior a 2026-03-01.

| herramienta | padre | URL | último commit | estrellas | licencia | añadida/omitida y por qué |
|---|---|---|---|---|---|---|
| langgraph | agentes-ia/construccion | github.com/langchain-ai/langgraph | 2026-09-03 | 40.976 | MIT | añadida |
| pydantic-ai | agentes-ia/construccion | github.com/pydantic/pydantic-ai | 2026-09-03 | 19.693 | MIT | añadida (ver nota abajo) |
| deepeval | agentes-ia/evaluacion | github.com/confident-ai/deepeval | 2026-09-03 | 18.072 | Apache-2.0 | añadida |
| promptfoo | agentes-ia/evaluacion | github.com/promptfoo/promptfoo | 2026-09-03 | 24.774 | MIT | añadida |
| inspect-ai | agentes-ia/evaluacion | github.com/UKGovernmentBEIS/inspect_ai | 2026-09-03 | 2.692 | MIT | añadida |
| fastmcp | agentes-ia/herramientas | github.com/PrefectHQ/fastmcp | 2026-09-03 | 27.498 | Apache-2.0 | añadida (ver nota abajo) |
| mcp-servers | agentes-ia/herramientas | github.com/modelcontextprotocol/servers | 2026-09-03 | 90.045 | MIT/Apache-2.0 (transición) | añadida |
| browser-use | agentes-ia/herramientas | github.com/browser-use/browser-use | 2026-09-03 | 112.126 | MIT | añadida |
| dspy | agentes-ia/construccion | github.com/stanfordnlp/dspy | 2026-08-31 | 37.744 | MIT | añadida |
| astro | web/construccion-de-sitios | github.com/withastro/astro | 2026-09-02 | 62.252 | MIT | añadida |
| vite | web/construccion-de-sitios | github.com/vitejs/vite | 2026-09-03 | 82.661 | MIT | añadida |
| tailwindcss | web/construccion-de-sitios | github.com/tailwindlabs/tailwindcss | 2026-08-31 | 97.431 | MIT | añadida |
| payload | web/construccion-de-sitios | github.com/payloadcms/payload | 2026-09-03 | 44.552 | MIT | añadida |
| medusajs | web/comercio-electronico | github.com/medusajs/medusa | 2026-09-03 | 36.115 | MIT (Enterprise aparte) | añadida (nombre `medusajs`, no `medusa`: ese lo usa `crytic/medusa`) |
| llama-cpp | modelos-locales/servir | github.com/ggml-org/llama.cpp | 2026-09-03 | 126.862 | MIT | añadida |
| vllm | modelos-locales/servir | github.com/vllm-project/vllm | 2026-09-03 | 90.859 | Apache-2.0 | añadida |
| unsloth | modelos-locales/servir | github.com/unslothai/unsloth | 2026-09-03 | 75.532 | Apache-2.0 | añadida (sin nicho `entrenamiento` en PADRES.txt, se queda en `servir`) |
| qdrant | modelos-locales/recuperacion | github.com/qdrant/qdrant | 2026-08-04 | 34.355 | Apache-2.0 | añadida |
| metabase | analitica/cuadros-de-mando | github.com/metabase/metabase | 2026-09-03 | 49.068 | AGPL-3.0 (comercial en enterprise/) | añadida |
| typst | documentos/publicacion | github.com/typst/typst | 2026-09-01 | 55.818 | Apache-2.0 | añadida |
| quarto | documentos/publicacion | github.com/quarto-dev/quarto-cli | 2026-09-03 | 5.980 | MIT | añadida |

0 omitidas: las 21 pasaron el filtro de viveza. Cero repetidos: `grep -rl "github.com/<slug>" galaxia/`
no encontró ninguno de los 21 slugs ya presente como pueblo (sí aparecen mencionados como rivales
en textos ajenos — p.ej. `langgraph` y `unsloth` en `claude-agent-sdk` y `mlx-lm` — pero eso no es
duplicado de pueblo).

**Nota sobre `pydantic-ai` (encargo 2) y `fastmcp` (encargo 6), verificación de asunciones:**
- El encargo decía "nombra al vecino `claude-agent-sdk-python` si existe con ese nombre en
  `ls galaxia/pueblos`". Comprobado: **no existe ningún pueblo con ese nombre literal.** El pueblo
  real es `galaxia/pueblos/claude-agent-sdk/` (repo `anthropics/claude-agent-sdk-python`, nombre de
  pueblo sin el sufijo `-python`). Se nombra a `claude-agent-sdk` como vecino real, con la aclaración
  en el propio cuerpo de que empaqueta ese repo, en vez de omitir la comparación por el desajuste de
  nombre.
- El encargo decía `PrefectHQ/fastmcp`. Verificado: `github.com/PrefectHQ/fastmcp` es la URL **canónica**
  (200 directo); `github.com/jlowin/fastmcp` (el nombre por el que se conoció al principio) hace 301
  hacia `PrefectHQ/fastmcp`. Se usó el slug del encargo tal cual, ya confirmado como el correcto.

## Tanda 2 — 8 pueblos existentes, reescritura de criterio (hallazgo C-10)

Grep usado en los 8 + `rill`: `grep -n -iE '8 ?GB|sin GPU|GPU dedicada|m[aá]quina justa|esta
m[aá]quina|este port[aá]til' <fichero>`.

| pueblo | frase encontrada | qué se cambió |
|---|---|---|
| `mlx-lm` | "Gana en esta máquina concreta a `llama.cpp`..." | criterio pasado a "gana en Apple Silicon por la memoria unificada" (arquitectura, no una máquina); añadido en Ojo, literal: solo corre en Apple Silicon y el estándar portable es `llama-cpp` |
| `mlx-vlm` | "...que `mlx-lm` gana en esta máquina..." + bullet "Solo Apple Silicon" | mismo ajuste de criterio; bullet de Ojo ampliado con la frase literal "Solo corren en Apple Silicon" y la mención a `llama-cpp` como estándar portable |
| `ollama` | "...GPU dedicada, que esta máquina no tiene..." + "no entra como pueblo propio" sobre llama.cpp | `llama-cpp` y `vllm` dejan de descartarse por la máquina: se nombran como pueblos vecinos con reparto de tareas (control fino vs. conveniencia; throughput concurrente vs. uso local). El requisito de GPU de `vllm` queda como dato en el Ojo |
| `streamlit` | "...una maquina justa de memoria, y las dos anaden un proceso permanente..." | deja de "descartar" a Metabase/Superset; ahora es frontera con `metabase` (pueblo vecino) por criterio de oficio (no-code / autoservicio vs. control de código). El peso JVM/servicios se movió a un párrafo de Ojo nuevo, explícito como dato y no como criterio |
| `godot` | "el editor abre en una maquina justa de memoria..." | ya estaba en un aviso de recursos (no decidía nada): se generalizó la redacción quitando la referencia a una máquina concreta |
| `compose-multiplatform` | "Gradle es lo que aprieta en una maquina justa de memoria..." | ya era un bullet de "lo que no hace bien": se generalizó a "portátil de desarrollo normal" sin referencia a una máquina concreta |
| `flutter` | "En una maquina justa de memoria corre, pero..." | ya era un aviso de recursos: se generalizó igual |
| `unlighthouse` | "...en una máquina justa de memoria hay que bajar la concurrencia..." | ya estaba en el párrafo de Ojo: se generalizó a "con poca memoria libre" |
| `rill` | (comprobado, sin resultado de grep) | **no tocado**: su texto sobre Metabase/Superset ("por peso", "no hay JVM, ni Postgres, ni Redis") no usa ninguna de las frases del patrón — es ya un criterio de peso operativo, no una cifra de RAM/GPU de una máquina concreta. Queda una referencia cruzada ("ya quedaron descartadas en este árbol") que ahora es parcialmente inexacta porque `streamlit` ya no descarta a Metabase — se señala aquí para que quien lo lea lo sepa, pero no se edita: fuera del disparador literal que fija el encargo |

Ninguna decisión se invirtió: los 8 pueblos se quedan donde estaban: solo cambió la justificación.
Las frases sobre coste de contexto/tokens no se tocaron (no había ninguna en estos 8).

## `cosmos validar`

Estado al cerrar (repo compartido, mutando en vivo por otros agentes de galaxia — confirmado con
timestamps: `pa11y`, `ansible`, `blender`, `butler`, `coolify`, `crawlee`, `f5-tts`, `firecrawl`,
`grafana`, `loki`, `love2d`, `opentofu`, `osquery`, `piper`, `vector`, `yt-dlp` se crearon o
modificaron entre las 11:09 y las 11:12 de hoy, mientras este informe se escribía; el contador de
errores subió de 12 a 17 solo, sin que este agente tocase nada de eso):

```
COSMOS  rojo  17 errores
```

**Ninguno de los 17 errores referencia ningún pueblo de esta tanda** (los 21 nuevos ni los 8
reescritos) — comprobado con grep de cada uno de los 29 nombres contra la salida completa de
`validar`: cero coincidencias. Los errores son E07 (resumen de `pa11y`, de otro agente, >120
caracteres) y E19 (`vista plana desincronizada`, pueblos de otros agentes que aún no han pasado por
`cosmos compilar` — comando que este brief no me pide ejecutar y que además tocaría el trabajo en
curso de otros agentes). Por la regla 5 del brief ("retira la última que añadiste al nicho
culpable"): no hay nicho culpable propio que retirar, así que no se retira nada.

## `cosmos medir`

```
COSMOS  medir

  Entrada base .... 1.234 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±5,2 % medio (peor fichero 33,6 %), heurística v3)
  Peor nicho ...... 2.484 tokens   (ciberseguridad, 35 pueblos)
  Agua condicional  1.163 tokens   (6 aguas por paths:, fuera de la entrada)
  Peor con agua ... 3.647 tokens   (el peor caso + agua condicional)
  Universo ........ 164.289 tokens   (estimado, ±5,2 % medio (peor fichero 33,6 %), heurística v3)
  Descarga ........ 98,5 %
  Presupuesto ..... 4.000     OK, quedan 163 tokens con el margen calibrado (+5,2 %) en el peor caso con agua (ciberseguridad)

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)

  Lo más caro de la entrada evaluada:
    1.  1.525 tok  catálogo visible
    2.  555 tok  índice de galaxia
    3.  101 tok  oceano/irreversible

  Vista compilada . 7.968 tokens   (278 entradas en ~/cosmos/.cosmos/vista-galaxia; los paga un runtime que escanee ese directorio; fuera de E16)
```

Presupuesto OK. El peor nicho sigue siendo `ciberseguridad` (35 pueblos) — ninguno de los países
tocados en esta tanda (`agentes-ia`, `web`, `modelos-locales`, `analitica`, `documentos`) es el
peor caso, tal como anticipaba el encargo.

## Ficheros tocados

Nuevos (21):
```
galaxia/pueblos/langgraph/SKILL.md
galaxia/pueblos/pydantic-ai/SKILL.md
galaxia/pueblos/deepeval/SKILL.md
galaxia/pueblos/promptfoo/SKILL.md
galaxia/pueblos/inspect-ai/SKILL.md
galaxia/pueblos/fastmcp/SKILL.md
galaxia/pueblos/mcp-servers/SKILL.md
galaxia/pueblos/browser-use/SKILL.md
galaxia/pueblos/dspy/SKILL.md
galaxia/pueblos/astro/SKILL.md
galaxia/pueblos/vite/SKILL.md
galaxia/pueblos/tailwindcss/SKILL.md
galaxia/pueblos/payload/SKILL.md
galaxia/pueblos/medusajs/SKILL.md
galaxia/pueblos/llama-cpp/SKILL.md
galaxia/pueblos/vllm/SKILL.md
galaxia/pueblos/unsloth/SKILL.md
galaxia/pueblos/qdrant/SKILL.md
galaxia/pueblos/metabase/SKILL.md
galaxia/pueblos/typst/SKILL.md
galaxia/pueblos/quarto/SKILL.md
```

Editados (8, solo cuerpo, `resumen` intacto en todos):
```
galaxia/pueblos/mlx-lm/SKILL.md
galaxia/pueblos/mlx-vlm/SKILL.md
galaxia/pueblos/ollama/SKILL.md
galaxia/pueblos/streamlit/SKILL.md
galaxia/pueblos/godot/SKILL.md
galaxia/pueblos/compose-multiplatform/SKILL.md
galaxia/pueblos/flutter/SKILL.md
galaxia/pueblos/unlighthouse/SKILL.md
```

No tocados (comprobado, no cumplía el gate): `rill/SKILL.md`.

No se tocó `spec/`, `README.md`, `GOAL.md`, `cosmos/`, `puente/`, `tests/`, ni el `resumen` de
ningún pueblo existente. No se ejecutó `cosmos generar` ni `cosmos compilar`. Sin commit, sin push,
sin cambio de rama.
