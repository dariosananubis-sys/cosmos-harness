# Auditoría 360 COSMOS — Revisor C: el contenido de la galaxia

**Ángulo:** ¿las herramientas son de verdad las mejores que existen, y falta alguna?
**Premisa de entrada (invertida):** la galaxia está llena de relleno y le faltan las piezas buenas.

## Pin de estado

```bash
git -C ~/cosmos rev-parse HEAD          # b0c1ebdeb2d9bac7e068d10714213ff2f9eda926
git -C ~/cosmos status --porcelain | wc -l   # 0  (árbol limpio, antes y después de esta auditoría)
```

Solo lectura sobre el repo. Lo único escrito es este fichero. Cero red de pago, cero correo.

## Método y cobertura

| Qué | Cómo | Cuántos |
|---|---|---|
| Inventario del árbol | frontmatter de `galaxia/**` parseado a JSON | 247 pueblos, 22 oficios, 87 provincias |
| Existencia y renombrado | `curl -sI https://github.com/<slug>` (200 / 301 + `Location`) | **209 / 209** (el 100% de las que declaran repo) |
| Último commit real | `curl -s https://github.com/<slug>/commits/HEAD.atom` → `<updated>` | **209 / 209** |
| Archivado | HTML del repo, `Public archive` / `has been archived` | **209 / 209** |
| Canonicidad (fork vs. oficial) | `api.github.com/repos/<slug>`, sin token, 60/h | 29 dirigidas |
| Contrato de ficha (`spec/PUEBLO.md`) | conteo sobre los 247 cuerpos | 247 / 247 |
| Candidatas a añadir | mismo método que arriba, **antes** de recomendarlas | 80 verificadas, 9 descartadas por muertas |

Las 38 restantes de las 247 no declaran repo: son herramientas propias reescritas (dicen
literalmente «herramienta propia, no de GitHub» y traen su guion). Se auditaron leyéndolas.

Nada de esto necesitó credenciales: `gh auth status` dice *not logged into any GitHub hosts* y no se
usó ningún token. La API sin autenticar tiene 60 llamadas/hora, por eso el barrido masivo va por
HTTP plano y solo 29 comprobaciones puntuales van por API.

## Veredicto en cinco líneas

1. **La premisa era falsa en lo grande y cierta en lo concreto.** Intenté tumbar el árbol entero y
   no pude: 209/209 repos vivos, **cero archivados**, cero duplicados, cero `usa:` roto, y los
   renombrados de org están **al día** (ver «lo que no pude tumbar»).
2. El relleno existe pero está **concentrado en tres sitios**: `agentes-ia`, `web/construccion-de-sitios`
   y `visibilidad`.
3. Lo que falta pesa más que lo que sobra, y son ausencias de libro: **`nmap`, ni una herramienta de
   infraestructura como código, ni un perfilador de memoria, ni una herramienta de evaluación de agentes.**
4. Hay un sesgo transversal no declarado: **24 fichas (10%) eligen por las restricciones de UNA
   máquina** (8 GB, sin GPU, Apple Silicon), en un repo que GOAL §5 declara genérico.
5. **17 herramientas a retirar o degradar, 24 a añadir**, y la aritmética del presupuesto dice que
   casi todas caben (§ LO QUE FALTA).

---

# HALLAZGOS

## C-01 · ALTO · `agentes-ia` no es el oficio que declara: es «operar Claude Code»

El oficio dice *«Agentes que hacen trabajo real, con herramientas, memoria y evaluación»*. Lo que hay:

```bash
for d in $(grep -l 'padre: agentes-ia' galaxia/pueblos/*/SKILL.md | xargs -n1 dirname); do
  grep -q github.com "$d/SKILL.md" && echo "GH   $(basename $d)" || echo "propio $(basename $d)"
done | sort | uniq -c
#   15 propio      ← 71%
#    6 GH
```

| provincia | contenido |
|---|---|
| `coste` (7) | **7 de 7 propios**, todos sobre abaratar sesiones de Claude Code: `auditar-gasto`, `captura-recortada`, `codigo-al-modelo`, `cuentas-del-asistente`, `lanzadores-de-modelo`, `medir-contexto`, `quota-oficial` |
| `construccion` (3) | 2 propios + **un solo SDK, de un solo proveedor** (`anthropics/claude-agent-sdk-python`) |
| `evaluacion` (2) | `mlflow` (rastreador de experimentos de ML, no de agentes) + `revision-cruzada` (propio) |
| `herramientas` (4) | `agent-browser`, `openclaw` + 2 propios |
| `memoria` (3) | `claude-mem`, `mem0` + 1 propio — la única provincia bien surtida |

Y es **el catálogo más caro de toda la galaxia**: 646 tokens, por delante de `ciberseguridad` (645),
que tiene 27 herramientas de verdad.

`lanzadores-de-modelo` repone `additionalModelOptionsCache` del CLI de Claude Code. Eso no es el
oficio «construir agentes»: es el taller de una persona. GOAL §5 — *«público-limpio y genérico, fuera
de cualquier organización, cliente o negocio»*.

Cero de: `langchain-ai/langgraph`, `pydantic/pydantic-ai`, `stanfordnlp/dspy`, `confident-ai/deepeval`,
`promptfoo/promptfoo`, `langfuse/langfuse`, `PrefectHQ/fastmcp`, `modelcontextprotocol/servers`,
`browser-use/browser-use`, `UKGovernmentBEIS/inspect_ai`. Ninguna está **ni siquiera nombrada como
rival descartado**, que es como el resto del árbol defiende sus decisiones.

