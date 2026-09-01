---
cosmos: pueblo
nombre: aviso-por-chat
padre: automatizacion
resumen: Avisa en el chat de trabajo donde ya esta la gente, por cuenta de servicio o por permiso de un usuario real.
---

`cosecha/google-chat-dm.py` — mensaje directo desde una cuenta de servicio, con el aviso que ahorra
la tarde: la plataforma **no deja que un robot abra una conversacion**, asi que el destinatario tiene
que haberle escrito una vez o no hay delegacion a nivel de dominio. Si eso no se sabe, el envio
falla sin motivo aparente y se busca el error en los permisos.

`cosecha/google-chat-oauth-notify.js` — la otra via, para cuando la organizacion solo tiene aprobado
el flujo de usuario o se quiere que el aviso salga de parte de alguien conocido. Sin dependencias, y
con dos decisiones que se copian: la lista de destinatarios solo viene del entorno, sin valor de
reserva escrito en el codigo, para que nadie reciba un mensaje por un resto olvidado; y **nunca
lanza excepcion**, porque un aviso que falla no puede tumbar el trabajo que lo dispara.

Distinto de un servidor de notificaciones propio, que avisa al movil de quien se suscribe: esto
llega a la herramienta donde el equipo ya esta, sin pedirle que instale nada.
