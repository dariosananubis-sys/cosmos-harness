"""Bing Webmaster Tools API — REST JSON.

Doc: https://learn.microsoft.com/en-us/bingwebmaster/getting-started
Auth: ?apikey=<KEY> en query string. Una key por cuenta Bing.

Endpoints cubiertos:
- AddSite, VerifySite, SubmitFeed, SubmitUrl, GetUrlInfo, GetUrlSubmissionQuota.

Verificación: Bing NO expone getToken como Google. El meta `msvalidate.01` se
obtiene una vez en la UI de Bing Webmaster Tools y se guarda en BING_META_TOKEN
(entorno) o donde prefieras. Alternativa: importar verificación desde GSC en la
UI (one-shot manual).

Requiere BING_API_KEY en el entorno.

Uso CLI:
    python -m bing-webmaster ping
    python -m bing-webmaster add-site https://ejemplo.es/
    python -m bing-webmaster verify https://ejemplo.es/        # tras inyectar meta msvalidate.01
    python -m bing-webmaster submit-feed https://ejemplo.es/ https://ejemplo.es/sitemap_index.xml
    python -m bing-webmaster submit-url https://ejemplo.es/ https://ejemplo.es/contacto/
    python -m bing-webmaster quota https://ejemplo.es/
    python -m bing-webmaster url-info https://ejemplo.es/ https://ejemplo.es/contacto/
"""

from __future__ import annotations

import os
import re
import sys

import httpx
import typer
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

from log import api_call, api_response, fail, info, ok, step

load_dotenv()

API_BASE = "https://ssl.bing.com/webmaster/api.svc/json"

app = typer.Typer(no_args_is_help=True)


def _api_key() -> str:
    key = os.environ.get("BING_API_KEY")
    if not key:
        fail("BING_API_KEY no definida en el entorno")
        sys.exit(1)
    return key


def meta_content() -> str:
    """Devuelve el content del meta `msvalidate.01` (constante por cuenta Bing).

    Fuente: variable de entorno BING_META_TOKEN. Si el valor guardado es el
    `<meta ... />` completo (no solo el hex), extrae el `content`.
    """
    raw = (os.environ.get("BING_META_TOKEN") or "").strip()
    if not raw:
        fail("BING_META_TOKEN no definida en el entorno (sácala de Bing Webmaster Tools → Settings → Site verification)")
        sys.exit(1)
    m = re.search(r'content=["\']([^"\']+)["\']', raw)
    return m.group(1) if m else raw


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def _post(method: str, payload: dict) -> dict:
    url = f"{API_BASE}/{method}"
    api_call("POST", url, payload)
    with httpx.Client(timeout=30) as c:
        r = c.post(url, params={"apikey": _api_key()}, json=payload)
    api_response(r.status_code, r.text[:200] if r.status_code >= 400 else "")
    r.raise_for_status()
    return r.json() if r.text else {}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def _get(method: str, params: dict) -> dict:
    url = f"{API_BASE}/{method}"
    api_call("GET", url, params)
    full = {"apikey": _api_key(), **params}
    with httpx.Client(timeout=30) as c:
        r = c.get(url, params=full)
    api_response(r.status_code, r.text[:200] if r.status_code >= 400 else "")
    r.raise_for_status()
    return r.json() if r.text else {}


# ─── Operaciones ──────────────────────────────────────────────────────────


class BingApiError(RuntimeError):
    """Bing devolvió 200 OK pero el cuerpo indica fallo (`{"d": false}` o ausente)."""


def _ensure_d_true(body: dict, method: str, site_url: str) -> None:
    """Bing envuelve la respuesta en `{"d": <valor>}` (JSONP-style WCF).

    Para métodos booleanos, `d` debe ser `True`. Si es `False` o falta, fallar
    explícitamente — `r.raise_for_status()` no detecta este caso (HTTP 200).
    """
    d = body.get("d") if isinstance(body, dict) else None
    if d is not True:
        fail(f"✗ {method} NO confirmado para {site_url} (respuesta: {body!r})")
        raise BingApiError(f"{method} fallido para {site_url}: d={d!r}")


def _ensure_void_ok(body: dict, method: str, site_url: str) -> None:
    """Métodos `void` de la API (SubmitFeed, SubmitUrl) devuelven `{"d": null}`
    TAMBIÉN cuando tienen éxito — `d` no confirma ni desmiente nada.

    Solo `d is False` es un rechazo real. Exigir aquí `d is True` produce un falso
    negativo: un sitemap puede estar enviado Y ya rastreado por Bing (GetFeeds lo
    confirma) y aun así reportarse como fallido por leer `d` de más. El veredicto
    de estos métodos se pide al origen (GetFeeds), no al `d` de la respuesta.
    """
    d = body.get("d") if isinstance(body, dict) else None
    if d is False:
        fail(f"✗ {method} rechazado para {site_url} (respuesta: {body!r})")
        raise BingApiError(f"{method} rechazado para {site_url}")


