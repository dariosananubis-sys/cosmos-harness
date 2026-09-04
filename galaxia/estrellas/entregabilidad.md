---
cosmos: estrella
nombre: entregabilidad
ilumina: entregabilidad
resumen: Lo que es cierto cuando quien manda el correo es una maquina.
---

Que el servidor acepte el envio no significa que el mensaje se entregue: el rechazo llega despues, en un rebote, y si nadie lo lee la lista se pudre sola.
Sin SPF, DKIM y DMARC alineados el correo no es de nadie, y da igual lo bueno que sea el contenido.
La reputacion es del dominio y de la direccion que envia, y se quema en un dia: las bajas y los rebotes duros se retiran antes del siguiente envio, no despues.
El aviso que el cliente necesita y la promocion que puede ignorar no comparten dominio: cuando se quema uno, el otro tiene que seguir llegando.
En desarrollo no se escribe a direcciones reales: buzon de pruebas local, o el dia del despiste el aviso sale hacia la lista entera.
Un correo automatico se manda una vez: si el reintento no lleva llave de idempotencia, el cliente recibe el mismo aviso cuatro veces y se da de baja.
