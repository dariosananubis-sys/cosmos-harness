---
cosmos: pueblo
nombre: talipp
padre: trading/investigacion
resumen: Recalcula solo el ultimo valor al llegar un precio nuevo, sin rehacer la serie en cada tick.
---

Es la diferencia entre un bot que aguanta el ritmo del mercado y uno que se atasca cuando hay que
mantener cincuenta indicadores sobre veinte pares.

La comprobacion obligatoria al usarlo: pasar la misma serie por el calculo en lote y por el
incremental y exigir que coincidan. Si no coinciden, el bot en vivo esta operando con numeros que el
backtest nunca vio, y ese descuadre no da error, da perdidas.
