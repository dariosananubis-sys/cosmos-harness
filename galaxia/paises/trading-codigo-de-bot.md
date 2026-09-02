---
cosmos: pais
nombre: codigo-de-bot
padre: trading/bots
resumen: Escribir el bot: aqui un fallo no lanza una excepcion, deja una posicion abierta y una perdida.
---

El codigo que mueve dinero no se parece a ningun otro codigo. Las cuatro preguntas que lo definen:
que pasa si se cae la red justo despues de mandar la orden, que pasa si el mismo aviso de ejecucion
llega dos veces, que pasa si el proceso arranca con una posicion ya abierta, y como se demuestra
cualquiera de las tres sin poner dinero.

Ninguna se contesta leyendo: se provocan. Y ninguna se cierra con una excepcion capturada, porque el
sintoma no es un error en el registro, es un descuadre en el saldo.

Correr 24/7 no tiene pais propio aqui a proposito: el reinicio automatico, las alertas y las copias
son `infraestructura`; perfilar el bucle y la concurrencia es `rendimiento`; las claves, el oceano
de secretos. Lo que si falta en todos ellos es el angulo de mercado — avisar de que el resultado real
se ha separado del que prometia el backtest, o de que una posicion lleva abierta mas de lo previsto.
