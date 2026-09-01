---
cosmos: pueblo
nombre: wp-app-password
padre: web/construccion-de-sitios
resumen: Crea, guarda y comprueba la clave de aplicacion del gestor, que solo se puede emitir desde su interfaz.
---

`cosecha/bootstrap-app-pass.py` — entra sin ventana, la crea en el perfil, la guarda en el gestor de
secretos y la verifica contra la API. Existe porque el gestor de contenidos no permite crear esa
clave por API: solo por interfaz, asi que hay que automatizar la interfaz.

`cosecha/save-app-pass.py` — el hermano sin acceso: registra una clave creada a mano, la verifica y
borra el fichero temporal.

`cosecha/wp-rest-base.js` — resuelve donde vive la API cuando el gestor no esta en la raiz del
dominio, que es el paso previo que hace fallar a los dos anteriores sin explicar por que.

El detalle que ahorra la tarde entera: la verificacion se hace contra el recurso de ajustes, no
contra el de usuarios. Muchas webs capan la enumeracion de usuarios y devuelven prohibido aunque la
credencial sea perfectamente valida, y ahi es donde uno se convence de que la clave esta mal.
