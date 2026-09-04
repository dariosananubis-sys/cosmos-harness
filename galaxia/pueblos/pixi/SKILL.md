---
cosmos: pueblo
nombre: pixi
padre: cientifico/reproducible
resumen: Entorno reproducible con fichero de bloqueo multiplataforma de serie, en un solo binario.
---

https://github.com/prefix-dev/pixi · BSD-3-Clause · 7.666★ · último push 2026-09-01 (comprobado 2026-09-01)
(comprobado por API de GitHub el 2026-09-01).

```bash
brew install pixi
```

```bash
pixi init experimento && cd experimento
pixi add python=3.12 numpy scipy matplotlib
pixi add --pypi statsforecast
pixi run python -c "import scipy; print(scipy.__version__)"
pixi shell            # entra al entorno
```

El fichero que importa es `pixi.lock`, y se commitea. Fija version, compilacion y plataforma de cada
paquete, para macOS ARM y para Linux x86 a la vez, sin ejecutar nada en la otra maquina.

Gana a `conda` con `environment.yml` (la alternativa clasica del nicho) en lo unico que decide aqui:
alli el bloqueo es un paso extra, con `conda-lock`, que alguien olvida — y sin bloqueo,
"reproducible" es una palabra. Ademas es un binario en Rust, sin el tiempo de ejecucion pesado de
conda por debajo: resuelve entornos en segundos donde `conda` se queda pensando minutos, con
memoria de sobra o sin ella. Frente a `uv`, que es mas rapido todavia, este cubre el ecosistema
conda-forge —
compiladores, BLAS, CUDA, R— que en ciencia no es opcional.

Y lo que no hace bien: el bloqueo garantiza el mismo paquete, no el mismo resultado. La semilla, la
version de BLAS que elige el sistema en tiempo de ejecucion y el orden de reduccion en coma flotante
siguen sueltos. Para eso estan `hydra` (fija la entrada) y `reprozip` (captura lo que de verdad se
uso).

Y el falso verde: `pixi add` sin fijar version escribe un rango en `pixi.toml`. El bloqueo lo cierra
hoy, pero un `pixi update` lo mueve. Si el experimento tiene que sobrevivir un ano, versiones
exactas.
