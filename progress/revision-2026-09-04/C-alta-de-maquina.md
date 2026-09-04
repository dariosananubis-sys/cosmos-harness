# Revisión C — alta de máquina y CLI (2026-09-04)

Informe de un revisor adversarial de solo lectura sobre `cosmos/configurar.py`, `cosmos/cli.py`, `cosmos/guardarrailes.py`, `puente/proyectar.py` y `puente/modelos.py`. 22 hallazgos reproducidos con comando y salida sobre un HOME falso. **Los 22 arreglados el mismo día**: tests en `tests/test_revision_c.py` y `puente/tests/test_proyectar.py`, mutaciones M89–M111 en `puente/tests/mutaciones.py`. Los dos plausibles (carrera del reponedor, secreto por argv en `--llavero`) quedan abiertos.

El repo real sigue intacto (solo el `settings.local.json` que ya estaba sin versionar) y el HOME real no se ha tocado; todo corrió con `HOME=…/scratchpad/revC/home*`, un clon del repo en `revC/clon` (sin `.git` original ni `pruebas/encargos-validacion.json`), un repo ajeno de juguete en `revC/ajeno` y un `launchctl` falso en `revC/fakebin` para las pruebas del vigilante.

# Informe de revisión C — alta de máquina y CLI

Abreviaturas: `SCR=/private/tmp/claude-501/-Users-juansantino/6fa7e5a0-7bc7-47f0-bd61-6a942adcf553/scratchpad/revC`; todos los comandos se lanzan desde `$SCR/clon` con `unset CLAUDE_CONFIG_DIR`.

## 1. `--autonomia manual` pierde el `defaultMode` que el usuario ya tenía (GRAVE)
`cosmos/configurar.py:419-438` (`retirar_claves`). Si el usuario tenía `permissions.defaultMode = "acceptEdits"` (o `plan`), `--autonomia auto` lo cambia y lo apunta como «cambiado desde acceptEdits»; al deshacer, `podado` (sin nuestra clave) nunca coincide con `previo` (que conserva `acceptEdits`), así que no se restaura el original: se escribe `podado`, que ya no lleva `permissions`, y el mensaje culpa a «alguien» que lo cambió.
```
printf '{"permissions": {"defaultMode": "acceptEdits"}, "model": "opus"}\n' > $SCR/homeD1/.claude/settings.json
HOME=$SCR/homeD1 python3 -m cosmos configurar --autonomia auto      # (cambiado desde "acceptEdits")
HOME=$SCR/homeD1 python3 -m cosmos configurar --autonomia manual
#  ~/.claude/settings.json: sin las claves de COSMOS (el resto lo había cambiado alguien, se conserva)
cat $SCR/homeD1/.claude/settings.json   ->  { "model": "opus" }
```
Corrección: cuando el valor actual es el nuestro y el respaldo trae un valor previo distinto para esa clave, reponer el valor previo (no borrar la clave); comparar `podado` contra `original` con nuestra clave sustituida por la previa, no podada.

## 2. `enganchar --sesion` dos veces pisa el respaldo; `desenganchar` dice «byte a byte» y deja los hooks (GRAVE)
`cosmos/guardarrailes.py:494` y `:515`: cada enganche guarda como «original» el fichero *actual* (que ya lleva los hooks de COSMOS), a diferencia de `configurar.fijar_claves`, que conserva el primer respaldo. Al desenganchar, `podar(original) == podado` → «restaurado» → se reescribe el original con los cinco hooks dentro.
```
printf '{"model": "x"}\n' > $SCR/repoA/.claude/settings.json   # repo git de juguete
HOME=$SCR/home python3 -m cosmos enganchar --sesion --config $SCR/repoA/cosmos.toml
HOME=$SCR/home python3 -m cosmos enganchar --sesion --config $SCR/repoA/cosmos.toml
HOME=$SCR/home python3 -m cosmos desenganchar --config $SCR/repoA/cosmos.toml
#  Cableado de sesión: … devuelto byte a byte al estado anterior
grep -c puente.sesion $SCR/repoA/.claude/settings.json   ->  5
```
Corrección: si ya hay respaldo con `existia`/`original`, conservarlo (como hace `fijar_claves` en `configurar.py:372-376`).

