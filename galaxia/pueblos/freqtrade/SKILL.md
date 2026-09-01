---
cosmos: pueblo
nombre: freqtrade
padre: trading/motores
resumen: Bot completo de cripto con protecciones integradas que cortan solas tras una racha mala.
---

Entra por las protecciones: parada por perdidas repetidas, limite de caida y periodo de enfriamiento
vienen de serie y se configuran, no se programan. Un bot sin cortacircuitos no se pone en vivo. La
cuenta seca usa literalmente la misma clase de estrategia que el vivo, asi que no hay un modo
simulado que pueda divergir por su cuenta.

Su backtest declara sus asunciones sin adornarlas y hay que leerlas: rellena al precio pedido, SIN
deslizamiento, siempre que ese precio caiga dentro del maximo y el minimo de la vela. Trabaja sobre
velas, asi que no ve el libro ni la latencia.

Lo que no tiene ningun otro de esta lista: comprobadores dedicados de sesgo de anticipacion y de
recursion como subcomandos de primera. Son la forma barata de cazar la trampa que uno mismo se ha
metido sin darse cuenta. Descartados los dos bots todo en uno rivales: menos actividad y sin
equivalente de esas protecciones.