**La prueba del oficio, aplicada a la provincia:** *«¿alguien contrataría `agentes-ia/coste`?»* No.
Se contrata «hazme un agente que haga X». `coste` es una categoría temática de las que UNIVERSO.md
dice haber expulsado.

## C-02 · ALTO · `web/construccion-de-sitios`: 7 de 7 son WordPress, cero frameworks

```bash
grep -l 'padre: web/construccion-de-sitios' galaxia/pueblos/*/SKILL.md | xargs -n1 dirname | xargs -n1 basename
# dominios-libres  elementor-mcp  punto-de-restauracion-web
# web-fidelidad-elementor  wordpress-skills  wp-app-password  wp-remoto
```

Una provincia llamada **construcción de sitios** sin una sola herramienta con la que se construya un
sitio. El oficio declarado es *«Un sitio o una tienda que carga, convierte y no se cae»* — eso lo
contrata quien quiere Astro, Next o una tienda headless igual que quien quiere WordPress. Ausentes y
sin defensa: `withastro/astro`, `vitejs/vite`, `tailwindlabs/tailwindcss`, `medusajs/medusa`,
`payloadcms/payload`. `vercel/next.js` solo aparece dentro de la ficha de `context7`, como ejemplo de
consulta de documentación.

Del nicho `web` entero (17), **10 son WordPress/Elementor/Woo/Shopify** y 7 son propios (41%, el
segundo ratio más alto del árbol tras `agentes-ia`).

## C-03 · ALTO · `infraestructura` sin infraestructura como código, y con métricas que nadie puede ver

El oficio dice *«Que corra 24/7: despliegue, copias restaurables, monitorización»*. Medido:

```bash
grep -ril -E 'ansible|opentofu' galaxia/ | wc -l     # 0
grep -ril terraform galaxia/                          # solo galaxia/pueblos/trivy  (como objeto a escanear)
grep -ril grafana galaxia/                            # solo galaxia/pueblos/victoriametrics
```

- **Cero herramientas de infraestructura como código en las 247.** El despliegue se cubre con tres
  patrones propios (`contrato-de-publicacion`, `despliegue-reanudable`, `contenedor-efimero`) que
  describen el *proceso*, no la herramienta que declara el servidor.
- **`victoriametrics` guarda métricas y no hay nada que las pinte.** Grafana aparece una sola vez, en
  el argumento de venta de la propia ficha: *«los paneles de Grafana existentes valen sin tocarlos»* —
  paneles que en esta galaxia no existen. Es un almacén de métricas sin visor.
- Cero logs (`grafana/loki`, `vectordotdev/vector`), cero PaaS autoalojada (`coollabsio/coolify`),
  cero orquestación (`k3s-io/k3s`, `traefik/traefik`).

## C-04 · ALTO · `ciberseguridad` es el nicho más grande de la galaxia y no tiene `nmap`

```bash
grep -ril nmap galaxia/ | wc -l    # 0  — ni como pueblo, ni como rival descartado, ni de pasada
```

La provincia `ofensiva/reconocimiento` son dos herramientas: `amass` (subdominios) y `nuclei`
(plantillas de vulnerabilidad). Falta el escaneo de puertos y servicios, que es literalmente el primer
comando de cualquier reconocimiento autorizado. Es el caso exacto del encargo: *«una herramienta que
cualquier profesional del oficio nombraría primero»*.

En la misma línea, y todas verificadas vivas: `ffuf/ffuf` (descubrimiento de contenido),
`projectdiscovery/httpx` + `projectdiscovery/subfinder` (los compañeros naturales de `nuclei`, del
mismo autor), `hashcat/hashcat` (auditoría de contraseñas — hoy no hay ninguna),
`wireshark/wireshark` (forense de red: `chainsaw` solo lee EVTX de Windows y `volatility3` solo
memoria; **la red no la mira nadie**), `github/codeql` (gratis para código abierto, el motor de
seguimiento de datos entre procedimientos más fuerte que existe; `semgrep` está y no lo nombra).

## C-05 · ALTO · `rendimiento` promete «memoria» en su propia definición y no trae un solo perfilador de memoria

`spec/UNIVERSO.md`, fila 21: *«Que el código vaya rápido: perfilado, depuración de lo raro, **memoria**»*.

Las 8 de `rendimiento`: `py-spy`, `samply`, `hyperfine`, `bpftrace` (perfilado de CPU y de núcleo),
`rr`, `sanitizers` (depuración), `mimalloc`, `tokio` (bibliotecas con las que se escribe, no con las
que se mide).

`valgrind` aparece una vez, descartado dentro de `sanitizers` por lento — y ese descarte solo cubre
C/C++. **Python y Node se quedan sin nada**: `bloomberg/memray` (2026-09-01) y
`plasma-umass/scalene` (2026-08-27) no están ni nombrados. Es una contradicción entre el alcance que
el oficio declara y lo que contiene, medible en una línea.

## C-06 · MEDIO-ALTO · Herramientas de propósito general encerradas en un nicho, inalcanzables desde donde hacen falta

`trading/bots/codigo-de-bot` son 6 pueblos y **ninguno es de trading**:

| pueblo | qué es de verdad |
|---|---|
| `hypothesis` | LA biblioteca de pruebas basadas en propiedades de Python |
| `tenacity` | reintento con espera creciente, para cualquier cliente de red |
| `toxiproxy` | inyección de fallos de red, para cualquier sistema distribuido |
| `time-machine` | congelar el reloj en un test, para cualquier código con fechas |
| `eventsourcing` | registro que solo crece |
| `python-statemachine` | máquinas de estado |

