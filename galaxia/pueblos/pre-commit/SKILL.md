---
cosmos: pueblo
nombre: pre-commit
padre: automatizacion/flujos
resumen: Instala los ganchos de git desde un fichero versionado; cada linter corre en su propio entorno aislado.
---

https://github.com/pre-commit/pre-commit · MIT · 15.551★ · último push 2026-08-17 (comprobado
2026-09-03)

```bash
pipx install pre-commit
```

```yaml
# .pre-commit-config.yaml — en la raiz, versionado con el resto del proyecto
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
  - repo: local
    hooks:
      - id: just-test
        name: just test
        entry: just test
        language: system
        pass_filenames: false
```

```bash
pre-commit install                 # engancha .git/hooks/pre-commit una sola vez por clon
pre-commit run --all-files         # ejecuta todos los ganchos sin esperar a un commit
```

Se dispara solo, por el ciclo de vida de `git`, no a mano: la diferencia con `just` (el otro pueblo de
este país) es esa — `just test` hay que acordarse de teclearlo, `pre-commit` corre en cada intento de
commit sin que nadie tenga que recordarlo, y de hecho una receta de `just` puede ser uno de sus
ganchos (`language: system`, como el ejemplo de arriba). No compite con `ruff`, `eslint` ni
`sqlfluff`: los orquesta — cada gancho declara su repositorio y versión, y `pre-commit` le monta un
entorno aislado propio (virtualenv, node_modules, lo que pida) sin que el desarrollador tenga que
instalar cada herramienta a mano.

Gana a un guion de `git hooks` casero en dos cosas: **versión fijada por gancho** (`rev: v0.6.9`), así
que todo el equipo corre la misma versión de cada linter sin depender de lo que cada uno tuviera
instalado, y **entornos aislados por herramienta**, así que un gancho en Python y otro en Node no se
pisan las dependencias.

Ojo: `pre-commit install` es **por clon**, no por repositorio — un colaborador nuevo que clona el
proyecto y no ejecuta ese comando no tiene ningún gancho corriendo, y el `.pre-commit-config.yaml`
versionado no lo instala solo. Y el falso verde clásico: si un gancho no está declarado
(`ruff` sin `sqlfluff` para SQL, por ejemplo), un commit que rompe esa regla pasa limpio — la
cobertura es exactamente la lista de repos declarados, ni una regla más.