def add_site(site_url: str) -> dict:
    body = _post("AddSite", {"siteUrl": site_url})
    _ensure_d_true(body, "AddSite", site_url)
    return body


def verify_site(site_url: str) -> dict:
    body = _post("VerifySite", {"siteUrl": site_url})
    _ensure_d_true(body, "VerifySite", site_url)
    return body


def submit_feed(site_url: str, feed_url: str) -> dict:
    body = _post("SubmitFeed", {"siteUrl": site_url, "feedUrl": feed_url})
    _ensure_void_ok(body, "SubmitFeed", site_url)
    # El veredicto real: que el feed aparezca listado en la cuenta.
    feeds = _get("GetFeeds", {"siteUrl": site_url}).get("d") or []
    want = feed_url.rstrip("/")
    if not any((f.get("Url") or "").rstrip("/") == want for f in feeds):
        fail(f"✗ SubmitFeed: {feed_url} no aparece en GetFeeds de {site_url}")
        raise BingApiError(f"SubmitFeed no registrado para {site_url}: {feed_url}")
    return body


def submit_url(site_url: str, url: str) -> dict:
    body = _post("SubmitUrl", {"siteUrl": site_url, "url": url})
    _ensure_void_ok(body, "SubmitUrl", site_url)
    return body


def get_url_info(site_url: str, url: str) -> dict:
    return _get("GetUrlInfo", {"siteUrl": site_url, "url": url})


def get_quota(site_url: str) -> dict:
    return _get("GetUrlSubmissionQuota", {"siteUrl": site_url})


# ─── CLI ────────────────────────────────────────────────────────────────────


@app.command()
def ping() -> None:
    """Valida API key listando quota de un site dummy (revela si key es válida)."""
    step("Ping Bing Webmaster (validar API key)")
    info("Si falla 401 → key inválida. Si falla por siteUrl → key OK.")
    try:
        get_quota("https://example.com/")
        ok("API key válida")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            fail("API key inválida (401)")
            sys.exit(1)
        ok(f"API key OK (error esperado por siteUrl dummy: {e.response.status_code})")


@app.command(name="add-site")
def cmd_add_site(site_url: str) -> None:
    step(f"Alta sitio {site_url}")
    add_site(site_url)
    ok("Sitio añadido")


@app.command()
def verify(site_url: str) -> None:
    """Verifica el sitio (requiere msvalidate.01 ya en <head>)."""
    step(f"Verificando {site_url}")
    verify_site(site_url)
    ok("Sitio verificado")


@app.command(name="submit-feed")
def cmd_submit_feed(site_url: str, feed_url: str) -> None:
    step(f"Submit sitemap {feed_url} → {site_url}")
    submit_feed(site_url, feed_url)
    ok("Sitemap enviado")


@app.command(name="submit-url")
def cmd_submit_url(site_url: str, url: str) -> None:
    step(f"Submit URL {url}")
    submit_url(site_url, url)
    ok("URL enviada")


@app.command(name="quota")
def cmd_quota(site_url: str) -> None:
    """Quota disponible para SubmitUrl."""
    step(f"Consultando quota {site_url}")
    q = get_quota(site_url)
    ok(f"Quota: {q}")


@app.command(name="url-info")
def cmd_url_info(site_url: str, url: str) -> None:
    step(f"Url info {url}")
    info_data = get_url_info(site_url, url)
    ok(f"Info: {info_data}")


@app.command(name="meta-content")
def cmd_meta_content() -> None:
    """Imprime el content del meta msvalidate.01 vigente (BING_META_TOKEN)."""
    ok(f"msvalidate.01 = {meta_content()}")


def _smoke_test_ensure_d_true() -> None:
    """Smoke test ad-hoc del validador `_ensure_d_true` (no toca red)."""
    # Caso OK: d=True no lanza.
    _ensure_d_true({"d": True}, "VerifySite", "https://example.com/")

    casos_fallo = [
        {"d": False},          # negación explícita
        {},                    # respuesta vacía
        {"d": None},           # null
        {"otro": True},        # falta clave d
        {"d": "true"},         # string en vez de bool
    ]
    for body in casos_fallo:
        try:
            _ensure_d_true(body, "VerifySite", "https://example.com/")
        except BingApiError:
            continue
        raise AssertionError(f"_ensure_d_true debió fallar con body={body!r}")
    ok("_ensure_d_true smoke test OK")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "_smoke":
        _smoke_test_ensure_d_true()
        sys.exit(0)
    app()
