#!/usr/bin/env python3
"""Crea el aviso legal y la politica de cookies cuando la web no los tiene.

Por que existe: el 2026-08-27, revisando TODAS las webs subidas, una web no tenia
ninguna de las dos paginas. La LSSI (art. 10) obliga a facilitar de forma permanente,
directa y gratuita los datos del titular, y el Kit Digital lo revisa. Sin pagina no hay
nada que corregir: hay que crearla.

    python3 legales-crear-paginas.py <slug> --titular "Nombre Apellidos" \\
        --nif 12345678Z --domicilio "Calle X, 1, 28001 Madrid" \\
        --email correo@dominio.com [--telefono 600000000] [--web https://dominio.com] \\
        [--solo aviso|cookies] --aplicar

Los datos NO se inventan: salen del briefing, de las hojas de Google o de la politica de
privacidad que la propia web ya publica. Sin `--aplicar` solo enseña lo que crearia.
El texto es el minimo del articulo 10; la politica de cookies queda con el shortcode del
plugin, y el bloque de tipos y titularidad lo escribe despues `legales-bloque-cookies.py`.
"""
import argparse
import base64
import sys
import tempfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_sql import wp  # noqa: E402


def aviso_legal(datos):
    contacto = f'<li><strong>Correo electrónico:</strong> {datos["email"]}</li>'
    if datos.get("telefono"):
        contacto += f'\n<li><strong>Teléfono:</strong> {datos["telefono"]}</li>'
    if datos.get("web"):
        contacto += f'\n<li><strong>Sitio web:</strong> {datos["web"]}</li>'
    return f"""<h2>Identificación y titularidad</h2>
<p>En cumplimiento del artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios de la Sociedad
de la Información y de Comercio Electrónico (LSSI-CE), se facilitan los datos identificativos del
titular de este sitio web:</p>
<ul>
<li><strong>Titular:</strong> {datos["titular"]}</li>
<li><strong>NIF:</strong> {datos["nif"]}</li>
<li><strong>Domicilio:</strong> {datos["domicilio"]}</li>
{contacto}
</ul>
<h2>Objeto</h2>
<p>Este sitio web tiene por objeto ofrecer información sobre los servicios del titular y permitir
el contacto con él. El acceso y la navegación otorgan la condición de usuario e implican la
aceptación de las condiciones recogidas en este aviso legal.</p>
<h2>Condiciones de uso</h2>
<p>El usuario se compromete a hacer un uso adecuado de los contenidos y a no emplearlos para
actividades contrarias a la ley, a la buena fe o al orden público. El titular puede retirar o
suspender el acceso a quien incumpla estas condiciones.</p>
<h2>Propiedad intelectual e industrial</h2>
<p>Los textos, imágenes, marcas, logotipos y demás elementos de este sitio pertenecen al titular o
a terceros que han autorizado su uso. Queda prohibida su reproducción, distribución o
transformación sin autorización expresa.</p>
<h2>Responsabilidad</h2>
<p>El titular no se hace responsable del uso que el usuario haga de los contenidos, ni de los
daños derivados de fallos o desconexiones de las redes de telecomunicaciones ajenos a su control.
Los enlaces a sitios de terceros se ofrecen solo a título informativo: su contenido es
responsabilidad de quien los publica.</p>
<h2>Protección de datos y cookies</h2>
<p>El tratamiento de los datos personales se explica en la política de privacidad, y el uso de
cookies en la política de cookies, ambas accesibles desde este mismo sitio.</p>
<h2>Legislación aplicable</h2>
<p>Este aviso legal se rige por la legislación española. Para cualquier controversia, las partes
se someten a los juzgados y tribunales del domicilio del titular, salvo que la normativa de
consumo disponga otro fuero.</p>"""


COOKIES = """<h2>Política de cookies</h2>
<p>Esta web utiliza cookies propias y de terceros. A continuación se detallan los tipos que
utiliza, su finalidad, quién las gestiona y durante cuánto tiempo se conservan.</p>
[cmplz-document type="cookie-statement" region="eu"]"""


def php_crea(paginas):
    """Idempotente: si la pagina ya existe, no la toca; solo crea la que falta."""
    empaqueta = lambda t: base64.b64encode(zlib.compress(t.encode("utf-8"), 9)).decode("ascii")
    trozos = []
    for ranura, titulo, cuerpo in paginas:
        trozos.append(f"""
$ranura = '{ranura}';
$existe = get_page_by_path($ranura, OBJECT, 'page');
if ($existe) {{
    echo "YA EXISTE $ranura id=" . $existe->ID . "\\n";
}} else {{
    $id = wp_insert_post(array('post_type' => 'page', 'post_status' => 'publish',
        'post_title' => gzuncompress(base64_decode('{empaqueta(titulo)}')),
        'post_name' => $ranura,
        'post_content' => gzuncompress(base64_decode('{empaqueta(cuerpo)}'))), true);
    if (is_wp_error($id)) {{ echo "ERROR $ranura: " . $id->get_error_message() . "\\n"; }}
    else {{ echo "CREADA $ranura id=$id\\n"; }}
}}""")
    return "<?php\n" + "\n".join(trozos) + """
if (class_exists('WPO_Page_Cache')) { WPO_Page_Cache::instance()->purge(); }
if (function_exists('wp_cache_clear_cache')) { wp_cache_clear_cache(); }
do_action('litespeed_purge_all');
wp_cache_flush();
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("slug")
    parser.add_argument("--titular", required=True)
    parser.add_argument("--nif", required=True)
    parser.add_argument("--domicilio", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--telefono")
    parser.add_argument("--web")
    parser.add_argument("--solo", choices=("aviso", "cookies"))
    parser.add_argument("--aplicar", action="store_true")
    args = parser.parse_args()

    datos = {"titular": args.titular, "nif": args.nif, "domicilio": args.domicilio,
             "email": args.email, "telefono": args.telefono, "web": args.web}
    paginas = []
    if args.solo != "cookies":
        paginas.append(("aviso-legal", "Aviso legal", aviso_legal(datos)))
    if args.solo != "aviso":
        paginas.append(("politica-de-cookies", "Política de cookies", COOKIES))

    if not args.aplicar:
        for ranura, titulo, cuerpo in paginas:
            print(f"--- {ranura} ({titulo}) ---\n{cuerpo[:500]}\n")
        print("(usa --aplicar para crearlas)")
        return 0

    ruta = Path(tempfile.gettempdir()) / f"legales-crear-{args.slug}.php"
    ruta.write_text(php_crea(paginas), encoding="utf-8")
    salida = wp(args.slug, ["--php", str(ruta)], tiempo=300).strip()
    print(salida or f"SIN RESPUESTA; reintenta: wp-ssh.sh --sitio {args.slug} --php {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
