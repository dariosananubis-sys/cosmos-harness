---
cosmos: pueblo
nombre: panel-auth-cookie
padre: saas
resumen: Entrada por cookie a un panel interno con sesion aleatoria revocable, sin montar un servidor de identidad.
---

`cosecha/docker-secret-cookie-auth.js` — pagina de acceso y sesion por cookie para un panel interno,
sin framework: la clave se lee de un fichero de secreto (nunca de una variable de entorno, que
cualquiera ve al inspeccionar el contenedor), se compara en tiempo constante, la sesion es un valor
aleatorio que se puede revocar de verdad, y el intento de entrada tiene limite por IP.

Se prefiere a `casdoor` cuando el panel tiene uno o dos administradores: levantar un servidor de
identidad completo para eso es desproporcionado, y lo que hace falta cabe en un fichero. En cuanto
aparezcan usuarios, roles o inicio de sesion unico, gana `casdoor` y esto se retira.

El error que evita, y que es el motivo de que exista: usar el hash de la clave como identificador de
sesion. Con eso, copiar la cookie equivale a robar la clave para siempre y no hay forma de expulsar
a nadie.
