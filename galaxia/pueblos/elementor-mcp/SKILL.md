---
cosmos: pueblo
nombre: elementor-mcp
padre: web/construccion-de-sitios
resumen: Expone los controles nativos del maquetador como herramientas, tambien donde el servidor va con PHP viejo.
---

https://github.com/msrbuilds/elementor-mcp (plugin **EMCP Tools**) · GPL-2.0 · 661★ · último push
2026-08-30 (comprobado 2026-09-01). Requiere WordPress 6.9+ y **PHP 8.1+**. Expone **más de 200
herramientas MCP**.

Del lado de esta casa, dos guiones propios: `cosecha/wp-mcp-sync.py` y `cosecha/wp-mcp-stdio-bridge.sh`.

```bash
curl -s https://example.com/wp-json/ | grep -c emcp-tools-server   # ¿carga el plugin?
python3 cosecha/wp-mcp-sync.py                 # lista lo que registraría, sin tocar nada
python3 cosecha/wp-mcp-sync.py --aplicar --solo <id-de-sitio>
# si el vhost va por debajo de PHP 8.1:
WP_SSH_HOST=<host> WP_SSH_USER=<usuario> WP_SSH_PASS=<clave> WP_DOCROOT=/ruta/al/wordpress \
  cosecha/wp-mcp-stdio-bridge.sh 1
```

Por qué esto y no hablar con la base de datos: con el plugin el maquetado se hace con **los controles
que el propio Elementor expone** (contenedores, flexbox, plantillas de tema), en vez de escribir a
mano su estructura interna serializada — que es el origen de la mitad de las páginas que luego no se
pueden editar desde la interfaz.

`wp-mcp-sync.py` registra un servidor por sitio del índice local **sin que ninguna credencial entre en
el repositorio** (las escribe en la configuración del usuario, fuera del control de versiones) y
descarta los sitios con marcadores de ejemplo sin tocarlos. El puente STDIO existe por un diagnóstico
que engaña: con PHP viejo el endpoint devuelve **404 aunque el plugin figure activo**, y la conclusión
natural —«falta la ruta»— es la equivocada; lo que pasa es que el plugin no llega a cargarse. El
puente no toca el PHP del vhost: usa el PHP moderno del CLI del servidor, probando candidatos de más
nuevo a más viejo porque no todos los alojamientos traen los mismos.

Gana a `wppilot-labs/wordpress-mcp-elementor-wppilot` (67★, 133 habilidades) por adopción y cobertura,
y a `respira-press/agent-skills-wordpress` (42★) porque aquel **depende de un servidor MCP comercial de
pago**; aquí la capa que se usa es la gratuita del plugin.

Ojo, y es lo más caro: **200+ herramientas se pagan en el contexto de cada sesión en la que el servidor
esté conectado**. Conectarlo «por si acaso» es la fuga de contexto por excelencia — se conecta para el
encargo y se desconecta al terminar. El plugin trae además una capa Pro de pago que no se contrata sin
orden expresa; todo lo de arriba funciona en la gratuita. Y aunque las escrituras vienen desactivadas
de fábrica y exigen `confirm: true`, sigue siendo un agente escribiendo en una web viva: punto de
restauración antes.
