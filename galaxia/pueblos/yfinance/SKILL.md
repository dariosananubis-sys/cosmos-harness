---
cosmos: pueblo
nombre: yfinance
padre: trading/datos-de-mercado
resumen: Historico gratis de acciones, divisas e indices a cambio de ninguna garantia de seguir manana.
---

No es una interfaz oficial: raspa el frontal de un portal financiero, se rompe cuando ese portal
cambia y su uso queda en zona gris de sus condiciones. Se acepta porque para prototipar no hay nada
gratis mejor, y porque el coste de que falle es un script roto, no una perdida.

No vale para cripto a nivel de tick. Para cripto, `trading/conectividad/ccxt` da el historico del
propio mercado, que ademas es el que se ejecuto de verdad.
