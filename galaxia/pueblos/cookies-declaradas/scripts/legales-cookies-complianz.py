#!/usr/bin/env python3
"""Rellena la ficha de cada cookie en Complianz: finalidad, caducidad y titularidad.

Por que existe, con nombre y fecha: el 2026-08-26 el Kit Digital rechazo webs
porque su politica de cookies no recogia "tipo de cookies utilizadas, su
finalidad, identificacion si son propias o de terceros; plazo de conservacion o
caducidad". Complianz genera esa pagina desde su base de datos, y cuando no
reconoce una cookie escribe literalmente "Proposito pendiente de investigacion"
y deja la caducidad en blanco. Eso es justo el incumplimiento.

No es codigo a medida en la web: son los campos del propio plugin, los mismos
que se editan en Complianz > Cookies. Se hace por wp-cli porque son ~30 cookies
por web y diez webs.

    python3 legales-cookies-complianz.py <slug> --ver
    python3 legales-cookies-complianz.py <slug> --aplicar

`purpose` es la categoria que Complianz imprime como titulo del bloque,
`cookieFunction` la linea "Funcion" y `retention` la linea "Caducidad".
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wp_sql import consulta, ejecuta, php, prefijo, wp  # noqa: E402
from cookies_catalogo import (  # noqa: E402  el catalogo vive aparte para no duplicarlo
    FICHA_SERVICIO, clasifica, servicio_de, solo_panel)


# Complianz guarda la ficha en ingles aunque la web sea castellana: "session",
# "persistent", "6 months". El Kit Digital lee la pagina en castellano.
PLAZOS_EN = {"session": "sesión", "persistent": "persistente", "various": "",
             "permanent": "permanente"}
UNIDADES_EN = {"year": "año", "years": "años", "month": "mes", "months": "meses",
               "week": "semana", "weeks": "semanas", "day": "día", "days": "días",
               "hour": "hora", "hours": "horas", "minute": "minuto", "minutes": "minutos",
               "second": "segundo", "seconds": "segundos"}


def traduce_plazo(valor):
    """Devuelve el plazo en castellano, o '' si no habia nada util que traducir."""
    limpio = (valor or "").strip()
    if not limpio:
        return ""
    if limpio.lower() in PLAZOS_EN:
        return PLAZOS_EN[limpio.lower()]
    partido = re.fullmatch(r"(\d+)\s*([A-Za-z]+)", limpio)
    if partido and partido.group(2).lower() in UNIDADES_EN:
        return f"{partido.group(1)} {UNIDADES_EN[partido.group(2).lower()]}"
    return limpio


def servicios(slug, pre, completo=False):
    campos = "ID,name,language,thirdParty,sharesData,privacyStatementURL,serviceType"
    crudo = consulta(slug, f"SELECT {campos} FROM {pre}cmplz_services")
    mapa, fichas = {}, {}
    for linea in crudo.splitlines():
        partes = linea.split("\t")
        if len(partes) >= 3 and partes[0].strip().isdigit():
            clave = (partes[1].strip(), partes[2].strip())
            mapa[clave] = int(partes[0])
            fichas[clave] = partes[3:7] if len(partes) >= 7 else ["", "", "", ""]
    return (mapa, fichas) if completo else mapa


def corrige_servicios(slug, pre, aplicar):
    """Dos defectos del plugin que la politica publica como verdad: marca como propios
    servicios que son de terceros (Google Analytics en un caso real, y entonces
    afirma que los datos no se comparten), y deja el tipo de servicio vacio o en ingles,
    con lo que la linea "Uso" sale en blanco o dice "Usamos X para content creation"."""
    mapa, fichas = servicios(slug, pre, completo=True)
    tocados, sin_ficha = 0, []
    for (nombre, idioma), identificador in mapa.items():
        if nombre not in FICHA_SERVICIO:
            if not (fichas.get((nombre, idioma), ["", "", "", ""])[3] or "").strip():
                sin_ficha.append(nombre)
            continue
        tipo_es, tipo_en, tercero, comparte, url = FICHA_SERVICIO[nombre]
        tipo = tipo_es if idioma == "es" else tipo_en
        actual = fichas.get((nombre, idioma), ["", "", "", ""])
        campos = {"thirdParty": str(tercero), "sharesData": str(comparte),
                  "serviceType": tipo}
        if url:
            campos["privacyStatementURL"] = url
        vistos = {"thirdParty": actual[0], "sharesData": actual[1],
                  "privacyStatementURL": actual[2], "serviceType": actual[3]}
        pendiente = {k: v for k, v in campos.items() if (vistos.get(k) or "").strip() != v}
        if not pendiente:
            continue
        tocados += 1
        print(f"{'APLICA' if aplicar else 'PREVIO'}  servicio {nombre} [{idioma}] "
              + ", ".join(f"{k}={v}" for k, v in pendiente.items())[:120])
        if aplicar:
            sets = ", ".join(f"{k}='{escapa(v)}'" for k, v in pendiente.items())
            ejecuta(slug, f"UPDATE {pre}cmplz_services SET {sets} WHERE ID={identificador}")
    if sin_ficha:
        print("SERVICIO SIN TIPO (sale 'Uso' en blanco): " + ", ".join(sorted(set(sin_ficha))))
    return tocados


def asegura_servicio(slug, pre, mapa, nombre, idioma, aplicar):
    """Complianz necesita una fila por idioma; si falta, la web la muestra como 'Varios'."""
    if (nombre, idioma) in mapa:
        return mapa[(nombre, idioma)]
    tipo_es, tipo_en, tercero, comparte, url = FICHA_SERVICIO[nombre]
    tipo = tipo_es if idioma == "es" else tipo_en
    ranura = nombre.lower().replace(" ", "-")
    if not aplicar:
        print(f"PREVIO  servicio nuevo: {nombre} [{idioma}]")
        return None
    ejecuta(slug,
            f"INSERT INTO {pre}cmplz_services (name,slug,serviceType,category,thirdParty,"
              f"sharesData,secondParty,privacyStatementURL,language,isTranslationFrom,sync) "
            f"VALUES ('{escapa(nombre)}','{escapa(ranura)}','{escapa(tipo)}','',"
            f"{tercero},{comparte},0,'{escapa(url)}','{idioma}',0,0)")
    nuevo = servicios(slug, pre)
    mapa.update(nuevo)
    return nuevo.get((nombre, idioma))


def cookies(slug, pre):
    crudo = consulta(slug, f"SELECT ID,name,retention,purpose,cookieFunction,"
                             f"isOwnDomainCookie,language,serviceID FROM {pre}cmplz_cookies "
                             f"WHERE deleted=0 AND showOnPolicy=1")
    filas = []
    for linea in crudo.splitlines():
        partes = linea.split("\t")
        if len(partes) < 8 or not partes[0].strip().isdigit():
            continue
        filas.append({"ID": int(partes[0]), "name": partes[1], "retention": partes[2],
                      "purpose": partes[3], "cookieFunction": partes[4],
                      "propia": partes[5], "language": partes[6],
                      "serviceID": partes[7]})
    return filas




def siembra(slug, pre, nombres, idiomas, mapa_servicios, aplicar):
    """Complianz solo conoce lo que vio su escaneo. Las cookies que instala de verdad y no
    estan en su base no aparecen en la politica: sin nombre, no hay finalidad ni plazo."""
    existentes = {(c["name"], c["language"]) for c in cookies(slug, pre)}
    puestas = 0
    for nombre in nombres:
        ficha = clasifica(nombre)
        if not ficha:
            print(f"NO SE SIEMBRA {nombre}: no esta en cookies_catalogo.py")
            continue
        propia, purpose, funcion, retencion = ficha
        for idioma in idiomas:
            if (nombre, idioma) in existentes:
                continue
            servicio = servicio_de(nombre) or ("WordPress" if propia else None)
            destino = asegura_servicio(slug, pre, mapa_servicios, servicio, idioma,
                                       aplicar) if servicio else 0
            puestas += 1
            print(f"{'APLICA' if aplicar else 'PREVIO'}  siembra {nombre} [{idioma}] "
                  f"servicio={servicio or 'ninguno'}")
            if not aplicar:
                continue
            ejecuta(slug, f"INSERT INTO {pre}cmplz_cookies (name,slug,sync,ignored,retention,"
                          f"type,serviceID,cookieFunction,purpose,language,isTranslationFrom,"
                          f"isOwnDomainCookie,deleted,isMembersOnly,showOnPolicy,"
                          f"lastUpdatedDate,lastAddDate,firstAddDate) VALUES ("
                          f"'{escapa(nombre)}','{escapa(nombre.lower())}',0,0,"
                          f"'{escapa(retencion or 'persistente')}','',{destino or 0},"
                          f"'{escapa(funcion)}','{escapa(purpose)}','{idioma}',0,"
                          f"{1 if propia else 0},0,0,1,0,0,0)")
    return puestas


def oculta_panel(slug, pre, lista, aplicar):
    """Saca de la politica publica las cookies que solo existen en el panel."""
    fuera = [c for c in lista if solo_panel(c["name"])]
    if not fuera:
        return 0
    nombres = sorted({c["name"] for c in fuera})
    print(f"{'APLICA' if aplicar else 'PREVIO'}  fuera de la politica publica "
          f"({len(fuera)} filas, solo panel): {', '.join(nombres)[:160]}")
    if aplicar:
        for cookie in fuera:
            ejecuta(slug, f"UPDATE {pre}cmplz_cookies SET showOnPolicy=0 WHERE ID={cookie['ID']}")
    return len(fuera)


def escapa(valor):
    return valor.replace("\\", "\\\\").replace("'", "\\'")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("slug")
    parser.add_argument("--aplicar", action="store_true",
                        help="sin esto solo enseña lo que cambiaría")
    parser.add_argument("--sin-panel", action="store_true",
                        help="saca de la politica las cookies que solo existen en /wp-admin")
    parser.add_argument("--sembrar", help="cookies que la web instala y el plugin no conoce, "
                                         "separadas por comas")
    parser.add_argument("--json", dest="salida")
    args = parser.parse_args()

    pre = prefijo(args.slug)
    lista = cookies(args.slug, pre)
    mapa_servicios = servicios(args.slug, pre)
    if args.sembrar:
        idiomas = sorted({c["language"] for c in lista}) or ["es"]
        siembra(args.slug, pre, [n.strip() for n in args.sembrar.split(",") if n.strip()],
                idiomas, mapa_servicios, args.aplicar)
        if args.aplicar:
            lista = cookies(args.slug, pre)
    cambios, sin_clasificar = [], []

    for cookie in lista:
        veredicto = clasifica(cookie["name"])
        if not veredicto:
            if not cookie["purpose"].strip() or not cookie["retention"].strip():
                sin_clasificar.append(cookie["name"])
            continue
        propia, purpose, funcion, retencion = veredicto
        nuevo = {"purpose": purpose, "cookieFunction": funcion,
                 "isOwnDomainCookie": "1" if propia else "0"}
        # retencion None: el catalogo no sabe el plazo exacto. Se respeta el del plugin,
        # traducido; si no hay ninguno, se declara persistente (el caso peor).
        if retencion:
            nuevo["retention"] = retencion
        else:
            nuevo["retention"] = traduce_plazo(cookie["retention"]) or "persistente"
        actual = {"purpose": cookie["purpose"], "cookieFunction": cookie["cookieFunction"],
                  "retention": cookie["retention"], "isOwnDomainCookie": cookie["propia"]}
        actual = {k: v for k, v in actual.items() if k in nuevo}
        # Sin servicio, Complianz las agrupa en "Varios" y escribe que el intercambio de
        # datos esta pendiente de investigacion. Las propias son del propio WordPress.
        servicio = servicio_de(cookie["name"]) or ("WordPress" if propia else None)
        if servicio and (cookie["serviceID"] or "0").strip() in ("", "0"):
            destino = asegura_servicio(args.slug, pre, mapa_servicios, servicio,
                                       cookie["language"], args.aplicar)
            if destino:
                nuevo["serviceID"] = str(destino)
                actual["serviceID"] = cookie["serviceID"]
        # Solo se toca lo que esta vacio o difiere: el texto ya revisado por un humano manda.
        pendiente = {k: v for k, v in nuevo.items() if (actual[k] or "").strip() != v}
        if pendiente:
            cambios.append((cookie, pendiente))

    for cookie, pendiente in cambios:
        detalle = ", ".join(f"{k}={v}" for k, v in pendiente.items())
        print(f"{'APLICA' if args.aplicar else 'PREVIO'}  {cookie['name'][:34]:<34} {detalle[:150]}")
        if not args.aplicar:
            continue
        sets = ", ".join(f"{k}='{escapa(v)}'" for k, v in pendiente.items())
        ejecuta(args.slug, f"UPDATE {pre}cmplz_cookies SET {sets} WHERE ID={cookie['ID']}")

    if args.sin_panel:
        oculta_panel(args.slug, pre, lista, args.aplicar)
    corrige_servicios(args.slug, pre, args.aplicar)

    if sin_clasificar:
        print("SIN CLASIFICAR (revisar a mano): " + ", ".join(sorted(set(sin_clasificar))))
    print(f"{args.slug}: {len(cambios)} cookie(s) a completar, "
          f"{len(sin_clasificar)} sin catalogo, {len(lista)} en la politica")

    if args.aplicar:
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

    if args.salida:
        Path(args.salida).write_text(json.dumps(
            {"slug": args.slug, "cambios": [c[0]["name"] for c in cambios],
             "sin_clasificar": sorted(set(sin_clasificar))}, indent=1, ensure_ascii=False),
            encoding="utf-8")
    return 1 if sin_clasificar else 0


if __name__ == "__main__":
    sys.exit(main())