Los resúmenes están redactados en jerga de trading («cierres de vela», «una orden»), lo que disimula
el problema en vez de resolverlo. Y la contención lo cierra: **solo `blockchain` declara `usa: trading`**,
así que quien trabaja en `saas`, `web` o `infraestructura` nunca sabrá que `hypothesis` existe en este
repo.

Lo agrava que los mares describen ese terreno con precisión y **no nombran ninguna**:

```bash
for m in galaxia/agua/mar-*.md; do printf '%-28s ' "$(basename $m)"; grep -o '`[a-z0-9/._-]*`' $m | tr '\n' ' '; echo; done
# mar-pruebas.md      `refactorizacion/mutacion`
# mar-resistencia.md
# mar-criterio.md     `refactorizacion`
```

`mar-pruebas` dice *«El caso que rompe no se escribe a mano: se muta la entrada»* — que es exactamente
`hypothesis` — y apunta a `refactorizacion/mutacion`, no a donde está. **El mecanismo de apuntar
existe y funciona; aquí simplemente no se usó.** El arreglo es barato: mover los cuatro genéricos a un
sitio neutro, o que `mar-pruebas` y `mar-resistencia` los nombren.

## C-07 · MEDIO · `claude-seo-ai`: un repositorio terminado en cuatro minutos hace tres meses

```bash
curl -s https://api.github.com/repos/Hainrixz/claude-seo-ai | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['stargazers_count'],d['created_at'],d['pushed_at'])"
# 47 2026-06-01T... 2026-06-01T...
curl -s https://github.com/Hainrixz/claude-seo-ai/commits/HEAD.atom | grep -c '<entry>'   # 5
curl -s https://github.com/Hainrixz/claude-seo-ai/commits/HEAD.atom | grep -oE '<updated>[^<]+'
# <updated>2026-06-01T19:22:54Z   <updated>2026-06-01T19:22:54Z   <updated>2026-06-01T19:18:58Z
```

47 estrellas, **5 commits, todos el mismo día entre las 19:18 y las 19:22**, y nada más en tres meses.
Es el ejemplo más claro de relleno de toda la galaxia, y ocupa un puesto en un nicho que solo tiene 7.
Criterio 4 de UNIVERSO.md (*«está vivo»*) es eliminatorio y esto no lo pasa.

## C-08 · MEDIO · `visibilidad`: 3 de 7 no son herramientas que se ejecuten

- `bing-webmaster` → `https://learn.microsoft.com/en-us/bingwebmaster/...` (documentación de producto)
- `search-console` → `https://developers.google.com/webmaster-tools/v1` (ídem)
- `claude-seo-ai`, `geo-optimizer` → colecciones de skills en markdown

Los dos primeros se salvan por poco: traen guiones propios (3 ficheros cada uno), así que **sí se
ejecutan** — pero entonces son pueblos propios mal presentados, no herramientas de GitHub, y su
primera línea incumple la regla 1 de `spec/PUEBLO.md`. `geo-optimizer` está vivo (759★, push de hoy);
`claude-seo-ai` no (C-07).

Falta la capa medible del oficio: `sitespeedio/sitespeed.io` (2026-08-27) y `projectdiscovery/katana`
(2026-08-31) para rastrear el sitio de verdad. Nota: `GoogleChrome/lighthouse-ci` **no** lo recomiendo,
su último commit es de 2025-06-26.

## C-09 · MEDIO · `mythril` ocupa el puesto de análisis simbólico y está parado

```bash
curl -s https://github.com/ConsenSysDiligence/mythril/commits/HEAD.atom | grep -m1 -oE '<updated>[^<]+'
# <updated>2025-01-31T15:33:53Z      (rama por defecto; pushed_at de la API: 2026-04-27)
```

Entre 4 y 19 meses parado, según se mire la rama o el `pushed_at`, en un nicho donde el propio
UNIVERSO.md dice que *«el valor está en la auditoría»*. Su relevo natural, `crytic/medusa`
(2026-05-14, del mismo equipo que `slither` y `echidna`, que ya están), no está.
`a16z/halmos` lo comprobé y **también lo descarto**: 2025-08-06.

## C-10 · MEDIO · 24 fichas eligen por las restricciones de una sola máquina

```bash
grep -ril -E '8 ?GB|sin GPU|GPU dedicada|m[aá]quina justa|esta m[aá]quina|este port[aá]til' galaxia/pueblos/*/SKILL.md | wc -l
# 24   (10% de las 247)
```

El caso que lo define, en `mlx-lm`:

> «Gana **en esta máquina concreta** a `ggml-org/llama.cpp` (126.621★, **el estándar de facto**) por la memoria»

Y en `streamlit`: Metabase y Superset descartadas porque *«ninguna de las dos cabe cómoda en una
máquina justa de memoria»*. Y en `ollama`: `vllm` descartado porque *«esta máquina no tiene GPU dedicada»*.

Dos consecuencias medibles:

1. `mlx-lm` y `mlx-vlm` **solo corren en Apple Silicon**: 2 de las 9 de `modelos-locales` no arrancan
   en ninguna otra máquina, en un nicho cuya promesa es *«IA que corre en tu máquina»*.
