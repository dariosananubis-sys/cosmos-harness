#!/usr/bin/env python3
"""Antepone a la politica de cookies el bloque que exige la LSSI y que ningun
generador escribe: tipos de cookies e identificacion de propias y de terceros.

Por que existe, con nombre y fecha: el 2026-08-26 el Kit Digital rechazo webs
porque su politica "no recoge informacion sobre el tipo de cookies; tipo de
cookies utilizadas, su finalidad, identificacion si son propias o de terceros;
plazo de conservacion o caducidad". Complianz y sus primos publican la ficha por
cookie (nombre, funcion, caducidad) pero NUNCA dicen la frase "propias o de
terceros", asi que la revision del organismo la da por ausente.

    python3 legales-bloque-cookies.py <slug> --ver
    python3 legales-bloque-cookies.py <slug> --aplicar
    python3 legales-bloque-cookies.py <slug> --terceros "Google Fonts,Google Maps" --aplicar

Idempotente: el bloque vive entre marcadores HTML y se reescribe entero, no se
duplica. El resto del contenido de la pagina no se toca.
"""
import argparse
import base64
import html
import re
import sys
import tempfile
import zlib
from pathlib import Path
from urllib.parse import urljoin, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cookies_catalogo import clasifica, servicio_de  # noqa: E402
from wp_sql import consulta, prefijo, wp  # noqa: E402  helpers compartidos
INICIO = "<!-- lssi:propias-terceros:inicio -->"
FIN = "<!-- lssi:propias-terceros:fin -->"
RANURAS = ("politica-de-cookies-ue", "politica-de-cookies", "cookies", "politica-cookies",
           "cookie-policy", "politica-de-cookies-eu")
HUELLAS = {
    "Google Fonts": r"fonts\.googleapis\.com", "Mixpanel": r"mixpanel|mxpnl", "Usetiful": r"usetiful",
    "Google Maps": r"maps\.google|maps\.googleapis|google\.[^/]+/maps/embed", "AddToAny": r"addtoany",
    "Google Translate": r"gtranslate|translate\.google|googtrans", "reCAPTCHA": r"recaptcha|grecaptcha", "Instagram": r"instagram\.com/(?:p|reel|embed)|instagram\.com/embed", "Vimeo": r"player\.vimeo\.com",
    "YouTube": r"youtube(?:-nocookie)?\.com/embed|(?:i\.)?ytimg\.com", "PayPal": r"paypal\.com/sdk|paypalobjects\.com",
    "Intercom": r"intercomcdn|intercom\.io|widget\.intercom", "TikTok": r"analytics\.tiktok|tiktok\.com/embed|tiktokcdn", "Automattic": r"stats\.wp\.com|pixel\.wp\.com",
    "LinkedIn": r"platform\.linkedin|linkedin\.com/embed|snap\.licdn", "Twitter": r"platform\.twitter\.com|twitter\.com/i/jot", "Google Analytics": r"google-analytics\.com|googletagmanager\.com/(?:gtag|gtm)",
    "Google Adsense": r"pagead2\.googlesyndication|adsbygoogle", "Google Ads": r"googleadservices|doubleclick|aw-[0-9]+", "Meta": r"connect\.facebook\.net|facebook\.com/tr|fbq\(",
}
ALIAS_HUELLAS = {"Intercom Messenger": "Intercom", "Facebook": "Meta"}


