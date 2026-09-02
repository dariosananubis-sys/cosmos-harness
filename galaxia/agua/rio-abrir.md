---
cosmos: rio
nombre: abrir
moja: []
invoca: python3 -m cosmos abrir RUTA --tocando FICHERO
resumen: Carga un nodo cuando toca: su cuerpo, su estrella y por donde seguir bajando.
---

El catalogo da rutas cosmograficas y el disco tiene ficheros planos con otro nombre. Sin este
verbo, un agente que leia una ruta en su contexto solo podia abrirla barriendo con `grep` — el
gasto que COSMOS existe para eliminar. Un mapa que da direcciones que no se pueden seguir no es
un mapa.

Trae el cuerpo del nodo, el de su estrella si la tiene, y **los nombres** de sus hijos: nombrarlos
es una cosa y cargarlos otra. Con `--tocando <fichero>` anade el agua que moja ese fichero
concreto, por su glob real; sin fichero no devuelve agua, porque adivinar que se toca es
indistinguible de devolverlo todo.
