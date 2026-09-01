---
cosmos: pueblo
nombre: ib-async
padre: trading/conectividad
resumen: Cliente asincrono mantenido para la pasarela del broker que da acceso a mercados clasicos.
---

Continuacion mantenida del cliente historico, que su autor archivo en 2024. Es la unica via razonable
a acciones, futuros y opciones desde Python, y trae reconexion y resincronizacion de estado, que es
justo donde se cae un bot que lleva semanas encendido.

La cuenta de papel del broker es gratuita, asi que la conectividad real se prueba sin arriesgar
capital y sin pedir permiso a nadie.

Para renta variable estadounidense existe otra interfaz pensada desde el origen para bots, tambien
con cuenta de papel gratis, pero es un broker de Estados Unidos: hay que comprobar si admite la
residencia antes de contar con ella.
