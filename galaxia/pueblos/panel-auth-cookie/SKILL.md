---
cosmos: pueblo
nombre: panel-auth-cookie
padre: saas
resumen: Entrada por cookie a un panel interno con sesion aleatoria revocable, sin montar un servidor de identidad.
---

`scripts/docker-secret-cookie-auth.js` — herramienta propia, no hay repositorio público. La ruta ES
la referencia. Node 18+, sin dependencias (`node:crypto` y `node:http` nativos).

```bash
# la clave se lee de un fichero de secreto, NUNCA de una variable de entorno
printf '%s' "<CLAVE_DEL_PANEL>" > /run/secrets/app_password
export APP_PASSWORD_FILE=/run/secrets/app_password
export APP_NAME="PANEL" APP_SESSION_TTL_MS=2592000000

node --input-type=module -e "
import http from 'node:http';
import { handleAuth } from './scripts/docker-secret-cookie-auth.js';
http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  if (handleAuth(req, res, url) === 'handled') return;   // login/logout ya respondidos
  res.end('panel privado');
}).listen(8080);"
```

Se prefiere a `casdoor` cuando el panel tiene **uno o dos administradores**: levantar un servidor de
identidad completo para eso es desproporcionado, y lo que hace falta cabe en un fichero. En cuanto
aparezcan usuarios, roles o inicio de sesión único, gana `casdoor` y esto se retira. Y se prefiere al
`basic_auth` de un proxy inverso porque aquel enseña el popup del navegador, no tiene cierre de
sesión de verdad y manda la credencial en cada petición.

El error que evita, y que es el motivo de que exista: **usar el hash de la clave como identificador
de sesión**. Con eso, copiar la cookie equivale a robar la clave para siempre y no hay forma de
expulsar a nadie. Aquí la sesión es un valor aleatorio revocable, la comparación de la clave es en
tiempo constante y el intento de entrada tiene límite por IP.

Ojo: las sesiones viven **en memoria del proceso**. Reiniciar echa a todo el mundo, y con dos
instancias detrás de un balanceador la sesión solo vale en una de ellas — para eso ya no sirve, hace
falta almacén compartido o `casdoor`. Y una clave única compartida no es autenticación de personas:
no hay auditoría de quién entró. Detrás siempre va TLS (`caddy`); en claro, la cookie viaja a la
vista.
