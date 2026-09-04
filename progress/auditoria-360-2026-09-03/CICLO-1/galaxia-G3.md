# Galaxia G3 — auditoría 360, ciclo 1 (completado por el fixer tras el corte del subagente)

El subagente G3 se cortó a media tarea: dejó los 21 pueblos nuevos y las correcciones de `chonkie`
y `consola-interactiva-tmux`, y su log de verificación en vivo (`g3-verif/verif1.txt`). El resto de
la tarea B (F-03, F-08, F-10, M-5, C-16, C-06, aviso openclaw, C-07) lo cerró el fixer directamente.

## Tarea A — 21 pueblos nuevos (verificados vivos, `g3-verif/verif1.txt`, 2026-09-03)

`medusa` (crytic, blockchain/auditoria, releva a mythril) · `syft` (anchore, cumplimiento/licencias) ·
`scancode` (aboutcode-org, cumplimiento/licencias) · `pa11y` (cumplimiento/web-legal) ·
`yt-dlp` (audiovisual/video; la galaxia ya lo usaba sin catalogar) · `piper` (OHF-Voice, audiovisual/voz) ·
`f5-tts` (SWivid, audiovisual/voz) · `blender` (juegos/activos) · `butler` (itchio, juegos/motores) ·
`love2d` (juegos/motores) · `crawlee` (apify, extraccion/fuentes-web) · `firecrawl` (extraccion/fuentes-web) ·
`sqlmesh` (SQLMesh, ingenieria-datos/orquestacion, rival de dbt) · `arrow` (apache, ingenieria-datos/motor) ·
`nextflow` (cientifico/reproducible) · `jax` (jax-ml, cientifico/computo) · `just` (casey, automatizacion/flujos) ·
`pre-commit` (automatizacion/flujos) · `keycloak` (saas/identidad) · `sitespeed` (visibilidad/medicion) ·
`katana` (projectdiscovery, visibilidad/auditoria). Cero repetidos, cero archivados, ninguna con
push anterior a 2026-03-01.

## Tarea B — correcciones (cerradas por el fixer)

- **C-12** `chonkie`: URL canónica `feyninc/chonkie` (301 desde chonkie-inc). Hecho por G3.
- **C-14 / F-03** `auditor-de-skills`: atribución correcta (origen `alirezarezvani/claude-skills`,
  autor, licencia MIT leída en el LICENSE, comprobado 2026-09-03) — «de un arnés propio» era falso.
- **F-03** `consola-interactiva-tmux`: atribución del `tmux-wrapper.sh` (Jesse Vincent / `obra`,
  MIT). Hecho por G3. Ambas atribuciones también en `NOTICE`.
- **F-10** `foundry` y `rill`: aviso `curl | bash` como el de `openclaw`; en `rill`, `brew` preferible.
- **F-08** `openclaw`: `scripts/telegram-bridge.py` (y su gemelo `cosecha/`) reescrito — prompt como
  argumento de lista sin `shell=True` (el `%_VANGUARDIA_PROMPT%` de CMD nunca expandía en POSIX),
  `--dangerously-skip-permissions` solo con `OPENCLAW_SIN_PERMISOS=1`, `export` en el mensaje de
  error; la ficha advierte del salto de permisos. `py_compile` verde.
- **M-5** `aflplusplus`: frase de alcance autorizado.
- **C-16** `usa:`: añadidos juegos→moviles, audiovisual→modelos-locales, analitica→web,
  embebidos→ciberseguridad, refactorizacion→agentes-ia (E20 verde).
- **C-06** `mar-pruebas` nombra `hypothesis`; `mar-resistencia` nombra `tenacity`, `toxiproxy`,
  `time-machine` (E17 verde tras reescribir para no solapar).
- **C-07** `claude-seo-ai`: aviso reforzado con la evidencia exacta (5 commits, todos el 2026-06-01
  entre 19:18 y 19:22, nada después). La retirada es decisión de Darío (PENDIENTE-DARIO §5).

## Verificación

`python3 -m cosmos validar` → verde 0 errores. `python3 -m cosmos medir` → peor nicho ciberseguridad
2.484 tok, peor con agua con margen OK, quedan 91 tokens. 306 pueblos (247 + 59 de G1/G2/G3).
