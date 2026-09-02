#!/usr/bin/env python3
"""Captura una VENTANA concreta de macOS por nombre, aunque esté tapada o en
segundo plano.

Usa `screencapture -l <windowid>`, que fotografía el contenido de esa ventana aunque
tenga otras ventanas encima y sin traerla al frente — puedes seguir trabajando encima
mientras se captura la de atrás. Resuelve el windowid por nombre de app / título con
Quartz (CGWindowListCopyWindowInfo).

Más barato en tokens que la pantalla entera si vas a pasarle la imagen a un LLM:
captura solo la ventana pedida en vez del escritorio completo.

Uso:
    python3 captura-ventana.py "<patrón>" [salida.png]
    python3 captura-ventana.py --listar          # ver qué ventanas hay

  <patrón>  substring insensible a mayúsculas; matchea "app  título"
            ej. "chrome", "terminal", "code", "slack"
  salida    ruta PNG (por defecto captura-ventana.png en el cwd)

Sale 0 y escribe la ruta si captura; 1 si no encuentra la ventana (lista las disponibles).
Requiere permiso de Grabación de pantalla para el proceso que lo lanza (TCC); si sale en
negro, concederlo en Ajustes > Privacidad > Grabación de pantalla.
"""
from __future__ import annotations
import subprocess
import sys

from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGWindowListExcludeDesktopElements,
    kCGNullWindowID,
)


def ventanas() -> list[dict]:
    """Ventanas normales en pantalla (incluye tapadas; excluye minimizadas/escritorio)."""
    opts = kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements
    out = []
    for w in CGWindowListCopyWindowInfo(opts, kCGNullWindowID) or []:
        if w.get("kCGWindowLayer", 0) != 0:  # 0 = ventana de app normal (no menú/overlay)
            continue
        b = w.get("kCGWindowBounds", {})
        area = b.get("Width", 0) * b.get("Height", 0)
        if area < 5000:  # descarta ventanitas fantasma (tooltips, etc.)
            continue
        out.append({
            "id": int(w.get("kCGWindowNumber", 0)),
            "app": w.get("kCGWindowOwnerName", "") or "",
            "title": w.get("kCGWindowName", "") or "",
            "area": area,
        })
    return out


def listar() -> None:
    for v in sorted(ventanas(), key=lambda x: -x["area"]):
        t = f" · {v['title']}" if v["title"] else ""
        print(f"  [{v['id']}] {v['app']}{t}")


def elegir(patron: str) -> dict | None:
    p = patron.lower()
    cand = [v for v in ventanas() if p in f"{v['app']} {v['title']}".lower()]
    return max(cand, key=lambda x: x["area"]) if cand else None


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if args[0] == "--listar":
        listar()
        return 0

    patron = args[0]
    salida = args[1] if len(args) > 1 else "captura-ventana.png"
    win = elegir(patron)
    if not win:
        print(f"Sin ventana que matchee «{patron}». Disponibles:")
        listar()
        return 1

    # -o sin sombra, -x sin sonido, -l ventana concreta (aunque esté detrás)
    r = subprocess.run(["screencapture", "-o", "-x", f"-l{win['id']}", salida])
    if r.returncode != 0:
        print(f"screencapture falló (¿permiso de Grabación de pantalla?). Ventana: {win['app']}")
        return 1
    t = f" · {win['title']}" if win["title"] else ""
    print(f"OK -> {salida}  (ventana [{win['id']}] {win['app']}{t})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
