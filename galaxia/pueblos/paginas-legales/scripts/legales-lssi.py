#!/usr/bin/env python3
"""Audita las paginas legales de una web publicada contra la LSSI (Ley 34/2002).

Por que existe, con nombre y fecha: el 2026-08-26 el organismo del Kit Digital
rechazo justificaciones con dos motivos textuales:

  (a) el aviso legal "no consta denominacion social completa" (ademas de
      domicilio, medio de contacto directo y NIF/CIF);
  (b) la politica de cookies no recoge "tipo de cookies utilizadas, su
      finalidad, identificacion si son propias o de terceros; plazo de
      conservacion o caducidad".

El gate visual de las webs no miraba nada de esto: una web podia estar PASA y
seguir siendo rechazada. Este script lo mide, y `web-gate.py` lo usa como C22.

    python3 legales-lssi.py https://<dominio-cliente>/
    python3 legales-lssi.py https://<dominio-1>/ https://<dominio-2>/ --json informe.json
    python3 legales-lssi.py https://<dominio-cliente>/ --razon-social "Ejemplo S.L."

Codigos de salida: 0 todo pasa, 1 alguna comprobacion falla, 2 solo hubo webs
que no se pudieron descargar.
"""
import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

RUTAS_CANDIDATAS = {
    "aviso_legal": ["aviso-legal", "legal", "aviso-legal-y-condiciones",
                    "aviso-legal-y-politica-de-privacidad"],
    "cookies": ["cookies", "politica-de-cookies", "politica-de-cookies-ue",
                "politica-cookies"],
    "privacidad": ["privacidad", "politica-de-privacidad", "politica-privacidad"],
}

FORMAS = (r"S\.?\s?L\.?\s?U\.?|S\.?\s?L\.?\s?L\.?|S\.?\s?L\.?\s?P\.?|S\.?\s?L\.?|"
          r"S\.?\s?A\.?\s?U\.?|S\.?\s?A\.?|S\.?\s?COOP\.?|S\.?\s?C\.?|C\.?\s?B\.?|"
          r"S\.?\s?R\.?\s?L\.?|SOCIEDAD LIMITADA|SOCIEDAD ANONIMA|SOCIEDAD CIVIL")
RE_FORMA = re.compile(
    r"([A-ZÁÉÍÓÚÑÜ][\wÁÉÍÓÚÑÜáéíóúñü&.\-]*(?:\s+[\wÁÉÍÓÚÑÜáéíóúñü&.\-]+){0,6})"
    r"[\s,]+(" + FORMAS + r")(?=[\s.,;)]|$)")
RE_ETIQUETA_TITULAR = re.compile(
    r"(titular(?:idad)?|denominacion social|razon social|responsable|"
    r"denominacion|prestador(?: de servicios)?|pertenecen? a|"
    r"propiedad de|a nombre de)\b", re.I)
# Nombre y dos apellidos, en Capitalizado o TODO EN MAYUSCULAS (asi lo escriben
# muchos avisos legales: "MARTA IGLESIAS HERRANZ").
_PALABRA = r"[A-ZÁÉÍÓÚÑÜ](?:[a-záéíóúñü]{2,}|[A-ZÁÉÍÓÚÑÜ]{2,})"
_NEXO = r"(?:\s+(?:de|del|la|las|los|y|DE|DEL|LA|LAS|LOS|Y)\s+|\s+)"
RE_TRES_PALABRAS = re.compile(_PALABRA + _NEXO + _PALABRA + _NEXO + _PALABRA)
RE_NIF = re.compile(
    r"\b(?:[ABCDEFGHJNPQRSUVW][0-9]{7}[0-9A-J]|[0-9]{8}[-\s]?[A-Za-z]|"
    r"[XYZ][0-9]{7}[-\s]?[A-Za-z])\b")
