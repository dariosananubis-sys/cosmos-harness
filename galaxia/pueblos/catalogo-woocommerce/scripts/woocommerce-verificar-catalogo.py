#!/usr/bin/env python3
"""Verifica el catálogo WooCommerce de una web: comprable, con precio y con foto.

  python3 woocommerce-verificar-catalogo.py <slug> [--json]

Sale 0 si todo está bien y 1 si hay algún producto defectuoso. Un producto es
correcto si está publicado, tiene precio, es comprable, tiene imagen principal y
categoría propia; las variaciones se comprueban una a una.

Se apoya en wp_sql.py (que a su vez usa wp-ssh.sh --sitio <slug>): configura el
índice de sitios (~/.wp-sites/sites.json) antes de usarlo.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_sql import php  # noqa: E402

VERIFICADOR_PHP = r"""<?php
$fallos = [];
$q = new WP_Query(['post_type'=>'product','post_status'=>'publish','posts_per_page'=>-1,'fields'=>'ids']);
$total = 0;
foreach ($q->posts as $id) {
    $p = wc_get_product($id);
    if (!$p) { $fallos[] = "$id: no se pudo cargar el producto"; continue; }
    $total++;
    $nombre = $p->get_name();
    if ($p->get_price() === '' || $p->get_price() === null) { $fallos[] = "$id $nombre: sin precio"; }
    if (!$p->is_purchasable() && $p->get_price() !== '') { $fallos[] = "$id $nombre: no comprable"; }
    if (!get_post_thumbnail_id($id)) { $fallos[] = "$id $nombre: sin imagen principal"; }
    $cats = get_the_terms($id, 'product_cat') ?: [];
    $nombres_cat = wp_list_pluck($cats, 'slug');
    if (!$cats || $nombres_cat === ['uncategorized']) { $fallos[] = "$id $nombre: sin categoria propia"; }
    if ($p->is_type('variable')) {
        $hijos = $p->get_children();
        if (!$hijos) { $fallos[] = "$id $nombre: variable sin variaciones"; }
        foreach ($hijos as $vid) {
            $v = wc_get_product($vid);
            if (!$v) { $fallos[] = "$id $nombre: variacion $vid rota"; continue; }
            if ($v->get_status() !== 'publish') { $fallos[] = "$id $nombre: variacion $vid en {$v->get_status()}"; }
            if ($v->get_price() === '' || $v->get_price() === null) { $fallos[] = "$id $nombre: variacion $vid sin precio"; }
            foreach ($v->get_attributes() as $tax => $valor) {
                if ($valor === '' || $valor === null) { $fallos[] = "$id $nombre: variacion $vid sin valor de $tax"; }
            }
        }
    }
}
echo json_encode(['productos'=>$total, 'fallos'=>$fallos], JSON_UNESCAPED_UNICODE);
"""


def main():
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not argumentos:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    slug = argumentos[0]
    como_json = "--json" in sys.argv

    salida = php(slug, VERIFICADOR_PHP).strip()
    inicio = salida.find("{")
    if inicio < 0:
        print(f"no_medido: el verificador no devolvió JSON: {salida[:200]}", file=sys.stderr)
        return 2
    datos = json.loads(salida[inicio:])

    if como_json:
        print(json.dumps(datos, ensure_ascii=False))
    elif datos["fallos"]:
        for f in datos["fallos"]:
            print(f"FALLO {f}")
        print(f"{len(datos['fallos'])} defectos en {datos['productos']} productos publicados")
    else:
        print(f"{datos['productos']} productos publicados: todos con precio, comprables, "
              f"con imagen y con categoría")
    return 1 if datos["fallos"] else 0


if __name__ == "__main__":
    sys.exit(main())
