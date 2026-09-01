---
cosmos: pueblo
nombre: wp-remoto
padre: web/construccion-de-sitios
resumen: Consola y SQL contra un gestor de contenidos remoto por conexion reutilizada, con el PHP ejecutado desde fichero.
---

`cosecha/wp-ssh.sh` — consolida seis guiones casi identicos en uno. Dos decisiones que se pagan caras
si no se toman: reutilizar la conexion en vez de abrir una por llamada, que es lo que acaba
provocando un bloqueo por intentos repetidos; y ejecutar PHP siempre desde un fichero, nunca como
cadena interpolada en el comando, que es por donde entra la inyeccion al construir el argumento.

`cosecha/wp_sql.py` — consulta SQL sobre el sitio, con vuelta atras a PHP y la capa de base de datos
del propio gestor cuando en el servidor no hay cliente de base de datos instalado.

`cosecha/wpcli-remote.sh` — prueba binario y version de PHP del panel del servidor en orden hasta dar
con uno ejecutable. Lleva anotada la leccion que le da sentido: una consola que en realidad es una
envoltura de interprete puede aceptar el comando, imprimir texto y no haber ejecutado nada.

Complementa a las guias oficiales del gestor, que explican como se extiende; esto es como se le
habla desde fuera sin abrir el navegador.