2. El criterio se ha deslizado de «lo mejor que existe para ese trabajo» a «lo mejor que corre en el
   portátil de quien lo escribe», en un repo que GOAL §5 declara genérico y fuera de cualquier
   organización.

**No pido invertir las decisiones**, que están bien argumentadas una a una. Pido que el sesgo se
declare (una línea en la estrella del nicho o en UNIVERSO.md) y que el estándar de facto entre como
pueblo con su aviso de hardware, en vez de quedarse fuera. Un catálogo genérico que oculta
`llama.cpp` y `vLLM` no es el harness más completo que existe.

## C-11 · MEDIO · `analitica/cuadros-de-mando` tiene 5 herramientas y ninguna es una plataforma de BI

`datasette`, `evidence`, `marimo`, `rill`, `streamlit`. Cinco formas de pintar un cuadro de mando desde
un guion, y cero herramientas de inteligencia de negocio con servidor. Es el caso más claro de
«acumulación» que el criterio 2 de UNIVERSO.md prohíbe (*«uno por trabajo»*), y el descarte de
`metabase/metabase` y `apache/superset` vuelve a ser por peso de máquina (C-10), no por oficio. Quien
contrata *«cuadros de mando y métricas de negocio en los que se puede confiar»* nombra Metabase primero.

## C-12 · BAJO-MEDIO · `chonkie` cambió de organización y la ficha sigue con la vieja

```bash
curl -sI -o /dev/null -w '%{http_code} %{redirect_url}\n' https://github.com/chonkie-inc/chonkie
# 301 https://github.com/feyninc/chonkie
```

Es **el único de los 209** cuyo enlace ya no es el canónico. La ficha dice «comprobado». Regla 2 de
`spec/PUEBLO.md`: *«un dato sin fecha envejece en silencio»* — aquí el dato tiene fecha y aun así
envejeció, lo que sugiere que hace falta el guion que revalide, no más disciplina.

## C-13 · BAJO · El contrato de `spec/PUEBLO.md` se cumple en la mayoría, no en todo

Medido sobre los 247 cuerpos:

| Regla de `spec/PUEBLO.md` | Cumple |
|---|---|
| bloque de código | **247/247 (100%)** |
| URL en la primera línea del cuerpo | 208/247 (84%) — las 39 restantes son propias |
| licencia + estrellas + fecha en la primera línea | 204/247 (82%) |
| regla 4, «la comparación nombra al rival» | 186/247 (75%) |
| regla 5, «lo que no hace bien, también» | 184/247 (74%) |
| comando de instalación reconocible | 206/247 (83%); de los 41 sin él, **solo 7 son herramientas externas** |

Los 7 externos sin instalación: `coraza`, `elementor-mcp`, `miniaudio`, `openrewrite`, `sanitizers`
(justificado: se activa con una bandera del compilador y la ficha lo explica), `claude-seo-ai`,
`auditor-de-skills`. Los 63 sin apartado de límites se concentran en `audiovisual`, `analitica`,
`ingenieria-datos` y `embebidos` — nichos de la última tanda, lo que apunta a que la regla 5 se
incorporó a mitad y no se retroaplicó.

## C-14 · BAJO · `auditor-de-skills` es el único pueblo sin URL de repositorio, y su marcador da un 404

Su único enlace http es `https://github.com/usuario/repo`, dentro de un ejemplo de uso. Como ejemplo es
**legítimo** (regla 6 lo exige así) y aclaro que mi primer barrido lo marcó como repo muerto: era un
falso positivo mío. El fallo real es otro y es menor: es una herramienta propia que no se presenta
como tal en la primera línea, y hace que cualquier verificación automática de URLs del árbol dé un 404
que no lo es. Se arregla con la línea `herramienta propia, no de GitHub` que usan sus 37 hermanas.

## C-15 · BAJO · `juegos` promete distribución y activos 3D, y no trae ninguno

*«Un juego que se publica: motor, bucle, activos, **distribución**»*. Los activos son 2D
(`libresprite`, `tiled`) y audio (`miniaudio`); no hay `blender/blender` (2026-09-03). Y de
distribución, nada: `itchio/butler` (2026-09-03) es la herramienta de línea de comandos con la que se
publica, y no está. Es el nicho más famélico junto a `cientifico` (7), y el que más margen de
presupuesto tiene (§ LO QUE FALTA).

## C-16 · BAJO · Huecos de vecindad: `usa:` está sano pero incompleto

```bash
# comprobado por script: 0 destinos inexistentes en todo el árbol (sistemas, pueblos y aguas)
```

Cero rotos — pero faltan cruces evidentes, todos unidireccionales:

| Nicho | Le falta apuntar a | Por qué |
|---|---|---|
| `juegos` | `moviles` | publicar en tiendas es su propia promesa, y `fastlane` vive allí |
| `audiovisual` | `modelos-locales` | `whisper-cpp` y `kokoro` son modelos que corren en local |
| `analitica` | `web` | `matomo`, que es analítica web, vive en `visibilidad/medicion` |
| `embebidos` | `ciberseguridad` | la relación existe pero solo en el otro sentido |
| `refactorizacion` | `agentes-ia` | el cambio en masa hoy se conduce con agentes; `agentes-ia` sí le apunta |

## C-17 · BAJO · Dos pueblos propios dependen de un servicio externo con cuenta

