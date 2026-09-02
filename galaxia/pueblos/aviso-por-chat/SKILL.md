---
cosmos: pueblo
nombre: aviso-por-chat
padre: automatizacion/avisos
resumen: Avisa en el chat de trabajo donde ya esta la gente, por cuenta de servicio o por permiso de un usuario real.
---

`scripts/google-chat-dm.py` y `scripts/google-chat-oauth-notify.js` — herramienta propia, no hay
repositorio público. La ruta ES la referencia.

```bash
# vía cuenta de servicio (la app de Chat necesita Receive 1:1 + Join spaces)
export GOOGLE_CHAT_SA_JSON=~/.secrets/<cuenta-servicio>.json
python3 scripts/google-chat-dm.py list-spaces
python3 scripts/google-chat-dm.py send persona@ejemplo.test "Copia nocturna terminada"

# vía OAuth de un usuario real (cuando la organizacion solo aprueba el flujo de usuario)
export GCHAT_NOTIFY_RECIPIENTS="persona@ejemplo.test,otra@ejemplo.test"
export GCHAT_CREDENTIALS_FILE=/run/secrets/gchat_credentials
export GCHAT_TOKEN_FILE=/run/secrets/gchat_token
node --input-type=module -e "
import { notifyTeam } from './scripts/google-chat-oauth-notify.js';
console.log(await notifyTeam({ status: 'ok', queue: 'copias', label: 'nocturna' }));"
```

Se prefiere al **Incoming Webhook** del espacio (que es lo que usa la skill `google-chat-send`)
porque un webhook publica en un espacio, no en el privado de una persona, y no se puede revocar por
destinatario: quien tenga la URL escribe. Y se prefiere a `ntfy` cuando el aviso tiene que llegar
donde el equipo ya está mirando, sin pedirle que instale una aplicación.

Ojo, y es el fallo que cuesta la tarde: la API de Chat **no deja que un robot abra una
conversación**. El destinatario tiene que haber escrito al bot una vez, o hace falta delegación a
nivel de dominio; si no, el envío falla y el error apunta a permisos que están bien.

A las tres de la mañana: `notifyTeam` **nunca lanza excepción** a propósito —un aviso roto no puede
tumbar el trabajo que lo dispara—, así que un fallo de envío es silencioso salvo que se mire el
`{ok, sent, errors}` que devuelve. Regístralo. Y la lista de destinatarios sale solo del entorno,
sin valor de reserva en el código: con `ENABLED=1` y la lista vacía, corta sin enviar en vez de
escribir a quien quedó apuntado hace un año.
