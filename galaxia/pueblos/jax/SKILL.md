---
cosmos: pueblo
nombre: jax
padre: cientifico/computo
resumen: Compila la funcion numerica a XLA y la deriva sola; donde scipy corre en CPU esto corre igual en GPU o TPU.
---

https://github.com/jax-ml/jax · Apache-2.0 · 36.244★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
pip install -U jax          # CPU; para GPU: pip install -U "jax[cuda12]"
```

```python
import jax
import jax.numpy as jnp

def perdida(parametros, x, y):
    pred = jnp.dot(x, parametros)
    return jnp.mean((pred - y) ** 2)

gradiente = jax.grad(perdida)                 # diferenciacion automatica: deriva la funcion sola
perdida_rapida = jax.jit(perdida)             # la compila a XLA la primera vez que se llama
lote = jax.vmap(perdida, in_axes=(None, 0, 0))  # vectoriza sobre un lote sin escribir el bucle
```

Frente a `scipy`, que es el álgebra y la optimización de referencia sobre el array de `numpy` en CPU,
`jax` añade tres cosas que `scipy` no tiene: **diferenciación automática** de cualquier función
Python (`grad`), **compilación justo a tiempo** a XLA que corre igual en CPU, GPU o TPU sin cambiar el
código (`jit`), y vectorización automática de una función escalar sobre un lote (`vmap`) sin escribir
el bucle. Es la base de bibliotecas de aprendizaje profundo funcional (Flax, Optax) igual que
`numpy` es la base del cómputo científico clásico.

Gana a escribir el gradiente a mano —la alternativa real antes de que existiera diferenciación
automática— en exactitud: `grad` deriva la expresión simbólicamente sobre el grafo de operaciones, no
aproxima por diferencias finitas. Frente a PyTorch, la diferencia de diseño es que aquí las funciones
son **puras** (sin estado mutable oculto) y la transformación (`jit`, `grad`, `vmap`) se compone
libremente sobre cualquier función; PyTorch sigue siendo la opción cuando el proyecto ya vive en su
ecosistema de módulos con estado.

Ojo: los arrays de `jax` son **inmutables** — `x[0] = 1` no compila, hay que usar `x.at[0].set(1)`, y
ese cambio de estilo es la primera sorpresa de quien viene de `numpy`. Y el falso verde de `jit`: la
primera llamada traza la función y compila un grafo fijo para esa forma y tipo de entrada; si el
tamaño del array cambia en cada llamada, recompila cada vez y el ahorro desaparece sin ningún aviso —
hay que fijar formas estáticas o aceptar la recompilación a propósito. En una máquina sin GPU, `jax`
corre en CPU pero sin la ventaja de rendimiento que lo justifica: para ese caso, `scipy` sigue siendo
la opción más simple.