RE_ETIQUETA_NIF = re.compile(r"\b(NIF|CIF|DNI|NIE|N\.I\.F|C\.I\.F)\b", re.I)
RE_CP = re.compile(r"\b[0-5][0-9]{4}\b")
# "Av." y "C/" no encajan con \\b por el punto y la barra: se listan aparte. Las
# formas catalanas/valencianas (Placa, Carrer) salen en webs de Girona y Alicante.
RE_VIA = re.compile(
    r"(\bcalle\b|\bc/|\bc\.\s|\bavenida\b|\bavda\b|\bav\.|\bavd\b|\bplaza\b|\bpza\b|"
    r"\bplaca\b|\bpla[cç]a\b|\bcarrer\b|\bpaseo\b|\bpasaje\b|\bpje\b|\bcamino\b|"
    r"\bcarretera\b|\bctra\b|\bpoligono\b|\bparcela\b|\bronda\b|\brambla\b|"
    r"\btravesia\b|\burbanizacion\b|\bbarrio\b|\bedificio\b|\bgran via\b|\bvia\b|"
    r"\bcallejon\b|\bbulevar\b|\bsector\b|\bpartida\b|\bnave\b)", re.I)
# "Doctor Maranon 22, 03600 ...": nombre propio de via + numero, sin la palabra.
RE_PORTAL = re.compile(r"[A-ZÁÉÍÓÚÑ][\wáéíóúñ.]+(?:\s+[\wáéíóúñ.]+){0,3},?\s+\d{1,4}\s*[,ºª]")
RE_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")
RE_TEL = re.compile(r"(?:\+?34[\s.-]?)?[6789][0-9]{2}[\s.-]?[0-9]{3}[\s.-]?[0-9]{3}\b")

FAMILIAS = {
    "tecnicas": ("tecnica", "funcional", "necesaria", "esencial"),
    "analiticas": ("analitica", "estadistica", "analisis", "rendimiento", "medicion"),
    "publicidad": ("publicidad", "publicitaria", "marketing", "seguimiento",
                   "comportamental", "comportamiento"),
    "preferencias": ("preferencia", "personalizacion"),
}
RE_FINALIDAD = re.compile(r"\b(finalidad|funcion|proposito|para que sirve|se utilizan para)\b")
RE_PLAZO = re.compile(
    r"\b(caducidad|expiracion|expira|plazo de conservacion|conservacion|duracion|"
    r"vigencia|persistencia|vencimiento)\b")
RE_VALOR_TEMPORAL = re.compile(
    r"\b(\d+\s*(?:minuto|hora|dia|dias|semana|mes|meses|ano|anos|year|years|day|days|"
    r"month|months|hour|hours|minute|minutes)|sesion|session|persistente|permanente)\b")
PLACEHOLDERS = ("proposito pendiente de investigacion", "purpose pending investigation",
                "pendiente de investigacion", "lorem ipsum", "[nombre", "xxxxx",
                "tu empresa", "nombre de la empresa", "[razon social")


# host de tercero -> como se llama en la politica. Se anadio el 2026-08-26: el auditor
# comprobaba que apareciesen las palabras "propias" y "terceros", no que lo declarado
# fuese CIERTO, y una web que afirmaba no instalar cookies de terceros mientras cargaba
# Google Analytics le salia en verde.
PROVEEDORES = {
    "googletagmanager.com": "Google Analytics", "google-analytics.com": "Google Analytics",
    "fonts.googleapis.com": "Google Fonts", "fonts.gstatic.com": "Google Fonts",
    "maps.googleapis.com": "Google Maps", "maps.google.com": "Google Maps",
    "google.com/maps": "Google Maps", "googleads.g.doubleclick.net": "Google Ads",
    "doubleclick.net": "Google Ads", "googleadservices.com": "Google Ads",
    "translate.google.com": "Google Translate", "static.addtoany.com": "AddToAny",
    "addtoany.com": "AddToAny", "youtube.com": "YouTube", "youtu.be": "YouTube",
    "player.vimeo.com": "Vimeo", "instagram.com": "Instagram",
    "connect.facebook.net": "Meta", "facebook.net": "Meta",
    # El pixel se sirve como <img src="facebook.com/tr?id=...">, no desde connect.facebook.net:
    # sin esta entrada, una web con pixel figuraba como que no cargaba Meta (caso real medido).
    "facebook.com/tr": "Meta",
    "cdn.trustindex.io": "Trustindex", "widget.intercom.io": "Intercom",
    "intercom.io": "Intercom", "paypal.com": "PayPal", "redsys.es": "Redsys",
    "cdn.jsdelivr.net": "jsDelivr", "hcaptcha.com": "hCaptcha",
    "google.com/recaptcha": "reCAPTCHA", "gstatic.com/recaptcha": "reCAPTCHA",
    "mxpnl.com": "Mixpanel", "usetiful.com": "Usetiful",
}
RE_RECURSO = re.compile(r'(?:src|href)=["\']([^"\']+)["\']', re.I)

