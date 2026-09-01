---
cosmos: pueblo
nombre: tenacity
padre: trading/codigo-de-bot
resumen: Reintento con espera creciente y limite declarado, en vez de un while con sleep escrito a mano.
---

La reconexion es donde un bot muere de madrugada. Aqui se declara que excepciones se reintentan,
cuantas veces, con cuanta espera y con cuanto ruido aleatorio para no golpear todos a la vez — y
sobre todo, cuando se deja de reintentar.

La regla que lo vuelve peligroso si se ignora: reintentar el ENVIO de una orden solo es seguro si la
orden lleva identificador propio de cliente y el mercado lo respeta. Sin eso, el reintento no
recupera nada, duplica la posicion. Leer antes de reintentar y reintentar la lectura, no el envio.

El envoltorio de reintento mas citado del ecosistema esta archivado desde 2024; este es el que sigue.