def html_medido(base):
    """Descarga la home y hasta tres paginas interiores representativas."""
    import requests
    cabeceras = {"User-Agent": "legales-bloque/1.0"}
    def descarga(url):
        try:
            respuesta = requests.get(url, timeout=25, headers=cabeceras)
        except requests.RequestException:
            return ""
        return respuesta.text if respuesta.status_code == 200 else ""

    portada_url, mapa = base.rstrip("/") + "/", ""
    portada = descarga(portada_url)
    if not portada: raise SystemExit(f"no se pudo medir la home de {base}; no se reescribe")
    for sitemap in ("wp-sitemap.xml", "sitemap.xml", "sitemap_index.xml"):
        mapa = descarga(urljoin(portada_url, sitemap))
        if mapa:
            break
    localizaciones = re.findall(r"<loc>\s*(.*?)\s*</loc>", mapa, re.I)
    indices = sorted((u for u in localizaciones if u.lower().endswith(".xml")), key=lambda u: "page" not in u.casefold())
    for indice in indices[:3]:
        localizaciones += re.findall(r"<loc>\s*(.*?)\s*</loc>", descarga(indice), re.I)
    if not localizaciones:
        localizaciones = [urljoin(portada_url, u) for u in
                           re.findall(r'href=["\']([^"\']+)', portada, re.I)]
    host = urlparse(base).netloc
    urls = [html.unescape(u) for u in localizaciones if urlparse(html.unescape(u)).netloc == host
            and urlparse(html.unescape(u)).path not in ("", "/")
            and not re.search(r"cookie|privacidad|privacy|aviso-legal|accesibilidad|"
                              r"\.(?:xml|jpe?g|png|webp)", u, re.I)]
    urls.sort(key=lambda u: "contact" not in u.casefold())
    textos = [portada] + [descarga(u) for u in list(dict.fromkeys(urls))[:3]]
    textos = [texto for texto in textos if texto]
    if len(textos) < 3: raise SystemExit(f"solo se midieron {len(textos)} paginas de {base}; no se reescribe")
    print(f"medicion HTML: {len(textos)} pagina(s)")
    return "\n".join(textos).casefold()


def terceros_de_complianz(slug, pre, base):
    """El catalogo solo aporta candidatos; la declaracion nace del HTML medido."""
    try:
        crudo = consulta(slug, f"SELECT DISTINCT s.name FROM {pre}cmplz_services s "
                               f"WHERE s.thirdParty=1 AND s.language='es'")
    except SystemExit as error:
        if "doesn't exist" not in str(error):
            raise
        crudo = ""
    catalogo = [linea.strip() for linea in crudo.splitlines() if linea.strip()]
    medido = html_medido(base)
    hallados = [nombre for nombre, huella in HUELLAS.items() if re.search(huella, medido)]
    for nombre in catalogo:
        huella = HUELLAS.get(ALIAS_HUELLAS.get(nombre, nombre))
        if not huella or not re.search(huella, medido):
            print(f"AVISO: {nombre} esta en Complianz pero no se ha detectado en el HTML")
    return hallados


def tabla_html(dominio, nombres):
    """La tabla que pide el Kit Digital: nombre, titularidad, tipo, finalidad y plazo."""
    celda = "padding:8px;border-bottom:1px solid #e0e0e0;text-align:left;vertical-align:top"
    filas = []
    for nombre in nombres:
        # Complianz guarda tambien SERVICIOS en su tabla de cookies ("Google Fonts API",
        # "Google Maps API"). No son cookies —ningun nombre de cookie lleva espacios— y
        # colarlos en la tabla les inventa una finalidad: se declaran como terceros en el
        # parrafo, que es su sitio. Medido en un caso real 2026-08-28: salian con
        # "Marketing/seguimiento", que ademas es falso para Fonts y Maps.
        if " " in nombre:
            print(f"AVISO: {nombre} es un servicio, no una cookie: fuera de la tabla "
                  f"(declaralo con --terceros)")
            continue
        ficha = clasifica(nombre)
        if not ficha:
            print(f"AVISO: sin catalogo para {nombre}: se omite de la tabla")
            continue
        propia, tipo, finalidad, plazo = ficha
        titular = dominio.split("/")[0] if propia else (
            servicio_de(nombre) or "proveedor externo")
        filas.append(
            f'<tr><td style="{celda}"><code>{nombre}</code></td>'
            f"<td style=\"{celda}\">{'Propia' if propia else 'De terceros'} ({titular})</td>"
            f'<td style="{celda}">{tipo}</td>'
            f'<td style="{celda}">{finalidad[0].upper() + finalidad[1:]}</td>'
            f'<td style="{celda}">{plazo or "persistente"}</td></tr>')
    if not filas:
        return ""
    # A 390 px cinco columnas no caben: la tabla va dentro de una caja que desplaza sola.
    # Sin esto la pagina entera desborda en horizontal y el gate lo marca (C19).
    celda = "padding:8px;border-bottom:1px solid #e0e0e0;text-align:left;vertical-align:top"
    return ('<h3>Detalle de las cookies utilizadas</h3>\n'
            '<div style="display:block;max-width:100%;overflow-x:auto;'
            '-webkit-overflow-scrolling:touch">'
            '<table style="min-width:640px;width:100%;border-collapse:collapse">'
            f'<thead><tr><th style="{celda}">Nombre</th>'
            f'<th style="{celda}">Titularidad</th><th style="{celda}">Tipo</th>'
            f'<th style="{celda}">Finalidad</th>'
            f'<th style="{celda}">Plazo de conservación</th></tr></thead>\n<tbody>\n'
            + "\n".join(filas) + "\n</tbody></table></div>")


