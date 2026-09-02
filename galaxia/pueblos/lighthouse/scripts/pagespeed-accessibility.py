"""Wrapper PageSpeed Insights API — score de accesibilidad + audits que fallan.

Doc: https://developers.google.com/speed/docs/insights/v5/get-started

Uso CLI:
    python -m pagespeed-accessibility <url> [--strategy desktop|mobile]

Requiere PAGESPEED_API_KEY en el entorno (opcional: sin key funciona con cuota
anónima, muy limitada).
"""

from __future__ import annotations

import os
import sys

import httpx
import typer
from dotenv import load_dotenv

from log import api_call, api_response, fail, info, ok, step

load_dotenv()

API_BASE = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

app = typer.Typer(no_args_is_help=True)


def get_accessibility_score(url: str, strategy: str = "desktop") -> dict:
    """Devuelve dict con score (0-1) + lista de audits que fallan."""
    api_key = os.environ.get("PAGESPEED_API_KEY")
    params = {
        "url": url,
        "category": "accessibility",
        "strategy": strategy.upper(),
    }
    if api_key:
        params["key"] = api_key
    api_call("GET", API_BASE, {"url": url, "strategy": strategy})
    with httpx.Client(timeout=180) as client:
        r = client.get(API_BASE, params=params)
    api_response(r.status_code)
    r.raise_for_status()

    data = r.json()
    lhr = data["lighthouseResult"]
    score = lhr["categories"]["accessibility"]["score"]
    audits = lhr["audits"]

    failures = [
        {
            "id": k,
            "title": v.get("title"),
            "description": v.get("description"),
            "score": v.get("score"),
        }
        for k, v in audits.items()
        if v.get("score") is not None and v["score"] < 1
    ]
    return {"url": url, "strategy": strategy, "score": score, "failures": failures}


@app.command()
def check(
    url: str = typer.Argument(..., help="URL a auditar"),
    strategy: str = typer.Option("desktop", help="desktop | mobile"),
) -> None:
    """Audita una URL contra PageSpeed Insights y muestra score accesibilidad."""
    step(f"PageSpeed Insights — {url} ({strategy})")
    try:
        result = get_accessibility_score(url, strategy)
    except Exception as e:
        fail(f"Error PageSpeed: {e}")
        sys.exit(1)

    score = result["score"]
    pct = int(score * 100) if score is not None else "N/A"
    if score == 1.0:
        ok(f"Accesibilidad {pct}% — pasa")
    else:
        fail(f"Accesibilidad {pct}% — NO llega al 100%")
        for f in result["failures"]:
            info(f"  · {f['id']}: {f['title']}")


if __name__ == "__main__":
    app()
