---
cosmos: pueblo
nombre: rotki
padre: trading
resumen: Cuadra lo que dice el mercado con lo que dice tu registro, y calcula lo que hay que declarar.
---

Cierra el unico hueco que ningun motor cubre: que el saldo que cree el bot y el saldo real coincidan,
y que de ahi salga un numero presentable a Hacienda con metodo de coste y ejercicio fiscal.

Es una aplicacion de escritorio que corre al lado del bot, no una libreria que el bot invoque: lee
las operaciones por la interfaz del mercado y las contrasta contra su propia contabilidad. Todo en
local — claves e historico no salen de la maquina.

No sustituye al registro del propio bot: lo audita. Si los dos numeros no cuadran, el que miente casi
siempre es el del bot. Licencia con copyleft de red y una capa de pago opcional que no hace falta
para esto.
