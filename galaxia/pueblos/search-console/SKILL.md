---
cosmos: pueblo
nombre: search-console
padre: visibilidad
resumen: Da de alta y verifica el sitio en el buscador, envia el mapa y pregunta por que una URL no esta indexada.
---

`cosecha/gsc-search-console.py` — consola para alta y verificacion de propiedad, envio del mapa del
sitio e inspeccion de una URL concreta, con cuenta de servicio.

`cosecha/gsc-service-account-token.js` — acuna el testigo de acceso firmando el vale a mano, sin
arrastrar la biblioteca oficial de autenticacion. Sirve para cualquier API del mismo proveedor
cambiando el ambito, asi que tambien vale para la de analitica.

Se prefiere al servidor externo publico que expone la misma consola con decenas de herramientas de
analisis: aqui hace falta el trozo accionable —dar de alta, verificar, enviar, preguntar por que no
esta indexada— y ese trozo no necesita ni instalacion ni intermediario. Si lo que se busca es
analisis de consultas y canibalizacion, ese servidor es mejor herramienta que esto.

Los dos comparten `cosecha/log.py`, que da el formato de registro comun a esta familia de
envoltorios de API; no es una herramienta, es su dependencia.

Es la unica pieza de este nicho que le habla al buscador; el resto mide el sitio desde fuera.
