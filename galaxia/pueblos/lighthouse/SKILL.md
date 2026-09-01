---
cosmos: pueblo
nombre: lighthouse
padre: web/calidad-de-sitio
resumen: Motor canonico que audita una URL y devuelve informe con las metricas de experiencia de carga.
---

Referencia oficial y gratuita, corre en local y no manda datos a ningun sitio. Es el motor que hay
debajo de casi todo lo demas, incluida la parte de accesibilidad.

Descartada la coleccion de skills de auditoria web que lo envuelve: aporta listas de causas y
arreglos por framework, que es exactamente el tipo de consejo que un modelo bueno ya tiene. El motor
si aporta; la envoltura no.

Tambien queda fuera `cosecha/pagespeed-accessibility.py`, envoltura del servicio alojado que filtra
las comprobaciones de accesibilidad que fallan: ese servicio es este mismo motor corriendo en casa
ajena, con cuota y sin control de version. Se usa este en local; aquello solo cuando hace falta la
medicion de campo del propio buscador.
