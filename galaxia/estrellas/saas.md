---
cosmos: estrella
nombre: saas
ilumina: saas
resumen: Lo que es cierto cuando varios clientes comparten la misma instalacion.
---

El aislamiento entre clientes se demuestra atacandolo: una prueba que intenta leer datos de otro y suspende si lo consigue, no un filtro en el que se confia.
El aviso de cobro llega repetido y desordenado: si el manejador no es idempotente, se cobra dos veces o se activa una cuenta que no pago.
El estado de la suscripcion lo manda la pasarela; lo que guarda la aplicacion es una copia que puede estar vieja, y ante la duda se pregunta a la fuente.
Cambiar el esquema con clientes dentro no admite bloqueo largo: pasos reversibles y compatibles con la version anterior, o parada anunciada.