# Terceros que NO se ven midiendo el HTML porque su peticion se dispara al INTERACTUAR:
# el plugin sirve un script local y solo llama a su proveedor cuando el visitante pulsa.
# Se detectan por la huella del plugin. Caso real observado el 2026-08-28: GTranslate
# aparecia solo como `/plugins/gtranslate/js/flags.js`, y `translate.google` y la cookie
# `googtrans` no salian por ningun lado; el check daba verde con el tercero sin declarar,
# y lo mismo pasaba en varias webs mas del catalogo.
# Cada entrada: ruta del plugin -> (tercero, señales de que ESTA CORRIENDO). La ruta sola
# no basta: un plugin desactivado deja rastro (una ruta dentro de un CSS de otro, un resto de
# caché) y declararlo meteria un tercero falso en un documento legal del cliente. Medido el
# 2026-08-28: las webs con GTranslate activo imprimen `gtranslate_wrapper` y 3 veces
# `gtranslateSettings`; una con el plugin instalado pero apagado deja 1 mención suelta y nada más.
PLUGINS_DIFERIDOS = {
    "/plugins/gtranslate/": ("Google Translate", ("gtranslateSettings", "gtranslate_wrapper")),
    "/plugins/wp-google-maps/": ("Google Maps", ("wpgmza",)),
    "/plugins/wp-youtube-lyte/": ("YouTube", ("lyte-wrapper", "lyMe")),
    "/plugins/lazy-load-for-videos/": ("YouTube", ("lazy-load-youtube", "preview-youtube")),
    "/plugins/wp-recaptcha-integration/": ("reCAPTCHA", ("g-recaptcha",)),
    # Las pasarelas son de la misma familia: el plugin sirve su JS desde el propio dominio
    # y la llamada al proveedor sale al ir al pago. Medido en una tienda real (2026-08-28).
    "/plugins/pymntpl-paypal-woocommerce/": ("PayPal", ("wc-ppcp", "ppcp")),
    "/plugins/woocommerce-paypal-payments/": ("PayPal", ("ppcp", "paypal-button")),
    "/plugins/woocommerce-gateway-stripe/": ("Stripe", ("wc-stripe", "stripe-elements")),
    "/plugins/woo-redsys-gateway/": ("Redsys", ("redsys",)),
}


def proveedores_diferidos(html):
    """Terceros que solo se piden al pulsar. Devuelve (confirmados, dudosos):
    confirmados = [(tercero, plugin)] con señal de que el plugin corre;
    dudosos = [(tercero, plugin)] con la ruta presente pero sin señal — no se declaran."""
    confirmados, dudosos = [], []
    for huella, (nombre, señales) in PLUGINS_DIFERIDOS.items():
        if huella not in html:
            continue
        plugin = huella.strip("/").split("/")[-1]
        destino = confirmados if any(s in html for s in señales) else dudosos
        if nombre not in [n for n, _ in destino]:
            destino.append((nombre, plugin))
    return confirmados, dudosos



RE_ID_GA4 = re.compile(r"gtag/js\?id=G-([A-Z0-9]+)", re.I)


