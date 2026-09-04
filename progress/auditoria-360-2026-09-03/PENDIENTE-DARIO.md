# Lo que necesita el sí de Darío — auditoría 360, ciclo 1 (2026-09-03)

Todo lo de aquí está **preparado y sin aplicar**. Ninguna de estas acciones la puede tomar un agente:
reescriben historia publicada, cambian la licencia del repo, retiran contenido del producto o deciden
sobre datos de terceros. Cada punto lleva el diff o el comando listo y el riesgo en una línea.

Rama con el resto de arreglos: `arreglos-2026-09-03` (sin merge, sin push; el orquestador lo hace
cuando el revisor dé el visto bueno).

---

## 1. F-02 · Un CIF español auténtico vive en la historia publicada (ALTO)

**Qué hay.** `galaxia/pueblos/validadores-frontera/SKILL.md` y `cosecha/nif-cif-validator.js` llevaron
un identificador fiscal real de una empresa cliente (empieza por `B039`, dígito de control correcto)
usado como ejemplo. El árbol de hoy dice `B00000000`, pero el valor sigue alcanzable desde
`origin/main`, `origin/historia-limpia`, `origin/limpia-2026-09-02`, `origin/trabajo-2026-09-02`, sus
cuatro equivalentes locales y `refs/original/refs/heads/trabajo-2026-09-02` (blob `c71218cf`,
commits `b05e7a0` → `4c06e72` → `3a655b5`).

**Riesgo.** Publicar el repo tal cual expone el identificador fiscal de un tercero identificable, en
un repositorio cuyo argumento de venta es que sabe detectar exactamente eso. Mientras el repo sea
privado, no es una brecha; la decisión de si lo es y de quién es el dato **es tuya**.

**Preparado (NO ejecutado — reescribe historia y hace `push --force`, prohibidos sin tu orden).**
Corregido tras la revisión R-38, que lo ejecutó sobre un clon y encontró cuatro fallos: `--refs --all`
no es sintaxis válida, `filter-repo` exige `--force` sobre un clon que no es fresco, borra el remoto
`origin` que el paso siguiente necesita, y sin `set -e` los pasos destructivos corrían igual. Y el
fichero con el valor a sustituir se borra al final, no se queda en `$HOME`.

```bash
set -euo pipefail
cd ~/cosmos
ORIGEN="$(git remote get-url origin)"                      # filter-repo borra el remoto: se guarda antes
# 1) el valor a sustituir, en un fichero temporal con permisos 600 (no se escribe aquí entero a propósito)
umask 077; PURGA="$(mktemp)"; printf 'B039<resto del CIF>==>B00000000\n' > "$PURGA"
# 2) reescritura de TODAS las refs (locales, remotas y refs/original)
~/.cosmos/calib/bin/pip install -q git-filter-repo          # libre, sin cuenta; o brew install git-filter-repo
~/.cosmos/calib/bin/git-filter-repo --force --replace-text "$PURGA"
# 3) el volcado de F-05, en la misma reescritura
~/.cosmos/calib/bin/git-filter-repo --force --invert-paths --path research/scratch/q14_analytics.txt
# 4) el fichero con el valor, fuera
rm -P "$PURGA" 2>/dev/null || rm "$PURGA"
# 5) respaldos locales fuera y objetos expirados
git for-each-ref --format='%(refname)' refs/original | xargs -r -n1 git update-ref -d
git branch -D respaldo-antes-reescritura respaldo-main-20260903 trabajo-2026-09-02 2>/dev/null || true
git reflog expire --expire=now --all && git gc --prune=now
# 6) el remoto vuelve, y se empujan las ramas reescritas (FORCE: solo con tu sí)
git remote add origin "$ORIGEN"
git push --force origin main historia-limpia
git push origin --delete limpia-2026-09-02 trabajo-2026-09-02
```

Después: todo clon existente conserva los objetos hasta que se vuelva a clonar.

## 2. F-05 · Volcado con datos de terceros borrado del árbol y vivo en `origin/main` (MEDIO)

`research/scratch/q14_analytics.txt` (101 KB, blob `94384193`, commit `3d75020e`): una página HTML
completa de GitHub capturada como «descripción», con el correo de un tercero (`kebi…@gmail.com`), un
`csrf-token` muerto y una IP pública. Misma purga que el punto 1 (paso 3). **Riesgo:** dato personal
de un tercero en un repositorio; bajo si el repo sigue privado.

