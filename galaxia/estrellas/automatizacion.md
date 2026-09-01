---
cosmos: estrella
nombre: automatizacion
ilumina: automatizacion
resumen: Lo que es cierto en algo que corre solo mientras nadie mira.
---

Un flujo que se rompe en silencio a las tres de la manana es peor que no tenerlo: si no avisa al fallar, no esta terminado.
Se reintenta, luego cada paso es idempotente: la misma entrada dos veces no puede cobrar dos veces ni mandar dos correos.
Lo que no se pudo procesar va a una cola aparte, con su motivo y su carga original: ni se descarta ni se reintenta eternamente.
Lo que dispara el flujo cambia sin avisar -un campo, un formato, una respuesta del otro lado-, asi que se comprueba que lo que llega es lo esperado antes de actuar.
