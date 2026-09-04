---
cosmos: lluvia
nombre: reescritura-de-historia-2026-09-02
moja: []
resumen: Acta de la reescritura de historia del 2026-09-02, que no purgo nada sensible; sus respaldos siguen vivos.
---

# Acta: la historia se reescribió el 2026-09-02 y no quedó registrado

**Fecha del acta:** 2026-09-03 · **Estado:** registrado a posteriori · **Reversible:** los respaldos existen

## Qué pasó

El 2026-09-02 se reescribió la historia de la rama de trabajo con `git filter-branch`. Quedaron
`refs/original/refs/heads/trabajo-2026-09-02` (el respaldo que deja `filter-branch`), cuatro ramas
de respaldo locales (`historia-limpia`, `respaldo-antes-reescritura`, `respaldo-main-20260903`,
`trabajo-2026-09-02`) y tres remotas (`origin/historia-limpia`, `origin/limpia-2026-09-02`,
`origin/trabajo-2026-09-02`). En todo `registro/` no había una sola entrada sobre la operación, en
un repositorio que documenta hasta el cierre de un fallo menor (auditoría 360, F-12).

## Qué reescribió, y qué NO purgó

Lo que `historia-limpia` deja fuera respecto de `respaldo-antes-reescritura` son **162 versiones de
ficheros de contenido ordinario**. La reescritura **no eliminó ningún dato sensible**: el
identificador fiscal auténtico de un tercero (F-02, en `galaxia/pueblos/validadores-frontera/` y
`cosecha/nif-cif-validator.js` hasta `3a655b5`) y el volcado con datos de terceros
(`research/scratch/q14_analytics.txt`, F-05, hasta `3d75020e`) siguen alcanzables desde las cinco
ramas, incluida la que se llama `historia-limpia`.

## Qué se decide aquí

1. La reescritura queda registrada con esta acta; no se repite sin acta previa.
2. **No se reescribe nada más sin orden de Darío** (`PLAN-MAESTRO.md` §1.1: nada de `filter-repo`,
   `rebase -i` ni `--force`). La purga de F-02 y F-05, los `push --force` a las cinco ramas y el
   borrado de `refs/original/*` y de los respaldos están **preparados y sin aplicar** en
   `progress/auditoria-360-2026-09-03/PENDIENTE-DARIO.md`.
3. Mientras la purga no se haga, el repositorio **no se publica**: el dato de F-02 es de un tercero
   identificable y su exposición sería una decisión que no toma nadie más que Darío.

## Cómo comprobarlo

```bash
git -C ~/cosmos for-each-ref --format='%(refname)' refs/original refs/heads refs/remotes
git -C ~/cosmos log --all --oneline -S'B039' -- galaxia/pueblos/validadores-frontera cosecha | head
```
