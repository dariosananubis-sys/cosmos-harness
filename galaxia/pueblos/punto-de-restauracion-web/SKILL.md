---
cosmos: pueblo
nombre: punto-de-restauracion-web
padre: web/construccion-de-sitios
resumen: Guarda y devuelve el maquetado de Elementor por wp-cli, vaciando el CSS generado que finge que no paso nada.
origen: propio
---

Destilado generico de la red de seguridad de un arnes propio, escrita despues de dejar una web peor
en vivo sin vuelta atras. El guion viaja con el pueblo: `scripts/punto_restauracion.py`, solo
biblioteca estandar; necesita `wp-cli` alcanzable.

```bash
python3 scripts/punto_restauracion.py autotest        # ciclo entero con un wp de mentira
python3 scripts/punto_restauracion.py guardar   --wp "wp --path=/ruta/al/wordpress"
python3 scripts/punto_restauracion.py listar
python3 scripts/punto_restauracion.py restaurar --wp "wp --path=/ruta/al/wordpress"
```

`--wp` es el prefijo entero, asi que vale igual en local, por SSH (`--wp "ssh usuario@servidor wp
--path=/ruta"`) o dentro de un contenedor. Guarda `_elementor_data` y `_elementor_page_settings` de
todo lo que use Elementor: paginas, plantillas de cabecera y pie, ventanas emergentes.

Dos gotchas que son el motivo de que esto exista, y que no se deducen leyendo la documentacion:

1. **Restaurar sin vaciar el CSS generado no se nota.** Elementor compila cada pagina a un CSS en
   disco; si devuelves el maquetado y no lo vacias, el sitio sigue sirviendo el CSS viejo y parece
   que la restauracion no ha hecho nada. Se pierde media hora buscando un fallo que no existe. Por
   eso `restaurar` termina siempre en `elementor flush-css`, y si ese comando no esta, borra
   `_elementor_css` a mano.
2. **`update_post_meta` sin `wp_slash` se come las barras invertidas** del JSON del maquetado y
   Elementor abre la pagina en blanco. Se escribe por `wp eval` con el valor en base64 para no
   pelearse ademas con el escapado del shell.

Gana a `restic` —que esta en `infraestructura` y es mejor herramienta de copias— por granularidad y
coste: aquello guarda el sistema entero y no se invoca antes de cada retoque; esto guarda solo el
maquetado, tarda segundos y se puede llamar diez veces en una tarde. Gana a exportar la base de datos
entera (`wp db export`) en el otro extremo: restaurar un volcado devuelve tambien los pedidos, los
comentarios y los usuarios que llegaron mientras tanto. Aqui vuelve el maquetado y nada mas.

Ojo, y es serio: **no guarda medios ni CSS del tema ni ajustes globales del kit**. Si el cambio que
quieres deshacer fue subir una imagen o tocar los colores globales, esto no lo devuelve. Tampoco cubre
lo que se edito fuera de Elementor. Y el punto se guarda donde diga `--estado`: en la maquina desde la
que lanzas, no en el servidor — si se pierde esa carpeta, se perdio la vuelta atras.
