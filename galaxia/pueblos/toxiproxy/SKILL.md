---
cosmos: pueblo
nombre: toxiproxy
padre: trading/codigo-de-bot
resumen: Corta la red a proposito: latencia, timeout y conexion caida entre el bot y el mercado, cuando quieras.
---

La pregunta que ningun manual contesta —que pasa si la conexion cae justo despues de mandar la orden
y antes de recibir la confirmacion— solo se contesta provocandola.

Se pone en medio como intermediario y el fallo se enciende y apaga desde el propio test: mil
milisegundos de retardo, cortar a mitad de respuesta, aceptar y no contestar. Es la unica forma de
comprobar de verdad la idempotencia del envio y el arranque con posicion abierta, en vez de confiar
en que el codigo de reconexion hace lo que dice.

Se ejecuta como proceso aparte y se maneja por su interfaz, asi que sirve igual para un bot en Python
que para uno en cualquier otro lenguaje.
