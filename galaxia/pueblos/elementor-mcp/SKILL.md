---
cosmos: pueblo
nombre: elementor-mcp
padre: web/construccion-de-sitios
resumen: Expone los controles nativos del maquetador como herramientas, tambien donde el servidor va con PHP viejo.
---

`cosecha/wp-mcp-sync.py` — registra un servidor de herramientas por cada sitio del indice local, sin
que ninguna credencial entre en el repositorio: las escribe en la configuracion del usuario, fuera
del control de versiones, y descarta los sitios con marcadores de ejemplo sin tocarlos.

`cosecha/wp-mcp-stdio-bridge.sh` — el mismo servicio cuando el sitio se sirve con una version de PHP
por debajo de la que exige el complemento. Ahi el punto de entrada devuelve no encontrado aunque el
complemento figure activo, y el diagnostico natural —falta la ruta— es el equivocado: lo que pasa es
que el complemento no llega a cargarse. El puente no toca la version del sitio; usa un interprete
moderno de la consola del servidor, elegido probando candidatos de mas nuevo a mas viejo porque no
todos los alojamientos traen los mismos.

Por que importa mas que hablar con la base de datos: con esto el maquetado se hace con los controles
que el propio maquetador expone, en vez de escribir a mano su estructura interna serializada, que es
la fuente de la mitad de las paginas que luego no se pueden editar desde la interfaz.
