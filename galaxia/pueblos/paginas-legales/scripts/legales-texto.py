#!/usr/bin/env python3
"""Sustituye un texto exacto en una pagina legal, este en el editor o en Elementor.

Para los datos del titular que el Kit Digital exige y estan mal escritos: la
etiqueta del NIF, el domicilio incompleto, la denominacion social a medias. Es
una sustitucion literal, no una plantilla: se dice que se busca y con que se
cambia, y el script dice cuantas veces lo encontro.

    python3 legales-texto.py <slug> --pagina aviso-legal \\
        --buscar "Identificador fiscal: ES 12345678Z" \\
        --sustituir "NIF: 12345678Z" --aplicar

Sin `--aplicar` solo cuenta las apariciones. Idempotente: si el texto buscado ya
no esta, no toca nada.
"""
import argparse
import base64
import sys
import tempfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_sql import wp  # noqa: E402


def php_sustituye(ranura, buscar, sustituir, aplicar):
    """Los textos viajan comprimidos: por SSH, un PHP largo se corta sin avisar."""
    empaqueta = lambda texto: base64.b64encode(
        zlib.compress(texto.encode("utf-8"), 9)).decode("ascii")
    return f"""<?php
$ranura = '{ranura}';
$buscar = gzuncompress(base64_decode('{empaqueta(buscar)}'));
$sustituir = gzuncompress(base64_decode('{empaqueta(sustituir)}'));
$aplicar = {'true' if aplicar else 'false'};
$pagina = get_page_by_path($ranura, OBJECT, 'page');
if (!$pagina) {{ echo "SIN PAGINA $ranura\\n"; exit(1); }}
$vistas = 0;

$contenido = $pagina->post_content;
$vistas += substr_count($contenido, $buscar);
if ($aplicar && substr_count($contenido, $buscar)) {{
    wp_update_post(array('ID' => $pagina->ID,
        'post_content' => str_replace($buscar, $sustituir, $contenido)));
}}

$datos = get_post_meta($pagina->ID, '_elementor_data', true);
if ($datos) {{
    $arbol = json_decode($datos, true);
    $tocado = false;
    $anda = function (&$nodos) use (&$anda, $buscar, $sustituir, $aplicar, &$vistas, &$tocado) {{
        foreach (array_keys($nodos) as $clave) {{
            if (!empty($nodos[$clave]['settings'])) {{
                foreach ($nodos[$clave]['settings'] as $control => $valor) {{
                    if (!is_string($valor) || substr_count($valor, $buscar) === 0) {{ continue; }}
                    $vistas += substr_count($valor, $buscar);
                    if ($aplicar) {{
                        $nodos[$clave]['settings'][$control] =
                            str_replace($buscar, $sustituir, $valor);
                        $tocado = true;
                    }}
                }}
            }}
            if (!empty($nodos[$clave]['elements'])) {{ $anda($nodos[$clave]['elements']); }}
        }}
    }};
    $anda($arbol);
    if ($tocado) {{
        update_post_meta($pagina->ID, '_elementor_data',
            wp_slash(wp_json_encode($arbol, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)));
        global $wpdb;
        $wpdb->query("DELETE FROM {{$wpdb->postmeta}} WHERE meta_key='_elementor_element_cache'");
    }}
}}
if ($aplicar && $vistas) {{
    if (class_exists('WPO_Page_Cache')) {{ WPO_Page_Cache::instance()->purge(); }}
    if (function_exists('rocket_clean_domain')) {{ rocket_clean_domain(); }}
    do_action('litespeed_purge_all');
    wp_cache_flush();
}}
echo ($aplicar ? 'APLICADO' : 'ENCONTRADO'), " id=", $pagina->ID, " veces=$vistas\\n";
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("slug")
    parser.add_argument("--pagina", required=True, help="ranura de la pagina, p.ej. aviso-legal")
    parser.add_argument("--buscar", required=True)
    parser.add_argument("--sustituir", required=True)
    parser.add_argument("--aplicar", action="store_true")
    args = parser.parse_args()

    ruta = Path(tempfile.gettempdir()) / f"legales-texto-{args.slug}.php"
    ruta.write_text(php_sustituye(args.pagina, args.buscar, args.sustituir, args.aplicar),
                    encoding="utf-8")
    salida = wp(args.slug, ["--php", str(ruta)], tiempo=300).strip()
    print(salida or f"SIN RESPUESTA; reintenta: wp-ssh.sh --sitio {args.slug} --php {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
