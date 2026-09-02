"""Sugeridor determinista de dominios disponibles.

La compra queda fuera de este módulo: aquí solo se valida disponibilidad con
fuentes públicas (NS publicados, whois, RDAP) y se devuelven candidatos ya
comprobados como libres.

Uso: python3 domain-suggester.py <dominio|nombre> [...]
  - Si el argumento tiene un punto, se trata como dominio exacto y se imprime
    LIBRE / PILLADO / ? (incierto).
  - Si no, se trata como base y se imprimen hasta 5 variaciones .es/.com libres.
"""

from __future__ import annotations

import re
import socket
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request

USER_AGENT = "domain-suggester/1.0"
RDAP_TIMEOUT = 15
WHOIS_TIMEOUT = 15

AVAILABLE_MARKERS = (
    "no match",
    "not found",
    "no existe",
    "status: available",
    "is available for registration",
    "domaininfo: free",
)
TAKEN_MARKERS = (
    "registrant",
    "status: active",
    "creation date",
    "fecha de registro",
    "registrar:",
    "holder",
)


def _normalize(domain: str) -> str:
    """Normaliza entradas humanas antes de consultar servicios externos."""
    clean = (domain or "").strip().lower()
    clean = re.sub(r"^https?://", "", clean)
    clean = re.sub(r"^www\.", "", clean)
    return clean.rstrip("/").strip()


def _rdap_available(domain: str) -> bool | None:
    url = f"https://rdap.org/domain/{domain}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(request, timeout=RDAP_TIMEOUT) as response:
            status = getattr(response, "status", getattr(response, "code", None))
            if status == 200:
                return False
            if status == 404:
                return True
            return None
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return True
        return None
    except (urllib.error.URLError, socket.timeout, TimeoutError, OSError, Exception):
        return None


def _whois_available(domain: str) -> bool | None:
    try:
        result = subprocess.run(
            ["whois", domain],
            timeout=WHOIS_TIMEOUT,
            capture_output=True,
            text=True,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError, Exception):
        return None

    text = ((result.stdout or "") + "\n" + (result.stderr or "")).lower()
    if any(marker in text for marker in AVAILABLE_MARKERS):
        return True
    if any(marker in text for marker in TAKEN_MARKERS):
        return False
    return None


def _has_ns(domain: str) -> bool:
    """¿El dominio tiene NS publicados? Un dominio registrado casi siempre los tiene; uno libre no.
    Señal fuerte y sin rate-limit. Imprescindible para TLD sin RDAP (p.ej. .es: rdap.org da 404
    tanto para registrados como libres -> 404 NO significa libre ahí)."""
    try:
        out = subprocess.run(
            ["dig", "+short", "NS", domain],
            capture_output=True, text=True, timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return any(line.strip() for line in out.stdout.splitlines())


def is_available(domain: str) -> bool | None:
    """Devuelve None en errores porque este módulo no debe bloquear nada aguas abajo.
    Orden: NS-check (registrado si tiene NS) → whois/RDAP solo confirman 'registrado' o el caso libre.
    NUNCA devolver True solo por RDAP 404 (los ccTLD sin RDAP, p.ej. .es, dan 404 siempre)."""
    normalized = _normalize(domain)
    if not normalized or "." not in normalized:
        return None

    # 1. NS publicados → registrado (mata el falso-positivo de un dominio famoso con RDAP 404 pero NS reales).
    if _has_ns(normalized):
        return False

    # 2. Sin NS: confirmar que no esté registrado (whois/RDAP dicen 'taken').
    whois_result = _whois_available(normalized)
    if whois_result is False:
        return False
    rdap_result = _rdap_available(normalized)
    if rdap_result is False:
        return False

    # 3. Sin NS + ninguna fuente dice registrado + alguna lo da libre → libre. Si no, incierto (None).
    if rdap_result is True or whois_result is True:
        return True
    return None


def _slugify_base(base: str) -> str:
    text = unicodedata.normalize("NFKD", base or "")
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def _candidate_domains(base_slug: str, tlds: tuple) -> list[str]:
    suffixes = ("web", "online", "oficial", "app")
    candidates: list[str] = []

    for tld in tlds:
        clean_tld = str(tld).strip().lstrip(".").lower()
        if clean_tld:
            candidates.append(f"{base_slug}.{clean_tld}")

    for suffix in suffixes:
        for tld in tlds:
            clean_tld = str(tld).strip().lstrip(".").lower()
            if clean_tld:
                candidates.append(f"{base_slug}{suffix}.{clean_tld}")

    return candidates


def suggest_alternatives(base: str, tlds: tuple = ("es", "com"), n: int = 5) -> list[dict]:
    """Solo se devuelven dominios validados como libres para evitar falsos positivos."""
    base_slug = _slugify_base(base)
    if not base_slug or n <= 0:
        return []

    suggestions: list[dict] = []
    for domain in _candidate_domains(base_slug, tlds):
        if is_available(domain) is True:
            suggestions.append({"domain": domain, "available": True})
            if len(suggestions) >= n:
                break
    return suggestions


def evaluate(candidatos: list[str]) -> dict:
    result = {"available": [], "taken": [], "unknown": []}

    for candidato in candidatos:
        domain = _normalize(candidato)
        status = is_available(domain)
        if status is True:
            result["available"].append(domain)
        elif status is False:
            result["taken"].append(domain)
        else:
            result["unknown"].append(domain)

    return result


def _print_domain_status(domain: str) -> None:
    status = is_available(domain)
    if status is True:
        print("LIBRE")
    elif status is False:
        print("PILLADO")
    else:
        print("?")


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Uso: python3 domain-suggester.py <dominio|nombre> [...]")
        return 1

    for arg in args:
        if "." in arg:
            _print_domain_status(arg)
        else:
            for suggestion in suggest_alternatives(arg):
                print(suggestion["domain"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
