# Ciclo 2 — agente GA (galaxia/pueblos, galaxia/paises)

Pin de estado (árbol compartido con otros agentes en paralelo, muta mientras trabajo — por eso cito
por símbolo/nombre de pueblo, no por línea):
`git rev-parse HEAD` = `b0c1ebdeb2d9bac7e068d10714213ff2f9eda926` · `git status --porcelain | wc -l` = 332
(la mayoría de esas líneas son de OTROS agentes trabajando a la vez en `cosmos/`, `spec/`, `tests/`,
`cosecha/` y en fichas `origen: propio` — no las toqué). Rama `arreglos-2026-09-03`. Sin commit, sin
push, sin cambio de rama.

Boundary respetado: solo edité dentro de `galaxia/pueblos/*/SKILL.md` y `galaxia/paises/`. No toqué
`cosmos/`, `spec/`, `tests/`, `puente/`, `README.md`, `GOAL.md`, ni ninguna ficha `origen: propio`
(comprobado con `grep -n "origen: propio"` antes de tocar `consola-interactiva-tmux`, que solo leí).

---

## 1. R-15 — `brew install <x>` roto o incompleto (clase completa)

**vector** (el caso citado): `brew info --json=v2 vector` → vacío; `brew info vector` en plano →
`Error: No available formula with the name "vector". Did you mean pgvector or veccore?`. Confirmado
el tap real: `curl -s https://api.github.com/repos/vectordotdev/homebrew-brew` → `archived: false`,
`contents/Formula` → `vector.rb`. **Fix**: `brew tap vectordotdev/brew && brew install vector`.

**Método de la clase**: descargué la base completa de Homebrew (`formulae.brew.sh/api/formula.json`,
8.586 fórmulas; `cask.json`, 7.716 casks — evita 90+ llamadas de red individuales) y crucé contra
cada paquete de cada línea `brew install` de la galaxia. 93 fichas mencionan `brew install` en algún
sitio (88 como comando principal, con 104 paquetes extraídos entre formulas/casks/multi-paquete);
otras 5 lo mencionan solo como alternativa en comentario.

Resultado:
- **NO EXISTEN, corregidas (4)**: `vector` (tap, arriba) · `bearer` (`brew tap bearer/tap` +
  `brew install bearer` → colapsado a `brew install bearer/tap/bearer`, tap verificado en
  `Bearer/homebrew-tap`) · `squawk` (`brew install squawk` no existe ni como fórmula ni como tap
  propio — comprobado `curl -sI https://github.com/sbdchd/homebrew-squawk` → `404`; su propio
  README solo documenta npm/pip/cargo/releases → cambiado a `npm install -g squawk-cli`) ·
  `butler` (ver punto 2).
- **Ya funcionan aunque no exista fórmula "pelada" (verificado, sin tocar, 3)**: `codeql`,
  `osquery`, `quarto` — `brew install --dry-run <x>` confirma que Homebrew resuelve solo al cask
  (`==> Would install 1 cask`) y ese cask deja el binario correcto en el `PATH`
  (`codeql.rb` artifact `binary: .../codeql/codeql`; `osquery`/`quarto` son `.pkg` que instalan su
  CLI). No hacía falta `--cask` explícito.
- **Taps de terceros verificados vivos (2)**: `openfga/tap/fga` (repo `openfga/homebrew-tap`,
  `Formula/fga.rb` existe) · `probe-rs/probe-rs/probe-rs` (repo `probe-rs/homebrew-probe-rs`,
  `Formula/probe-rs.rb` existe).
- **Ya documentada correctamente la ausencia (1, no tocar)**: `libresprite` — la propia ficha ya dice
  «No hay fórmula ni cask en Homebrew... `brew install --cask libresprite` responde Error» y da la
  descarga real del `.dmg`. Ejemplar, sin cambios.
- **Resto (83 restantes de las 88 con comando principal, más `agent-browser`/`ruff`/`maestro`/`rill`
  como alternativa en comentario)**: todas existen en la base y apuntan al proyecto correcto
  (verificado por `homepage` de cada entrada — p.ej. `httpx` → `projectdiscovery/httpx`, `katana` →
  `projectdiscovery/katana`, `loki` → `grafana.com/oss/loki`, `just` → `just.systems`).

Ficheros tocados: `galaxia/pueblos/vector/SKILL.md`, `galaxia/pueblos/bearer/SKILL.md`,
`galaxia/pueblos/squawk/SKILL.md`.

