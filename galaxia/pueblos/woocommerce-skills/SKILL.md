---
cosmos: pueblo
nombre: woocommerce-skills
padre: web/comercio-electronico
resumen: Guia oficial para extender la tienda tras el cambio de almacenamiento de pedidos y con bloques.
---

https://github.com/woocommerce/agent-skills · **licencia sin SPDX** · 9★ · último push 2026-08-25
(comprobado 2026-09-01). Oficial de WooCommerce/Automattic.

```bash
git clone https://github.com/woocommerce/agent-skills.git
node agent-skills/shared/scripts/skillpack-install.mjs      # empaqueta para Claude/Cursor/Codex
```

Es la **única fuente que documenta el contenedor de servicios y la Store API después del cambio de
almacenamiento de pedidos (HPOS)**, que es justo donde se rompe el código escrito con ejemplos viejos:
acceder al pedido como si fuera un post ya no vale, y el fallo aparece en producción, no al escribirlo.
Trae herramientas de construcción reales, no solo prosa.

Gana a `woocommerce/woocommerce-claude` (28★, también oficial) porque aquel responde otra pregunta
—analítica de una tienda viva, «pregúntale a tu tienda»— y se solapa con el cuadro de mando de datos.
Y gana a las colecciones de terceros con más estrellas en lo único que importa aquí: la fuente
canónica es la que se actualiza cuando la API cambia.

Ojo, dos avisos: **9 estrellas y dos skills documentadas** — es muy nuevo, la cobertura es fina y hay
huecos enteros sin cubrir; no sustituye leer la documentación oficial. Y la licencia no trae
identificador SPDX: leer el fichero antes de redistribuir nada derivado.