Ya aplicado sin tu sí (no toca historia): `puente.secretos` no mira la historia — el modo `--historia`
que propone F (recorrer `git rev-list --objects --all`, ~90 s) queda anotado como mejora; el escáner
del índice tiene ahora la huella del valor y el patrón de rutas de máquina (F-01, F-11).

## 3. F-04 · Licencia — HECHO con tu decisión (Apache-2.0, 2026-09-03)

`LICENSE` (Apache-2.0, «Copyright 2026 Darío Satiño») y `NOTICE` actualizado: COSMOS es tuyo, no de
ninguna organización. Nada pendiente aquí.

## 4. F-03 · Código ajeno redistribuido: conservar o retirar (ya es legal; la preferencia es tuya)

Las licencias de origen están **leídas en su `LICENSE`** (ciclo 2): `alirezarezvani/claude-skills`
es **MIT** (Copyright 2025 Alireza Rezvani) y `obra/superpowers-lab` (Jesse Vincent) es **MIT**. Las
dos permiten redistribuir con atribución, que ya está en `NOTICE` y en las fichas. Conservar los dos
guiones es legal. Lo único que queda es tu preferencia:

| Fichero ajeno | Origen | Estado |
|---|---|---|
| `galaxia/pueblos/auditor-de-skills/scripts/skill_security_auditor.py` (1.066 líneas) + `references/threat-model.md` (271) | `github.com/alirezarezvani/claude-skills`, MIT | atribuido; se conserva salvo que digas lo contrario |
| `galaxia/pueblos/consola-interactiva-tmux/scripts/tmux-wrapper.sh` (84) | `github.com/obra/superpowers-lab`, MIT (no es de Anthropic) | atribuido; se conserva salvo que digas lo contrario |

Retirar: `mv galaxia/pueblos/<x>/scripts ~/.Trash/` y la ficha pasa a catalogar y enlazar.

## 5-bis · Lo que salió del producto HOY por tu encargo A (reversible: está en la papelera)

Orden literal: *«tiene que estar este harnés fuera de <agencia>, no pongas datos de <agencia>, es para
Darío, no <agencia>»*. Todo lo retirado está en `~/.Trash/cosmos-retirados-2026-09-03/`, no borrado:

| Retirado | Por qué |
|---|---|
| `auditar-gasto`, `cuentas-del-asistente`, `lanzadores-de-modelo`, `quota-oficial` | proceso interno del arnés de la agencia: cuentas del asistente, cuota de la suscripción, lanzadores del CLI de una persona, auditoría del gasto de ese arnés |
| `contrato-de-publicacion`, `manifiesto-de-evidencias` | el contrato de publicación «de ocho puertas» y el manifiesto de evidencias de un programa de subvenciones: proceso de la agencia, no una capacidad contratable |
| `ordenes-entre-ventanas` | órdenes entre las ventanas del editor de una persona; el guion nombra el producto propio |
| `web-fidelidad-elementor` | «mecanismo propio de esta casa» cuyo guion vive en otro arnés: prosa sin herramienta (R-37) |
| `cosecha/` (80 ficheros) | la cantera de importación, duplicada byte a byte en `galaxia/pueblos/*/scripts` (76/80) más 4 lanzadores de una máquina concreta (revisión §4.3) |
| `galaxia/paises/juegos--distribucion.md` | provincia con un solo hijo (`butler`): la taxonomía exige que lo que agrupa agrupe; `butler` vuelve a `juegos/motores` hasta que haya una segunda herramienta viva de distribución |

Los otros 30 pueblos propios se quedan **reescritos en genérico** (sin nombres de la agencia, de
clientes, de máquinas ni de su arnés; detalle en `CICLO-2/propios-GB.md`). Si quieres recuperar
alguno de los retirados: `mv ~/.Trash/cosmos-retirados-2026-09-03/<x> galaxia/pueblos/` y
`cosmos arrancar`.

## 5. C · 17 herramientas a retirar o degradar (cambia el contenido del producto)

Retirar cambia lo que el catálogo ofrece: se propone con motivo, **se archiva, nunca se borra**
(`mv galaxia/pueblos/<x> ~/.Trash/` o a `cosecha/retiradas/`), y luego `cosmos arrancar` + `cosmos generar`.

**Retirar (3, firmes):**

