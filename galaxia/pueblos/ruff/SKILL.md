---
cosmos: pueblo
nombre: ruff
padre: rendimiento/calidad
resumen: Un solo binario hace de linter y de formateador de Python, y sustituye a media docena de herramientas.
---

https://github.com/astral-sh/ruff · MIT · 49.425★ · push 2026-09-01 (comprobado 2026-09-01, v0.16.5)

```bash
pip install ruff          # o: uv tool install ruff   /   brew install ruff

ruff check .              # analiza
ruff check --fix .        # arregla lo que sabe arreglar
ruff format .             # formatea
ruff check --diff .       # ver el cambio sin escribirlo

# configuracion, en pyproject.toml
# [tool.ruff.lint]
# select = ["E", "F", "I", "UP", "B"]   # pycodestyle, pyflakes, isort, pyupgrade, bugbear
```

El argumento no es que encuentre cosas que `flake8` no encuentre: reimplementa sus reglas, y las de
`isort`, `pyupgrade`, `pydocstyle`, `bandit` y varias mas, en **un binario sin dependencias**. Son
dos ganancias distintas y las dos importan.

La primera es **velocidad**: recorre un repositorio grande en el tiempo que la cadena clasica tarda
en arrancar, asi que cabe en el gancho de pre-commit y en el editor al guardar, que es donde una
regla de estilo sirve de algo. Una comprobacion que tarda dos minutos se acaba corriendo solo en
integracion continua, y entonces ya no evita el error: lo denuncia cuando la revision ya empezo.

La segunda es **unificacion**, y a la larga pesa mas. `flake8` (3.824★, push 2026-08-17) y `black`
(41.828★, push 2026-09-01) siguen perfectamente vivos, pero la cadena de verdad no son dos piezas:
son dos mas los complementos de flake8 que cada proyecto elige, mas `isort`, mas el orden en que se
llaman para que no se peleen entre ellos, mas cuatro ficheros de configuracion con sintaxis
distinta. Eso es lo que ruff sustituye por una seccion de `pyproject.toml`.

Ojo: `ruff format` **no es identico a black** en todos los casos; es compatible en la practica
totalidad del codigo real, pero las diferencias estan documentadas y existen, asi que la migracion
produce un commit de reformateo que conviene aislar. **No tiene interfaz de complementos**: una regla
propia o de un complemento de nicho que no este implementada no se puede anadir, y ahi la cadena
clasica sigue ganando. **No comprueba tipos**: `mypy` o equivalente sigue haciendo falta. Y esta por
debajo de la version 1.0: hay reglas en vista previa que cambian de comportamiento entre versiones
menores, asi que en integracion continua se fija la version exacta y no un rango.