## 3. `proyectar sincronizar` reescribe ajustes del repositorio ajeno y `comprobar` los impone (GRAVE)
`puente/proyectar.py:39-46` y `:572`. El README promete «sin pisar nada suyo» y solo documenta el bloque y las skills; en realidad escribe `.claude/settings.json` con `autoMemoryEnabled=false`, `includeGitInstructions=false`, `attribution` vacía, notificaciones apagadas… **pisando** los valores que el anfitrión tenía, y `comprobar` da rojo si el dueño los vuelve a poner.
```
printf '{ "autoMemoryEnabled": true, "includeGitInstructions": true, "attribution": {"commit": "Firmado por mi"}, "model": "opus" }' > $SCR/ajeno/.claude/settings.json
HOME=$SCR/home python3 -m cosmos proyectar iniciar $SCR/ajeno --nicho agentes-ia
HOME=$SCR/home python3 -m cosmos proyectar sincronizar $SCR/ajeno
cat $SCR/ajeno/.claude/settings.json  ->  autoMemoryEnabled: false, includeGitInstructions: false, attribution.commit: "" …
# el dueño restaura autoMemoryEnabled=true:
HOME=$SCR/home python3 -m cosmos proyectar comprobar $SCR/ajeno  ->  ERROR: desactualizado .claude/settings.json
```
Corrección: no escribir ajustes del anfitrión desde `proyectar` (o solo añadir claves ausentes, nunca sustituir las presentes) y documentarlo en README/`--help`.

## 4. `--modelos quitar --seco` quita de verdad y descarga el agente (GRAVE)
`cosmos/cli.py:583`: `mod.quitar()` no recibe `seco`; la ayuda dice «con --llavero, --autonomia o --modelos: enseña lo que haría sin escribir nada».
```
PATH=$SCR/fakebin:$PATH HOME=$SCR/homeD2 python3 -m cosmos configurar --modelos instalar >/dev/null
PATH=$SCR/fakebin:$PATH HOME=$SCR/homeD2 python3 -m cosmos configurar --modelos quitar --seco
#  Agente launchd .... descargado y …/Library/LaunchAgents/com.cosmos.modelos.plist borrado
ls $SCR/homeD2/.cosmos/bin $SCR/homeD2/Library/LaunchAgents  -> vacíos ;  launchctl.log: "launchctl bootout gui/501/com.cosmos.modelos"
```
Corrección: pasar `seco` a `quitar()` y limitarse a listar lo que borraría.

## 5. `--autonomia manual --seco` deshace de verdad
`cosmos/cli.py:534`: la rama `manual` no mira `seco`.
```
HOME=$SCR/homeD3 python3 -m cosmos configurar --autonomia auto >/dev/null
HOME=$SCR/homeD3 python3 -m cosmos configurar --autonomia manual --seco
#  ~/.claude/settings.json: eliminado: no existía antes de fijar la autonomía
ls $SCR/homeD3/.claude/settings.json  ->  No such file or directory
```
Corrección: en `manual` con `--seco`, calcular el estado (`retirar_claves` en modo lectura) e imprimirlo sin escribir.

## 6. `instalar` interactivo ignora `--autonomia libre` y `--modelos` (el ejemplo del README)
`cosmos/cli.py:654-656`: sin `--oficios`, el alta pregunta y los flags de máquina se descartan; el ejemplo de portada `instalar --autonomia auto --modelos --lanzador` en realidad pregunta y con Enter/`n` no hace lo pedido.
```
printf '1\n\n\nn\n' | HOME=$SCR/home14 python3 -m cosmos instalar --autonomia libre --modelos --no-abrir
#  … [Enter = auto]:  COSMOS configurar autonomia auto
#  autonomia .......... auto   /   modelos ............ falta   vigilante no instalado
```
Corrección: si el flag viene dado, no preguntar por esa cara (o usar el flag como valor por defecto del prompt).

