---
cosmos: pueblo
nombre: vectorbt
padre: trading/backtesting
resumen: Miles de combinaciones de parametros en el tiempo que un motor evento a evento tarda en una.
---

Sirve para descartar rapido, no para decidir. Modela comisiones y deslizamiento por operacion y trae
validacion hacia delante por ventanas.

Lo que NO hace es lo importante: al trabajar sobre matrices de senales ya calculadas, nada te obliga
a preguntarte que sabias en el instante t, asi que un desplazamiento mal puesto mete sesgo de
anticipacion sin que salte ningun error. Lo que sobreviva al barrido se vuelve a correr en un motor
evento a evento antes de creerselo.

Licencia Apache con clausula de no reventa: usarlo y modificarlo es libre, venderlo o alquilarlo como
servicio no. Para montar bots propios o de cliente no estorba; para un producto de backtesting, si.