def proveedores_cargados(html, dominio):
    """Terceros que la pagina CARGA de verdad. Solo cuentan las etiquetas que traen un
    recurso: un <a href="instagram.com/..."> del pie es un enlace, no un embed, y no
    instala ninguna cookie (declararlo como tercero es tan falso como omitirlo)."""
    sopa = BeautifulSoup(html, "html.parser")
    recursos = []
    for etiqueta, atributo in (("script", "src"), ("link", "href"), ("iframe", "src"),
                               ("img", "src"), ("embed", "src"), ("object", "data")):
        recursos += [n.get(atributo, "") for n in sopa.find_all(etiqueta) if n.get(atributo)]
    # Un recurso aplazado sigue siendo un tercero: el cookie-blocker de Complianz guarda la
    # URL real en `data-src-cmplz` y los lazy-loaders en `data-src`/`data-lazy-src`, asi que
    # mirando solo `src` un mapa incrustado parece no existir. Medido el 2026-08-28 en
    # una web real, donde el mapa incrustado viajaba en `data-src-cmplz` y no se declaraba.
    for aplazado in ("data-src-cmplz", "data-src", "data-lazy-src", "data-cmplz-src"):
        recursos += [n.get(aplazado, "") for n in sopa.find_all(attrs={aplazado: True})]
    # Google Fonts se carga a menudo con un `@import` DENTRO de un <style>, no con un <link>:
    # cualquier deteccion basada en hojas de estilo enlazadas se lo salta, y Fonts es el
    # tercero mas comun del parque y de los que no depositan cookies (doblemente invisible).
    for estilo in sopa.find_all("style"):
        recursos += re.findall(r"@import\s+(?:url\()?[\"']?(https?://[^\"')\s]+)",
                               estilo.get_text() or "")
    # Complianz etiqueta el servicio por su nombre, pero SOLO vale si ese nodo incrusta algo:
    # la propia pagina de cookies pinta un panel con `data-service` de TODOS los servicios que
    # el plugin conoce (un <label> por cada uno), y contarlos daria por cargado medio catalogo.
    # Se exige que el nodo lleve ademas la URL aplazada del recurso.
    for nodo in sopa.find_all(attrs={"data-service": True}):
        if not any(nodo.get(a) for a in ("data-src-cmplz", "data-cmplz-src", "data-src",
                                         "data-cmplz-target", "src")):
            continue
        servicio = (nodo.get("data-service") or "").replace("-", " ").strip().lower()
        for nombre in set(PROVEEDORES.values()):
            if servicio and servicio == nombre.lower():
                recursos.append(f"https://{[h for h, v in PROVEEDORES.items() if v == nombre][0]}/")
    vistos = []
    for recurso in recursos:
        # Se compara el HOST, no la cadena: el pixel de Meta lleva el dominio propio dentro
        # de un parametro (`cd[event_url]=<dominio>.com%2F`), y buscarlo como subcadena
        # hacia pasar por propio un recurso de un tercero. Medido el 2026-08-28.
        anfitrion = urlparse(recurso if "//" in recurso else "//" + recurso).netloc
        if dominio and anfitrion and dominio in anfitrion:
            continue
        for host, nombre in PROVEEDORES.items():
            if host in recurso and nombre not in vistos:
                vistos.append(nombre)
    # Analytics suele inyectarse por un script inline que crea la etiqueta al vuelo, asi que
    # su host no aparece en ningun `src` del HTML servido. El ID `G-XXXX` del gtag si.
    if "Google Analytics" not in vistos and RE_ID_GA4.search(html):
        vistos.append("Google Analytics")
    return vistos


def revisa_id_analytics(html, texto_cookies):
    """El comodin `_ga_*` no vale: el Kit Digital pide la cookie que se instala de verdad,
    y su nombre lleva el ID de la propiedad (una web declaraba el comodín en vez del ID real)."""
    ids = sorted(set(RE_ID_GA4.findall(html)))
    if not ids:
        return None
    faltan = [i for i in ids if f"_ga_{i}" not in texto_cookies]
    if faltan:
        return ficha("id_analytics", "falla",
                     "la politica no nombra la cookie real de medicion: "
                     + ", ".join(f"_ga_{i}" for i in faltan))
    return ficha("id_analytics", "pasa", ", ".join(f"_ga_{i}" for i in ids))


