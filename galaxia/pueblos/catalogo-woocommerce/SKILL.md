---
cosmos: pueblo
nombre: catalogo-woocommerce
padre: web/comercio-electronico
resumen: Recorre la tienda publicada y dice que ficha no tiene precio, foto, categoria o variacion que se pueda comprar.
---

`cosecha/woocommerce-verificar-catalogo.py` — verificacion del catalogo entero despues de una
importacion: precio, si es comprable de verdad, imagen, categoria y variaciones.

Es la mitad que ninguna guia de extension cubre. Importar mil productos siempre dice que fueron mil;
lo que nadie mira es cuantos quedaron sin precio o sin foto, y eso solo se ve producto a producto o
contandolo con un guion.
