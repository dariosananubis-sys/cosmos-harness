---
cosmos: pueblo
nombre: paginas-legales
padre: cumplimiento
resumen: Crea y audita el aviso legal y la politica de cookies de una web publicada, y cambia su texto sin romperla.
---

`cosecha/legales-crear-paginas.py` — genera el aviso legal minimo exigido por la ley de servicios de
la sociedad de la informacion y la politica de cookies, de forma repetible: pasarlo dos veces no
duplica paginas.

`cosecha/legales-lssi.py` — audita lo que hay publicado contra lo que la ley pide, que es la parte
que nadie repite pasado el primer mes.

`cosecha/legales-texto.py` — sustituye texto literal en una pagina legal, sea del editor clasico o
del maquetador, sin tocar el resto del contenido.

Es el otro extremo del nicho respecto a `presidio` y `arx`: aquellos protegen el dato personal
dentro; esto es lo que la web tiene que decir por fuera, y es lo que mira quien inspecciona.
