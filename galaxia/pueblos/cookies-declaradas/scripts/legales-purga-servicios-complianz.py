#!/usr/bin/env python3
"""Deja en Complianz solo los servicios medidos como realmente cargados.

Por que existe, con nombre y fecha: el 2026-08-28 se comprobo que el catalogo
de Complianz publica en la politica de cookies servicios que la web NO carga
(Meta, LinkedIn, YouTube, Vimeo, WhatsApp, Intercom, Google Fonts, Google
Maps...), heredados del asistente del plugin o del clonado, no de un escaneo
real. Sobre-declarar no incumple el articulo 22.2 de la LSSI, pero engaña a
quien lee la politica.

El script deja SOLO los servicios medidos como realmente cargados. Medir no es
tarea suya: la lista real llega por ``--mantener``.

    python3 legales-purga-servicios-complianz.py <slug> \
        --mantener "WordPress,Complianz,Elementor,Google Analytics"
    python3 legales-purga-servicios-complianz.py <slug> \
        --mantener "WordPress,Complianz" --purgar-servicios --asistente --aplicar
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_sql import consulta, ejecuta, php, prefijo

import argparse
import base64
import json


def escapa(valor):
    return valor.replace("\\", "\\\\").replace("'", "\\'")


def normaliza(valor):
    return valor.casefold().strip()


def normaliza_slug(valor):
    return "-".join(valor.casefold().strip().split())


def lee_servicios(slug, pre):
    crudo = consulta(slug, f"SELECT ID,name,language FROM {pre}cmplz_services")
    filas = []
    for linea in crudo.splitlines():
        partes = linea.split("\t")
        if len(partes) >= 3 and partes[0].strip().isdigit():
            filas.append({"ID": int(partes[0]), "name": partes[1].strip(),
                          "language": partes[2].strip()})
    return filas


def lee_cookies(slug, pre):
    crudo = consulta(
        slug,
        f"SELECT ID,name,serviceID,language FROM {pre}cmplz_cookies "
        "WHERE deleted=0 AND showOnPolicy=1",
    )
    filas = []
    for linea in crudo.splitlines():
        partes = linea.split("\t")
        if len(partes) >= 4 and partes[0].strip().isdigit():
            filas.append({"ID": int(partes[0]), "name": partes[1],
                          "serviceID": partes[2].strip(),
                          "language": partes[3].strip()})
    return filas


def servicio_de_cookie(cookie, por_id):
    identificador = cookie["serviceID"]
    if identificador in ("", "0", "NULL", "null"):
        return None
    return por_id.get(int(identificador)) if identificador.isdigit() else None


def cookies_sobrantes(cookies, por_id, mantener):
    sobrantes = []
    for cookie in cookies:
        identificador = cookie["serviceID"]
        if identificador in ("", "0", "NULL", "null"):
            continue
        servicio = servicio_de_cookie(cookie, por_id)
        if not servicio or normaliza(servicio["name"]) not in mantener:
            sobrantes.append(cookie)
    return sobrantes


def imprime_resumen(servicios, cookies, por_id, mantener):
    grupos = {}
    for servicio in servicios:
        clave = normaliza(servicio["name"])
        grupos.setdefault(clave, {"nombre": servicio["name"],
                                  "se_queda": clave in mantener, "cookies": []})
    for cookie in cookies:
        identificador = cookie["serviceID"]
        if identificador in ("", "0", "NULL", "null"):
            clave = "\0sin-servicio"
            grupos.setdefault(clave, {"nombre": "Sin servicio", "se_queda": True,
                                      "cookies": []})
        else:
            servicio = servicio_de_cookie(cookie, por_id)
            if servicio:
                clave = normaliza(servicio["name"])
            else:
                clave = f"\0servicio-inexistente-{identificador}"
                grupos.setdefault(
                    clave,
                    {"nombre": f"Servicio inexistente #{identificador}",
                     "se_queda": False, "cookies": []},
                )
        grupos[clave]["cookies"].append(cookie["name"])

    for grupo in sorted(grupos.values(), key=lambda item: normaliza(item["nombre"])):
        nombres = ", ".join(grupo["cookies"]) or "ninguna"
        estado = "SE QUEDA" if grupo["se_queda"] else "SE QUITA"
        print(f"{grupo['nombre']}: {estado} | {len(grupo['cookies'])} fila(s) de cookie | "
              f"{nombres}")


def nombres_unicos(filas):
    nombres = {}
    for fila in filas:
        nombres.setdefault(normaliza(fila["name"]), fila["name"])
    return sorted(nombres.values(), key=normaliza)


def ids_con_cookies_visibles(slug, pre):
    crudo = consulta(
        slug,
        f"SELECT serviceID,COUNT(*) FROM {pre}cmplz_cookies "
        "WHERE showOnPolicy=1 AND deleted=0 GROUP BY serviceID",
    )
    identificadores = set()
    for linea in crudo.splitlines():
        partes = linea.split("\t")
        if (len(partes) >= 2 and partes[0].strip().isdigit()
                and partes[1].strip().isdigit() and int(partes[1]) > 0):
            identificadores.add(int(partes[0]))
    return identificadores


def lee_asistente(slug):
    crudo = php(slug, """<?php
