#!/usr/bin/env python3
"""Registra en Claude Code un MCP de Elementor por cada sitio de ~/.wp-sites/sites.json.

OJO — esto vale para webs SERVIDAS con PHP 8.1+. El plugin EMCP Tools exige esa versión, y
si el vhost va por debajo el endpoint responde 404 aunque el plugin figure activo: no es que
falte la ruta, es que el plugin no llega a cargarse. Ahí el camino bueno es un puente por
STDIO sobre SSH en su lugar (ver wp-mcp-stdio-bridge.sh).
Comprobar antes:  curl -s <url>/wp-json/ | grep -c emcp-tools-server

Las credenciales NUNCA entran en el repo: se registran con `claude mcp add --scope user`,
que escribe en ~/.claude.json (fuera de git).

Uso:
    python3 wp-mcp-sync.py            # lista lo que haría
    python3 wp-mcp-sync.py --aplicar  # lo registra de verdad
    python3 wp-mcp-sync.py --aplicar --solo <id-de-sitio>
"""
import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path

INDICE = Path.home() / ".wp-sites" / "sites.json"
PREFIJO = "elementor-"
PLACEHOLDERS = ("xxxx", "yyyy", "zzzz")


def cargar_sitios():
    if not INDICE.exists():
        sys.exit(f"No existe {INDICE}. Créalo antes de sincronizar.")
    if INDICE.stat().st_mode & 0o077:
        sys.exit(f"{INDICE} tiene permisos abiertos. Corrige con: chmod 600 {INDICE}")
    datos = json.loads(INDICE.read_text(encoding="utf-8"))
    return datos.get("sites", {})


def endpoint_de(sitio):
    """El endpoint declarado, o el derivado de la url del WordPress."""
    declarado = (sitio.get("mcp_endpoint") or "").strip()
    if declarado:
        return declarado
    url = (sitio.get("url") or "").strip().rstrip("/")
    return f"{url}/wp-json/mcp/elementor-mcp-server" if url else ""


def revisar(sitio_id, sitio):
    """Devuelve (endpoint, cabecera) o (None, motivo del descarte)."""
    if sitio_id.startswith("_"):
        return None, "entrada de ejemplo"
    usuario = (sitio.get("username") or "").strip()
    clave = (sitio.get("app_password") or "").strip()
    endpoint = endpoint_de(sitio)
    if not endpoint:
        return None, "sin url ni mcp_endpoint"
    if not usuario or not clave:
        return None, "faltan username o app_password"
    if clave.split()[0].lower() in PLACEHOLDERS:
        return None, "app_password sigue siendo la plantilla"
    if not endpoint.startswith("https://"):
        return None, "endpoint no es https (la app_password viajaría en claro)"
    token = base64.b64encode(f"{usuario}:{clave}".encode()).decode()
    return endpoint, f"Authorization: Basic {token}"


def registrar(nombre, endpoint, cabecera):
    orden = ["claude", "mcp", "add", "--transport", "http", "--scope", "user",
             nombre, endpoint, "--header", cabecera]
    hecho = subprocess.run(orden, capture_output=True, text=True)
    if hecho.returncode != 0:
        return False, (hecho.stderr or hecho.stdout).strip().splitlines()[-1][:160]
    return True, "registrado"


def main():
    trato = argparse.ArgumentParser(description=__doc__)
    trato.add_argument("--aplicar", action="store_true", help="registra de verdad")
    trato.add_argument("--solo", metavar="SITIO", help="solo ese ID de sitio")
    args = trato.parse_args()

    sitios = cargar_sitios()
    if args.solo:
        sitios = {k: v for k, v in sitios.items() if k == args.solo}
        if not sitios:
            sys.exit(f"No hay ningún sitio '{args.solo}' en {INDICE}")

    listos, descartados = [], []
    for sitio_id, sitio in sitios.items():
        endpoint, extra = revisar(sitio_id, sitio)
        if endpoint:
            listos.append((sitio_id, endpoint, extra))
        else:
            descartados.append((sitio_id, extra))

    for sitio_id, motivo in descartados:
        print(f"  omitido  {sitio_id}: {motivo}")

    for sitio_id, endpoint, cabecera in listos:
        nombre = PREFIJO + sitio_id
        if not args.aplicar:
            print(f"  haría    {nombre} -> {endpoint}")
            continue
        ok, detalle = registrar(nombre, endpoint, cabecera)
        print(f"  {'OK      ' if ok else 'FALLO   '} {nombre}: {detalle}")

    if not args.aplicar and listos:
        print(f"\nNada registrado. Repite con --aplicar para dejarlo activo ({len(listos)} sitio/s).")
    if not listos:
        print("\nNingún sitio listo todavía: rellena url, username y app_password reales.")


if __name__ == "__main__":
    main()
