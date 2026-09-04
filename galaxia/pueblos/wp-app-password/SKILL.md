---
cosmos: pueblo
nombre: wp-app-password
padre: web/construccion-de-sitios
resumen: Crea, guarda y comprueba la clave de aplicacion del gestor, que solo se puede emitir desde su interfaz.
origen: propio
---

`scripts/bootstrap-app-pass.py`, `scripts/save-app-pass.py` y `scripts/wp-rest-base.js` —
herramientas propias, no de GitHub.

```bash
export BWS_ACCESS_TOKEN="<token>" BWS_PROJECT_ID="<id-de-proyecto>"
python3 scripts/bootstrap-app-pass.py <slug>                      # login headless, crea, guarda, verifica
python3 scripts/save-app-pass.py <slug> <usuario> /tmp/clave.txt  # si ya se creó a mano
curl -s -u "<usuario>:<clave-de-aplicacion>" https://example.com/wp-json/wp/v2/settings | head -c 200
```

Existe porque WordPress **no permite crear una contraseña de aplicación por API**: solo desde la
interfaz. Así que la única salida es automatizar la interfaz — login sin ventana con `agent-browser`,
crearla en `profile.php`, guardarla en el gestor de secretos y verificarla contra la REST, sin
imprimir nunca el secreto por salida estándar. `save-app-pass.py` es el hermano sin login: registra
una creada a mano, verifica y **borra el fichero temporal**. `wp-rest-base.js` resuelve dónde vive la
REST cuando WordPress no está en la raíz del dominio, que es el paso previo que hace fallar a los otros
dos sin explicar por qué.

El detalle que ahorra la tarde entera, y es la razón de preferir esto a un `curl` improvisado: la
verificación se hace contra **`/wp/v2/settings`, no contra `/wp/v2/users/me`**. Muchas webs capan la
enumeración de usuarios y devuelven `401`/`403` aunque la credencial sea perfectamente válida — y ahí
es donde uno se convence de que la clave está mal y la vuelve a crear tres veces.

Ojo: la contraseña de aplicación **no es la del usuario** y se revoca sola si se cambia esta última o
si el sitio la retira; un `401` de un día para otro suele ser eso, no un fallo del guion. Y el valor
nunca se pasa por argumentos (queda en el historial y en `ps`): siempre por fichero o por entorno.
