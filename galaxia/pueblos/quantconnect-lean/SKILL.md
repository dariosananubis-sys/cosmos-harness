---
cosmos: pueblo
nombre: quantconnect-lean
padre: trading/motores
resumen: Comision, deslizamiento y relleno con un modelo distinto por mercado, no uno generico para todo.
---

Es el motor que trata el realismo como piezas intercambiables y auditables: se puede leer, cambiar y
discutir el modelo de coste de cada mercado por separado, en vez de heredar un supuesto unico.

Modela: comisiones por broker, deslizamiento, relleno, restricciones del venue, multiactivo con
acciones, futuros, opciones, divisas y cripto. No modela: la posicion de tu orden en la cola del
libro. El motor y el CLI corren en local y son gratis; la nube y los datos premium de su empresa son
de pago y no hacen falta.

Frente a `nautilus-trader`, mismo hueco de motor completo: aquel garantiza que simulacion y vivo
comparten semantica; este da el realismo desmontado en modelos que se auditan uno a uno.