def bloque_html(dominio, terceros, tabla="", sin_cookies=False):
    # Solo el host: la ruta entera del staging no rompe linea y desborda a 390 px.
    dominio = dominio.split("/")[0]
    # Sin cookies no hay plazo que declarar: decirlo es mas exacto que un parrafo generico.
    plazos = ("<p>A día de hoy esta web <strong>no instala ninguna cookie</strong> en el navegador "
              "del visitante, por lo que no hay plazo de conservación que declarar. Si en el futuro "
              "se incorpora alguna, se detallará aquí con su finalidad y su plazo.</p>"
              if sin_cookies else
              "<p>Según <strong>su plazo de conservación</strong>, las cookies son <strong>de "
              "sesión</strong> —se borran al cerrar el navegador— o <strong>persistentes</strong>, "
              "que permanecen durante el plazo indicado para cada una. El detalle por cookie "
              "—nombre, finalidad y plazo de conservación o caducidad— figura en el apartado de "
              "cookies utilizadas de esta misma página.</p>")
    lista = ", ".join(terceros[:-1]) + " y " + terceros[-1] if len(terceros) > 1 else (
        terceros[0] if terceros else "")
    parrafo_terceros = (
        f"<p><strong>Cookies de terceros.</strong> Las instalan proveedores externos cuyos "
        f"servicios están incrustados en esta web. En este sitio son las de {lista}. "
        f"Estos proveedores tratan los datos conforme a sus propias políticas de privacidad, "
        f"enlazadas junto a cada servicio en el apartado de cookies utilizadas.</p>"
        if lista else
        "<p><strong>Cookies de terceros.</strong> Son las que instalan proveedores externos "
        "cuyos servicios estén incrustados en la web. Los que utiliza este sitio, si los hay, "
        "figuran identificados uno a uno en el apartado de cookies utilizadas de esta misma "
        "página, junto a su política de privacidad.</p>")
    crudo = f"""{INICIO}
<h2>Tipos de cookies, titularidad y plazo de conservación</h2>
<p>Según <strong>su finalidad</strong>, esta web puede utilizar cuatro tipos de cookies:</p>
<ul>
<li><strong>Técnicas o funcionales</strong> (necesarias): permiten la navegación y el uso de las
opciones del sitio, recuerdan las preferencias de la sesión y guardan la elección hecha en el
aviso de cookies. No requieren consentimiento.</li>
<li><strong>De preferencias o personalización</strong>: recuerdan opciones del usuario, como el
idioma con el que ve la web.</li>
<li><strong>De análisis o estadística</strong>: permiten contar las visitas y medir de forma
agregada cómo se usa la web, para mejorarla.</li>
<li><strong>De publicidad o marketing</strong>: permiten medir el rendimiento de campañas y
mostrar anuncios en función de la navegación. Solo se instalan si el usuario las acepta.</li>
</ul>
<p>Según <strong>quién las gestiona</strong>, las cookies son propias o de terceros:</p>
<p><strong>Cookies propias.</strong> Son las que instala y gestiona el titular de esta web desde
el dominio <strong>{dominio}</strong>. Se usan para que el sitio funcione, para recordar las
preferencias de navegación y para guardar el consentimiento de cookies.</p>
{parrafo_terceros}
{plazos}
{tabla}
{FIN}"""
    # Un salto de linea dentro de <p> o <li> lo pintan algunos temas como salto real.
    return re.sub(r"\n(?![<])", " ", crudo)


