---
cosmos: pueblo
nombre: hftbacktest
padre: trading/backtesting
resumen: Simula posicion en cola y latencia sobre libro completo: el unico que no se engana solo.
---

Modela lo que los demas ignoran: donde queda tu orden en la cola del libro y cuanto tarda en llegar,
con retardo de datos y de orden configurables por separado. Sin eso, cualquier estrategia que ponga
precio sale rentable en el papel.

Lo que exige a cambio: datos de libro nivel 2 o 3 reconstruidos tick a tick. Ese dato ni es gratis ni
es comodo de conseguir, y es el motivo real por el que casi nadie backtestea asi.

Frente a sus hermanos: `backtesting-py` no ve el libro, `vectorbt` ni siquiera itera en el tiempo y
`quantconnect-lean` modela el coste pero no la cola. Si la estrategia cruza el diferencial y aguanta
horas, cualquiera de ellos vale; si vive dentro del diferencial, solo vale este.
