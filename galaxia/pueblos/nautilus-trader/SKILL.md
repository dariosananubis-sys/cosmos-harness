---
cosmos: pueblo
nombre: nautilus-trader
padre: trading/motores
resumen: Motor de eventos con nucleo en Rust: el mismo codigo corre en simulacion y en vivo sin tocarlo.
---

Que la simulacion y el vivo compartan la misma semantica de ejecucion y el mismo reloj determinista
es lo que impide el fallo clasico: tener dos comportamientos y descubrirlo con dinero puesto. Guarda
el estado fuera del proceso, que es lo que permite reiniciar con posiciones abiertas sin perderlas.

Modela: reloj de nanosegundos, cotizaciones y operaciones tick a tick, barras y libro real, con
comisiones y deslizamiento por adaptador. No modela por si solo la posicion en la cola — para eso,
`hftbacktest`.

Frente a `quantconnect-lean`, que ocupa el mismo hueco: aquel desmonta el realismo en modelos por
mercado que se auditan uno a uno; este garantiza que lo que probaste es literalmente lo que corre.
