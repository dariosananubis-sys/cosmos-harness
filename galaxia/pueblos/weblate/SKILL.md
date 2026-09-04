---
cosmos: pueblo
nombre: weblate
padre: localizacion
resumen: Traduccion continua atada al repositorio: se traduce en el navegador y sale un commit, no un fichero por correo.
---

https://github.com/WeblateOrg/weblate · GPL-3.0 · 6.051★ · último push 2026-09-04 (comprobado
2026-09-04, API de GitHub y `commits/HEAD.atom`: HEAD 2026-09-04T06:57Z; no archivado)

```bash
# la vía que documenta el proyecto: la pila entera (Weblate + PostgreSQL + Redis) en contenedores
git clone https://github.com/WeblateOrg/docker-compose.git weblate-docker
cd weblate-docker && docker compose up -d          # interfaz en http://localhost/
docker compose exec weblate weblate createadmin    # imprime la contraseña inicial, cámbiala
```

```bash
# desde fuera, con el cliente oficial de línea de comandos
pip install wlc
wlc --url http://localhost/api/ --key TU-CLAVE-DE-API list-projects
wlc pull mi-proyecto/mi-componente      # trae del repositorio lo que se haya escrito en el código
wlc commit mi-proyecto/mi-componente    # baja las traducciones nuevas a un commit del repositorio
```

Gana a `crowdin` y a `lokalise`, que son el estándar comercial de este hueco, en las dos cosas que
`GOAL.md` §5 exige: se instala uno mismo y no cobra por cadena ni pide tarjeta. Y gana a mandar un
`.po` por correo en lo que de verdad cuesta tiempo: el traductor no toca ficheros, y el resultado
entra como commit en la rama, con revisión, comprobaciones de calidad automáticas (marcadores de
formato que faltan, plurales incompletos) y memoria de traducción compartida entre componentes.

Frontera con `i18next` y `formatjs`, que están en el mismo oficio: aquellos son el código que elige
el texto en tiempo de ejecución; `weblate` es dónde ese texto lo escriben y lo revisan personas. No
compiten, se encadenan.

Ojo de licencia: GPL-3.0. Usarlo dentro de casa no obliga a nada, pero si se modifica y se ofrece
como servicio a terceros, la licencia pide publicar el cambio — dato a mirar antes de convertirlo en
producto.

Ojo de máquina: la pila son tres contenedores y el propio proyecto pide 4 GB de RAM libres como
mínimo. En un M3 Pro de 18 GB va sobrado; en una máquina de 8 GB con el navegador y el editor
abiertos, la primera migración se arrastra. Y `docker compose up` sin `WEBLATE_ALLOWED_HOSTS` ni
correo configurado arranca igual: el registro de usuarios falla después, sin avisar en el arranque.
