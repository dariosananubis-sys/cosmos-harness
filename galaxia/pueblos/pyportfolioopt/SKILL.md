---
cosmos: pueblo
nombre: pyportfolioopt
padre: trading/riesgo
resumen: Reparte capital entre activos con frontera eficiente, CVaR y paridad de riesgo jerarquica.
---

Resuelve cuanto va a cada activo. No resuelve cuanto se arriesga en UNA entrada concreta: la fraccion
fija y el criterio de Kelly no tienen libreria madura en ningun sitio, y hoy se escriben a mano
dentro del bot. Es de las pocas piezas de este nicho que hay que escribir en vez de instalar.

Se apoya en `cientifico/scipy`, que es el sustrato de la optimizacion.
