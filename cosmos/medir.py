"""Medición honesta del contexto controlado por COSMOS."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Callable

from .generar import generar_indice
from .modelo import NIVELES_AGUA, RANGOS, Arbol, Nodo, cuerpo, nicho_de_nodo, nombres_nichos, normalizar_nichos


HEURISTICA = "heurística v2"
# Medido el 2026-09-01 contra tiktoken/cl100k_base sobre 78 ficheros de este repo
# (prosa en castellano, fichas de herramienta, código y agua). Ver docs/CALIBRACION.md.
# Sin el factor, contar palabras y signos subestimaba un 20,4 %.
FACTOR_CALIBRACION = 1.204
MARGEN_ERROR: float | None = 0.052
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
    nichos: tuple[str, ...] = field(default_factory=tuple)
    pueblos_visibles: int = 0
    agua: int = 0
    detalle_agua: list[ParteMedida] = field(default_factory=list)
    fuera_cosmos: str = field(init=False, default="no_medido")

    @property
    def arbol(self) -> int:
        """Alias de compatibilidad; NUCLEO denomina universo al total."""

        return self.universo

    @property
    def entrada_con_agua(self) -> int:
        """Lo que se paga sin invocar nada: entrada + agua que se carga por 'paths:'.

        NUCLEO §3. El agua condicional ya está dentro de 'resto', así que no se
        vuelve a sumar a 'universo': solo se publica y se compara con el presupuesto.
        """

        return self.entrada + self.agua

    def como_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ResumenMedicion:
    base: ResultadoMedicion
    peor_nicho: str | None
    peor: ResultadoMedicion
    seleccion_nichos: tuple[str, ...] = field(default_factory=tuple)
    seleccion: ResultadoMedicion | None = None

    @property
    def evaluada(self) -> ResultadoMedicion:
        return self.seleccion or self.peor

    def como_dict(self) -> dict[str, object]:
        return {
            "base": self.base.como_dict(),
            "peor_nicho": self.peor_nicho,
            "peor": self.peor.como_dict(),
            "seleccion_nichos": list(self.seleccion_nichos),
            "seleccion": self.seleccion.como_dict() if self.seleccion is not None else None,
            "evaluada": "seleccion" if self.seleccion is not None else "peor_nicho",
        }


def contar_aprox(texto: str) -> int:
    """Cuenta palabras y signos, corregido por el factor medido contra un tokenizador real.

    Contar palabras es reproducible en cualquier máquina, pero **subestima**: un
    tokenizador BPE parte las palabras largas y los acentos. Medido sobre 78 ficheros
    de este repo, el sesgo era del 20,4 % y siempre en la misma dirección — es decir,
    predecible, y por tanto corregible.

    Con el factor, el error medio baja a 5,2 %. Ese número no es cosmético: sin él,
    el presupuesto era un 20 % más laxo de lo que decía ser, y un presupuesto que
    miente a su favor es peor que no tenerlo.
    """

    return round(len(PATRON_TOKEN.findall(texto)) * FACTOR_CALIBRACION)


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


def agua_condicional(arbol: Arbol) -> list[Nodo]:
    """Agua que no está en la entrada y se carga sola al tocar un fichero que moja.

    NUCLEO §3. Son los mares y lagos: entran por `paths:`, sin que nadie los
    invoque, y por eso su coste es real aunque no aparezca en `contexto_inicial`.
    Quedan fuera los océanos (ya están en la entrada) y el agua con `moja: []`
    —río y lluvia—, que se invoca a mano y cuyo resumen ya se paga en el catálogo.
    """

    return [
        nodo
        for nodo in arbol.nodos
        if nodo.cosmos in NIVELES_AGUA
        and nodo.cosmos != "oceano"
        and isinstance(nodo.datos.get("moja"), list)
        and nodo.datos["moja"]
        and cuerpo(nodo)
    ]


def catalogo_visible(arbol: Arbol, nichos: list[str] | tuple[str, ...] | None = None) -> str:
    """Materializa exactamente los nombres/resúmenes visibles antes de bajar."""

    seleccion = normalizar_nichos(arbol, nichos)
    con_resumen = {"pueblo", "rio"}
    solo_nombre = {"planeta", "continente", "pais", "provincia"}
    invocables = {"pueblo"}
    orden_agua = {"rio": len(RANGOS) + 1}

    def clave(nodo: Nodo) -> tuple[int, str]:
        return RANGOS.get(nodo.cosmos, orden_agua.get(nodo.cosmos, len(RANGOS) + 2)), nodo.referencia

    lineas: list[str] = []
    for nodo in sorted(arbol.nodos, key=clave):
        if nodo.cosmos in invocables and (seleccion is None or nicho_de_nodo(arbol, nodo) not in seleccion):
            continue
        if nodo.cosmos in con_resumen:
            lineas.append(f"{nodo.referencia}: {nodo.resumen}")
        elif nodo.cosmos in solo_nombre:
            lineas.append(nodo.ruta_cosmos)
    return "\n".join(lineas)


def _bloques_contexto_inicial(
    arbol: Arbol,
    indice: str | None = None,
    nichos: list[str] | tuple[str, ...] | None = None,
) -> list[tuple[str, str]]:
    indice_real = generar_indice(arbol) if indice is None else indice
    bloques: list[tuple[str, str]] = []
    if indice_real:
        bloques.append(("índice de galaxia", indice_real.rstrip("\n")))
    for nodo in sorted((n for n in arbol.nodos if n.cosmos == "oceano"), key=lambda n: n.nombre):
        contenido = cuerpo(nodo)
        if contenido:
            bloques.append((f"oceano/{nodo.nombre}", contenido))
    catalogo = catalogo_visible(arbol, nichos)
    if catalogo:
        bloques.append(("catálogo visible", catalogo))
    return bloques


def contexto_inicial(
    arbol: Arbol,
    nichos: list[str] | tuple[str, ...] | None = None,
    *,
    indice: str | None = None,
) -> str:
    """Materializa la secuencia normativa única que se paga al entrar."""

    return "\n".join(texto for _, texto in _bloques_contexto_inicial(arbol, indice, nichos))


def medir_arbol(
    arbol: Arbol,
    *,
    metodo: str = "aprox",
    presupuesto: int = 4000,
    indice: str | None = None,
    nichos: list[str] | tuple[str, ...] | None = None,
) -> ResultadoMedicion:
    contador, metodo_real, tokenizador, estimado = _seleccionar_contador(metodo)
    seleccion = normalizar_nichos(arbol, nichos)
    partes_entrada = _bloques_contexto_inicial(arbol, indice, seleccion)
    entrada = contador(contexto_inicial(arbol, seleccion, indice=indice))
    detalle_entrada = [ParteMedida(nombre, contador(texto)) for nombre, texto in partes_entrada]
    nodos_resto = [nodo for nodo in arbol.nodos if nodo.cosmos != "oceano"]
    detalle_arbol = [
        ParteMedida(nodo.referencia, contador(cuerpo(nodo)))
        for nodo in sorted(nodos_resto, key=lambda n: (RANGOS.get(n.cosmos, 99), n.referencia, n.ruta_relativa))
    ]
    resto = sum(parte.tokens for parte in detalle_arbol)
    universo = entrada + resto
    descarga: float | str = "no_definida" if universo == 0 else 1 - entrada / universo
    detalle_agua = [
        ParteMedida(f"{nodo.cosmos}/{nodo.nombre}", contador(cuerpo(nodo)))
        for nodo in agua_condicional(arbol)
    ]
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
        nichos=seleccion or (),
        pueblos_visibles=sum(
            1
            for nodo in arbol.nodos
            if nodo.cosmos == "pueblo" and seleccion is not None and nicho_de_nodo(arbol, nodo) in seleccion
        ),
        agua=sum(parte.tokens for parte in detalle_agua),
        detalle_agua=sorted(detalle_agua, key=lambda parte: parte.tokens, reverse=True),
    )


def medir_casos(
    arbol: Arbol,
    *,
    metodo: str = "aprox",
    presupuesto: int = 4000,
    indice: str | None = None,
    nichos: list[str] | tuple[str, ...] | None = None,
) -> ResumenMedicion:
    """Mide el caso base, cada nicho y, si se pidió, una selección concreta."""

    base = medir_arbol(arbol, metodo=metodo, presupuesto=presupuesto, indice=indice, nichos=None)
    por_nicho = [
        (
            nombre,
            medir_arbol(arbol, metodo=metodo, presupuesto=presupuesto, indice=indice, nichos=[nombre]),
        )
        for nombre in nombres_nichos(arbol)
    ]
    if por_nicho:
        peor_nicho, peor = max(por_nicho, key=lambda caso: caso[1].entrada)
    else:
        peor_nicho, peor = None, base
    seleccion_nichos = normalizar_nichos(arbol, nichos)
    seleccion = (
        medir_arbol(
            arbol,
            metodo=metodo,
            presupuesto=presupuesto,
            indice=indice,
            nichos=seleccion_nichos,
        )
        if seleccion_nichos is not None
        else None
    )
    return ResumenMedicion(base, peor_nicho, peor, seleccion_nichos or (), seleccion)


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
    evaluado = resultado.entrada_con_agua
    if evaluado <= resultado.presupuesto:
        estado = f"OK, quedan {_numero(resultado.presupuesto - evaluado)} tokens"
    else:
        estado = f"ROJO, excede en {_numero(evaluado - resultado.presupuesto)} tokens"
    lineas = [
        "COSMOS  medir",
        "",
        f"  Entrada ......... {_numero(resultado.entrada)} tokens   ({metodo})",
        f"  Agua condicional  {_numero(resultado.agua)} tokens   ({len(resultado.detalle_agua)} aguas por paths:, fuera de la entrada)",
        f"  Entrada con agua  {_numero(evaluado)} tokens   (lo que se paga sin invocar nada)",
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


def formatear_casos(resultado: ResumenMedicion, *, detalle: bool = False) -> str:
    evaluada = resultado.evaluada
    if evaluada.metodo == "exacto":
        metodo = f"exacto, {evaluada.tokenizador}"
    else:
        margen = "±desconocido" if evaluada.margen_error is None else f"±{evaluada.margen_error:.0%}"
        metodo = f"estimado, {margen}, {HEURISTICA}"
    descarga = (
        "no_definida"
        if evaluada.descarga == "no_definida"
        else f"{float(evaluada.descarga) * 100:.1f} %".replace(".", ",")
    )
    evaluado = evaluada.entrada_con_agua
    if evaluado <= evaluada.presupuesto:
        estado = f"OK, quedan {_numero(evaluada.presupuesto - evaluado)} tokens"
    else:
        estado = f"ROJO, excede en {_numero(evaluado - evaluada.presupuesto)} tokens"
    peor_nombre = resultado.peor_nicho or "sin nichos"
    lineas = [
        "COSMOS  medir",
        "",
        f"  Entrada base .... {_numero(resultado.base.entrada)} tokens   (índice + océanos + estructura, sin pueblos; {metodo})",
        f"  Peor nicho ...... {_numero(resultado.peor.entrada)} tokens   ({peor_nombre}, {resultado.peor.pueblos_visibles} pueblos)",
        f"  Agua condicional  {_numero(evaluada.agua)} tokens   ({len(evaluada.detalle_agua)} aguas por paths:, fuera de la entrada)",
    ]
    if resultado.seleccion is not None:
        nombres = ", ".join(resultado.seleccion_nichos)
        etiqueta = "Nicho activo ...." if len(resultado.seleccion_nichos) == 1 else "Combinación ....."
        lineas.append(
            f"  {etiqueta} {_numero(resultado.seleccion.entrada)} tokens   ({nombres}; {resultado.seleccion.pueblos_visibles} pueblos)"
        )
    if resultado.seleccion is None:
        ambito = "el peor caso"
    elif len(resultado.seleccion_nichos) == 1:
        ambito = "el nicho activo"
    else:
        ambito = "la combinación"
    lineas.extend(
        [
            f"  Peor con agua ... {_numero(evaluado)} tokens   ({ambito} + agua condicional)",
            f"  Universo ........ {_numero(evaluada.universo)} tokens   ({metodo})",
            f"  Descarga ........ {descarga}",
            f"  Presupuesto ..... {_numero(evaluada.presupuesto)}     {estado} en {ambito} con agua",
            "",
            "  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)",
            "",
            "  Lo más caro de la entrada evaluada:",
        ]
    )
    if evaluada.detalle_entrada:
        for numero, parte in enumerate(evaluada.detalle_entrada if detalle else evaluada.detalle_entrada[:3], start=1):
            lineas.append(f"    {numero}.  {_numero(parte.tokens)} tok  {parte.nombre}")
    else:
        lineas.append("    (entrada vacía)")
    if detalle:
        if evaluada.detalle_agua:
            lineas.extend(["", "  Agua condicional, nodo a nodo:"])
            lineas.extend(f"    {_numero(parte.tokens)} tok  {parte.nombre}" for parte in evaluada.detalle_agua)
        lineas.extend(["", "  Resto, nodo a nodo:"])
        lineas.extend(f"    {_numero(parte.tokens)} tok  {parte.nombre}" for parte in evaluada.detalle_arbol)
    return "\n".join(lineas) + "\n"


def medicion_json(resultado: ResultadoMedicion) -> str:
    return json.dumps(resultado.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def casos_json(resultado: ResumenMedicion) -> str:
    return json.dumps(resultado.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
