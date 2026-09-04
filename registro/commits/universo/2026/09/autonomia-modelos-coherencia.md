---
cosmos: lluvia
nombre: autonomia-modelos-coherencia
moja: []
resumen: Libre por oceano y cumplido por el alta de maquina; todos los modelos en el selector; 38 incoherencias cerradas.
---

# Autonomía, modelos y coherencia — la tanda del 2026-09-04

Fecha: 2026-09-04 · Árbol: `galaxia/` · Config: `cosmos.toml` · Pin de partida: `892f669` (el merge de la
auditoría 360). Informes de la tanda en `progress/mejoras-2026-09-04/`: `A-autonomia.md`,
`B-coherencia.md`, `G-arbol.md`.

Encargo de Darío, literal: *«que en otros PC aprenda a hacer las cosas automáticamente como aquí y
que no pidan permiso, eso que esté en una guía de COSMOS de cuando se abra; y no solo eso, muchas
más cosas, como `claude-modelos` —a lo mejor está muy crudo pero impleméntalo súper ordenado sin
romper coherencia con nada, y eso lo tienes que revisar en todo el harness»*.

Método: dos Opus en paralelo con ángulos disjuntos (A: autonomía en máquina nueva e integración de
`claude-modelos`; B: coherencia adversarial de todo el repositorio), un tercero sobre el árbol
(oficios nuevos y hallazgos de catálogo), y la implementación en la ventana principal. Cada agente
escribió a fichero y devolvió una línea.

## 1. La carta de autonomía es un océano, no un README

`galaxia/agua/oceano-irreversible.md` pasa a `oceano-autonomia.md`: la misma política por sus dos
caras («se ejecuta sin pedir permiso» y «solo lo irreversible espera un sí»). No es un océano nuevo
porque el techo que muerde no es E12 (5 de 7) sino E16: quedaban 106 tokens y un océano con contenido
cuesta ~110. Medido con el medidor del repositorio, no a ojo:

| | Peor con agua | Margen |
|---|---:|---:|
| Partida (`892f669`) | 3.701 | 106 |
| Con el océano fusionado (143 tok) | 3.743 | 62 |
| Con los 3 oficios nuevos + B-31 | 3.797 | **5** |
| Océano recortado a 108 tok | 3.772 | **31** |

La lección, que B §7.2 había estimado mal: **un oficio nuevo no cuesta cero en E16**. Su línea entra
en el índice de galaxia, y el índice entra en todos los nichos. Tres oficios se comieron 52 tokens.
El catálogo está a una herramienta de lleno; las salidas (subir `presupuesto.entrada`, podar
`ciberseguridad`, adelgazar los mares) son decisión de producto y quedan en `PROGRESS.md`.

E17 contra los 36 co-cargables: 0,0000. `spec/UNIVERSO.md` no se tocó por la carta (no es oficio ni
mar). La carta viaja gratis a repos ajenos porque `proyectar` ya emite todos los océanos.

## 2. Que la máquina cumpla la carta es alta, no enganche

Hecho verificado en Claude Code 2.1.260 (doc oficial y binario): `permissions.defaultMode` en `auto`
o `bypassPermissions` **se ignora en silencio desde el `.claude/settings.json` de un repositorio**
desde 2.1.257; solo vale en ajustes de usuario. Un `enganchar --libre` habría sido un verde que
miente. Por eso:

- `cosmos configurar --autonomia auto|libre|manual` escribe en el `settings.json` de USUARIO
  (`CLAUDE_CONFIG_DIR` o `~/.claude`), guarda los bytes del fichero anterior en
  `~/.cosmos/autonomia.json` y deshace byte a byte; una clave que alguien cambió a mano después no se
  toca y se dice. `libre` escribe además `skipDangerousModePermissionPrompt` (clave no documentada:
  la aceptación del diálogo de responsabilidad, sin la cual una máquina nueva se para).
- El evento `SessionStart` **no trae `permission_mode`** (medido: `cwd`, `hook_event_name`,
  `session_id`, `source`, `transcript_path`). G01 lee los ajustes de usuario y es trivalente: avisa
  en rojo con manual, calla con `auto`/`bypassPermissions`, dice `desconocido` sin fichero legible.
- `cosmos estado --maquina`: inventario trivalente (python3, git, claude, tmux, llavero, perfil,
  credenciales, autonomía, modelos, lanzador). `cosmos instalar` encadena todo el alta.
- El alta interactiva pregunta por la autonomía y por el vigilante de modelos; con `--oficios` no
  toca ningún ajuste de usuario sin bandera explícita.

## 3. `claude-modelos`, reescrito genérico en `puente/modelos.py`