## 2. R-16 — `butler`

`brew info --json=v2` del cask `itch`: artifacts = `{"app": ["itch.app"]}` — solo instala la app de
escritorio, sin `binary` que exponga `butler` en el `PATH`. `brew install butler` a secas: cask
`manytricks.com/butler` (app de organización de tareas, sin relación con itch.io) — confirmado
`homepage: https://manytricks.com/butler/`. No existe tap oficial de Homebrew para el `butler` de
itch.io. Instalación real verificada (`curl -sI` → `307` con redirect firmado a R2, es decir sirve):
`https://broth.itch.zone/butler/darwin-amd64/LATEST/archive/default` (y `darwin-arm64` para Apple
Silicon) — es la vía que la propia documentación de itch.io (`itch.io/docs/butler/installing.html`)
señala como «automation-friendly», con URL fija que no expira. Ficha corregida a esa descarga +
aviso explícito de los dos falsos amigos (`--cask itch` y `brew install butler`).

Fichero: `galaxia/pueblos/butler/SKILL.md`.

## 3. R-36 — colisión de nombre de paquete

- `httpx`: confirmado que `brew install httpx` YA instala el correcto (`brew info --json=v2 httpx` →
  `homepage: https://github.com/projectdiscovery/httpx`); la ficha ya usaba ese comando, no `pip`.
  Añadida la línea de colisión (estilo `medusajs`): `pip install httpx` es `encode/httpx`, otra
  herramienta.
- `arrow`: la ficha ya usaba `pip install pyarrow` (correcto). Añadida la línea de colisión: `pip
  install arrow` es `arrow-py` (fechas), no Apache Arrow.
- Revisados por si su comando instala un homónimo: `just` (`brew info` → `just.systems`, OK),
  `piper` (`pip install piper-tts`, nombre no ambiguo, OK), `medusa` (`go install
  github.com/crytic/medusa@latest`, ruta cualificada, sin ambigüedad — y no colisiona con el
  `medusa` de fuerza bruta de contraseñas porque no se instala por ese nombre suelto), `vector`
  (arreglado en el punto 1; el core de Homebrew no tiene ningún `vector` que pueda confundirse),
  `loki` (`brew info loki` → `grafana.com/oss/loki`, OK, no es el escáner IOC de Neo23x0), `katana`
  (`brew info katana` → `projectdiscovery/katana`, OK), `crawlee` (`npm install crawlee`, nombre no
  ambiguo, OK). Ninguno de estos seis necesitó cambio.

Ficheros tocados: `galaxia/pueblos/httpx/SKILL.md`, `galaxia/pueblos/arrow/SKILL.md`.

## 4. R-24 — aviso de `curl | bash` sin revisar (clase completa)

`grep -lE 'curl [^|]*\| *(ba)?sh' galaxia/pueblos/*/SKILL.md` → 5 fichas: `coolify`, `foundry`,
`nextflow`, `openclaw`, `rill`. De esas, `foundry` y `rill` YA llevaban el aviso (comprobado con
`grep -n "revisar" <fichero>`). Añadido el aviso (texto calcado del de `openclaw`) a las dos que
faltaban:

- `coolify`: «Y el instalador por `curl | bash` ejecuta código remoto sin revisar: para producción,
  leer el guion antes.»
- `nextflow`: mismo texto.

Ficheros tocados: `galaxia/pueblos/coolify/SKILL.md`, `galaxia/pueblos/nextflow/SKILL.md`.

## 5. R-33 — rival sin nombrar

- `nmap`: añadido `masscan`/`rustscan` (velocidad de barrido de puertos vs. profundidad de huella)
  con el patrón habitual de encadenarlos.
- `osquery`: añadido `auditd` (registro nativo del kernel, más ligero, menos alcance) y
  `wazuh`/`velociraptor` (plataformas de detección completas que usan `osquery` como motor de
  recolección). Comprobado que ninguno de los tres existe como pueblo propio en la galaxia
  (`ls galaxia/pueblos | grep -E 'masscan|rustscan|wazuh|velociraptor|auditd|tcpdump|zeek'` → vacío),
  así que se nombran en prosa con backticks, sin crear pueblo nuevo (no lo pedía el encargo).
