#!/usr/bin/env python3
"""Preflight de solo lectura para BrowserOS Neo/BrowserClaw.

Descubre únicamente datos operativos no secretos y comprueba que los endpoints
sean loopback. No imprime install_id, cookies, perfiles ni configuración completa.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import platform
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def is_loopback_host(host: str | None) -> bool:
    if not host:
        return False
    value = host.strip("[]").lower()
    if value == "localhost":
        return True
    try:
        return ipaddress.ip_address(value).is_loopback
    except ValueError:
        return False


def validate_loopback_url(url: str, suffix: str | None = None) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"esquema no permitido: {parsed.scheme or 'ausente'}")
    if not is_loopback_host(parsed.hostname):
        raise ValueError("el endpoint no es loopback")
    if parsed.port is None:
        raise ValueError("el endpoint no declara puerto")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("el endpoint contiene credenciales, query o fragmento")
    if suffix and parsed.path != suffix:
        raise ValueError(f"el endpoint no coincide exactamente con {suffix}")
    host = parsed.hostname or ""
    rendered_host = f"[{host}]" if ":" in host else host
    return urllib.parse.urlunsplit(
        (parsed.scheme, f"{rendered_host}:{parsed.port}", parsed.path, "", "")
    )


def reject_symlink_components(path: Path) -> None:
    absolute = path.expanduser().absolute()
    home = Path.home().absolute()
    if absolute.is_symlink():
        raise ValueError(f"se rechaza configuración mediante symlink: {absolute}")
    try:
        relative = absolute.relative_to(home)
    except ValueError as exc:
        raise ValueError(f"la configuración debe estar dentro del home: {absolute}") from exc
    current = home
    if current.is_symlink():
        raise ValueError(f"se rechaza home mediante symlink: {current}")
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"se rechaza configuración mediante symlink: {current}")


def read_json(path: Path) -> dict[str, Any]:
    reject_symlink_components(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON raíz no es objeto: {path}")
    return data


def find_urls(value: Any, suffix: str) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for child in value.values():
            found.extend(find_urls(child, suffix))
    elif isinstance(value, list):
        for child in value:
            found.extend(find_urls(child, suffix))
    elif isinstance(value, str) and value.startswith(("http://", "https://")):
        if urllib.parse.urlparse(value).path.endswith(suffix):
            found.append(value)
    return found


def candidate_paths(explicit: str | None = None) -> list[Path]:
    if explicit:
        return [Path(explicit).expanduser()]
    home = Path.home()
    candidates = [
        home / "Library/Application Support/BrowserClaw/.browseros/config.json",
        home / ".browserclaw/runtime.json",
    ]
    appdata = os.environ.get("APPDATA")
    localappdata = os.environ.get("LOCALAPPDATA")
    for base in (appdata, localappdata):
        if base:
            candidates.extend(
                [
                    Path(base) / "BrowserClaw/.browseros/config.json",
                    Path(base) / "BrowserClaw/runtime.json",
                ]
            )
    result: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key not in seen:
            result.append(path)
            seen.add(key)
    return result


def extract_endpoints(data: dict[str, Any]) -> dict[str, Any]:
    ports = data.get("ports") if isinstance(data.get("ports"), dict) else {}
    result: dict[str, Any] = {}
    for name in ("proxy", "cdp", "server"):
        value = ports.get(name)
        if value is not None and (not isinstance(value, int) or not 1 <= value <= 65535):
            raise ValueError(f"puerto {name} inválido")
    if isinstance(ports.get("proxy"), int):
        result["mcp_url"] = f"http://127.0.0.1:{ports['proxy']}/mcp"
    if isinstance(ports.get("cdp"), int):
        result["cdp_url"] = f"http://127.0.0.1:{ports['cdp']}"
    if isinstance(ports.get("server"), int):
        result["server_url"] = f"http://127.0.0.1:{ports['server']}"

    if "mcp_url" not in result:
        runtime_url = data.get("url")
        if isinstance(runtime_url, str):
            parsed = urllib.parse.urlparse(runtime_url)
            if parsed.path in {"", "/"}:
                validate_loopback_url(runtime_url)
                canonical = validate_loopback_url(runtime_url)
                result["mcp_url"] = canonical.rstrip("/") + "/mcp"

    if "mcp_url" not in result:
        urls = []
        for url in find_urls(data, "/mcp"):
            try:
                urls.append(validate_loopback_url(url, "/mcp"))
            except ValueError:
                continue
        unique = sorted(set(urls))
        if len(unique) == 1:
            result["mcp_url"] = unique[0]
        elif len(unique) > 1:
            raise ValueError("la configuración contiene varios endpoints MCP loopback")
    return result


def tcp_probe(url: str, timeout: float = 1.0) -> bool:
    parsed = urllib.parse.urlparse(url)
    try:
        with socket.create_connection((parsed.hostname or "", parsed.port or 0), timeout):
            return True
    except OSError:
        return False


def cdp_probe(url: str, timeout: float = 1.5) -> tuple[bool, str | None]:
    endpoint = url.rstrip("/") + "/json/version"
    try:
        with urllib.request.urlopen(endpoint, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        browser = data.get("Browser") if isinstance(data, dict) else None
        return bool(browser), str(browser) if browser else None
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return False, None


def inspect(explicit: str | None = None) -> dict[str, Any]:
    existing = [path for path in candidate_paths(explicit) if path.is_file()]
    report: dict[str, Any] = {
        "platform": platform.system(),
        "base_ready": False,
        "inspector_ready": False,
        "config_path": None,
        "config_sources": [],
        "mcp_url": None,
        "cdp_url": None,
        "mcp_tcp": False,
        "cdp_http": False,
        "browser": None,
        "issues": [],
    }
    if not existing:
        report["issues"].append(
            "no se encontró configuración; usa --config con la ruta correcta"
        )
        return report

    valid: list[tuple[Path, dict[str, Any]]] = []
    try:
        for path in existing:
            endpoints = extract_endpoints(read_json(path))
            if endpoints.get("mcp_url"):
                validate_loopback_url(str(endpoints["mcp_url"]), "/mcp")
                valid.append((path, endpoints))
        if not valid:
            raise ValueError("ninguna configuración contiene un endpoint MCP válido")
        merged: dict[str, Any] = {}
        for key in ("mcp_url", "cdp_url", "server_url"):
            values = {str(item[1][key]) for item in valid if key in item[1]}
            if len(values) > 1:
                raise ValueError(f"las fuentes de configuración discrepan sobre {key}")
            if values:
                merged[key] = values.pop()
        path, _richest = max(valid, key=lambda item: len(item[1]))
        endpoints = merged
        report["config_path"] = str(path)
        report["config_sources"] = [str(item[0]) for item in valid]
        mcp_url = endpoints.get("mcp_url")
        cdp_url = endpoints.get("cdp_url")
        if not mcp_url:
            raise ValueError("no se encontró endpoint MCP")
        report["mcp_url"] = validate_loopback_url(str(mcp_url), "/mcp")
        report["mcp_tcp"] = tcp_probe(report["mcp_url"])
        report["base_ready"] = report["mcp_tcp"]
        if not report["mcp_tcp"]:
            report["issues"].append("el puerto MCP no acepta conexiones")
        if cdp_url:
            report["cdp_url"] = validate_loopback_url(str(cdp_url))
            ready, browser = cdp_probe(report["cdp_url"])
            report["cdp_http"] = ready
            report["browser"] = browser
            report["inspector_ready"] = ready
            if not ready:
                report["issues"].append("CDP no responde con /json/version válido")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report["issues"].append(str(exc))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="ruta explícita al JSON de runtime/configuración")
    parser.add_argument("--json", action="store_true", help="salida JSON")
    parser.add_argument(
        "--field",
        choices=("mcp_url", "cdp_url", "config_path"),
        help="imprime solo un campo no secreto",
    )
    args = parser.parse_args()
    report = inspect(args.config)
    if args.field:
        value = report.get(args.field)
        if value is None:
            return 2
        print(value)
    elif args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("READY" if report["base_ready"] else "NOT_READY")
        for issue in report["issues"]:
            print(f"- {issue}")
    return 0 if report["base_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
