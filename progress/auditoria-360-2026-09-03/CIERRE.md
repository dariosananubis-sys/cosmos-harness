# CIERRE — auditoría 360 de COSMOS · 2026-09-03/04

Lo cierra el orquestador: el fixer final (Fable) y dos revisores (Opus) cayeron por sobrecarga de la
API (HTTP 500/529, status.claude.com «Minor Service Outage») sin escribir nada. Todo lo de abajo
está **medido a mano**, con la salida íntegra en `CIERRE/verif/`.

## Batería final (árbol de `arreglos-2026-09-03`, índice completo)

| Comprobación | Resultado |
|---|---|
| `python3 -m cosmos validar` | verde, 0 errores |
| `python3 -m cosmos generar` / `arrancar` | verde |
| `python3 -m cosmos medir` | presupuesto 4.000 OK, quedan 106 tok con margen calibrado (+5,2 %) en el peor caso (ciberseguridad) |
| `python3 -m unittest discover -s tests` | Ran 359 · OK (2 saltos: comparativas que exigen el tokenizador exacto local) |
| `python3 -m unittest discover -s puente/tests` | Ran 139 · OK |
| `python3 -m puente.gate --sin-pruebas` | EXIT 0 |
| `python3 -m puente.secretos --todo` (sobre el índice) | limpio de nuevos; 3 inventariados |
| `python3 puente/tests/mutaciones.py` | 79/79 invariantes vistas fallar |
| clon en frío (`CICLO-1/clon-en-frio.sh`) | 9/9 pasos en verde, 5,51 s, 0 rutas de máquina en `settings.json` |

## Decisiones de Darío aplicadas (2026-09-03, «te doy el verdadero sí»)

- **Licencia Apache-2.0 a su nombre** (`LICENSE`, `NOTICE`).
- **Código ajeno retirado** (opción B): `skill_security_auditor.py` + `threat-model.md` (1.337 líneas,
  MIT de Alireza Rezvani) y `tmux-wrapper.sh` (84, MIT de Jesse Vincent) a `~/.Trash/cosmos-retirado-2026-09-03/`.
  Las fichas enlazan la **ruta exacta en el origen, verificada contra el árbol de GitHub** ese día.
- **3 retiradas firmes**: `claude-seo-ai`, `mythril`, `talipp` (a la Papelera, reversibles). Las menciones
  en prosa de `ta-lib`, `katana`, `geo-optimizer`, `medusa`, `slither` reescritas.
- Al retirar `talipp`, `trading/mercado/investigacion` quedó con un solo hijo (test
  `LoQueAgrupaTieneQueAgrupar`). Cubierto con **`ta`** (bukosabino/ta · MIT · 5.183★ · push 2026-03-18,
  verificado por API y `HEAD.atom`; `pandas-ta` devolvía 404). Y `ta-lib` documenta ahora `talib.stream`
  (comprobado: `talib/stream.py` en el repo), que es como el país garantiza lote = vivo.
- **Hook de pre-commit** instalado (`cosmos enganchar --sesion`): `.claude/settings.json` portable, 0 `/Users/`.
- **Cero Anubis**: 3 restos en el índice (`anuubis-*.md` en el registro, un nombre de cliente en
  `research/scratch`) → genéricos. `cosecha/` (80 guiones de la agencia) fuera. El escáner caza ahora
  rutas de máquina: detectó 3 en mis propias salidas de verificación → anonimizadas.
- `spec/VALIDADOR.md`: cifra 470 → 468 nodos. `PROGRESS.md` regenerado desde `cosmos estado`.
- Identidad git local del repo: «Dario Satiño» con el correo noreply de GitHub de su cuenta (la anterior
  llevaba el hostname del Mac).

## Hallazgo del propio cierre: el hook bloqueaba TODO commit del árbol nuevo

Con `cosmos enganchar` instalado, el gate corre la suite sobre una **instantánea del índice**
(`git checkout-index` + `git init`, cero commits). Cinco tests del ciclo 2 solo pasaban en el árbol de
trabajo: uno leía `docs/credenciales.plantilla.txt`, que el `.gitignore` del propio ciclo 2 excluía
(`credenciales.*.txt`), y cuatro de `test_juez_honesto` leen la historia git, que la instantánea no
tiene. El ciclo 2 nunca corrió el gate CON pruebas (solo `--sin-pruebas`): el «verde» era parcial.
Fix: excepción `!docs/credenciales.plantilla.txt` en `.gitignore`, y las tres clases que leen historia
saltan con motivo cuando `git rev-parse HEAD` falla (siguen corriendo en el árbol real y en CI).

## Queda abierto (con nombre)

1. **Purga de historia** (F-02 CIF de cliente, F-05 volcado con correo e IP): autorizada por Darío;
   se hace DESPUÉS del push, con bundle previo, `git filter-repo`, `push --force` e incluyendo el clon
   `~/cosmos-respaldo`. Receta en `PENDIENTE-DARIO.md` §1-2.
2. **Holdout v2 ciego**: la nota sigue **DESCONOCIDA**. Encargos reales anonimizados, extraídos por un
   agente que no haya visto la galaxia, a `~/.cosmos/holdout/`, sellados con procedencia (§6).
3. **3 oficios nuevos** (`localizacion`, `entregabilidad`, `aprendizaje-automatico`, §7): decididos,
   no montados — cada uno necesita sistema, estrella, fila en `spec/UNIVERSO.md` y pueblos vivos.
4. Las 6 retiradas «dudosas» de §5 siguen dentro: se retiran cuando su ficha no justifique el solape.
5. Sin revisor Opus final sobre este árbol (dos caídas de API). Lo firma la batería, no un revisor.