$opciones = get_option('cmplz_options', array());
if (!is_array($opciones)) { $opciones = array(); }
$claves = array('socialmedia_on_site', 'thirdparty_services_on_site',
                'uses_social_media', 'uses_thirdparty_services');
$salida = array();
foreach ($claves as $clave) {
    $salida[$clave] = array_key_exists($clave, $opciones) ? $opciones[$clave] : null;
}
echo "CMPLZ_OPCIONES=" . wp_json_encode($salida) . "\n";
""")
    for linea in crudo.splitlines():
        if linea.startswith("CMPLZ_OPCIONES="):
            return json.loads(linea.split("=", 1)[1])
    raise SystemExit("No se pudieron leer las respuestas del asistente de Complianz")


def calcula_cambios_asistente(opciones, mantener):
    cambios = {}
    pares = (("socialmedia_on_site", "uses_social_media"),
             ("thirdparty_services_on_site", "uses_thirdparty_services"))
    mantener_slugs = {normaliza_slug(nombre) for nombre in mantener}
    for clave, clave_uso in pares:
        actual = opciones.get(clave)
        if actual is None:
            actual = []
        if not isinstance(actual, list):
            raise SystemExit(f"La opcion {clave} de Complianz no es un array; no se toca")
        nuevo = [valor for valor in actual
                 if isinstance(valor, str) and normaliza_slug(valor) in mantener_slugs]
        if nuevo != actual:
            cambios[clave] = {"antes": actual, "despues": nuevo}
        if not nuevo and opciones.get(clave_uso) != "no":
            cambios[clave_uso] = {"antes": opciones.get(clave_uso), "despues": "no"}
    return cambios


def aplica_cambios_asistente(slug, cambios):
    nuevos = {clave: cambio["despues"] for clave, cambio in cambios.items()}
    carga = base64.b64encode(json.dumps(nuevos, ensure_ascii=False).encode()).decode()
    php(slug, f"""<?php
$opciones = get_option('cmplz_options', array());
if (!is_array($opciones)) {{ fwrite(STDERR, "cmplz_options no es un array\n"); exit(1); }}
$cambios = json_decode(base64_decode('{carga}'), true);
$permitidas = array('socialmedia_on_site', 'thirdparty_services_on_site',
                    'uses_social_media', 'uses_thirdparty_services');
