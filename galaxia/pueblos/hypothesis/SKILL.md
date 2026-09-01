---
cosmos: pueblo
nombre: hypothesis
padre: trading/codigo-de-bot
resumen: Genera las secuencias de eventos que nadie escribiria y comprueba que el invariante aguanta.
---

Aqui no se prueban ejemplos, se prueban invariantes: el efectivo nunca queda negativo, la suma de
ejecuciones nunca supera lo pedido, el mismo aviso de ejecucion dos veces no cuenta dos veces, cerrar
una posicion que no existe no abre la contraria.

Su modo de maquina de estados construye ordenes de llamadas que a nadie se le ocurren y, cuando
rompe, reduce el fallo al caso minimo que lo reproduce — que es lo que convierte un fallo raro en un
test permanente.

Complementa al mar de pruebas sin repetirlo: alli la mutacion mide si un test afirma algo; aqui se
busca el contraejemplo. Licencia MPL, que la interfaz de GitHub no clasifica.
