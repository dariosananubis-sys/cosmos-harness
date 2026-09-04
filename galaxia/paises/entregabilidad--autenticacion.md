---
cosmos: pais
nombre: autenticacion
padre: entregabilidad
resumen: Demostrar que el correo lo mandas tu: SPF, DKIM, DMARC y los informes que devuelven.
---

Son dos momentos del mismo trabajo y se confunden a menudo. Antes de enviar nada se comprueba que
los registros publicados en el DNS existen, se alinean y no se pasan del limite de consultas. Ya
enviando, los informes que devuelven los receptores dicen quien esta mandando correo en tu nombre,
y ahi aparece tanto el proveedor que se olvido de declarar como el que suplanta.

Ninguno de los dos mide si un mensaje concreto llego a una bandeja: eso no lo publica nadie.
