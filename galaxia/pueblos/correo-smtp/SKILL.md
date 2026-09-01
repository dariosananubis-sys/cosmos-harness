---
cosmos: pueblo
nombre: correo-smtp
padre: automatizacion
resumen: Envia correo por su protocolo y ademas lo copia a Enviados, que muchos proveedores no hacen por su cuenta.
---

`cosecha/enviar-correo-smtp.py` — envio con cifrado directo o negociado, y copia del mensaje a la
carpeta de enviados por el protocolo de buzon.

Ese segundo paso es la razon de existir: el correo enviado por programa llega al destinatario y no
aparece en la carpeta de enviados de quien lo manda salvo que se ponga alli a mano. El efecto es que
nadie en la casa sabe que se envio, y el hilo se contesta dos veces.

Cubre el hueco que no llena ningun motor de flujos de este nicho, que integran servicios pero dan por
hecho que el correo sale de otro sitio.
