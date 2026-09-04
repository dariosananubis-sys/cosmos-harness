"""Generación determinista del índice compacto y del mapa completo."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .modelo import cerrojo, escribir_atomico, RANGOS, Arbol, NIVELES_SOLIDOS, Nodo


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
    sistemas = sorted((n for n in arbol.nodos if n.cosmos == "sistema-solar"), key=_orden)
    if galaxia and galaxia.resumen:
        # Los cardinales se cuentan aquí, nunca se escriben en el `resumen` de la galaxia:
        # «Veintiun oficios» sobrevivió dos veces a un oficio nuevo y viajó falso en la
        # primera línea de cada sesión, con E15 en verde —el índice estaba sincronizado
        # con una fuente que mentía (auditoría A-01 / E-16 / F-07). El artefacto que se
        # declara incapaz de mentir solo puede afirmar lo que acaba de contar.
        lineas.extend(["", f"{cardinales(arbol)} {galaxia.resumen}"])

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


def cardinales(arbol: Arbol) -> str:
    """La frase de tamaño del índice, contada sobre el árbol en el momento de generar."""

    def contar(nivel: str) -> int:
        return sum(1 for n in arbol.nodos if n.cosmos == nivel)

    oficios, mares, oceanos = contar("sistema-solar"), contar("mar"), contar("oceano")
    return (
        f"{oficios} oficio{'s' if oficios != 1 else ''}, "
        f"{mares} mar{'es' if mares != 1 else ''} que los cruzan y "
        f"{oceanos} oceano{'s' if oceanos != 1 else ''} siempre presentes."
    )


def escribir_indice(arbol: Arbol, ruta: str | Path) -> str:
    """Escribe el índice entero o no lo escribe, y no compite consigo mismo.

    Antes era un `write_text` pelado, mientras el manifiesto —menos crítico— ya tenía
    temporal, `fsync` y `os.replace`. El índice **es** el contexto de entrada: cortado a
    medias deja el árbol rojo por E15, y G03 impide arreglarlo a mano. Además dos
    `generar` a la vez se entrelazaban, porque ninguno tomaba cerrojo.
    """

    contenido = generar_indice(arbol)
    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with cerrojo(destino.parent / ".cosmos-generar.lock", que_hace="generación del índice"):
        escribir_atomico(destino, contenido)
    return contenido


def generar_mapa(arbol: Arbol) -> str:
    """Representación completa para inspección; no forma parte de la entrada."""

    por_padre: dict[str, list[Nodo]] = defaultdict(list)
    # Los adjuntos (estrella, luna) indexados por lo que iluminan u orbitan, en una
    # pasada: `visitar` recorría los N nodos por cada nodo (auditoría D-07), con el
    # índice correcto tres líneas más arriba.
    adjuntos_de: dict[str, list[Nodo]] = defaultdict(list)
    for nodo in arbol.nodos:
        if nodo.cosmos in NIVELES_SOLIDOS and nodo.cosmos != "galaxia":
            padre = nodo.datos.get("padre")
            if isinstance(padre, str):
                por_padre[padre].append(nodo)
        elif nodo.cosmos == "estrella" and isinstance(nodo.datos.get("ilumina"), str):
            adjuntos_de[nodo.datos["ilumina"]].append(nodo)
        elif nodo.cosmos == "luna" and isinstance(nodo.datos.get("orbita"), str):
            adjuntos_de[nodo.datos["orbita"]].append(nodo)

    # El precio se dice en la primera línea (auditoría E-10): el volcado completo de la
    # galaxia cuesta más que el recorrido guiado entero, y «a ver qué hay» es el gesto
    # más natural de un agente sin contexto.
    lineas = ["COSMOS mapa"]
    visitados: set[str] = set()

    def visitar(nodo: Nodo, prefijo: str) -> None:
        identidad = f"{nodo.referencia}@{nodo.ruta_relativa}"
        marca = " (ciclo)" if identidad in visitados else ""
        lineas.append(f"{prefijo}- {nodo.cosmos}/{nodo.nombre}{marca}")
        if marca:
            return
        visitados.add(identidad)
        adjuntos = sorted(adjuntos_de.get(nodo.referencia, []), key=_orden)
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
    # El precio, en tokens y en la primera línea (E-10 / R-42): el volcado entero cuesta más que el
    # recorrido guiado, y «a ver qué hay» es el gesto natural de un agente sin contexto. Se mide
    # sobre el propio texto, no se escribe a mano.
    from .medir import contar_generado

    cuerpo = "\n".join(lineas) + "\n"
    tokens = f"{contar_generado(cuerpo):,}".replace(",", ".")
    lineas[0] = (f"COSMOS mapa   (caro: ~{tokens} tokens, {len(arbol.nodos)} nodos; "
                 "para navegar usa 'cosmos buscar' y 'cosmos abrir')")
    return "\n".join(lineas) + "\n"
