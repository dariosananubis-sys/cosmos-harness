#!/usr/bin/env python3
"""Escribe el bloque LSSI de cookies por la REST API, para las webs sin SSH.

Por que existe: el 2026-08-27, revisando TODAS las webs subidas, tres clientes
(algunos ejemplos) viven en
servidores cuyo SSH no esta en el vault. Si que estan sus credenciales de
WP-ADMIN, asi que se crea una contrasena de aplicacion desde su perfil y se edita
la pagina por `wp-json`. Mismo texto y mismos marcadores que
`legales-bloque-cookies.py`; solo cambia el transporte.

    python3 legales-bloque-rest.py <dominio> --terceros "Google Analytics" \\
        [--tabla "_ga,_ga_XXXX"] [--pagina politica-de-cookies-ue] --aplicar

Las credenciales se leen de un JSON con {"<dominio>": {"base", "user", "app"}},
por defecto `~/.wp-sites/rest.json`. Nunca se escriben en el repo.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("bloque", Path(__file__).resolve().parent / "legales-bloque-cookies.py")
_bloque = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bloque)

RANURAS = ("politica-de-cookies-ue", "politica-de-cookies", "cookies", "politica-cookies",
           "cookie-policy")


def credenciales(dominio, ruta):
    datos = json.loads(Path(ruta).expanduser().read_text(encoding="utf-8"))
    if dominio not in datos:
        raise SystemExit(f"{dominio} no esta en {ruta}: hace falta base, user y app")
    c = datos[dominio]
    return c["base"].rstrip("/"), HTTPBasicAuth(c["user"], c["app"])


def busca_pagina(base, auth, ranuras):
    for ranura in ranuras:
        r = requests.get(f"{base}/wp-json/wp/v2/pages", params={"slug": ranura},
                         auth=auth, timeout=40)
        if r.status_code == 200 and r.json():
            return r.json()[0]
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("dominio")
    parser.add_argument("--terceros", default="")
    parser.add_argument("--tabla", help="cookies medidas, separadas por comas")
    parser.add_argument("--pagina", help="ranura concreta de la pagina")
    parser.add_argument("--credenciales", default="~/.wp-sites/rest.json")
    parser.add_argument("--sustituir-shortcode", action="store_true",
                        help="quita el listado del plugin y deja el bloque con la tabla medida "
                             "(para webs donde no se puede corregir la ficha de cada cookie)")
    parser.add_argument("--aplicar", action="store_true")
    args = parser.parse_args()

    base, auth = credenciales(args.dominio, args.credenciales)
    ranuras = (args.pagina,) + RANURAS if args.pagina else RANURAS
    pagina = busca_pagina(base, auth, ranuras)
    if not pagina:
        raise SystemExit(f"{args.dominio}: no encuentro la pagina de cookies")

    terceros = [t.strip() for t in args.terceros.split(",") if t.strip()]
    nombres = [n.strip() for n in (args.tabla or "").split(",") if n.strip()]
    tabla = _bloque.tabla_html(args.dominio, nombres) if nombres else ""
    bloque = _bloque.bloque_html(args.dominio, terceros, tabla)

    contenido = pagina["content"]["raw"] if "raw" in pagina["content"] else ""
    if not contenido:
        r = requests.get(f"{base}/wp-json/wp/v2/pages/{pagina['id']}", params={"context": "edit"},
                         auth=auth, timeout=40)
        r.raise_for_status()
        contenido = r.json()["content"]["raw"]

    patron = re.compile(re.escape(_bloque.INICIO) + ".*?" + re.escape(_bloque.FIN), re.S)
    if args.sustituir_shortcode:
        # El listado del plugin publica "Proposito pendiente de investigacion" y su ficha solo
        # se corrige desde la base de datos, a la que aqui no se llega. La tabla medida dice
        # lo mismo y sin huecos: se cambia una cosa por la otra.
        sin_bloque = patron.sub("", contenido)
        sin_lista = re.sub(r"\[cmplz-document[^\]]*\]", "", sin_bloque).strip()
        nuevo, accion = sin_lista + "\n\n" + bloque, "SUSTITUIDO EL LISTADO"
    elif patron.search(contenido):
        nuevo, accion = patron.sub(lambda _: bloque, contenido), "ACTUALIZADO"
    elif "[cmplz-document" in contenido:
        corte = contenido.index("[cmplz-document")
        nuevo = contenido[:corte] + bloque + "\n\n" + contenido[corte:]
        accion = "INSERTADO"
    else:
        nuevo, accion = contenido + "\n\n" + bloque, "INSERTADO"

    print(f"{args.dominio}: pagina {pagina['id']} ({pagina['slug']}) · {accion} · "
          f"terceros={terceros or 'ninguno'}")
    if nuevo == contenido:
        print("SIN CAMBIOS")
        return 0
    if not args.aplicar:
        print("(usa --aplicar para escribirlo)")
        return 0

    r = requests.post(f"{base}/wp-json/wp/v2/pages/{pagina['id']}", auth=auth, timeout=60,
                      json={"content": nuevo})
    if r.status_code >= 300:
        raise SystemExit(f"la REST API respondio {r.status_code}: {r.text[:200]}")
    print("escrito")
    return 0


if __name__ == "__main__":
    sys.exit(main())
