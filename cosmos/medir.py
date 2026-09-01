"""Medición honesta del contexto controlado por COSMOS."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Callable

from .generar import generar_indice
from .modelo import RANGOS, Arbol, Nodo, cuerpo


HEURISTICA = "heurística v1"
MARGEN_ERROR: float | None = None
PATRON_TOKEN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


class MetodoNoDisponible(RuntimeError):
    pass


@dataclass(frozen=True)
class ParteMedida:
    nombre: str
    tokens: int


@dataclass(frozen=True)
class ResultadoMedicion:
    entrada: int
    universo: int
    resto: int
    descarga: float | str
    metodo: str
    tokenizador: str | None
    estimado: bool
    margen_error: float | None
    presupuesto: int
    detalle_entrada: list[ParteMedida]
    detalle_arbol: list[ParteMedida]
    fuera_cosmos: str = field(init=False, default="no_medido")

    @property
    def arbol(self) -> int:
        """Alias de compatibilidad; NUCLEO denomina universo al total."""

        return self.universo

    def como_dict(self) -> dict[str, object]:
        return asdict(self)


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
    if metodo not in {"aprox", "exacto"}:
        raise ValueError("metodo debe ser aprox o exacto")
    if metodo == "exacto":
        exacto = _contador_exacto()
        if exacto is None:
            raise MetodoNoDisponible("se pidió método exacto, pero no hay tokenizador local")
        return exacto[0], "exacto", exacto[1], False
    return contar_aprox, "aprox", None, True


def catalogo_visible(arbol: Arbol) -> str:
    """Materializa exactamente los nombres/resúmenes visibles antes de bajar."""

    con_resumen = {"ciudad", "pueblo", "rio"}
    solo_nombre = {"planeta", "continente", "pais", "provincia"}
    orden_agua = {"rio": len(RANGOS) + 1}

    def clave(nodo: Nodo) -> tuple[int, str]:
        return RANGOS.get(nodo.cosmos, orden_agua.get(nodo.cosmos, len(RANGOS) + 2)), nodo.referencia

    lineas: list[str] = []
    for nodo in sorted(arbol.nodos, key=clave):
        if nodo.cosmos in con_resumen:
            lineas.append(f"{nodo.referencia}: {nodo.resumen}")
        elif nodo.cosmos in solo_nombre:
            lineas.append(nodo.ruta_cosmos)
    return "\n".join(lineas)


def _bloques_contexto_inicial(arbol: Arbol, indice: str | None = None) -> list[tuple[str, str]]:
    indice_real = generar_indice(arbol) if indice is None else indice
    bloques: list[tuple[str, str]] = []
    if indice_real:
        bloques.append(("índice de galaxia", indice_real.rstrip("\n")))
    for nodo in sorted((n for n in arbol.nodos if n.cosmos == "oceano"), key=lambda n: n.nombre):
        contenido = cuerpo(nodo)
        if contenido:
            bloques.append((f"oceano/{nodo.nombre}", contenido))
    catalogo = catalogo_visible(arbol)
    if catalogo:
        bloques.append(("catálogo visible", catalogo))
    return bloques


def contexto_inicial(arbol: Arbol, *, indice: str | None = None) -> str:
    """Materializa la secuencia normativa única que se paga al entrar."""

    return "\n".join(texto for _, texto in _bloques_contexto_inicial(arbol, indice))


def medir_arbol(
    arbol: Arbol,
    *,
    metodo: str = "aprox",
    presupuesto: int = 4000,
    indice: str | None = None,
) -> ResultadoMedicion:
    contador, metodo_real, tokenizador, estimado = _seleccionar_contador(metodo)
    partes_entrada = _bloques_contexto_inicial(arbol, indice)
    entrada = contador(contexto_inicial(arbol, indice=indice))
    detalle_entrada = [ParteMedida(nombre, contador(texto)) for nombre, texto in partes_entrada]
    nodos_resto = [nodo for nodo in arbol.nodos if nodo.cosmos != "oceano"]
    detalle_arbol = [
        ParteMedida(nodo.referencia, contador(cuerpo(nodo)))
        for nodo in sorted(nodos_resto, key=lambda n: (RANGOS.get(n.cosmos, 99), n.referencia, n.ruta_relativa))
    ]
    resto = sum(parte.tokens for parte in detalle_arbol)
    universo = entrada + resto
    descarga: float | str = "no_definida" if universo == 0 else 1 - entrada / universo
    return ResultadoMedicion(
        entrada=entrada,
        universo=universo,
        resto=resto,
        descarga=descarga,
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
        f"  Universo ........ {_numero(resultado.universo)} tokens   ({metodo})",
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
        lineas.extend(["", "  Resto, nodo a nodo:"])
        lineas.extend(f"    {_numero(parte.tokens)} tok  {parte.nombre}" for parte in resultado.detalle_arbol)
    return "\n".join(lineas) + "\n"


def medicion_json(resultado: ResultadoMedicion) -> str:
    return json.dumps(resultado.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