def php_actualiza(bloque, ranuras):
    """Idempotente: el bloque se reescribe entre marcadores, nunca se duplica."""
    ranuras_php = ", ".join(f"'{r}'" for r in ranuras)
    # Comprimido y en base64: el HTML lleva acentos, comillas y saltos, y el fichero
    # viaja por SSH; por encima de ~10 KB la copia remota se queda a medias sin avisar.
    bloque_php = base64.b64encode(zlib.compress(bloque.encode("utf-8"), 9)).decode("ascii")
    return f"""<?php
$ranuras = array({ranuras_php});
$bloque = gzuncompress(base64_decode('{bloque_php}'));
// La cache de pagina sirve el HTML viejo y parece que el cambio no se ha aplicado.
function purga_cache() {{
    // El plugin cachea su documento en transients y el servidor cachea la pagina: sin
    // esto el cambio esta en la base de datos y la web sigue sirviendo el texto viejo.
    global $wpdb;
    $wpdb->query("DELETE FROM {{$wpdb->options}} WHERE option_name LIKE '_transient%cmplz%'
                  OR option_name LIKE '_transient_timeout%cmplz%'");
    delete_option('cmplz_privacy_statement');
    if (class_exists('WPO_Page_Cache')) {{ WPO_Page_Cache::instance()->purge(); }}
    if (function_exists('rocket_clean_domain')) {{ rocket_clean_domain(); }}
    if (function_exists('w3tc_flush_all')) {{ w3tc_flush_all(); }}
    if (function_exists('wp_cache_clear_cache')) {{ wp_cache_clear_cache(); }}
    do_action('litespeed_purge_all');
    wp_cache_flush();
}}
$pagina = null;
foreach ($ranuras as $ranura) {{
    $encontrada = get_page_by_path($ranura, OBJECT, 'page');
    if ($encontrada && $encontrada->post_status === 'publish') {{ $pagina = $encontrada; break; }}
}}
if (!$pagina) {{
    $buscadas = get_posts(array('post_type' => 'page', 'post_status' => 'publish',
        'numberposts' => 50, 's' => 'cookie-statement'));
    foreach ($buscadas as $candidata) {{
        if (strpos($candidata->post_content, 'cookie-statement') !== false) {{
            $pagina = $candidata; break;
        }}
    }}
}}
if (!$pagina) {{ echo "SIN PAGINA DE COOKIES\n"; exit(1); }}
$inicio = '{INICIO}';
$fin = '{FIN}';
$patron = '/' . preg_quote($inicio, '/') . '.*?' . preg_quote($fin, '/') . '/s';

// Si la pagina la pinta Elementor, el post_content no se muestra: el texto tiene que
// entrar en el control del widget que lleva la politica.
$modo = get_post_meta($pagina->ID, '_elementor_edit_mode', true);
if ($modo === 'builder') {{
    $datos = get_post_meta($pagina->ID, '_elementor_data', true);
    $arbol = json_decode($datos, true);
    if (!is_array($arbol)) {{ echo "ELEMENTOR ILEGIBLE id=" . $pagina->ID . "\n"; exit(1); }}
    $tocado = false;
    // Primera pasada: el widget que lleva la politica generada por el plugin.
    // Si la web no usa plugin, se elige el texto MAS LARGO que hable de cookies: el
    // primero suele ser el titulo del hero, y el bloque acaba encima de la foto.
    // Se recorre por indice: `foreach ... as &$nodo` con recursion corrompe el arbol.
    $mejor = null;
    $mide = function (&$nodos, $ruta) use (&$mide, $inicio, &$mejor) {{
        foreach (array_keys($nodos) as $clave) {{
            foreach (array('editor', 'shortcode') as $control) {{
                if (empty($nodos[$clave]['settings'][$control])) {{ continue; }}
                $valor = $nodos[$clave]['settings'][$control];
                $exacto = strpos($valor, 'cookie-statement') !== false
                    || strpos($valor, $inicio) !== false;
                $laxo = $control === 'editor' && stripos($valor, 'cookie') !== false;
                if (!$exacto && !$laxo) {{ continue; }}
                $peso = ($exacto ? 1000000 : 0) + strlen($valor);
                if (!$mejor || $peso > $mejor['peso']) {{
                    $mejor = array('ruta' => $ruta . $clave, 'control' => $control, 'peso' => $peso);
                }}
            }}
            if (!empty($nodos[$clave]['elements'])) {{
                $mide($nodos[$clave]['elements'], $ruta . $clave . '.');
            }}
        }}
    }};
    if ($bloque === '') {{
        // Limpieza: quitar el bloque de TODOS los widgets (se metio donde no tocaba).
        $limpia = function (&$nodos) use (&$limpia, $patron, &$tocado) {{
            foreach (array_keys($nodos) as $clave) {{
                foreach (array('editor', 'shortcode') as $control) {{
                    if (empty($nodos[$clave]['settings'][$control])) {{ continue; }}
                    $valor = $nodos[$clave]['settings'][$control];
                    $nuevo = preg_replace($patron, '', $valor);
                    if ($nuevo !== $valor) {{
                        $nodos[$clave]['settings'][$control] = $nuevo;
                        $tocado = true;
                    }}
                }}
                if (!empty($nodos[$clave]['elements'])) {{ $limpia($nodos[$clave]['elements']); }}
            }}
        }};
        $limpia($arbol);
        $mejor = null;
    }}
    else {{ $mide($arbol, ''); }}
    if ($mejor) {{
        $pasos = explode('.', $mejor['ruta']);
        $puntero = &$arbol;
        foreach ($pasos as $indice => $paso) {{
            if ($indice === count($pasos) - 1) {{ break; }}
            $puntero = &$puntero[$paso]['elements'];
        }}
        $destino = &$puntero[end($pasos)]['settings'][$mejor['control']];
        $valor = $destino;
        // Con shortcode del plugin el bloque va delante (explica lo que viene despues);
        // en un texto escrito a mano va detras, como detalle del apartado que ya existe.
        if (preg_match($patron, $valor)) {{
            $nuevo = preg_replace($patron, $bloque, $valor);
        }} elseif (strpos($valor, 'cookie-statement') !== false) {{
            $nuevo = $bloque . "\n\n" . $valor;
        }} else {{
            $nuevo = $valor . "\n\n" . $bloque;
        }}
        if ($nuevo !== $valor) {{ $destino = $nuevo; $tocado = true; }}
        unset($destino, $puntero);
    }}
    if (!$tocado) {{ echo "SIN CAMBIOS (elementor) id=" . $pagina->ID . "\n"; exit(0); }}
    update_post_meta($pagina->ID, '_elementor_data',
        wp_slash(wp_json_encode($arbol, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)));
    // Sin purgar esta cache se sigue sirviendo el HTML anterior del widget.
    global $wpdb;
    $wpdb->query("DELETE FROM {{$wpdb->postmeta}} WHERE meta_key='_elementor_element_cache'");
    echo "ELEMENTOR id=" . $pagina->ID . " ranura=" . $pagina->post_name . "\n";
    exit(0);
}}

$contenido = $pagina->post_content;
if (preg_match($patron, $contenido)) {{
    $nuevo = preg_replace($patron, $bloque, $contenido);
    $accion = $bloque === '' ? 'LIMPIADO' : 'ACTUALIZADO';
}} elseif ($bloque === '') {{
    echo "SIN BLOQUE QUE QUITAR id=" . $pagina->ID . "\n"; exit(0);
}} elseif (($corte = strpos($contenido, '[cmplz-document')) !== false) {{
    // Delante del listado que genera el plugin, que es justo lo que el bloque explica.
    // Nunca al principio del contenido: el H1 de la pagina vive ahi dentro y el bloque
    // acabaria pintado sobre la cabecera con foto, ilegible.
    $nuevo = substr($contenido, 0, $corte) . $bloque . "\n\n" . substr($contenido, $corte);
    $accion = 'INSERTADO';
}} else {{
    $nuevo = $contenido . "\n\n" . $bloque;
    $accion = 'INSERTADO';
}}
if ($nuevo === $contenido) {{ echo "SIN CAMBIOS id=" . $pagina->ID . "\n"; exit(0); }}
$resultado = wp_update_post(array('ID' => $pagina->ID, 'post_content' => $nuevo), true);
if (is_wp_error($resultado)) {{ echo "ERROR: " . $resultado->get_error_message() . "\n"; exit(1); }}
purga_cache();
echo $accion . " id=" . $pagina->ID . " ranura=" . $pagina->post_name . "\\n";
"""