- `wireshark`: añadido `tcpdump` (mismo `libpcap`, sin disección) y `zeek` (análisis en vivo con
  registros estructurados para SIEM).

Ficheros tocados: `galaxia/pueblos/nmap/SKILL.md`, `galaxia/pueblos/osquery/SKILL.md`,
`galaxia/pueblos/wireshark/SKILL.md`.

## 6. R-34 — SQL dentro de bloque ```bash en `osquery`

Cambiado a `osqueryi <<'SQL' ... SQL` (heredoc real, pegable en terminal) más una segunda forma con
`osqueryi --json "<query>"` para uso en guion/cron. Ya no hay SQL suelto sin intérprete en un bloque
`bash`.

Fichero: `galaxia/pueblos/osquery/SKILL.md`.

## 7. R-35 — bloque de uso con líneas comentadas / dependencia no instalada

- `grafana`: el bloque de datasource (7/7 líneas comentadas) pasó a un `cat > ... <<'EOF'` real que
  escribe el YAML de aprovisionamiento en la ruta real de Homebrew (`$(brew --prefix)/etc/grafana/...`)
  seguido de `brew services restart grafana` y una `curl` que confirma el alta. Ejecutable de
  verdad.
- `vector`: el pipeline (13/15 líneas comentadas) pasó a un `vector.yaml` real vía heredoc con fuente
  `demo_logs` (autocontenida, no necesita ficheros de log reales) y sink `console`, más
  `vector validate` + `vector --config` — se puede pegar y corre sin preparar nada externo.
- `loki`: añadido `logcli` al `brew install` (formula propia confirmada: `brew info --json=v2
  logcli` → existe) y sustituido el YAML comentado de `promtail` por un heredoc real que lo escribe
  y arranca `promtail` antes de la consulta `logcli`.

Ficheros tocados: `galaxia/pueblos/grafana/SKILL.md`, `galaxia/pueblos/vector/SKILL.md`,
`galaxia/pueblos/loki/SKILL.md`.

## 8. R-26 / C-09 — `mythril` vs `medusa` (coherencia de fecha)

`curl -s https://github.com/ConsenSysDiligence/mythril/commits/HEAD.atom | grep -m1 -oE
'<updated>[^<]+'` → `2025-01-31` (coincide exactamente con lo que ya dice `medusa/SKILL.md` sobre
`mythril`). La propia ficha de `mythril` decía «último push 2026-04-27... Cuatro meses sin
movimiento: vivo» — dato equivocado. Corregido a `último push 2025-01-31` y reescrita la frase de
vida a «más de un año y medio sin commits... no es "vivo" en el sentido de mantenimiento activo»,
más un párrafo de coherencia explícito con `medusa`. Estrellas/licencia reverificadas: `curl -s
api.github.com/repos/ConsenSysDiligence/mythril` → `4265 MIT false` (coincide, sin cambio).

Fichero: `galaxia/pueblos/mythril/SKILL.md`.

## 9. R-27 — `qdrant` + clase de las 64 fichas «comprobado 2026-09-03»

`qdrant`: atom de hoy → `2026-09-03T12:36:18Z`, no `2026-08-04`. Corregido push y estrellas
(`api.github.com/repos/qdrant/qdrant` → `34362 Apache-2.0 false`, antes 34.355).

**Clase**: extraje con un script Python (evita el corte de línea que un `grep` de una sola línea se
come — así se me apareció `qdrant` original, con la fecha partida en dos líneas) todas las fichas
cuyo bloque de cabecera contiene `comprobado 2026-09-03`: **64 pueblos** (no 59; el número subió por
el trabajo de ciclo 1). Comprobé el `.atom` de las 64 en paralelo (12 hilos) contra la fecha
declarada. 6 discrepancias, de las cuales 2 eran falsos positivos de mi propio regex (`claude-seo-ai`
ya declara bien su fecha real en el cuerpo; `consola-interactiva-tmux` es `origen: propio`, fuera de
mi boundary, no tocado) y 4 reales, corregidas:

| pueblo | declarado | real (`.atom` hoy) |
|---|---|---|
| astro | 2026-09-02 | 2026-09-03 |
| codeql | 2026-09-02 | 2026-09-03 |
| loki | 2026-09-02 | 2026-09-03 |
| auditor-de-skills | 2026-08-30 | 2026-08-26 (`pushed_at` de la API cuenta cualquier rama; el HEAD del repo es del 26) |

