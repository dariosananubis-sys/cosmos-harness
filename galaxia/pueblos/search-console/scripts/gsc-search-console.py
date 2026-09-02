"""Google Search Console + Site Verification.

Auth: Service Account JSON. Scopes: webmasters + siteverification.

Doc:
- https://developers.google.com/webmaster-tools/v1
- https://developers.google.com/site-verification/v1

Requiere GSC_SERVICE_ACCOUNT_JSON en el entorno (ruta al JSON de la cuenta de
servicio, con esas dos APIs habilitadas en su proyecto GCP).

Uso CLI:
    python -m gsc-search-console add-property <site-url>
    python -m gsc-search-console get-token <site-url>      # devuelve <meta name="google-site-verification" content="...">
    python -m gsc-search-console verify <site-url>          # tras inyectar el meta vía wp-cli u otro medio
    python -m gsc-search-console submit-sitemap <site-url> <sitemap-url>
    python -m gsc-search-console inspect-url <site-url> <inspection-url>

site-url puede ser:
    - URL prefix:   https://ejemplo.es/
    - Domain:       sc-domain:ejemplo.es

Requiere: httpx, typer, python-dotenv, google-api-python-client, google-auth.
"""

from __future__ import annotations

import os
import sys

import typer
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

from log import api_call, fail, info, ok, step

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/siteverification",
]

app = typer.Typer(no_args_is_help=True)


def _credentials() -> service_account.Credentials:
    sa_path = os.environ.get("GSC_SERVICE_ACCOUNT_JSON")
    if not sa_path:
        fail("GSC_SERVICE_ACCOUNT_JSON no definido en el entorno")
        sys.exit(1)
    if not os.path.exists(sa_path):
        fail(f"Service Account JSON no existe: {sa_path}")
        sys.exit(1)
    return service_account.Credentials.from_service_account_file(sa_path, scopes=SCOPES)


def _sc_service():
    return build("searchconsole", "v1", credentials=_credentials(), cache_discovery=False)


def _sv_service():
    return build("siteVerification", "v1", credentials=_credentials(), cache_discovery=False)


# ─── Operaciones ──────────────────────────────────────────────────────────


def add_property(site_url: str) -> dict:
    """PUT /sites/{siteUrl} — alta propiedad."""
    api_call("PUT", f"searchconsole/sites/{site_url}")
    svc = _sc_service()
    svc.sites().add(siteUrl=site_url).execute()
    return {"siteUrl": site_url, "status": "added"}


def list_properties() -> list[dict]:
    return _sc_service().sites().list().execute().get("siteEntry", [])


def get_meta_token(site_url: str) -> str:
    """siteVerification.webResource.getToken (META). Devuelve <meta ...> completo."""
    api_call("POST", "siteVerification/v1/token")
    body = {
        "verificationMethod": "META",
        "site": {"type": "SITE", "identifier": site_url},
    }
    resp = _sv_service().webResource().getToken(body=body).execute()
    return resp["token"]


def verify_meta(site_url: str) -> dict:
    """siteVerification.webResource.insert — tras inyectar meta en <head>."""
    api_call("POST", "siteVerification/v1/webResource?verificationMethod=META")
    body = {"site": {"type": "SITE", "identifier": site_url}}
    return _sv_service().webResource().insert(verificationMethod="META", body=body).execute()


def submit_sitemap(site_url: str, sitemap_url: str) -> dict:
    api_call("PUT", f"searchconsole/sites/{site_url}/sitemaps/{sitemap_url}")
    _sc_service().sitemaps().submit(siteUrl=site_url, feedpath=sitemap_url).execute()
    return {"siteUrl": site_url, "sitemap": sitemap_url, "status": "submitted"}


def inspect_url(site_url: str, inspection_url: str, language_code: str = "es-ES") -> dict:
    api_call("POST", "searchconsole/v1/urlInspection/index:inspect")
    body = {
        "inspectionUrl": inspection_url,
        "siteUrl": site_url,
        "languageCode": language_code,
    }
    return _sc_service().urlInspection().index().inspect(body=body).execute()


# ─── CLI ────────────────────────────────────────────────────────────────────


@app.command(name="list")
def cmd_list() -> None:
    """Lista propiedades visibles para el Service Account."""
    step("Listando propiedades GSC")
    sites = list_properties()
    for s in sites:
        info(f"  · {s.get('siteUrl')} ({s.get('permissionLevel')})")
    ok(f"{len(sites)} propiedades")


@app.command(name="add-property")
def cmd_add(site_url: str) -> None:
    """Alta de propiedad GSC."""
    step(f"Alta propiedad {site_url}")
    add_property(site_url)
    ok(f"Propiedad añadida: {site_url}")


@app.command(name="get-token")
def cmd_get_token(site_url: str) -> None:
    """Devuelve el meta tag para inyectar en <head>."""
    step(f"Solicitando meta token para {site_url}")
    token = get_meta_token(site_url)
    ok("Meta tag obtenido:")
    print(token)


@app.command()
def verify(site_url: str) -> None:
    """Verifica propiedad (META). Requiere meta ya inyectado en <head>."""
    step(f"Verificando {site_url}")
    result = verify_meta(site_url)
    ok(f"Verificado: {result.get('site', {}).get('identifier')}")


@app.command(name="submit-sitemap")
def cmd_submit_sitemap(site_url: str, sitemap_url: str) -> None:
    step(f"Submit sitemap {sitemap_url} → {site_url}")
    submit_sitemap(site_url, sitemap_url)
    ok("Sitemap enviado")


@app.command(name="inspect-url")
def cmd_inspect(site_url: str, inspection_url: str) -> None:
    """Inspecciona una URL (verdict + coverage)."""
    step(f"Inspect {inspection_url}")
    result = inspect_url(site_url, inspection_url)
    idx = result.get("inspectionResult", {}).get("indexStatusResult", {})
    verdict = idx.get("verdict", "UNKNOWN")
    coverage = idx.get("coverageState", "?")
    canonical = idx.get("googleCanonical", "?")
    ok(f"verdict={verdict} coverage={coverage} canonical={canonical}")


if __name__ == "__main__":
    app()
