---
cosmos: pueblo
nombre: codigo-al-modelo
padre: agentes-ia/coste
resumen: Dar codigo a un modelo: el fragmento que pide la intencion, o el repositorio entero si no puede abrir ficheros.
---

`cosecha/semble-doctor.sh` — deja instalada la busqueda semantica de codigo, que localiza por
intencion y devuelve solo el fragmento con su fichero y su linea, en vez del fichero entero. Medido
en esta casa, un mismo lookup cuesta unas cuarenta veces menos asi que leyendo el fichero.

Lo importante del guion no es la instalacion sino la segunda mitad: **borra su servidor de
herramientas de la configuracion si alguien lo colo**. Esa herramienta se paga en cada sesion aunque
no se invoque, y por eso la garantia tiene que ser un mecanismo idempotente y no una nota. Tambien
pre-calienta el indice, porque el minuto largo de la primera busqueda es lo que hace que la gente
vuelva a la busqueda literal.

`cosecha/repomix-pack.sh` — lo contrario, y solo para su caso: empaqueta el repositorio en un unico
documento respetando las exclusiones del control de versiones y buscando secretos antes de escribir.
Gana cuando el modelo que va a leer **no puede abrir ficheros** (una consola ajena, otro proveedor,
una revision fuera de la maquina). Dentro de una sesion con acceso al disco es la forma mas cara
posible de mirar codigo.

La regla de eleccion es esa y no otra: si el que lee puede abrir ficheros, fragmento; si no puede,
paquete.