| Herramienta | Dónde | Evidencia | Sustituto |
|---|---|---|---|
| `claude-seo-ai` | `visibilidad/auditoria` | 47★, 5 commits, todos el 2026-06-01 en 4 minutos, nada después (la ficha ya lo dice en «Ojo») | `sitespeed` y `katana` (añadidos hoy) |
| `mythril` | `blockchain/auditoria` | último commit de rama 2025-01-31 | `medusa` (añadido hoy, mismo equipo que `slither`/`echidna`) |
| `talipp` | `trading/mercado/investigacion` | 2025-09-09, 12 meses parada; duplica el hueco de `ta-lib` | `ta-lib` (ya existe) |

**Dudosas (6): se quedan solo si su ficha justifica el solapamiento** — `a11y-auditoria-wcag` (al
lado de `axe-core`), `unlighthouse` (es `lighthouse` a escala), `arx` (app Java de escritorio;
`presidio` cubre lo mismo), `reprozip` (2026-01-18; `pixi` + `dvc` ya cubren), `tokio` y `mimalloc`
(bibliotecas, no medidores; el oficio es «que vaya rápido»), `openproject` y `twenty`
(producto final, no automatización: su sitio es `saas` o fuera).

**A vigilar (8):** `kokoro` 2025-08-06 · `ib-async` 2025-12-06 · `hftbacktest` 2025-12-23 ·
`quantstats` 2026-01-13 · `sanitizers` (documentación; la implementación viaja en `llvm-project`) ·
`woocommerce/agent-skills` 10★ · `revision-cruzada` y `quota-oficial` (dependen de un servicio con
cuenta; sus fichas ya lo advierten).

**Riesgo:** ninguno técnico (archivar es reversible); el presupuesto baja, no sube.

## 6. B-05 / B-09 · El holdout v2, ciego (GRAVE)

El único conjunto de validación (v1, 20 encargos) lo escribió el mismo agente que ajusta el árbol,
con el árbol delante, y hoy está en la historia git: el juez arreglado lo declara **QUEMADO** y la
cifra honesta es **DESCONOCIDA**. No puede escribirlo ningún agente que haya visto la galaxia (yo la
he visto entera). Hace falta que:

1. **Tú dictes** los encargos (o salgan de tickets/consultas reales), sin mirar el árbol: frases
   como las de un cliente («se me corrompió la base de datos y no tengo copia de anoche»), y para
   cada una el nodo que debería alcanzarse (basta el oficio; mejor un nodo profundo en un tercio).
2. **n ≥ 100**, cubriendo los 22 oficios (v1 dejaba fuera `rendimiento` y `visibilidad`) y al menos
   un tercio con espera a profundidad ≥ 3.
3. Se guarde FUERA del repo: `~/.cosmos/holdout/encargos-validacion.json` (formato: lista de
   `{"peticion": "...", "espera": "ruta/del/nodo"}`), y se selle con procedencia declarada:

```bash
cd ~/cosmos
python3 -m cosmos acertar --sellar --procedencia "v2, 2026-09-XX: dictado por Darío sin ver el árbol; n=NNN"
git add pruebas/encargos-validacion.SELLO && git commit -m "feat(juez): sello del holdout v2 ciego"
python3 -m cosmos acertar          # publica la cifra con IC95 y n, o dice por qué no
```

**Riesgo:** ninguno; hasta entonces `cosmos acertar --minimo` sale 1 y el CI no cobra listón.

## 7. C · Tres oficios nuevos propuestos (cambian el mapa que aprobaste el 2026-09-01)

`localizacion` (i18n: extracción de cadenas, memoria de traducción, pseudolocalización),
`entregabilidad` (SPF/DKIM/DMARC, reputación, rebotes) y `aprendizaje-automatico` (entrenar,
evaluar y servir un modelo propio). Pasan la prueba «¿alguien contrataría esto?» y añadir un oficio
**no mueve el peor caso** del presupuesto. Pero `spec/UNIVERSO.md` es el mapa que aprobaste: no se
toca sin tu sí. Preparado: cada uno necesita `galaxia/sistemas/<n>.md`, su estrella, una fila en
`UNIVERSO.md` y `cosmos generar`.

## 8. F-09 · El hook de pre-commit en tu clon

`cosmos enganchar --sesion` no está instalado en `~/cosmos` (solo `.sample` en `.git/hooks`). Es
local y reversible; no lo instalo por iniciativa porque cambia el comportamiento de tus commits
(corre el gate entero, ~90 s). Si quieres: `cd ~/cosmos && python3 -m cosmos enganchar --sesion`.