foreach ($cambios as $clave => $valor) {{
    if (in_array($clave, $permitidas, true)) {{ $opciones[$clave] = $valor; }}
}}
update_option('cmplz_options', $opciones);
echo "asistente actualizado\n";
""")


def guarda_json(ruta, resultado):
    if ruta:
        Path(ruta).write_text(json.dumps(resultado, indent=1, ensure_ascii=False),
                              encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("slug")
    parser.add_argument("--mantener", required=True,
                        help="servicios realmente cargados, separados por comas")
    parser.add_argument("--purgar-servicios", action="store_true",
                        help="borra servicios sin cookies visibles")
    parser.add_argument("--asistente", action="store_true",
                        help="corrige las respuestas que repueblan el catalogo")
    parser.add_argument("--aplicar", action="store_true",
                        help="sin esto solo enseña lo que cambiaría")
    parser.add_argument("--json", dest="salida")
    args = parser.parse_args()

    mantener, vistos = [], set()
    for nombre in args.mantener.split(","):
        limpio = nombre.strip()
        if limpio and normaliza(limpio) not in vistos:
            mantener.append(limpio)
            vistos.add(normaliza(limpio))
    mantener_normalizado = {normaliza(nombre) for nombre in mantener}

    pre = prefijo(args.slug)
    servicios = lee_servicios(args.slug, pre)
    cookies = lee_cookies(args.slug, pre)
    por_id = {servicio["ID"]: servicio for servicio in servicios}
    sobrantes = cookies_sobrantes(cookies, por_id, mantener_normalizado)
    antes, despues_previsto = len(cookies), len(cookies) - len(sobrantes)
    imprime_resumen(servicios, cookies, por_id, mantener_normalizado)
    print(f"cookies visibles: {antes} -> {despues_previsto}")

    existentes = {normaliza(servicio["name"]) for servicio in servicios}
    inexistentes = [nombre for nombre in mantener if normaliza(nombre) not in existentes]
    if inexistentes:
        print("ERROR: --mantener nombra servicio(s) inexistente(s) en esta web: "
              + ", ".join(inexistentes) + ". No se ha aplicado nada.")
        guarda_json(args.salida, {"slug": args.slug, "mantener": mantener,
                                  "servicios_quitados": [], "cookies_ocultadas": [],
                                  "servicios_borrados": [], "cambios_asistente": {},
                                  "antes": antes, "despues": antes})
        return 2

    servicios_quitados = nombres_unicos(
        [servicio for servicio in servicios
         if normaliza(servicio["name"]) not in mantener_normalizado]
    )
    cambios_asistente = {}
    if args.asistente:
        cambios_asistente = calcula_cambios_asistente(lee_asistente(args.slug), mantener)

    modo = "APLICA" if args.aplicar else "PREVIO"
    for cookie in sobrantes:
        servicio = servicio_de_cookie(cookie, por_id)
        nombre_servicio = servicio["name"] if servicio else f"servicio #{cookie['serviceID']}"
        print(f"{modo}  oculta {cookie['name']} [{cookie['language']}] ({nombre_servicio})")
        if args.aplicar:
            ejecuta(args.slug, f"UPDATE {pre}cmplz_cookies SET showOnPolicy=0 "
                               f"WHERE ID={cookie['ID']}")

    servicios_borrados = []
    if args.purgar_servicios:
        if args.aplicar:
            visibles_por_servicio = ids_con_cookies_visibles(args.slug, pre)
        else:
            ids_sobrantes = {cookie["ID"] for cookie in sobrantes}
            visibles_por_servicio = {
                int(cookie["serviceID"]) for cookie in cookies
                if cookie["ID"] not in ids_sobrantes and cookie["serviceID"].isdigit()
                and int(cookie["serviceID"]) != 0
            }
        candidatos = [servicio for servicio in servicios
                      if normaliza(servicio["name"]) not in mantener_normalizado
                      and servicio["ID"] not in visibles_por_servicio]
        for servicio in candidatos:
            print(f"{modo}  borra servicio {servicio['name']} [{servicio['language']}] "
                  f"(ID={servicio['ID']})")
            if args.aplicar:
                ejecuta(
                    args.slug,
                    f"DELETE FROM {pre}cmplz_services WHERE ID={servicio['ID']} "
                    f"AND NOT EXISTS (SELECT 1 FROM {pre}cmplz_cookies "
                    f"WHERE serviceID={servicio['ID']} AND showOnPolicy=1 AND deleted=0)",
                )
        if args.aplicar:
            restantes = {servicio["ID"] for servicio in lee_servicios(args.slug, pre)}
            borrados = [servicio for servicio in candidatos if servicio["ID"] not in restantes]
            no_borrados = [servicio for servicio in candidatos if servicio["ID"] in restantes]
            servicios_borrados = nombres_unicos(borrados)
            for servicio in no_borrados:
                print(f"AVISO: no se borro {servicio['name']} porque conserva una cookie visible")
        else:
            servicios_borrados = nombres_unicos(candidatos)

    if args.asistente:
        if cambios_asistente:
            for clave, cambio in cambios_asistente.items():
                antes_clave = json.dumps(cambio["antes"], ensure_ascii=False)
                despues_clave = json.dumps(cambio["despues"], ensure_ascii=False)
                print(f"{modo}  asistente {clave}: {antes_clave} -> {despues_clave}")
            if args.aplicar:
                aplica_cambios_asistente(args.slug, cambios_asistente)
        else:
            print("Asistente de Complianz: sin cambios")

    despues = despues_previsto
    if args.aplicar:
        despues = len(lee_cookies(args.slug, pre))
        if despues != despues_previsto:
            print(f"AVISO: se esperaban {despues_previsto} cookies visibles y hay {despues}")
        # Complianz cachea su documento en transients y el servidor cachea la pagina: sin
        # purgar las dos cosas, el cambio queda en la base y la web sirve el texto viejo
        # (una web seguia publicando el comodin `_ga_*` con la cookie ya puesta).
        php(args.slug, """<?php
global $wpdb;
$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE '_transient%cmplz%'
              OR option_name LIKE '_transient_timeout%cmplz%'");
delete_option('cmplz_privacy_statement');
if (class_exists('WPO_Page_Cache')) { WPO_Page_Cache::instance()->purge(); }
if (function_exists('rocket_clean_domain')) { rocket_clean_domain(); }
if (function_exists('wp_cache_clear_cache')) { wp_cache_clear_cache(); }
do_action('litespeed_purge_all');
wp_cache_flush();
echo "cache purgada\n";
""")

    guarda_json(args.salida, {
        "slug": args.slug,
        "mantener": mantener,
        "servicios_quitados": servicios_quitados,
        "cookies_ocultadas": [cookie["name"] for cookie in sobrantes],
        "servicios_borrados": servicios_borrados,
        "cambios_asistente": cambios_asistente,
        "antes": antes,
        "despues": despues,
    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
