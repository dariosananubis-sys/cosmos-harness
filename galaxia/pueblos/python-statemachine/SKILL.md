---
cosmos: pueblo
nombre: python-statemachine
padre: trading/codigo-de-bot
resumen: El ciclo de vida de una orden como transiciones declaradas: lo prohibido falla al intentarlo.
---

Una orden pasa por enviada, aceptada, parcial, llena, cancelada y rechazada, y el mercado manda esos
avisos desordenados, repetidos y a veces despues de haber cerrado. Escrito con condicionales sueltos,
la transicion imposible se cuela y se descubre con dinero puesto.

Declarada, el intento de pasar de cancelada a llena revienta en el sitio y con el nombre exacto, que
es la diferencia entre un fallo ruidoso y un descuadre silencioso.

Gana a la libreria de maquinas de estado mas veterana —cinco veces mas estrellas— por una razon
simple: aquella lleva un ano sin publicar y esta no.
