"""Generación determinista del índice compacto y del mapa completo."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .modelo import RANGOS, Arbol, NIVELES_SOLIDOS, Nodo


def _orden(nodo: Nodo) -> tuple[int, str, str]:
    return RANGOS.get(nodo.cosmos, 99), nodo.referencia, nodo.ruta_relativa


def generar_indice(arbol: Arbol) -> str:
    """Devuelve el contexto mínimo de galaxia; no describe niveles profundos."""

    if not arbol.nodos:
        return ""
    galaxias = sorted((n for n in arbol.nodos if n.cosmos == "galaxia"), key=_orden)
    galaxia = galaxias[0] if galaxias else None
    titulo = galaxia.nombre if galaxia and galaxia.nombre else "sin-galaxia"
    lineas = [f"# COSMOS — {titulo}"]
    if galaxia and galaxia.resumen:
        lineas.extend(["", galaxia.resumen])

    sistemas = sorted((n for n in arbol.nodos if n.cosmos == "sistema-solar"), key=_orden)
    lineas.extend(["", "## Sistemas solares", ""])
    if sistemas:
        lineas.extend(f"- {n.nombre}: {n.resumen}" for n in sistemas)
    else:
        lineas.append("- Ninguno")

    # Los océanos NO se listan aquí. El índice los anunciaba con su resumen y a
    # continuación se cargaba el cuerpo entero de los cinco: presentar algo que
    # viene dos líneas después es coste sin función. Medido el 2026-09-02: 108
    # tokens que se pagaban en cada sesión y en cada subagente, para siempre.
    #
    # No es lo mismo que ocultarlos: un océano se carga SIEMPRE y completo, así
    # que quien lee el contexto los tiene delante. Lo que sobra es el índice.
    #
    # Por el mismo criterio se fueron dos adornos más, medidos el 2026-09-02:
    #   · el comentario «Generado por cosmos generar. No editar a mano.»: 23 tok.
    #     Va dirigido a una persona que abra el fichero, pero quien lo lee en cada
    #     turno es el agente, y quien de verdad impide el retoque a mano es E15 —
    #     que ya dice esa frase exacta cuando el índice y el árbol divergen.
    #   · los acentos graves y la raya de `- `nombre` — resumen`: 58 tok. El
    #     catálogo, que se lee en el mismo bloque, ya usa `clave: resumen`; dos
    #     formatos para la misma cosa cuestan tokens y no añaden nada.
    # Total 81 tokens por sesión y por subagente, para siempre.
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
