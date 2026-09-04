---
cosmos: pueblo
nombre: just
padre: automatizacion/flujos
resumen: Un fichero declara los comandos del proyecto por nombre; hoy no habia una forma declarativa de repetir uno.
---

https://github.com/casey/just · CC0-1.0 (dominio público, verificado en su `LICENSE`) · 35.601★ ·
último push 2026-09-01 (comprobado 2026-09-03)

```bash
brew install just
```

```makefile
# justfile — en la raiz del proyecto
default:
    just --list

desplegar entorno="staging":
    echo "Desplegando en {{entorno}}"
    ./scripts/deploy.sh {{entorno}}

test:
    pytest -x
```

```bash
just              # sin argumento: corre la receta 'default' (aqui, lista las demas)
just desplegar produccion
just --list       # que recetas hay y que parametros aceptan
```

Ninguno de los pueblos de este país resolvía el caso más simple: **un comando con nombre que se
repite**. `celery`, `n8n`, `node-red` y `windmill` son motores de flujo con estado, colas y
reintentos — desproporcionados para "cuando escriba `just test`, corre esto". `just` es la
alternativa declarativa a la carpeta `scripts/` con nombres inconsistentes o al `Makefile` usado como
lanzador de comandos (que no es su trabajo: un `Makefile` piensa en ficheros y marcas de tiempo, y
`make test` con un fichero llamado `test` en el directorio no hace nada).

Gana a `make` en ese uso concreto por diseño explícito del propio autor: sin las reglas de
dependencia por fichero que `make` sí necesita, con parámetros con valor por defecto
(`entorno="staging"`), y con `just --list` autodocumentando qué recetas hay sin mantener un `README`
aparte. Frente a una colección de guiones en `scripts/`, gana en descubribilidad: un fichero, un
comando para verlos todos.

Ojo: **no** es un sustituto de `make` para compilación real — no rastrea dependencias entre ficheros
ni salta un paso porque el resultado ya exista; cada receta se ejecuta entera, siempre. Y las recetas
corren en `sh` por defecto en macOS/Linux: una receta multilínea que depende de variables exportadas
en una línea anterior no las hereda entre líneas salvo que se declare `set shell` o se una todo en una
sola invocación — el error clásico de quien viene de pegar comandos en una terminal y espera que se
comporten igual dentro de una receta.