def revisa_terceros_de_mas(html_ampliado, dominio, sopa_cookies):
    """El reverso de `terceros_reales`: cookies declaradas como de un tercero que la web
    NO carga. Declarar de mas no es inocuo — es afirmar algo falso en un documento legal.
    Caso real (2026-08-28): un patron sin ancla de fin hizo que las siete `sbjs_*` de
    WooCommerce salieran como cookies de Meta, y el comprobador daba 13/13 igual.

    Solo mira la TABLA, nunca el texto: la politica enlaza legitimamente a las paginas de
    privacidad de YouTube o Instagram sin que la web cargue nada de ellos.
    """
    declarados = set()
    for tabla in sopa_cookies.find_all("table"):
        for celda in tabla.find_all("td"):
            hallado = re.search(r"[Dd]e terceros \(([^)]+)\)", celda.get_text(" "))
            if hallado:
                declarados.add(hallado.group(1).strip())
    if not declarados:
        return None
    cargados = set(proveedores_cargados(html_ampliado, dominio))
    cargados |= {n for n, _ in proveedores_diferidos(html_ampliado)[0]}
    sobran = sorted(d for d in declarados
                    if d not in cargados and sin_acentos(d) not in sin_acentos(" ".join(cargados)))
    if not sobran:
        return ficha("terceros_de_mas", "pasa",
                     "no declara terceros que no cargue: " + ", ".join(sorted(declarados)))
    return ficha("terceros_de_mas", "avisa",
                 "declara cookies de " + ", ".join(sobran) + " y no se ha medido que la web "
                 "los cargue (puede ser correcto si solo aparecen en tienda, pago o una "
                 "pagina no revisada: comprobarlo antes de darlo por bueno)")


def revisa_terceros_reales(html_home, dominio, texto_cookies):
    """El check que faltaba: cruzar lo que la web carga contra lo que su politica declara.
    Cuenta dos familias: los que se ven en una etiqueta con recurso, y los que solo se
    disparan al pulsar (ver PLUGINS_DIFERIDOS) — estos ultimos pasaban invisibles."""
    cargados = proveedores_cargados(html_home, dominio)
    confirmados, dudosos = proveedores_diferidos(html_home)
    diferidos = [(n, h) for n, h in confirmados if n not in cargados]
    todos = cargados + [n for n, _ in diferidos]
    nota = ""
    if dudosos:
        nota = ("; huella debil, sin señal de que el plugin corra (no se declara): "
                + ", ".join(f"{n} ({h})" for n, h in dudosos if n not in todos))
        nota = "" if nota.endswith(": ") else nota
    if not todos:
        return ficha("terceros_reales", "pasa",
                     "el home no carga recursos de terceros conocidos" + nota)
    plano = sin_acentos(texto_cookies)
    faltan = [n for n in todos if sin_acentos(n) not in plano]
    if faltan:
        motivo = {n: h for n, h in diferidos}
        detalle = ", ".join(f"{n} (plugin {motivo[n]}, se dispara al pulsar)" if n in motivo else n
                            for n in faltan)
        return ficha("terceros_reales", "falla",
                     f"la web carga {detalle} y su politica no lo nombra "
                     f"(detectados: {', '.join(todos)}){nota}")
    return ficha("terceros_reales", "pasa",
                 "declara los terceros que carga: " + ", ".join(todos) + nota)


def sin_acentos(texto):
    """Las busquedas por palabra clave no pueden depender de la tilde."""
    normal = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in normal if not unicodedata.combining(c)).lower()


def ficha(clave, estado, evidencia):
    return {"clave": clave, "estado": estado, "evidencia": evidencia[:200]}


def descarga(url, tiempo, con_url_final=False):
    respuesta = requests.get(url, timeout=tiempo, allow_redirects=True,
                             headers={"User-Agent": UA})
    respuesta.raise_for_status()
    return (respuesta.text, respuesta.url) if con_url_final else respuesta.text


def texto_de(html):
    sopa = BeautifulSoup(html, "html.parser")
    for basura in sopa(["script", "style", "noscript"]):
        basura.decompose()
    return re.sub(r"\s+", " ", sopa.get_text(" ")).strip(), sopa


def enlaces_legales(html, base):
    """Que enlaza el home: la LSSI exige acceso permanente y directo."""
    sopa = BeautifulSoup(html, "html.parser")
    dominio = urlparse(base).netloc
    hallado = {}
    for ancla in sopa.find_all("a", href=True):
        url = urljoin(base, ancla["href"])
        if urlparse(url).netloc != dominio:
            continue
        pista = sin_acentos(ancla.get_text(" ") + " " + url)
        if "cookie" in pista:
            hallado.setdefault("cookies", url)
        elif "privacidad" in pista or "privacy" in pista:
            hallado.setdefault("privacidad", url)
        elif "aviso legal" in pista or "aviso-legal" in pista or re.search(
                r"/legal/?$", url):
            hallado.setdefault("aviso_legal", url)
    return hallado