## 7. `configurar --lanzador --seco` escribe el shim
`cosmos/cli.py:607` → `configurar.py:538`: `_lanzador` no recibe `seco`.
```
HOME=$SCR/home7 python3 -m cosmos configurar --lanzador --seco   ->  COSMOS  configurar  lanzador  creado
ls -la $SCR/home7/.local/bin/   ->  -rwxr-xr-x … cosmos
```
Corrección: aceptar `seco` en `_lanzador` (como hace `instalar --seco --lanzador`).

## 8. `configurar --oficios … --seco` y `--comprobar --seco` escriben perfil y credenciales
`cosmos/cli.py:441` y `:484`: `args.seco` solo se consulta en llavero/autonomía/modelos.
```
HOME=$SCR/home8 python3 -m cosmos configurar --oficios agentes-ia --herramientas revision-cruzada --seco --no-abrir
find $SCR/home8 -type f  ->  .cosmos/credenciales.txt  .cosmos/perfil.toml
stat -f %m perfil.toml; cosmos configurar --comprobar --seco; stat -f %m perfil.toml  -> mtime cambia (1788532550 -> 1788532646)
```
Corrección: o `--seco` cubre todas las caras, o `configurar` rechaza `--seco` sin llavero/autonomía/modelos.

## 9. `--lanzador --forzar` sobre un symlink ajeno sobrescribe el destino del enlace
`cosmos/configurar.py:534-538`: `write_text` sigue el symlink.
```
ln -s $SCR/home17/herramienta-real $SCR/home17/.local/bin/cosmos
HOME=$SCR/home17 python3 -m cosmos configurar --lanzador --forzar   ->  actualizado
head -2 $SCR/home17/herramienta-real  ->  "#!/usr/bin/env bash / # generado-por-cosmos-configurar…"   (el enlace sigue siendo enlace)
```
Corrección: si `ruta.is_symlink()`, `unlink` antes de escribir (o negarse como hace `escribir_privado`).

## 10. `estado --maquina` dice `modelos ok` con un intérprete que no existe
`puente/modelos.py:608-616`: «agente launchd ok» solo mira que `launchctl print` devuelva 0 y «hook ok» solo busca la marca; nadie comprueba que el intérprete/reponedor del plist y del hook existan. Un venv temporal (como `/tmp/calib`) borrado deja un agente que falla cada 5 min en verde.
```
HOME=$SCR/home12 python3 - <<'PY'   # instalar con interprete="/tmp/calib/bin/python3-que-no-existe", ejecutor falso, plataforma darwin
… mod.estado(...)  ->  reponedor ok / agente launchd ok / hook SessionStart ok ; plist: <string>/tmp/calib/bin/python3-que-no-existe</string>
PY
```
Corrección: en `estado`, leer el plist y el comando del hook y marcar `falta` si el intérprete o el reponedor no existen (y `desactualizado` si el plist no coincide con el generado hoy).

## 11. `estado --maquina` dice `credenciales ok` con el fichero en 644 y `~/.cosmos` en 755
`cosmos/estado.py:267`. El README promete «directorio 700, ficheros 600» y el inventario no lo comprueba.
```
chmod 644 $SCR/home8/.cosmos/credenciales.txt; chmod 755 $SCR/home8/.cosmos
HOME=$SCR/home8 python3 -m cosmos estado --maquina | grep credenciales  ->  credenciales ....... ok   1 de 1 rellenas
```
Corrección: comprobar `S_IMODE` de directorio y fichero; `falta` (o `inseguro`) si no son 700/600.