def datos_publicados(base, ranura=None):
    """Lee terceros y tabla vigentes porque reescribir no debe borrar decisiones."""
    import requests
    bloque, respondio = "", False
    rutas = (ranura,) + RANURAS if ranura else RANURAS
    for candidata in rutas:
        try:
            respuesta = requests.get(f"{base.rstrip('/')}/{candidata}/", timeout=25,
                                     headers={"User-Agent": "legales-bloque/1.0"})
        except requests.RequestException:
            continue
        respondio = respondio or (respuesta.status_code == 200 and bool(re.search(r"cookie-statement|cmplz-document|<h1[^>]*>.*?cookie", respuesta.text, re.I | re.S)))
        if respuesta.status_code == 200:
            i, j = respuesta.text.find(INICIO), respuesta.text.find(FIN)
            if i >= 0 and j > i:
                bloque = respuesta.text[i:j]
                break
    if not respondio: raise SystemExit(f"no se pudo leer la politica publicada de {base}; no se reescribe")
    limpio = html.unescape(re.sub(r"<[^>]+>", " ", bloque))
    coincidencia = re.search(r"En este sitio son las de\s+(.+?)\.\s+Estos proveedores",
                            limpio, re.I | re.S)
    terceros = re.split(r",\s*|\s+y\s+", coincidencia.group(1)) if coincidencia else []
    filas = re.findall(r"<tr[^>]*>\s*<t[dh][^>]*>(.*?)</t[dh]>",
                       bloque, re.S | re.I)
    nombres = [re.sub(r"<[^>]+>", "", celda).strip() for celda in filas]
    return ([nombre.strip() for nombre in terceros if nombre.strip()],
            [nombre for nombre in nombres
             if nombre and not re.match(r"(?i)^(cookie|nombre|name)$", nombre)])


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("slug")
    parser.add_argument("--dominio", help="dominio del titular; por defecto, el de la web")
    parser.add_argument("--terceros", help="lista separada por comas que se añade a Complianz")
    parser.add_argument("--pagina", help="ranura concreta de la pagina a tocar")
    parser.add_argument("--tabla", help="nombres de cookies separados por comas: añade la "
                                       "tabla completa (webs sin plugin que la genere)")
    parser.add_argument("--sin-cookies", action="store_true",
                        help="la web no instala ninguna cookie: se declara así")
    parser.add_argument("--quitar", action="store_true",
                        help="borra el bloque de la pagina (para rehacerlo bien)")
    parser.add_argument("--aplicar", action="store_true")
    args = parser.parse_args()

    dominio, base = args.dominio, None
    if not dominio:
        crudo = wp(args.slug, ["option", "get", "home"])
        # La web puede vivir en un subdirectorio (el staging es /<slug>/): para el texto
        # legal manda el dominio, pero para LEER la pagina publicada hace falta la ruta.
        urls = re.findall(r"https?://[\w.-]+(?:/[\w.-]+)*", crudo)
        if not urls:
            raise SystemExit(f"no pude leer el dominio de {args.slug}: usa --dominio")
        base = urls[-1]
        dominio = re.sub(r"^https?://", "", base).split("/")[0]
    if base is None:
        base = f"https://{dominio}"
    medidos = terceros_de_complianz(args.slug, prefijo(args.slug), base)
    conservados, tabla_anterior = datos_publicados(base, args.pagina)
    for nombre in conservados:
        if nombre not in medidos:
            print(f"AVISO: {nombre} ya estaba declarado pero no se ha detectado; se conserva")
    terceros = medidos + conservados
    terceros.extend(t.strip() for t in (args.terceros or "").split(",") if t.strip())
    terceros = sorted(set(terceros), key=terceros.index)
    print(f"terceros medidos={medidos or 'ninguno'}")

    nombres = [n.strip() for n in (args.tabla or "").split(",") if n.strip()]
    if not nombres and not args.quitar and not args.sin_cookies:
        # Sin --tabla se reutiliza la que ya esta publicada: reescribir el bloque la
        # borraria, y el texto que sobrevive sigue remitiendo a ella.
        nombres = tabla_anterior
        if nombres:
            print(f"tabla conservada de la pagina publicada: {len(nombres)} cookies "
                  f"({', '.join(nombres[:6])}{', ...' if len(nombres) > 6 else ''})")
    bloque = "" if args.quitar else bloque_html(
        dominio, terceros, tabla_html(dominio, nombres) if nombres else "",
        sin_cookies=args.sin_cookies)
    print(f"{args.slug}: dominio={dominio} terceros={terceros or 'ninguno'}")
    if not args.aplicar:
        print(bloque[:600] + "\n... (usa --aplicar para escribirlo)")
        return 0

    # El PHP se deja en disco a proposito: si algo falla, se reejecuta a mano.
    ruta = Path(tempfile.gettempdir()) / f"legales-bloque-{args.slug}.php"
    ranuras = (args.pagina,) + RANURAS if args.pagina else RANURAS
    ruta.write_text(php_actualiza(bloque, ranuras), encoding="utf-8")
    salida = wp(args.slug, ["--php", str(ruta)], tiempo=300).strip()
    print(salida or f"SIN RESPUESTA del servidor; reintenta: "
                    f"wp-ssh.sh --sitio {args.slug} --php {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