`revision-cruzada` necesita `OPENROUTER_API_KEY` (capa gratuita) y `quota-oficial` llama a
`api.anthropic.com`. Son gratuitos y no piden tarjeta, así que **no incumplen** la prohibición de GOAL
§5, pero su ficha admite que *«los identificadores de modelo envejecen en semanas»* y que una capa
gratuita que desaparece *«se ve igual que un fallo de red»*. Es deuda con fecha de caducidad en un
catálogo cuyo criterio 5 es «se ha usado una vez»: conviene una comprobación periódica, no una
retirada.

---

# LO QUE FALTA

Esta es la mitad del valor de la revisión, así que va con la aritmética delante.

## El presupuesto permite casi todo — pero no donde parece

```bash
python3 -m cosmos medir
#   Entrada base .... 1.343 tokens
#   Peor nicho ...... 2.383 tokens   (ciberseguridad, 27 pueblos)
#   Peor con agua ... 3.546 tokens
#   Presupuesto ..... 4.000     OK, quedan 454 tokens en el peor caso
```

Coste medido de una entrada de catálogo (nombre + resumen, los cuerpos no entran): **~26 tokens**
(26.597 caracteres / 247 pueblos / 4). De ahí, tres consecuencias que ordenan todo lo que sigue:

1. **En `ciberseguridad` caben ~17 herramientas más** antes de tocar el techo (454 / 26). Suficiente
   para todo el hueco de C-04.
2. **En los nichos famélicos el margen es enorme y gratis**: el techo lo marca el nicho más grande, así
   que `juegos` (176 tok) puede crecer hasta igualar a `ciberseguridad` (645) — unas **18 herramientas
   sin que el peor caso se mueva un token**. Igual `cientifico` (177) y `visibilidad` (195).
3. **Un oficio nuevo cuesta cero en el peor caso.** Añadir nichos es, con diferencia, la forma más
   barata de que «esté todo lo que hace falta». Lo caro es engordar `ciberseguridad` y `agentes-ia`.

## Prioridad 1 — tapan un agujero que hoy hace fallar el oficio

Todas verificadas el 2026-09-03 con el método de la cabecera: existe, no archivada, último commit citado.

| Herramienta | Dónde | Último commit | Por qué es prioridad 1 |
|---|---|---|---|
| `nmap/nmap` | `ciberseguridad/ofensiva/reconocimiento` | 2026-09-02 | C-04. El primer comando del oficio, ausente del nicho más grande |
| `ansible/ansible` | `infraestructura/despliegue` | 2026-09-02 | C-03. Cero IaC en 247 herramientas |
| `opentofu/opentofu` | `infraestructura/despliegue` | 2026-09-02 | C-03. El sucesor libre de Terraform, licencia MPL sin la trampa BUSL |
| `grafana/grafana` | `infraestructura/vigilancia` | 2026-09-03 | C-03. `victoriametrics` guarda métricas que hoy nadie puede ver |
| `bloomberg/memray` | `rendimiento/perfilado` | 2026-09-01 | C-05. El oficio dice «memoria» y no hay ninguno |
| `langchain-ai/langgraph` | `agentes-ia/construccion` | 2026-09-03 | C-01. Grafo de estados con checkpoint: el estándar para agentes con ciclos |
| `pydantic/pydantic-ai` | `agentes-ia/construccion` | 2026-09-03 | C-01. Rompe el monocultivo de un solo proveedor; salida tipada |
| `confident-ai/deepeval` | `agentes-ia/evaluacion` | 2026-09-02 | C-01. La provincia «evaluación» hoy solo tiene un rastreador de experimentos |
| `promptfoo/promptfoo` | `agentes-ia/evaluacion` | 2026-09-03 | C-01. Evaluación por fichero declarativo + red teaming, con código de salida |
| `withastro/astro` | `web/construccion-de-sitios` | 2026-09-02 | C-02. Con lo que se construye un sitio rápido que no es WordPress |
| `crytic/medusa` | `blockchain/auditoria` | 2026-05-14 | C-09. Releva a `mythril`, mismo equipo que `slither` y `echidna` |
| `ggml-org/llama.cpp` | `modelos-locales/servir` | 2026-09-03 | C-10. El estándar de facto (126.621★), hoy solo citado dentro de otra ficha |

## Prioridad 2 — el oficio funciona sin ellas, pero un profesional las echa de menos

| Herramienta | Dónde | Último commit | Nota |
|---|---|---|---|
| `wireshark/wireshark` | `ciberseguridad/analisis/forense` | 2026-09-03 | hoy el forense es disco y memoria; la red no la mira nadie |
| `github/codeql` | `ciberseguridad/analisis/vulnerabilidades` | 2026-09-02 | gratis para código abierto; `semgrep` no lo nombra |
| `ffuf/ffuf` | `ciberseguridad/ofensiva/reconocimiento` | 2026-08-20 | descubrimiento de contenido |
| `hashcat/hashcat` | `ciberseguridad/ofensiva/post-explotacion` | 2026-09-03 | no hay ninguna auditoría de contraseñas |
| `anchore/syft` | `cumplimiento/licencias` | 2026-09-02 | SBOM: hoy no hay ninguna, y ya es requisito regulatorio en Europa |
| `metabase/metabase` | `analitica/cuadros-de-mando` | 2026-09-03 | C-11, con su aviso de peso (JVM) en el apartado de límites |
| `yt-dlp/yt-dlp` | `audiovisual/video` | 2026-08-30 | **la galaxia ya lo usa** en `reel-a-texto/scripts/ig-dl.sh` y no está catalogado: dependencia oculta |
| `typst/typst` | `documentos/publicacion` | 2026-09-01 | informes desde la fuente, sin la cadena de LaTeX |
| `blender/blender` | `juegos/activos` | 2026-09-03 | C-15, y margen de presupuesto de sobra |
| `itchio/butler` | `juegos` (provincia nueva: distribución) | 2026-09-03 | C-15: «distribución» está en la definición del oficio |
| `vllm-project/vllm` | `modelos-locales/servir` | 2026-09-03 | con su aviso «necesita GPU dedicada»: el aviso es la ficha, no el descarte |
| `unslothai/unsloth` | `modelos-locales` (provincia nueva: ajuste) | 2026-09-03 | no hay ninguna forma de ajustar un modelo en local |