## 12. Hook SessionStart del vigilante roto con espacios en la ruta
`puente/modelos.py:285`: `{interprete} {reponedor}` sin comillas dentro de `bash -c "…"`. Un HOME o un Python con espacio (p. ej. `/Applications/Python 3.12/…`) no ejecuta nunca.
```
orden_hook('$SCR/dir con espacio/python3', Path('$SCR/dir con espacio/reponer.py'))  # ejecutado con bash -c
ls $SCR/marca-hook -> No such file   ;  bash: …/revC/dir: No such file or directory
```
Corrección: `shlex.quote` para intérprete y reponedor (y comillas dobles escapadas dentro del `bash -c`).

## 13. `desenganchar` sin respaldo reformatea un `settings.json` ajeno y borra claves suyas
`cosmos/guardarrailes.py:579-581`: sin respaldo (clon nuevo, `.cosmos/` no versionado) siempre cae en «podado» aunque no hubiera nada de COSMOS; además `podar_sesion` elimina listas vacías del usuario (`"hooks":{"Stop":[]}` desaparece). `puente/modelos.retirar_hook` sí devuelve «ausente» en ese caso.
```
printf '{"model":"x","hooks":{"Stop":[]},"env":{"A":"1"}}' > $SCR/repoA2/.claude/settings.json
HOME=$SCR/home python3 -m cosmos desenganchar --config $SCR/repoA2/cosmos.toml   ->  … podado
cat …/settings.json  ->  {\n  "model": "x",\n  "env": {…}\n}   (sin "hooks")
```
Corrección: si `podado == datos` (nada nuestro), devolver «ausente» sin escribir; y podar solo las entradas nuestras, no las listas vacías ajenas.

## 14. `proyectar sincronizar` convierte un `CLAUDE.md` CRLF a LF entero
`puente/proyectar.py:428`: `read_text()` normaliza saltos de línea y luego se reescribe todo el fichero.
```
printf '# Mi proyecto\r\n\r\nReglas mias.\r\n' > $SCR/ajeno/CLAUDE.md ; … sincronizar
tr -cd '\r' < $SCR/ajeno/CLAUDE.md | wc -c   ->  0   (antes 3);  git diff --stat: CLAUDE.md | 109 ++++---
```
Corrección: leer con `newline=""` (o bytes) y fusionar respetando el final de línea del anfitrión.

## 15. `proyectar sincronizar` mueve el bloque al final y desplaza lo que el dueño escribió después
`puente/proyectar.py:406-410`: `fuera + nuevo` siempre pone el bloque al final, aunque estuviera arriba; el contenido posterior queda delante y se añade una línea en blanco inicial.
```
printf '\n## Mis notas al final\n' >> $SCR/ajeno/AGENTS.md ; … sincronizar
head -3 AGENTS.md -> "" / "## Mis notas al final" / "" ;  tail -1 -> <!-- cosmos:fin -->
```
Corrección: sustituir el bloque en su posición (`prefijo + nuevo + resto`).

## 16. Ayuda de `--modelos` miente sobre dónde escribe
`cosmos/cli.py:192`: «solo escribe en ~/.cosmos, ~/.local/bin y … ~/Library/LaunchAgents»; también escribe `~/.claude/settings.json` (hook) y cada `~/.claude.json` vigilado.
```
HOME=$SCR/home9 python3 -c "… mod.instalar(perfil={}, ejecutor=falso, plataforma='darwin')"
find … -newer -> ./.claude.json  ./.claude/settings.json  (settings con el hook SessionStart, .claude.json de 2 a 1004 bytes)
```
Corrección: corregir la ayuda (el README sí lo dice).

## 17. `enganchar` calla cuando hay un `pre-push` ajeno
`cosmos/guardarrailes.py:356`: el pre-commit ajeno se denuncia; el pre-push ajeno se omite en silencio y la salida es «verde» sin mencionar que el escáner de pre-push no quedó instalado.
```
printf '#!/bin/sh\necho mio\n' > $SCR/repoB/.git/hooks/pre-push
HOME=$SCR/home python3 -m cosmos enganchar --config $SCR/repoB/cosmos.toml  -> COSMOS enganchar verde (solo habla del pre-commit)
tail -1 .git/hooks/pre-push -> echo mio
```
Corrección: decirlo en la salida (y ofrecer la línea para encadenarlo), como con el pre-commit.

