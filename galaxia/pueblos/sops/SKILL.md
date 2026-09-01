---
cosmos: pueblo
nombre: sops
padre: infraestructura
resumen: Cifra solo los valores del fichero de configuracion para poder versionarlo sin servidor de secretos.
---

Con claves de curva moderna y sin servidor: es la opcion sensata cuando no hay equipo que mantenga
una boveda. Las claves se quedan fuera del repositorio; lo que se versiona es el fichero con los
valores cifrados y las claves en claro.

De la cosecha propia quedan fuera tres clientes de gestores de secretos alojados:
`cosecha/bws-token-set.sh` (guarda y rota el testigo comprobando antes que funciona),
`cosecha/bws-secret-get.js` (busca un secreto por clave en varios proyectos) y
`cosecha/gh-token-set.sh` (deja el testigo del repositorio en el ayudante de credenciales). Son
clientes de un servicio concreto, con su cuenta y su plan; este cubre el hueco sin depender de
ninguno.
