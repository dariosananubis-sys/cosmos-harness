---
cosmos: pueblo
nombre: catalogo-woocommerce
padre: web/comercio-electronico
resumen: Recorre la tienda publicada y dice que ficha no tiene precio, foto, categoria o variacion que se pueda comprar.
---

`scripts/woocommerce-verificar-catalogo.py` — herramienta propia, no de GitHub. Se apoya en
`scripts/wp_sql.py` → `scripts/wp-ssh.sh --sitio <slug>` (ver el pueblo `wp-remoto`).

```bash
python3 scripts/woocommerce-verificar-catalogo.py <slug>
python3 scripts/woocommerce-verificar-catalogo.py <slug> --json > /tmp/fallos.json
echo $?    # 0 catalogo limpio · 1 hay productos defectuosos
```

Recorre la tienda publicada y da, producto a producto, lo que ninguna importación cuenta: si está
publicado, si tiene precio, si es **comprable de verdad**, si tiene imagen principal y categoría
propia, y las variaciones una a una.

Es la mitad que ninguna guía de extensión cubre. Importar mil productos siempre dice que fueron mil;
lo que nadie mira es cuántos quedaron sin precio o sin foto, y eso solo se ve producto a producto o
contándolo con un guion. Gana al panel de WooCommerce por eso: el panel lista, no audita — y un
producto sin precio se ve igual que uno con precio hasta que se abre.

Ojo: exige el índice de sitios (`~/.wp-sites/sites.json`) configurado y acceso SSH; sin eso no falla
por «catálogo correcto», falla por conexión, y hay que distinguirlo del `0`. Y verifica lo **publicado**
—los borradores no entran—, así que un catálogo a medio publicar sale limpio.