## 18. `{"permissions": {}}` no vuelve byte a byte y el mensaje culpa a otro
`cosmos/configurar.py:317-322` (`_quitar` poda el padre vacío) + `:425`.
```
printf '{"permissions": {}}\n' > $SCR/home18/.claude/settings.json ; --autonomia auto ; --autonomia manual
#  sin las claves de COSMOS (el resto lo había cambiado alguien, se conserva)   ->  fichero: {}
```
Corrección: recordar en el respaldo si el padre existía y no podarlo; y no imprimir «lo cambió alguien» cuando `ajenas` está vacía.

## 19. `estado --maquina` no admite `--directorio`
`cosmos/cli.py:1145`: `inventariar_maquina` sin `directorio`; tras `configurar --directorio X` el inventario dice que el perfil falta.
```
HOME=$SCR/home15 python3 -m cosmos configurar --oficios agentes-ia --herramientas revision-cruzada --directorio $SCR/home15/otro --no-abrir
HOME=$SCR/home15 python3 -m cosmos estado --maquina | grep perfil  ->  perfil ............. falta
```
Corrección: `--directorio` en `estado` (o leer `COSMOS_PERFIL`).

## 20. Una skill enlazada (symlink) en `.claude/skills` del repo ajeno aborta `proyectar` entero
`puente/proyectar.py:319`. Es ruidoso, no destructivo, pero un anfitrión con `.claude/skills/mia -> ../../skills/mia` no puede usar COSMOS.
```
ln -s ../../skills-propias/mia $SCR/ajeno/.claude/skills/mia ; proyectar comprobar $SCR/ajeno -> ERROR: una skill del destino no puede ser symlink (rc=1)
```
Corrección: ignorar los symlinks que no llevan nuestra marca en vez de abortar.

## 21. plist inválido si la ruta lleva `&` (espacios sí valen)
`puente/modelos.py:251` no escapa XML.
```
plutil -lint p1.plist (ruta "/Users/a b/…") -> OK ; p2.plist (ruta "/Users/a&b/…") -> Encountered unknown ampersand-escape sequence
```
Corrección: `xml.sax.saxutils.escape` (o `plistlib.dumps`).

## 22. `--modelos quitar` deja `~/.cosmos/bin`, `~/.cosmos/logs` (y el log) — no es «byte a byte»
Visto en la repro del hallazgo 16: tras `quitar`, `find ~/.cosmos` -> `.cosmos/bin`, `.cosmos/logs`. Menor; corrección: borrar los directorios vacíos que creó y decir que el log se conserva.

## Plausibles, no reproducidos
- **Carrera del reponedor con el CLI** (`puente/modelos.py:153-175` y el guion generado): lee `~/.claude.json`, y si Claude Code lo reescribe entre la lectura y el `os.replace`, la escritura del CLI se pierde (última escritura gana). La atomicidad evita el JSON a medias pero no el «lost update»; no se reprodujo porque exige sincronizar dos procesos.
- **`--llavero` pasa el secreto por argv** (`cosmos/cli.py`, `security add-generic-password -w VALOR`): visible en `ps` durante la llamada. Limitación de la herramienta; no se ejecutó contra el llavero real.

No reproducido y descartado: `$` en la ruta del clon del lanzador (`instalar_lanzador` resuelve el symlink y el caso real exige un directorio con `$`); `instalar --seco` sí es seco (0 ficheros escritos); `CLAUDE_CONFIG_DIR` se respeta en `ajustes_usuario`, `configs_vigilados`, G01 (`puente/sesion.py` usa `grado_vigente`) y `estado --maquina`.

**Recuento: 22 hallazgos reproducidos con comando y salida; 2 quedan en plausibles.**
