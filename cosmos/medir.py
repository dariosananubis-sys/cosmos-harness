"""Medición honesta del contexto controlado por COSMOS."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Callable

from .generar import generar_indice
from .modelo import Arbol, Nodo


HEURISTICA = "heurística v1"
MARGEN_ERROR: float | None = None
PATRON_TOKEN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


class MetodoNoDisponible(RuntimeError):
    pass


@dataclass(frozen=True)
class ParteMedida:
    nombre: str
    tokens: int


@dataclass
class ResultadoMedicion:
    entrada: int
    arbol: int
    descarga: float | str
    fuera_cosmos: str
    metodo: str
    tokenizador: str | None
    estimado: bool
    margen_error: float | None
    presupuesto: int
    detalle_entrada: list[ParteMedida]
    detalle_arbol: list[ParteMedida]

    def como_dict(self) -> dict[str, object]:
        resultado = asdict(self)
        # Se conserva como texto deliberadamente: jamás se representa como cero.
        resultado["fuera_cosmos"] = "no_medido"
        return resultado


def contar_aprox(texto: str) -> int:
    """Cuenta palabras Unicode y signos; no usa la falsa regla bytes/4."""

    return len(PATRON_TOKEN.findall(texto))


def _contador_exacto() -> tuple[Callable[[str], int], str] | None:
    try:
        import tiktoken  # type: ignore[import-not-found]
    except ImportError:
        return None
    codificacion = tiktoken.get_encoding("cl100k_base")
    return lambda texto: len(codificacion.encode(texto)), "tiktoken/cl100k_base"


def tokenizador_exacto_disponible() -> bool:
    return _contador_exacto() is not None


def _seleccionar_contador(metodo: str) -> tuple[Callable[[str], int], str, str | None, bool]:
    if metodo not in {"auto", "aprox", "exacto"}:
        raise ValueError("metodo debe ser auto, aprox o exacto")
    exacto = _contador_exacto()
    if metodo == "exacto":
        if exacto is None:
            raise MetodoNoDisponible("se pidió método exacto, pero no hay tokenizador local")
        return exacto[0], "exacto", exacto[1], False
    if metodo == "auto" and exacto is not None:
        return exacto[0], "exacto", exacto[1], False
    return contar_aprox, "aprox", None, True


def catalogo_visible(arbol: Arbol) -> str:
    """Materializa exactamente los nombres/resúmenes visibles antes de bajar."""

    con_resumen = {"sistema-solar", "ciudad", "pueblo", "rio"}
    solo_nombre = {"planeta", "continente", "pais", "provincia"}
    lineas: list[str] = []
    for nodo in sorted(arbol.nodos, key=lambda n: (n.cosmos, n.nombre, n.ruta_relativa)):
        if nodo.cosmos in con_resumen:
            lineas.append(f"{nodo.cosmos}/{nodo.nombre}: {nodo.resumen}")
        elif nodo.cosmos in solo_nombre:
            lineas.append(f"{nodo.cosmos}/{nodo.nombre}")
    return "\n".join(lineas) + ("\n" if lineas else "")


def medir_arbol(
    arbol: Arbol,
    *,
    metodo: str = "auto",
    presupuesto: int = 4000,
    indice: str | None = None,
) -> ResultadoMedicion:
    contador, metodo_real, tokenizador, estimado = _seleccionar_contador(metodo)
    indice_real = generar_indice(arbol) if indice is None else indice

    partes_entrada: list[tuple[str, str]] = []
    if indice_real:
        partes_entrada.append(("índice de galaxia", indice_real))
    for nodo in sorted((n for n in arbol.nodos if n.cosmos == "oceano"), key=lambda n: n.nombre):
        partes_entrada.append((f"oceano/{nodo.nombre}", nodo.contenido))
    catalogo = catalogo_visible(arbol)
    if catalogo:
        partes_entrada.append(("catálogo visible", catalogo))

    detalle_entrada = [ParteMedida(nombre, contador(texto)) for nombre, texto in partes_entrada]
    detalle_arbol = [
        ParteMedida(nodo.referencia, contador(nodo.contenido))
        for nodo in sorted(arbol.nodos, key=lambda n: (n.cosmos, n.nombre, n.ruta_relativa))
    ]
    entrada = sum(parte.tokens for parte in detalle_entrada)
    total_arbol = sum(parte.tokens for parte in detalle_arbol)
    descarga: float | str = "no_definida" if total_arbol == 0 else 1 - entrada / total_arbol
    return ResultadoMedicion(
        entrada=entrada,
        arbol=total_arbol,
        descarga=descarga,
        fuera_cosmos="no_medido",
        metodo=metodo_real,
        tokenizador=tokenizador,
        estimado=estimado,
        margen_error=MARGEN_ERROR if estimado else 0.0,
        presupuesto=presupuesto,
        detalle_entrada=sorted(detalle_entrada, key=lambda p: p.tokens, reverse=True),
        detalle_arbol=detalle_arbol,
    )


def _numero(numero: int) -> str:
    return f"{numero:,}".replace(",", ".")


def formatear_medicion(resultado: ResultadoMedicion, *, detalle: bool = False) -> str:
    if resultado.metodo == "exacto":
        metodo = f"exacto, {resultado.tokenizador}"
    else:
        margen = "±desconocido" if resultado.margen_error is None else f"±{resultado.margen_error:.0%}"
        metodo = f"estimado, {margen}, {HEURISTICA}"
    descarga = (
        "no_definida"
        if resultado.descarga == "no_definida"
        else f"{float(resultado.descarga) * 100:.1f} %".replace(".", ",")
    )
    if resultado.entrada <= resultado.presupuesto:
        estado = f"OK, quedan {_numero(resultado.presupuesto - resultado.entrada)} tokens"
    else:
        estado = f"ROJO, excede en {_numero(resultado.entrada - resultado.presupuesto)} tokens"
    lineas = [
        "COSMOS  medir",
        "",
        f"  Entrada ......... {_numero(resultado.entrada)} tokens   ({metodo})",
        f"  Árbol ........... {_numero(resultado.arbol)} tokens   ({metodo})",
        f"  Descarga ........ {descarga}",
        f"  Presupuesto ..... {_numero(resultado.presupuesto)}     {estado}",
        "",
        "  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)",
        "",
        "  Lo más caro de la entrada:",
    ]
    if resultado.detalle_entrada:
        for numero, parte in enumerate(resultado.detalle_entrada if detalle else resultado.detalle_entrada[:3], start=1):
            lineas.append(f"    {numero}.  {_numero(parte.tokens)} tok  {parte.nombre}")
    else:
        lineas.append("    (entrada vacía)")
    if detalle:
        lineas.extend(["", "  Árbol, nodo a nodo:"])
        lineas.extend(f"    {_numero(parte.tokens)} tok  {parte.nombre}" for parte in resultado.detalle_arbol)
    return "\n".join(lineas) + "\n"


def medicion_json(resultado: ResultadoMedicion) -> str:
    return json.dumps(resultado.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
