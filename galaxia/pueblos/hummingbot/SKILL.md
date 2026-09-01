---
cosmos: pueblo
nombre: hummingbot
padre: trading/motores
resumen: Creacion de mercado con cuenta de papel contra el libro real, sin claves de ningun mercado.
---

Entra por eso: es el unico de aqui que deja correr un bot completo contra precios de verdad sin
exponer una clave ni un euro. Las claves, cuando llegan, van a un almacen local cifrado y no a un
fichero de configuracion en claro.

Separa los conectores por tipo de riesgo —mercado centralizado que custodia tus fondos frente a
descentralizado que no—, que es una distincion de dinero, no de codigo.

Distinto de `freqtrade`: alli se apuesta a una direccion con protecciones que cortan; aqui se pone
precio en los dos lados y el riesgo es quedarse con inventario. La cifra de volumen que anuncia su
propio material es autodeclarada y no esta comprobada.
