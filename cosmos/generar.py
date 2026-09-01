"""Generación determinista del índice compacto y del mapa completo."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .modelo import RANGOS, Arbol, NIVELES_SOLIDOS, Nodo


MARCA = "<!-- Generado por cosmos generar. No editar a mano. -->"


def _orden(nodo: Nodo) -> tuple[int, str, str]:
    return RANGOS.get(nodo.cosmos, 99), nodo.referencia, nodo.ruta_relativa


def generar_indice(arbol: Arbol) -> str:
    """Devuelve el contexto mínimo de galaxia; no describe niveles profundos."""

    if not arbol.nodos:
        return ""
    galaxias = sorted((n for n in arbol.nodos if n.cosmos == "galaxia"), key=_orden)
    galaxia = galaxias[0] if galaxias else None
    titulo = galaxia.nombre if galaxia and galaxia.nombre else "sin-galaxia"
    lineas = [MARCA, "", f"# COSMOS — {titulo}"]
    if galaxia and galaxia.resumen:
        lineas.extend(["", galaxia.resumen])

    sistemas = sorted((n for n in arbol.nodos if n.cosmos == "sistema-solar"), key=_orden)
    lineas.extend(["", "## Sistemas solares", ""])
    if sistemas:
        lineas.extend(f"- `{n.nombre}` — {n.resumen}" for n in sistemas)
    else:
        lineas.append("- Ninguno")

    oceanos = sorted((n for n in arbol.nodos if n.cosmos == "oceano"), key=_orden)
    lineas.extend(["", "## Océanos", ""])
    if oceanos:
        lineas.extend(f"- `{n.nombre}` — {n.resumen}" for n in oceanos)
    else:
        lineas.append("- Ninguno")
    return "\n".join(lineas) + "\n"


def escribir_indice(arbol: Arbol, ruta: str | Path) -> str:
    contenido = generar_indice(arbol)
    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(contenido, encoding="utf-8")
    return contenido


def generar_mapa(arbol: Arbol) -> str:
    """Representación completa para inspección; no forma parte de la entrada."""

    por_padre: dict[str, list[Nodo]] = defaultdict(list)
    for nodo in arbol.nodos:
        if nodo.cosmos in NIVELES_SOLIDOS and nodo.cosmos != "galaxia":
            padre = nodo.datos.get("padre")
            if isinstance(padre, str):
                por_padre[padre].append(nodo)

    lineas = ["COSMOS mapa"]
    visitados: set[str] = set()

    def visitar(nodo: Nodo, prefijo: str) -> None:
        identidad = f"{nodo.referencia}@{nodo.ruta_relativa}"
        marca = " (ciclo)" if identidad in visitados else ""
        lineas.append(f"{prefijo}- {nodo.cosmos}/{nodo.nombre}{marca}")
        if marca:
            return
        visitados.add(identidad)
        adjuntos = sorted(
            (
                n
                for n in arbol.nodos
                if (n.cosmos == "estrella" and n.datos.get("ilumina") == nodo.referencia)
                or (n.cosmos == "luna" and n.datos.get("orbita") == nodo.referencia)
            ),
            key=_orden,
        )
        for adjunto in adjuntos:
            lineas.append(f"{prefijo}  * {adjunto.cosmos}/{adjunto.nombre}")
        for hijo in sorted(por_padre.get(nodo.referencia, []), key=_orden):
            visitar(hijo, prefijo + "  ")

    for galaxia in sorted((n for n in arbol.nodos if n.cosmos == "galaxia"), key=_orden):
        visitar(galaxia, "")

    agua = sorted((n for n in arbol.nodos if n.cosmos in {"oceano", "mar", "lago", "rio", "lluvia"}), key=_orden)
    if agua:
        lineas.append("Agua")
        lineas.extend(f"  - {n.cosmos}/{n.nombre}" for n in agua)
    return "\n".join(lineas) + "\n"