Se conserva la forma (reponer `additionalModelOptionsCache` de forma idempotente y atómica; agente de
launchd con `RunAtLoad` + `WatchPaths` + cada 300 s; hook de arranque de sesión con tres segundos de
espera; atajos `maxcode`/`ultracode`). Se tira lo que era de una máquina o una organización: la
etiqueta, la ruta de las cuentas, el preflight de cuota que leía un fichero de otro repositorio (un
aviso que nunca dispararía). Los configs vigilados salen de `$HOME`, `$CLAUDE_CONFIG_DIR` y la tabla
`[modelos]` del perfil, que `perfil_toml` ahora conserva al reescribir. No es un pueblo: el
2026-09-03 se retiraron del catálogo `lanzadores-de-modelo` y `quota-oficial` por orden literal, y
volverlos a meter sería deshacerla por la puerta de atrás.

Lista de modelos verificada contra el CLI el mismo día (`claude --model <id> -p ok`): Fable 5.1,
Opus 5, Sonnet 5, Haiku 4.5 y las tres variantes `[1m]`. Que la cuenta acepte cada id no se puede
comprobar sin red y `--modelos estado` lo publica como `no_comprobado`. La segunda pasada de
`maxcode -p` queda **apagada** por defecto (`COSMOS_VERIFICA=1`): duplicaba el gasto en silencio.

## 4. Coherencia: 38 hallazgos, y los dos críticos eran verdes que mentían

- **B-01**: la suite del núcleo estaba **roja en `main`** desde el merge de ayer: un test afirmaba
  «cero resúmenes cambiados desde el sello» y el merge había cambiado 37. Ahora afirma lo que mide.
- **B-02/B-03**: `mutaciones` daba 76/79 porque copiaba el repo sin `.git` y tres pruebas del juez se
  saltaban (un test saltado devuelve 0). La copia lleva `.git` y el CI ejecuta las mutaciones.
- Specs: `GOAL.md` declaraba un nivel `Universo` que el código no tiene; `FRONTMATTER.md` se
  contradecía sobre `moja`; `MEDIDOR.md` llamaba «Árbol» al universo y su bloque de ejemplo no se
  reproducía (siete cifras caducadas: ahora lo compara un canario); `GUARDARRAILES.md` hablaba de
  tres enganches con cuatro instalados (el pre-push no estaba en ninguna parte); `VALIDADOR.md`
  enseñaba un `cosmos.toml` que no es el que se usa.
- CLI: `--version`; los códigos de la válvula compuestos desde la fuente (la ayuda omitía P01/P02);
  el ejemplo de `abrir --help` fallaba y el error no sugería nada; `proyectar --help` con nombre y
  ayudas; la cifra a mano de `mapa` fuera; `pyproject.toml` (`pip install -e .` deja `cosmos` en el
  PATH); CI en matriz Linux × macOS × Python 3.11/3.13; `dependabot.yml`.
- **E07 exige ASCII en el resumen**: 453 de 454 ya lo cumplían y ninguna norma lo decía. Un resumen
  se paga en cada sesión y cada acento cuesta una pieza más al tokenizador. Test y mutación.
- **E20 tenía cero pruebas** que la vieran en rojo. Ahora dos, y una mutación.
- `secretos --historia`: recorre `git rev-list --objects --all` (32 s sobre este repo). Confirma que
  la purga pendiente sigue pendiente: 90 hallazgos vivos en la historia publicada.
- Árbol (`G-arbol.md`): tres oficios nuevos verificados por API y `HEAD.atom` (`localizacion`,
  `entregabilidad`, `aprendizaje-automatico`, 9 pueblos); `agentes-ia/instrumentacion` para las
  herramientas con las que se opera al propio agente (B-25); once deícticos «esta casa / este arnés /
  este Mac» sustituidos por el hecho; `butler`, `reprozip`, `mar-resistencia`, `TOPE_SESIONES`.
  `scancode-toolkit` ya existía. `mlflow` no se movió (razonado en su §1.5). `dvc` se comprobó y su
  URL es correcta: el repositorio sí se movió de organización (`iterative/dvc` responde 301).
- Documentos históricos con cartel: `PLAN-MAESTRO.md` y `research/README.md`. `CIERRE.md` y
  `PENDIENTE-DARIO.md` corregidos donde decían algo distinto de lo que había.

## 5. Lo que queda, y de quién es

- **Purga de historia** (F-02 CIF de un tercero, F-05 volcado con correo e IP): autorizada, no
  ejecutada aquí porque reescribe la historia publicada y necesita una sesión sola sobre el clon.
  Receta en `PENDIENTE-DARIO.md` §1; `secretos --historia` es la comprobación de después.
- **Holdout v2 ciego**: la única cifra desconocida del proyecto. No la puede escribir nadie que haya
  visto `galaxia/`.
- **El presupuesto**: 31 tokens de margen. Decidir entre subir `entrada`, podar `ciberseguridad` o
  adelgazar los mares antes de meter la siguiente herramienta en el peor nicho.
- `revision-cruzada` sigue dependiendo de un servicio con cuenta (B-26, «a vigilar»).