## Prioridad 3 — completan, y son baratas porque van a nichos famélicos

`projectdiscovery/httpx` + `subfinder` (ciberseguridad, compañeros de `nuclei`) · `osquery/osquery`
(visibilidad de puestos) · `grafana/loki` y `vectordotdev/vector` (logs) · `coollabsio/coolify`
(PaaS autoalojada) · `medusajs/medusa` y `payloadcms/payload` (web, tienda y CMS sin WordPress) ·
`vitejs/vite` + `tailwindlabs/tailwindcss` (web) · `PrefectHQ/fastmcp` y
`modelcontextprotocol/servers` (agentes-ia/herramientas) · `browser-use/browser-use` y
`UKGovernmentBEIS/inspect_ai` (agentes-ia) · `stanfordnlp/dspy` (agentes-ia) ·
`plasma-umass/scalene` (rendimiento) · `async-profiler/async-profiler` (rendimiento, JVM) ·
`aboutcode-org/scancode-toolkit` (cumplimiento; `ort` lo usa por dentro) · `pa11y/pa11y`
(cumplimiento, accesibilidad legal por línea de comandos) · `quarto-dev/quarto-cli` (documentos) ·
`apify/crawlee` y `firecrawl/firecrawl` (extraccion) · `SQLMesh/sqlmesh` (ingenieria-datos, rival
declarado de dbt) · `nextflow-io/nextflow` (cientifico, rival de snakemake) · `jax-ml/jax`
(cientifico: hoy no hay ni una biblioteca de cálculo con derivadas) · `go-task/task` o `casey/just`
y `pre-commit/pre-commit` (automatizacion: hoy no hay ninguna forma declarativa de repetir un
comando; `pre-commit` solo se cita dentro de `ruff`) · `keycloak/keycloak` (saas; `casdoor` lo
descarta bien, pero es el que todo cliente pide por nombre) · `sitespeedio/sitespeed.io` y
`projectdiscovery/katana` (visibilidad) · `love2d/love` (juegos) · `OHF-Voice/piper1-gpl` y
`SWivid/F5-TTS` (audiovisual/voz: hoy `kokoro` es la única síntesis y lleva parada desde 2025-08-06) ·
`qdrant/qdrant` (modelos-locales/recuperacion) · `apache/arrow` (ingenieria-datos).

**Descartadas tras verificarlas** — las comprobé precisamente para no cometer el fallo que audito:
`protectai/llm-guard` (**archivada**), `a16z/halmos` (2025-08-06), `brendangregg/FlameGraph`
(2024-10-20), `SYSTRAN/faster-whisper` (2025-11-19), `GoogleChrome/lighthouse-ci` (2025-06-26),
`explodinggradients/ragas` (renombrada a `vibrantlabsai/ragas` y parada desde 2026-02-24).

## Oficios contratables que no están en el universo

Añadir un oficio **no mueve el peor caso**, así que estos son los que mejor relación tienen entre
«lo que falta» y lo que cuesta:

| Oficio propuesto | El trabajo por el que te contratan | ¿Alguien contrataría esto? |
|---|---|---|
| `localizacion` | Que el producto hable otros idiomas y no se rompa al hacerlo: extracción de cadenas, memoria de traducción, pseudolocalización, formatos por región | Sí, y es un encargo recurrente y facturable por sí solo. Hoy no existe nada de i18n en las 247 |
| `entregabilidad` | Que el correo llegue a la bandeja de entrada: SPF, DKIM, DMARC, reputación, rebotes, listas | Sí. Hoy solo hay `correo-smtp` suelto en `automatizacion`, que envía pero no responde de que llegue |
| `aprendizaje-automatico` | Entrenar, evaluar y servir un modelo propio para un problema de un cliente | Sí, y es un oficio distinto de `modelos-locales` (correr modelos ajenos). Hoy `mlflow` está de prestado en `agentes-ia/evaluacion` y no hay ninguna biblioteca de entrenamiento |

Candidato de segunda fila: `fiabilidad` (guardia, incidentes, postmortem, SLO). No lo propongo con
fuerza porque se solapa con `infraestructura/vigilancia` y con el mar `resistencia`; primero
arreglaría C-03 y luego vería si sobra terreno.

## «Oficios» del árbol que no pasan la prueba

No hay ninguno a nivel de sistema solar: los 22 aguantan la prueba. Sí a nivel de provincia:

- **`agentes-ia/coste`** (7 pueblos, 7 propios). Nadie contrata «coste». Es una categoría temática, y
  además de un taller concreto (C-01). Su sitio natural es fuera del universo de oficios: es harness,
  no oficio.
- **`automatizacion/gestion`** (`openproject`, `twenty`, `docuseal`). Nadie contrata «gestión»: contrata
  un CRM montado o una firma electrónica funcionando, y eso es `saas`. Tres herramientas de producto
  final metidas en el oficio de *«que lo repetitivo se haga solo»*.

