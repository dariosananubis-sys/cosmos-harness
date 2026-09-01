---
cosmos: pueblo
nombre: wp-remoto
padre: web/construccion-de-sitios
resumen: Consola y SQL contra un gestor de contenidos remoto por conexion reutilizada, con el PHP ejecutado desde fichero.
---

`cosecha/wp-ssh.sh`, `cosecha/wp_sql.py` y `cosecha/wpcli-remote.sh` — herramientas propias, no de
GitHub. Requieren `sshpass` y, para el índice de sitios, `jq`.

```bash
chmod +x cosecha/wp-ssh.sh cosecha/wpcli-remote.sh
export WP_SITES_JSON="$HOME/.wp-sites/sites.json"      # { "sites": { "<slug>": { "ssh": {...} } } }
cosecha/wp-ssh.sh --sitio <slug> plugin list --status=active
python3 -c "import sys;sys.path.insert(0,'cosecha');from wp_sql import sql;print(sql('<slug>','SELECT COUNT(*) FROM wp_posts'))"
cosecha/wpcli-remote.sh <slug-de-servidor> /ruta/al/docroot -- core version
```

Dos decisiones que se pagan caras si no se toman, y por eso `wp-ssh.sh` consolida seis guiones casi
idénticos en uno: **reutilizar la conexión** (ControlMaster) en vez de abrir una por llamada, que en un
servidor con fail2ban acaba baneando la IP; y **ejecutar PHP siempre desde fichero** (`wp eval-file`),
nunca como cadena interpolada en el comando, que es por donde entra la inyección al construir el
argumento y por donde se rompe cualquier código con comillas.

`wp_sql.py` consulta SQL con red de seguridad: si el host no trae cliente de base de datos, cae a PHP
con `$wpdb` en vez de fallar. `wpcli-remote.sh` prueba binario y versión de PHP del panel del servidor
en orden hasta dar con uno ejecutable, y lleva anotada la lección que le da sentido.

Gana a `ssh <host> wp ...` a mano justo en esa lección: **una consola `wp` que en realidad es una
envoltura de intérprete puede aceptar el comando, imprimir texto y no haber ejecutado nada**. La salida
parece correcta. Por eso se prueba el binario, no se asume.

Ojo: `WP_SSH_PASS` viaja por entorno a propósito —nunca por argumento, que queda en `ps` y en el
historial— y eso significa que el entorno de esa sesión tiene la credencial en claro. Complementa a las
guías oficiales (`wordpress-skills`), que explican cómo se **extiende** WordPress; esto es cómo se le
habla desde fuera sin abrir el navegador.