def completa_por_rutas(base, hallado, tiempo):
    for tipo, rutas in RUTAS_CANDIDATAS.items():
        if tipo in hallado:
            continue
        for ruta in rutas:
            url = urljoin(base, ruta + "/")
            try:
                respuesta = requests.get(url, timeout=tiempo, allow_redirects=True,
                                         headers={"User-Agent": UA})
            except requests.RequestException:
                continue
            if respuesta.status_code == 200:
                hallado[tipo] = respuesta.url
                break
    return hallado


def revisa_aviso(texto, razon_social):
    checks = []
    plano = sin_acentos(texto)

    forma = RE_FORMA.search(texto)
    nombre_persona = None
    for etiqueta in RE_ETIQUETA_TITULAR.finditer(texto):
        ventana = texto[etiqueta.end():etiqueta.end() + 120]
        persona = RE_TRES_PALABRAS.search(ventana)
        if persona:
            nombre_persona = persona.group(0)
            break
    if forma:
        checks.append(ficha("denominacion_social", "pasa",
                            f"{forma.group(1)} {forma.group(2)}"))
    elif nombre_persona:
        checks.append(ficha("denominacion_social", "pasa",
                            f"persona fisica: {nombre_persona}"))
    else:
        checks.append(ficha("denominacion_social", "falla",
                            "no consta denominacion social completa: ni forma juridica "
                            "(S.L./S.A./C.B....) ni nombre y apellidos del titular"))

    if razon_social:
        esperada = sin_acentos(re.sub(r"[\s.]+", " ", razon_social)).strip()
        visto = re.sub(r"[\s.]+", " ", plano)
        if esperada not in visto:
            checks.append(ficha("razon_social_literal", "falla",
                                f"no aparece literal: {razon_social}"))
        else:
            checks.append(ficha("razon_social_literal", "pasa", razon_social))

    nif = RE_NIF.search(texto)
    if not nif:
        checks.append(ficha("nif_cif", "falla", "no consta NIF/CIF del titular"))
    elif RE_ETIQUETA_NIF.search(texto):
        checks.append(ficha("nif_cif", "pasa", nif.group(0)))
    else:
        checks.append(ficha("nif_cif", "avisa",
                            f"aparece {nif.group(0)} pero sin la etiqueta NIF/CIF"))

    cp, via = RE_CP.search(texto), RE_VIA.search(sin_acentos(texto))
    # El articulo 10 pide el domicilio, no la palabra "Calle": "Doctor Maranon 22, 1.o B,
    # 03600 Elda" identifica el lugar igual de bien. Basta nombre de via + numero + CP.
    portal = RE_PORTAL.search(texto)
    if cp and (via or portal):
        # La evidencia se recorta alrededor del codigo postal, no de la primera via que
        # aparezca en la pagina: si no, el check pasa por un motivo y enseña otro.
        ini = max(0, cp.start() - 70)
        checks.append(ficha("domicilio", "pasa",
                            re.sub(r"\s+", " ", texto[ini:cp.end() + 30]).strip()))
    else:
        falta = "codigo postal" if not cp else "via y numero"
        checks.append(ficha("domicilio", "falla", f"domicilio incompleto: falta {falta}"))

    correo, tel = RE_EMAIL.search(texto), RE_TEL.search(texto)
    if correo or tel:
        checks.append(ficha("contacto_directo", "pasa",
                            correo.group(0) if correo else tel.group(0)))
    else:
        checks.append(ficha("contacto_directo", "falla",
                            "sin email ni telefono de contacto directo"))
    return checks


