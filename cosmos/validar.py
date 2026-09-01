"""Validación offline de las invariantes estructurales de COSMOS."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable

from .compilar import errores_vista
from .generar import generar_indice
from .medir import medir_arbol
from .modelo import (
    NIVELES_ADJUNTOS,
    NIVELES_AGUA,
    NIVELES_SOLIDOS,
    NIVELES_VALIDOS,
    PATRON_NOMBRE,
    RANGOS,
    Arbol,
    Configuracion,
    Nodo,
    cuerpo,
)


PALABRAS_VACIAS_E08 = {"la", "de", "skill", "para", "sistema"}
PALABRAS_VACIAS_E17 = {
    "a", "al", "algo", "and", "ante", "con", "como", "cuando", "de", "del",
    "el", "en", "es", "esta", "este", "for", "in", "la", "las", "lo", "los",
    "of", "on", "o", "para", "por", "que", "se", "si", "sin", "su", "the",
    "to", "un", "una", "y",
}
CAMPOS_COMUNES = {"cosmos", "nombre", "resumen"}
CAMPOS_POR_NIVEL = {
    **{nivel: {"padre"} for nivel in NIVELES_SOLIDOS if nivel != "galaxia"},
    "galaxia": set(),
    "estrella": {"ilumina"},
    "luna": {"orbita"},
    **{nivel: {"moja"} for nivel in NIVELES_AGUA},
    "rio": {"moja", "invoca"},
}
NIVELES_APLANADOS = frozenset({"ciudad", "pueblo"})


@dataclass(frozen=True)
class ErrorValidacion:
    codigo: str
    ruta: str
    linea: int | None
    mensaje: str
    accion: str

    def como_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class ResultadoValidacion:
    errores: list[ErrorValidacion]
    configuracion_por_defecto: bool = False

    @property
    def valido(self) -> bool:
        return not self.errores

    @property
    def codigo_salida(self) -> int:
        return 0 if self.valido else 1

    def codigos(self) -> list[str]:
        return [error.codigo for error in self.errores]


def _error(
    codigo: str,
    nodo: Nodo | None,
    mensaje: str,
    accion: str,
    *,
    campo: str | None = None,
    ruta: str | None = None,
    linea: int | None = None,
) -> ErrorValidacion:
    return ErrorValidacion(
        codigo,
        ruta if ruta is not None else (nodo.ruta_relativa if nodo else "árbol"),
        linea if linea is not None else (nodo.linea(campo) if nodo and campo else None),
        mensaje,
        accion,
    )


def _normalizar(texto: str) -> str:
    sin_acentos = "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto.casefold())
        if unicodedata.category(caracter) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", " ", sin_acentos).strip()


def _comprobar_e00(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    errores = [
        _error("E00", None, error.mensaje, "Corrige la sintaxis o el esquema del frontmatter.", ruta=error.ruta, linea=error.linea)
        for error in arbol.errores
    ]
    for nodo in arbol.nodos:
        nivel = nodo.cosmos
        for campo in CAMPOS_COMUNES:
            if campo not in nodo.datos:
                errores.append(_error("E00", nodo, f"falta el campo obligatorio {campo!r}", f"Añade {campo!r} al frontmatter."))
            elif not isinstance(nodo.datos[campo], str):
                errores.append(_error("E00", nodo, f"{campo!r} debe ser texto", f"Escribe {campo!r} como un escalar de texto.", campo=campo))
        if isinstance(nodo.datos.get("nombre"), str) and not PATRON_NOMBRE.fullmatch(nodo.nombre):
            errores.append(_error("E00", nodo, f"nombre inválido: {nodo.nombre!r}", "Usa solo minúsculas ASCII, dígitos y guiones.", campo="nombre"))
        if nivel in NIVELES_VALIDOS:
            permitidos = CAMPOS_COMUNES | CAMPOS_POR_NIVEL[nivel]
            for campo in sorted(set(nodo.datos) - permitidos):
                errores.append(_error("E00", nodo, f"campo no permitido para {nivel}: {campo!r}", "Elimina el campo o mueve la información al cuerpo Markdown.", campo=campo))
            for campo in CAMPOS_POR_NIVEL[nivel] - {"padre"}:
                if campo not in nodo.datos:
                    errores.append(_error("E00", nodo, f"falta el campo obligatorio {campo!r}", f"Añade {campo!r} al frontmatter."))
            for campo, valor in nodo.datos.items():
                if campo == "moja" and not isinstance(valor, list):
                    errores.append(_error("E00", nodo, "'moja' debe ser una lista de texto", "Usa una lista YAML de escalares.", campo=campo))
                elif campo != "moja" and not isinstance(valor, str):
                    errores.append(_error("E00", nodo, f"{campo!r} debe ser texto", "Usa un escalar de texto.", campo=campo))
    return errores


def _comprobar_e01(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    return [
        _error("E01", nodo, "nodo sólido huérfano: falta 'padre'", "Declara el sólido de rango superior en 'padre'.")
        for nodo in arbol.nodos
        if nodo.cosmos in NIVELES_SOLIDOS[1:] and not isinstance(nodo.datos.get("padre"), str)
    ]


def _comprobar_e02(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    referencias = {nodo.referencia for nodo in arbol.nodos}
    return [
        _error("E02", nodo, f"padre inexistente: {nodo.datos['padre']!r}", "Corrige la referencia o crea primero el padre.", campo="padre")
        for nodo in arbol.nodos
        if nodo.cosmos in NIVELES_SOLIDOS[1:]
        and isinstance(nodo.datos.get("padre"), str)
        and nodo.datos["padre"] not in referencias
    ]


def _comprobar_e03(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    por_referencia: dict[str, list[Nodo]] = defaultdict(list)
    for nodo in arbol.nodos:
        por_referencia[nodo.referencia].append(nodo)
    errores: list[ErrorValidacion] = []
    for nodo in arbol.nodos:
        padre_ref = nodo.datos.get("padre")
        if nodo.cosmos not in RANGOS or not isinstance(padre_ref, str):
            continue
        for padre in por_referencia.get(padre_ref, []):
            if padre.cosmos not in RANGOS or RANGOS[padre.cosmos] >= RANGOS[nodo.cosmos]:
                errores.append(_error("E03", nodo, f"contención invertida o plana: {padre_ref!r} no puede contener a {nodo.referencia}", "Cuelga el nodo de un sólido de rango estrictamente superior.", campo="padre"))
                break
    return errores


def _comprobar_e04(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    por_referencia: dict[str, list[Nodo]] = defaultdict(list)
    for nodo in arbol.nodos:
        por_referencia[nodo.referencia].append(nodo)
    estado: dict[str, int] = {}
    pila: list[Nodo] = []
    errores: list[ErrorValidacion] = []

    def visitar(nodo: Nodo) -> None:
        clave = nodo.ruta_relativa
        estado[clave] = 1
        pila.append(nodo)
        padre_ref = nodo.datos.get("padre")
        if isinstance(padre_ref, str):
            for padre in por_referencia.get(padre_ref, []):
                estado_padre = estado.get(padre.ruta_relativa, 0)
                if estado_padre == 0:
                    visitar(padre)
                elif estado_padre == 1:
                    inicio = next(i for i, item in enumerate(pila) if item.ruta_relativa == padre.ruta_relativa)
                    ciclo = pila[inicio:] + [padre]
                    errores.append(_error("E04", nodo, "ciclo: " + " -> ".join(item.referencia for item in ciclo), "Rompe el ciclo haciendo que cada hijo apunte a un rango superior.", campo="padre"))
                break
        pila.pop()
        estado[clave] = 2

    for nodo in arbol.nodos:
        if nodo.cosmos in NIVELES_SOLIDOS and estado.get(nodo.ruta_relativa, 0) == 0:
            visitar(nodo)
    return errores


def _comprobar_e05(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    galaxias = [nodo for nodo in arbol.nodos if nodo.cosmos == "galaxia"]
    if len(galaxias) == 1:
        return []
    rutas = ", ".join(nodo.ruta_relativa for nodo in galaxias) or "ninguna"
    return [_error("E05", galaxias[0] if galaxias else None, f"se esperaba exactamente una galaxia; hay {len(galaxias)} ({rutas})", "Conserva una sola galaxia raíz.")]


def _comprobar_e06(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    grupos: dict[tuple[str, str], list[Nodo]] = defaultdict(list)
    for nodo in arbol.nodos:
        padre = nodo.datos.get("padre")
        if nodo.cosmos in NIVELES_SOLIDOS[1:] and isinstance(padre, str):
            grupos[(padre, nodo.nombre)].append(nodo)
    errores = []
    for (padre, nombre), nodos in grupos.items():
        if len(nodos) > 1:
            rutas = ", ".join(nodo.ruta_relativa for nodo in nodos)
            errores.append(_error("E06", nodos[1], f"nombre duplicado entre hermanos {nombre!r} bajo {padre}: {rutas}", "Renombra uno de los hermanos.", campo="nombre"))
    return errores


def _comprobar_e07(arbol: Arbol, config: Configuracion, __: Path) -> list[ErrorValidacion]:
    errores = []
    for nodo in arbol.nodos:
        if not nodo.resumen:
            errores.append(_error("E07", nodo, "resumen ausente", "Añade un resumen informativo.", campo="resumen"))
        elif len(nodo.resumen) > config.resumen:
            errores.append(_error("E07", nodo, f"resumen de {len(nodo.resumen)} caracteres; máximo {config.resumen}", "Recorta el resumen sin describir a los hijos.", campo="resumen"))
    return errores


def _comprobar_e08(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    errores = []
    for nodo in arbol.nodos:
        palabras_nombre = set(_normalizar(nodo.nombre.replace("-", " ")).split())
        palabras_resumen = set(_normalizar(nodo.resumen).split())
        no_informa = bool(nodo.resumen) and (
            _normalizar(nodo.resumen).replace(" ", "") == _normalizar(nodo.nombre).replace(" ", "")
            or bool(palabras_resumen) and palabras_resumen <= palabras_nombre | PALABRAS_VACIAS_E08
        )
        if no_informa:
            errores.append(_error("E08", nodo, "el resumen repite el nombre o solo añade palabras vacías", "Explica el propósito del nodo en una línea concreta.", campo="resumen"))
    return errores


def _comprobar_e09(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    return [
        _error("E09", nodo, f"nivel desconocido: {nodo.datos.get('cosmos')!r}", "Usa uno de los 16 niveles definidos por COSMOS.", campo="cosmos")
        for nodo in arbol.nodos
        if nodo.cosmos not in NIVELES_VALIDOS
    ]


def _comprobar_e10(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    errores = []
    for nodo in arbol.nodos:
        if nodo.cosmos not in NIVELES_AGUA:
            continue
        moja = nodo.datos.get("moja")
        valido = isinstance(moja, list) and all(isinstance(patron, str) and patron for patron in moja)
        if valido and nodo.cosmos not in {"rio", "lluvia"} and not moja:
            valido = False
        if valido and nodo.cosmos == "oceano" and moja != ["**"]:
            valido = False
        if not valido:
            errores.append(_error("E10", nodo, "agua sin alcance válido", "Declara 'moja' como lista no vacía; océano usa ['**'] y solo río/lluvia admiten [].", campo="moja"))
    return errores


def _comprobar_e11(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    return [
        _error("E11", nodo, "océano encubierto: solo 'oceano' puede usar moja: ['**']", "Acota el glob o declara un océano y asume su coste.", campo="moja")
        for nodo in arbol.nodos
        if nodo.cosmos in NIVELES_AGUA and nodo.cosmos != "oceano" and nodo.datos.get("moja") == ["**"]
    ]


def _comprobar_e12(arbol: Arbol, config: Configuracion, __: Path) -> list[ErrorValidacion]:
    oceanos = [nodo for nodo in arbol.nodos if nodo.cosmos == "oceano"]
    if len(oceanos) <= config.oceanos:
        return []
    return [_error("E12", oceanos[config.oceanos], f"hay {len(oceanos)} océanos; máximo configurado {config.oceanos}", "Reduce el alcance de reglas globales o cambia el umbral conscientemente.")]


def _comprobar_e13(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    por_referencia: dict[str, list[Nodo]] = defaultdict(list)
    for nodo in arbol.nodos:
        por_referencia[nodo.referencia].append(nodo)
    errores = []
    for nodo in arbol.nodos:
        if nodo.cosmos not in NIVELES_ADJUNTOS:
            continue
        campo = "ilumina" if nodo.cosmos == "estrella" else "orbita"
        referencia = nodo.datos.get(campo)
        destinos = por_referencia.get(referencia, []) if isinstance(referencia, str) else []
        correcto = destinos and (
            (nodo.cosmos == "estrella" and all(destino.cosmos in NIVELES_SOLIDOS for destino in destinos))
            or (nodo.cosmos == "luna" and all(destino.cosmos == "planeta" for destino in destinos))
        )
        if not correcto:
            errores.append(_error("E13", nodo, f"adjunto colgado del aire o de tipo incorrecto: {campo}={referencia!r}", "Apunta la estrella a un sólido o la luna a un planeta existente.", campo=campo))
    return errores


def _comprobar_e14(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    por_solido: dict[str, list[Nodo]] = defaultdict(list)
    for nodo in arbol.nodos:
        if nodo.cosmos == "estrella" and isinstance(nodo.datos.get("ilumina"), str):
            por_solido[nodo.datos["ilumina"]].append(nodo)
    return [
        _error("E14", nodos[1], f"{len(nodos)} estrellas iluminan {solido}: " + ", ".join(n.ruta_relativa for n in nodos), "Consolida el contexto en una sola estrella.", campo="ilumina")
        for solido, nodos in por_solido.items()
        if len(nodos) > 1
    ]


def _comprobar_e15(arbol: Arbol, _: Configuracion, indice: Path) -> list[ErrorValidacion]:
    esperado = generar_indice(arbol)
    try:
        actual = indice.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        actual = None
    if actual == esperado:
        return []
    return [_error("E15", None, f"índice desincronizado: {indice}", "Ejecuta 'cosmos generar'; no edites el índice a mano.", ruta=str(indice))]


def _comprobar_e16(arbol: Arbol, config: Configuracion, _: Path) -> list[ErrorValidacion]:
    medicion = medir_arbol(arbol, metodo=config.metodo, presupuesto=config.entrada)
    if medicion.entrada <= config.entrada:
        return []
    caros = ", ".join(f"{parte.nombre} ({parte.tokens})" for parte in medicion.detalle_entrada[:3])
    return [_error("E16", None, f"contexto de entrada {medicion.entrada} tokens > {config.entrada}; más caros: {caros}", "Ejecuta 'cosmos medir --detalle' y reduce las partes más caras.", ruta="presupuesto")]


def _shingles(nodo: Nodo) -> set[tuple[str, str, str, str]]:
    palabras = [palabra for palabra in _normalizar(cuerpo(nodo)).split() if palabra not in PALABRAS_VACIAS_E17]
    return {tuple(palabras[indice:indice + 4]) for indice in range(max(0, len(palabras) - 3))}


def _siempre_cargados(arbol: Arbol) -> list[Nodo]:
    referencias_galaxia = {nodo.referencia for nodo in arbol.nodos if nodo.cosmos == "galaxia"}
    return [
        nodo
        for nodo in arbol.nodos
        if nodo.cosmos in {"galaxia", "oceano"}
        or (nodo.cosmos == "estrella" and nodo.datos.get("ilumina") in referencias_galaxia)
    ]


def _comprobar_e17(arbol: Arbol, config: Configuracion, __: Path) -> list[ErrorValidacion]:
    nodos = sorted(_siempre_cargados(arbol), key=lambda nodo: nodo.ruta_relativa)
    errores = []
    for indice, primero in enumerate(nodos):
        a = _shingles(primero)
        if not a:
            continue
        for segundo in nodos[indice + 1:]:
            b = _shingles(segundo)
            union = a | b
            similitud = len(a & b) / len(union) if union else 0.0
            if similitud > config.umbral_solapamiento:
                frases = [" ".join(shingle) for shingle in sorted(a & b)[:3]]
                errores.append(_error("E17", segundo, f"solapamiento {similitud:.1%} entre {primero.ruta_relativa} y {segundo.ruta_relativa}; tramos: " + "; ".join(frases), "Consolida la política en un solo nodo siempre cargado o separa sus responsabilidades."))
    return errores


def _comprobar_e18(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    por_nombre: dict[str, list[Nodo]] = defaultdict(list)
    for nodo in arbol.nodos:
        if nodo.cosmos in NIVELES_APLANADOS:
            por_nombre[nodo.nombre].append(nodo)
    errores = []
    for nombre, nodos in por_nombre.items():
        if len(nodos) > 1:
            for primero, segundo in zip(nodos, nodos[1:]):
                errores.append(_error("E18", segundo, f"colisión al aplanar {nombre!r}: {primero.ruta_cosmos} y {segundo.ruta_cosmos}", "Renombra una de las dos skills; la vista plana exige nombres globalmente únicos.", campo="nombre"))
    return errores


def _comprobar_e19(arbol: Arbol, config: Configuracion, __: Path) -> list[ErrorValidacion]:
    problemas = errores_vista(
        arbol,
        config.destino_compilacion,
        config.manifiesto_compilacion,
        config.modo_compilacion,
        config_path=config.ruta,
    )
    return [
        _error(
            "E19",
            None,
            f"vista plana desincronizada: {problema}",
            "Ejecuta 'cosmos compilar'; no edites la vista plana a mano.",
            ruta=str(config.destino_compilacion),
        )
        for problema in problemas
    ]


Comprobacion = Callable[[Arbol, Configuracion, Path], list[ErrorValidacion]]
COMPROBACIONES: tuple[Comprobacion, ...] = (
    _comprobar_e00, _comprobar_e01, _comprobar_e02, _comprobar_e03, _comprobar_e04,
    _comprobar_e05, _comprobar_e06, _comprobar_e07, _comprobar_e08, _comprobar_e09,
    _comprobar_e10, _comprobar_e11, _comprobar_e12, _comprobar_e13, _comprobar_e14,
    _comprobar_e15, _comprobar_e16, _comprobar_e17, _comprobar_e18,
    _comprobar_e19,
)


def validar_arbol(
    arbol: Arbol,
    *,
    configuracion: Configuracion | None = None,
    indice: str | Path | None = None,
    comprobaciones: Iterable[Comprobacion] | None = None,
    omitir_codigos: frozenset[str] = frozenset(),
) -> ResultadoValidacion:
    config = configuracion or Configuracion(arbol=arbol.raiz, indice=arbol.raiz / "COSMOS.md")
    ruta_indice = Path(indice) if indice is not None else config.indice
    errores: list[ErrorValidacion] = []
    for comprobacion in COMPROBACIONES if comprobaciones is None else comprobaciones:
        errores.extend(error for error in comprobacion(arbol, config, ruta_indice) if error.codigo not in omitir_codigos)
    errores.sort(key=lambda error: (error.codigo, error.ruta, error.linea or 0, error.mensaje))
    return ResultadoValidacion(errores, configuracion_por_defecto=not config.encontrada)


def formatear_validacion(resultado: ResultadoValidacion) -> str:
    estado = "verde" if resultado.valido else "rojo"
    cantidad = len(resultado.errores)
    sufijo = " (presupuesto por defecto: no hay cosmos.toml)" if resultado.configuracion_por_defecto else ""
    lineas = [f"COSMOS  {estado}  {cantidad} errores{sufijo}"]
    for error in resultado.errores:
        ubicacion = error.ruta + (f":{error.linea}" if error.linea is not None else "")
        lineas.extend(["", f"{error.codigo}  {ubicacion}", f"     {error.mensaje}", f"     {error.accion}"])
    return "\n".join(lineas) + "\n"


def validacion_json(resultado: ResultadoValidacion) -> str:
    return json.dumps(
        {
            "valido": resultado.valido,
            "codigo_salida": resultado.codigo_salida,
            "configuracion_por_defecto": resultado.configuracion_por_defecto,
            "errores": [error.como_dict() for error in resultado.errores],
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