---

# MUERTAS O DUDOSAS A RETIRAR

Ninguna de las 209 está archivada y ninguna da 404. Estas son por actividad, por adopción o por
encaje. **17 en total: 3 firmes, 6 dudosas, 8 a vigilar.**

## Retirar (3)

| Herramienta | Dónde | Evidencia | Motivo |
|---|---|---|---|
| `claude-seo-ai` | `visibilidad/auditoria` | 47★, 5 commits, todos el 2026-06-01 en 4 minutos | criterio 4 (vivo), eliminatorio. C-07 |
| `mythril` | `blockchain/auditoria` | último commit de rama 2025-01-31 | superada por `crytic/medusa`. C-09 |
| `talipp` | `trading/mercado/investigacion` | 2025-09-09, 12 meses parada | duplica el hueco de `ta-lib` en la misma provincia |

## Dudosas — se quedan solo si su ficha justifica el solapamiento (6)

| Herramienta | Dónde | Duda |
|---|---|---|
| `a11y-auditoria-wcag` | `web/calidad-de-sitio` | 56★, colección de skills de una persona, push 2026-06-13, al lado de `axe-core` (el estándar de la industria, mismo terreno) |
| `unlighthouse` | `web/calidad-de-sitio` | es `lighthouse` a escala; dos pueblos para un motor. O se fusionan, o la ficha dice qué decide cuál |
| `arx` | `cumplimiento/datos-personales` | 2025-10-01, aplicación Java de escritorio en un árbol de herramientas de línea de comandos; `presidio` cubre lo mismo y se ejecuta |
| `reprozip` | `cientifico/reproducible` | 2026-01-18, y `pixi` + `dvc` ya cubren entorno y datos |
| `tokio`, `mimalloc` | `rendimiento` | son bibliotecas con las que se escribe, no herramientas que midan; la ficha lo defiende como «el país de código del nicho», pero el oficio es «que vaya rápido». Si se quedan, que el margen se use antes en un perfilador de memoria (C-05) |
| `openproject`, `twenty` | `automatizacion/gestion` | producto final, no automatización. Su sitio es `saas` o fuera |

## A vigilar — vivas pero lentas (8)

`kokoro` 2025-08-06 · `ib-async` 2025-12-06 · `hftbacktest` 2025-12-23 · `quantstats` 2026-01-13 ·
`sanitizers` 2026-05-19 (el repo es documentación; la implementación viaja en `llvm-project`, y la
ficha lo dice bien) · `woocommerce/agent-skills` 10★ (fuente oficial, adopción mínima) ·
`revision-cruzada` y `quota-oficial` (C-17, caducidad por servicio externo).

## Corregir sin retirar (2)

- `chonkie`: la URL canónica es `feyninc/chonkie` (C-12).
- `auditor-de-skills`: falta la línea «herramienta propia, no de GitHub» que usan sus 37 hermanas; su
  marcador `usuario/repo` provoca un 404 falso en cualquier verificación automática (C-14).

---

# DUPLICADOS

**Cero.** La regla dura *«una herramienta vive en un solo sitio»* se cumple, medida por tres vías
sobre el árbol completo:

```bash
cut -f3 repos.txt | tr 'A-Z' 'a-z' | sort | uniq -d          # (vacío)  slugs de GitHub
ls galaxia/pueblos | tr 'A-Z' 'a-z' | sort | uniq -d          # (vacío)  directorios
grep -h '^nombre:' galaxia/pueblos/*/SKILL.md | sed 's/nombre: //' | tr 'A-Z' 'a-z' | sort | uniq -d
                                                              # (vacío)  campo nombre
```

Comprobé también la variante que se me pidió normalizar (`ripgrep`/`rg` y familia): no hay ningún par
con nombre distinto y repositorio igual. Intenté tumbarlo por sinónimos y por herramienta envuelta en
otra (`ollama`↔`llama.cpp`, `ocrmypdf`↔`tesseract`, `ort`↔`scancode`) y en los tres casos la
herramienta interior **no** es un pueblo: se nombra dentro de la ficha de quien la envuelve, que es
exactamente lo que la regla pide.

**Lo que sí hay son solapamientos funcionales dentro de una misma provincia**, que es otra regla —el
criterio 2, «uno por trabajo»— y esa sí se dobla en cinco sitios:

| Provincia | Cuántas | Solapamiento |
|---|---|---|
| `analitica/cuadros-de-mando` | 5 | C-11: cinco formas de pintar un panel, ninguna plataforma de BI |
| `trading` (agregado) | 7 cosas que hacen backtest | `backtesting-py` + `vectorbt` + `hftbacktest` + los 4 motores, que traen el suyo |
| `web/calidad-de-sitio` | 5 | `lighthouse` + `unlighthouse` (mismo motor) y `axe-core` + `a11y-auditoria-wcag` (mismo terreno) |
| `audiovisual/voz` | 5 | `whisper-cpp` + `whisperx` está bien argumentado; `kokoro` sola cubre la síntesis y está parada |
| `automatizacion/flujos` | 3 | `n8n` + `node-red` + `windmill`, con fichas que sí se distinguen entre sí |

Los dos últimos los doy por defendidos: sus resúmenes dicen en qué se distinguen, que es lo que el
criterio 2 exige cuando de verdad empatan. Los tres primeros, no.

---

# LO QUE ESTÁ BIEN ELEGIDO (y lo que intenté tumbar sin conseguirlo)