def revisa_cookies(texto, sopa):
    checks = []
    plano = sin_acentos(texto)

    familias = [n for n, claves in FAMILIAS.items() if any(c in plano for c in claves)]
    if len(familias) >= 2:
        checks.append(ficha("tipos", "pasa", ", ".join(familias)))
    else:
        checks.append(ficha("tipos", "falla",
                            f"solo {len(familias)} familia(s) de cookies descritas: "
                            f"{', '.join(familias) or 'ninguna'}"))

    menciones = len(RE_FINALIDAD.findall(plano))
    filas = max((len(t.find_all("tr")) for t in sopa.find_all("table")), default=0)
    if menciones >= 3 or filas >= 3:
        checks.append(ficha("finalidad", "pasa",
                            f"{menciones} menciones de finalidad/funcion, tabla mayor: {filas} filas"))
    elif menciones:
        checks.append(ficha("finalidad", "falla",
                            f"la finalidad se menciona {menciones} vez/veces pero no hay "
                            "descripcion por cookie (ni 3 menciones ni tabla de 3 filas)"))
    else:
        checks.append(ficha("finalidad", "falla", "no se declara la finalidad de las cookies"))

    # El detalle POR COOKIE es lo que pide el Kit Digital, y la prosa no lo sustituye:
    # `finalidad` daba verde con 11 menciones genericas y CERO filas de tabla. Se midio el
    # 2026-08-28, cuando reescribir el bloque sin `--tabla` borro la tabla de una web y el
    # comprobador siguio diciendo 11/11.
    if re.search(r"no instala ninguna cookie|no utiliza cookies\b", plano):
        checks.append(ficha("detalle_por_cookie", "pasa",
                            "declara que la web no instala ninguna cookie"))
    elif filas >= 3:
        checks.append(ficha("detalle_por_cookie", "pasa",
                            f"tabla de cookies con {filas} filas"))
    else:
        checks.append(ficha("detalle_por_cookie", "falla",
                            f"sin tabla de cookies con su nombre, finalidad y plazo "
                            f"(tabla mayor: {filas} filas)"))

    propias = re.search(r"\bpropia", plano)
    terceros = re.search(r"\btercero", plano)
    if propias and terceros:
        checks.append(ficha("propias_terceros", "pasa", "distingue propias y de terceros"))
    else:
        falta = "propias" if not propias else "de terceros"
        checks.append(ficha("propias_terceros", "falla",
                            f"no identifica las cookies {falta}"))

    # Una web sin cookies no tiene plazo que declarar: exigirselo es exigir un dato falso.
    if re.search(r"no instala ninguna cookie|no utiliza cookies\b", plano):
        checks.append(ficha("plazo_conservacion", "pasa",
                            "declara que la web no instala ninguna cookie"))
        checks.append(ficha("sin_placeholder", "pasa", "sin marcadores del generador"))
        return checks
    valores = set(RE_VALOR_TEMPORAL.findall(plano))
    if RE_PLAZO.search(plano) and len(valores) >= 2:
        checks.append(ficha("plazo_conservacion", "pasa",
                            f"{len(valores)} plazos distintos declarados"))
    else:
        checks.append(ficha("plazo_conservacion", "falla",
                            f"sin plazo de conservacion/caducidad util "
                            f"(termino={bool(RE_PLAZO.search(plano))}, valores={len(valores)})"))

    sucios = [(p, plano.count(p)) for p in PLACEHOLDERS if p in plano]
    if sucios:
        detalle = ", ".join(f"'{p}' x{n}" for p, n in sucios)
        checks.append(ficha("sin_placeholder", "falla",
                            f"texto del generador sin rellenar: {detalle}"))
    else:
        checks.append(ficha("sin_placeholder", "pasa", "sin marcadores del generador"))
    return checks