Ficheros tocados: `galaxia/pueblos/qdrant/SKILL.md`, `galaxia/pueblos/astro/SKILL.md`,
`galaxia/pueblos/codeql/SKILL.md`, `galaxia/pueblos/loki/SKILL.md` (ya tocado en el punto 7),
`galaxia/pueblos/auditor-de-skills/SKILL.md`.

## 10. C-05 — perfilador de memoria de Node

`clinicjs/node-clinic`: atom → `<updated>2024-09-19...` (`pushed_at` API confirma lo mismo) — más de
dos años parado. La alternativa que sugería el encargo, `davidmarkclements/0x`, TAMBIÉN está fría:
atom → `2025-07-07` (npm `registry.npmjs.org/0x` confirma la misma fecha de publicación), más de un
año. Busqué una tercera opción y verifiqué `facebook/memlab`: atom → `2026-09-02` (ayer), `5.033★`,
MIT, no archivado — la única de las tres realmente viva. Creado el pueblo nuevo con el formato del
brief, ejemplo autocontenido (fuga de juguete → `.heapsnapshot` → `memlab view-heap`) y un segundo
ejemplo de assertion de memoria en test (`takeNodeMinimalHeap`), más frontera explícita con `memray`
(Python vs. Node/JS/browser).

Fichero nuevo: `galaxia/pueblos/memlab/SKILL.md` (padre `rendimiento/perfilado`, existente y
verificado con `cosmos validar`).

## 11. C-08 — `bing-webmaster` / `search-console`

No tocados. Son del otro agente (ver `git status`: ambos aparecen modificados por otro proceso
durante esta sesión).

## 12. C-15 — provincia `juegos/distribucion`

`PADRES.txt` (de ciclo 1) confirma `sistema-solar juegos` como único padre válido para un país nuevo
del sistema. Creado `galaxia/paises/juegos--distribucion.md` con el mismo formato que
`juegos--activos.md`/`juegos--motores.md`. Movido `butler` a `padre: juegos/distribucion`, corregido
su `resumen` (decía «no hay país propio de distribución, entra aquí», que ya no es cierto) y su nota
de padre.

Ficheros: `galaxia/paises/juegos--distribucion.md` (nuevo), `galaxia/pueblos/butler/SKILL.md`.

## 13. Verificación final

```
$ python3 -m cosmos compilar
COSMOS  compilar  verde (1 salto activo: P01, caduca en 7 d)
Creadas 1; actualizadas 0; iguales 305; adoptadas 0; ajenas respetadas 0; obsoletas eliminadas 0; obsoletas preservadas 0.

$ python3 -m cosmos validar
COSMOS  verde (1 salto activo: P01, caduca en 7 d)  0 errores

$ python3 -m cosmos medir
COSMOS  medir
  Entrada base .... 1.220 tokens
  Peor nicho ...... 2.470 tokens   (ciberseguridad, 35 pueblos)
  Agua condicional  1.231 tokens   (6 aguas por paths:, fuera de la entrada)
  Peor con agua ... 3.701 tokens   (el peor caso + agua condicional)
  Universo ........ 172.956 tokens
  Descarga ........ 98,6 %
  Presupuesto ..... 4.000     OK, quedan 106 tokens con el margen calibrado (+5,2 %) en el peor caso con agua (ciberseguridad); ≈ 3 herramienta(s) más en ese nicho
  Vista compilada . 8.818 tokens   (306 entradas)
```

Verde, sin necesidad de retirar nada (`memlab` cayó en `rendimiento/perfilado`, no en el nicho más
caro — `ciberseguridad` — así que no movió el peor caso).

El salto activo `P01` es preexistente, no lo abrí ni lo toqué en esta tarea.

## Ficheros tocados (resumen)

Editados: `galaxia/pueblos/{vector,butler,bearer,squawk,httpx,arrow,coolify,nextflow,nmap,osquery,
wireshark,grafana,loki,mythril,qdrant,astro,codeql,auditor-de-skills}/SKILL.md`.

Nuevos: `galaxia/paises/juegos--distribucion.md`, `galaxia/pueblos/memlab/SKILL.md`.

No tocados a propósito: `consola-interactiva-tmux` (origen: propio), `bing-webmaster`,
`search-console` (de otro agente), `cosmos/`, `spec/`, `tests/`, `puente/`, `README.md`, `GOAL.md`.