Entré dando por hecho que la galaxia era relleno. Esto es lo que ataqué y aguantó:

1. **Vitalidad: 209/209.** Cero repositorios archivados, cero 404 reales, un solo enlace desactualizado
   (`chonkie`). Para un catálogo de 209 herramientas es un resultado muy por encima de lo normal.
2. **Los renombrados de organización están al día, y yo estaba equivocado en nueve.** Marqué como
   sospechosos `react/react-native`, `treeverse/dvc`, `hydra-ecosystem/hydra`, `otter-sec/anchor`,
   `PyPortfolio/PyPortfolioOpt`, `stripe/ai`, `d2lang/d2`, `huggingface/sentence-transformers` y
   `ConsenSysDiligence/mythril` porque recordaba los nombres viejos. Los nueve son **el nombre
   canónico de hoy**; los que yo daba por buenos devuelven `Moved Permanently`:
   ```bash
   curl -s https://api.github.com/repos/facebook/react-native  | head -3   # "Moved Permanently"
   curl -s https://api.github.com/repos/iterative/dvc          | head -3   # "Moved Permanently"
   ```
   Alguien los verificó en vivo, como manda la regla 2 de `spec/PUEBLO.md`.
3. **Las fichas ejecutan de verdad.** 247/247 traen bloque de código, y de los 41 sin comando de
   instalación solo 7 son herramientas externas — y una (`sanitizers`) explica correctamente por qué
   no hay nada que instalar. El hallazgo H05 que originó `spec/PUEBLO.md` (0/189 con comando) está
   resuelto por completo.
4. **Los descartes están argumentados y son honestos.** `ollama` nombra `llama.cpp` con sus estrellas
   y lo llama «el estándar de facto» antes de descartarlo; `casdoor` explica por qué gana a Keycloak
   *y* a Authentik; `streamlit` y `rill` descartan Metabase y Superset diciendo exactamente por qué.
   Discrepo del criterio (C-10) pero no de la honestidad: nada está escondido.
5. **Los apartados de límites valen lo que la spec prometía.** `osv-scanner` avisa del falso verde sin
   lockfile; `bloodhound` avisa de que una ausencia de camino no es prueba; `mermaid` admite que su
   colocación automática es «la peor de las tres». Eso es una ficha útil, no un anuncio.
6. **`ciberseguridad`, `ingenieria-datos`, `embebidos`, `refactorizacion` y `moviles` están bien
   construidos.** Fuera del hueco de `nmap`, la selección ofensiva/defensiva/forense es la que
   elegiría un profesional. `duckdb`+`polars`+`qsv` / `pandera`+`sqlfluff`+`elementary` /
   `dagster`+`dbt`+`dlt` es exactamente el reparto correcto del oficio.
7. **`usa:` no tiene un solo destino inexistente** en 22 sistemas, 247 pueblos y 28 aguas.
8. **Los pueblos propios no son prosa.** Los 38 sin GitHub dicen literalmente «herramienta propia, no
   de GitHub», traen su guion dentro del directorio y su comando se copia y pega. Cumplen el criterio
   1. Mi objeción a `agentes-ia` (C-01) es de **encaje con el oficio**, no de calidad ni de honestidad.
9. **El medidor y el estado no mienten.** `cosmos medir` y `cosmos estado` corren sin red y sus cifras
   cuadran con mi conteo independiente (247 pueblos, 22 oficios, mayor 27 / menor 7).

## Equilibrio hoy, medido

`registro` habla de haber llevado los oficios «de 26/4 a 26/7». Hoy, medido:

```bash
python3 -m cosmos estado   # (mayor 27, menor 7)
```

**27 / 7.** El reparto está más plano que antes, pero los tres extremos merecen decisión, y no son
los que parecen:

- **Famélicos**: `juegos` (7), `cientifico` (7), `visibilidad` (7). Los tres tienen margen de
  presupuesto gratis y huecos concretos ya identificados (C-15, C-08, y `jax` en científico).
- **Hinchados por acumulación**: `trading` (22, con 7 cosas que hacen backtest y 6 bibliotecas que no
  son de trading) y `agentes-ia` (21, de los que 15 son el taller de una persona). Estos dos no
  necesitan crecer: necesitan repartir.
- **Grande y justificado**: `ciberseguridad` (27). Es el nicho que UNIVERSO.md declaró explícitamente
  como el más amplio, y aun así le faltan piezas de primera línea (C-04) que sí caben en el
  presupuesto.

---

## Resumen numérico

| | |
|---|---|
| Pueblos auditados | 247 / 247 |
| Repositorios verificados en vivo | 209 / 209 (existencia, renombrado, último commit, archivado) |
| Archivados | 0 |
| Enlaces no canónicos | 1 (`chonkie`) |
| Duplicados (regla dura) | 0 |
| `usa:` rotos | 0 |
| Hallazgos | 17 (5 ALTO, 1 MEDIO-ALTO, 5 MEDIO, 6 BAJO) |
| Herramientas a retirar o degradar | 17 (3 firmes, 6 dudosas, 8 a vigilar) + 2 a corregir |
| Herramientas a añadir | 24 en prioridad 1 y 2, más 30 en prioridad 3 |
| Candidatas descartadas por muertas antes de recomendarlas | 6 |
| Oficios contratables que faltan | 3 (`localizacion`, `entregabilidad`, `aprendizaje-automatico`) |
| Provincias que no pasan la prueba del oficio | 2 (`agentes-ia/coste`, `automatizacion/gestion`) |