def audita(base, tiempo, razon_social):
    resultado = {"paginas": {}, "checks": []}
    try:
        home, url_final = descarga(base, tiempo, con_url_final=True)
        # Si el dominio redirige (ejemplo.com -> www.ejemplo.com), el home que se lee ya es el del
        # destino, pero `base` seguia siendo el de origen: `enlaces_legales` descarta por netloc
        # distinto y el resultado era "el home no enlaza aviso legal ni cookies" en una web que
        # SI los enlaza. Se adopta el dominio final, que es el canonico.
        if urlparse(url_final).netloc != urlparse(base).netloc:
            base = url_final if url_final.endswith("/") else url_final + "/"
    except requests.RequestException as error:
        resultado["checks"].append(ficha("descarga", "falla", str(error)[:120]))
        return resultado

    paginas = completa_por_rutas(base, enlaces_legales(home, base), tiempo)
    resultado["paginas"] = paginas

    # El mapa de contacto, el captcha del formulario y la pasarela viven en paginas
    # interiores: mirar solo el home deja fuera la mitad de los terceros (caso real medido).
    html_ampliado = home
    for interior in ("contacto", "contact", "contacto-2"):
        try:
            html_ampliado += descarga(urljoin(base, interior + "/"), tiempo)
            break
        except requests.RequestException:
            continue

    enlazadas = enlaces_legales(home, base)
    faltan = [t for t in ("aviso_legal", "cookies") if t not in enlazadas]
    if faltan:
        resultado["checks"].append(ficha(
            "enlaces_footer", "falla",
            f"el home no enlaza: {', '.join(faltan)} (la LSSI exige acceso permanente y directo)"))
    else:
        resultado["checks"].append(ficha("enlaces_footer", "pasa",
                                         "home enlaza aviso legal y cookies"))

    for tipo, revisor in (("aviso_legal", revisa_aviso), ("cookies", revisa_cookies)):
        url = paginas.get(tipo)
        if not url:
            resultado["checks"].append(ficha(
                f"pagina_ausente_{tipo}", "falla", f"no existe la pagina de {tipo}"))
            continue
        try:
            texto, sopa = texto_de(descarga(url, tiempo))
        except requests.RequestException as error:
            resultado["checks"].append(ficha(f"descarga_{tipo}", "falla", str(error)[:120]))
            continue
        if tipo == "aviso_legal":
            resultado["checks"].extend(revisa_aviso(texto, razon_social))
        else:
            resultado["checks"].extend(revisa_cookies(texto, sopa))
            resultado["checks"].append(
                revisa_terceros_reales(html_ampliado, urlparse(base).netloc, texto))
            ficha_mas = revisa_terceros_de_mas(html_ampliado, urlparse(base).netloc, sopa)
            if ficha_mas:
                resultado["checks"].append(ficha_mas)
            ficha_id = revisa_id_analytics(html_ampliado, texto)
            if ficha_id:
                resultado["checks"].append(ficha_id)
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("bases", nargs="+", help="URL raiz de cada web publicada")
    parser.add_argument("--json", dest="salida", help="escribe el informe completo ahi")
    parser.add_argument("--razon-social", help="denominacion social que debe aparecer literal")
    parser.add_argument("--tiempo", type=int, default=20, help="timeout HTTP por peticion")
    args = parser.parse_args()

    informe = {"generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "webs": {}}
    hubo_falla = hubo_red = False

    for base in args.bases:
        base = base if base.endswith("/") else base + "/"
        slug = urlparse(base).netloc or base
        datos = audita(base, args.tiempo, args.razon_social)
        cuenta = {"pasa": 0, "avisa": 0, "falla": 0}
        print(f"\n== {slug}  paginas: " +
              ", ".join(f"{k}={v}" for k, v in datos["paginas"].items()) or "(ninguna)")
        for check in datos["checks"]:
            cuenta[check["estado"]] += 1
            print(f"{slug}  {check['clave']:<26} {check['estado'].upper():<6} {check['evidencia']}")
        datos["resumen"] = cuenta
        informe["webs"][base] = datos
        print(f"{slug}: {cuenta['pasa']} pasa, {cuenta['avisa']} avisa, {cuenta['falla']} falla")
        if cuenta["falla"]:
            hubo_falla = True
            if any(c["clave"].startswith("descarga") for c in datos["checks"]):
                hubo_red = True

    if args.salida:
        with open(args.salida, "w", encoding="utf-8") as fichero:
            json.dump(informe, fichero, indent=1, ensure_ascii=False)
        print(f"\nInforme -> {args.salida}")

    solo_red = hubo_red and all(
        all(c["clave"].startswith("descarga") for c in d["checks"] if c["estado"] == "falla")
        for d in informe["webs"].values())
    return 2 if solo_red else (1 if hubo_falla else 0)


if __name__ == "__main__":
    sys.exit(main())
