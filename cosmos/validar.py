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
from .medir import medir_casos
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


PALABRAS_GRAMATICALES = {
    "a", "al", "algo", "and", "ante", "aunque", "con", "como", "cuando", "cuyo",
    "de", "del", "donde", "e", "el", "en", "era", "eran", "es", "esa", "esas",
    "ese", "eso", "esos", "esta", "estas", "este", "esto", "estos", "for", "fue",
    "ha", "han", "hasta", "in", "la", "las", "le", "les", "lo", "los", "mientras",
    "ni", "no", "o", "of", "on", "para", "pero", "por", "porque", "que", "se",
    "sea", "si", "sin", "son", "su", "sus", "the", "to", "u", "un", "una", "y",
    "ya",
}
# Nombrar el nivel al que el nodo ya pertenece no informa de nada.
PALABRAS_TAXONOMIA = {
    "casa", "casas", "ciudad", "ciudades", "continente", "continentes", "cosmos",
    "estrella", "estrellas", "galaxia", "lago", "lagos", "lluvia", "luna", "lunas",
    "mar", "mares", "nivel", "niveles", "nodo", "nodos", "oceano", "pais", "paises",
    "planeta", "planetas", "provincia", "provincias", "pueblo", "pueblos", "rio",
    "rios", "sistema", "sistemas", "skill", "skills", "solar",
}
# Comodines que caben en cualquier ficha, y por eso no distinguen ninguna.
PALABRAS_RELLENO = {
    "ademas", "alguna", "algunas", "alguno", "algunos", "alli", "aqui", "bien",
    "cada", "cosa", "cosas", "cualquier", "cualquiera", "forma", "formas", "general",
    "generales", "generico", "genericos", "hacer", "hay", "mal", "mas", "menos",
    "misma", "mismas", "mismo", "mismos", "modo", "modos", "muy", "nueva", "nuevas",
    "nuevo", "nuevos", "otra", "otras", "otro", "otros", "propia", "propio", "ser",
    "tambien", "tener", "tiene", "tipo", "tipos", "toda", "todas", "todo", "todos",
    "varias", "varios",
}
PALABRAS_VACIAS_E08 = PALABRAS_GRAMATICALES | PALABRAS_TAXONOMIA | PALABRAS_RELLENO
PALABRAS_VACIAS_E17 = PALABRAS_GRAMATICALES

# Corpus normativo de sondas de E11 (NUCLEO §9). Ninguna familia de ficheros sin
# representar: con extensión y sin ella, en raíz y anidadas, ocultas y visibles.
SONDAS_E11 = (
    "main.py",
    "src/app/main.py",
    "tests/test_x.py",
    "web/index.html",
    "docs/guia.md",
    "Makefile",
    "src/Makefile",
    "LICENSE",
    "x",
    ".gitignore",
    "a/b/c/d/e.txt",
    "deep/nested/very/long/path/file.min.js",
)
# E17: niveles que pueden estar en contexto a la vez sin que nadie los invoque.
NIVELES_CO_CARGABLES = frozenset({"oceano", "mar", "lago", "estrella"})
MINIMO_PALABRAS_AFIRMACION = 4
MINIMO_PALABRAS_COMPARTIDAS = 3
MARCAS_MARKDOWN = re.compile(r"[`*_>#|\[\]]")
CORTES_DE_FRASE = re.compile(r"[.;:\n]+")
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
# Campos permitidos pero nunca obligatorios. 'usa' declara con qué se trabaja junto
# (spec/COMPOSICION.md): un nodo sin vecinos es perfectamente válido, y forzarlo
# llenaría el árbol de relaciones inventadas para rellenar un campo.
CAMPOS_OPCIONALES = {nivel: {"usa"} for nivel in NIVELES_SOLIDOS}


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
            permitidos = CAMPOS_COMUNES | CAMPOS_POR_NIVEL[nivel] | CAMPOS_OPCIONALES.get(nivel, set())
            for campo in sorted(set(nodo.datos) - permitidos):
                errores.append(_error("E00", nodo, f"campo no permitido para {nivel}: {campo!r}", "Elimina el campo o mueve la información al cuerpo Markdown.", campo=campo))
            for campo in CAMPOS_POR_NIVEL[nivel] - {"padre"}:
                if campo not in nodo.datos:
                    errores.append(_error("E00", nodo, f"falta el campo obligatorio {campo!r}", f"Añade {campo!r} al frontmatter."))
            for campo, valor in nodo.datos.items():
                if campo in {"moja", "usa"} and not isinstance(valor, list):
                    errores.append(_error("E00", nodo, f"{campo!r} debe ser una lista de texto", "Usa una lista YAML de escalares.", campo=campo))
                elif campo not in {"moja", "usa"} and not isinstance(valor, str):
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


# E04 («ciclo») está RETIRADA a propósito; su hueco no se reutiliza (NUCLEO §1).
#
# Ningún árbol legal puede producir un ciclo: para todo sólido distinto de la galaxia
# `ruta(n) = ruta(padre(n)) + "/" + nombre(n)` con `nombre` de longitud >= 1, luego la
# ruta crece estrictamente al subir y un ciclo se contradice a sí mismo. Si el padre no
# resuelve, salta E02 antes. La comprobación que había aquí no la podía disparar ningún
# árbol y su test la fingía subclasando `Nodo` para cambiar la identidad — un efecto
# provocado por un atajo, que no es un efecto reproducible.
#
# En su lugar se vigila la PREMISA del teorema, que sí es falsable:
# `test_canario_la_identidad_es_la_ruta_completa` mide que la ruta crece, y
# `test_meta_el_canario_de_aciclicidad_salta_si_la_identidad_cambia` sustituye la
# identidad y exige que el canario se ponga rojo.


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
        if not nodo.resumen:
            continue  # el resumen ausente lo dice E07; aquí solo se juzga el que hay
        del_nombre = set(_normalizar(nodo.nombre.replace("-", " ")).split())
        contenido = {
            palabra
            for palabra in _normalizar(nodo.resumen).split()
            if palabra not in PALABRAS_VACIAS_E08 and palabra not in del_nombre
        }
        if not contenido:
            errores.append(
                _error(
                    "E08",
                    nodo,
                    "el resumen no aporta ninguna palabra con contenido fuera del nombre",
                    "Di qué hace el nodo con palabras que no valdrían para cualquier otro.",
                    campo="resumen",
                )
            )
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


def _glob_a_regex(patron: str) -> re.Pattern[str]:
    """Traduce un glob de 'moja' a expresión regular. Semántica normativa: NUCLEO §9."""

    patron = patron[2:] if patron.startswith("./") else patron
    partes: list[str] = []
    indice = 0
    while indice < len(patron):
        if patron.startswith("**/", indice):
            partes.append("(?:[^/]+/)*")  # cero o más directorios completos
            indice += 3
        elif patron.startswith("**", indice):
            partes.append(".*")
            indice += 2
        elif patron[indice] == "*":
            partes.append("[^/]*")  # nunca cruza un separador
            indice += 1
        elif patron[indice] == "?":
            partes.append("[^/]")
            indice += 1
        else:
            partes.append(re.escape(patron[indice]))
            indice += 1
    return re.compile("".join(partes) + r"\Z")


def _sin_anclaje(patron: str) -> bool:
    """Un patrón sin un solo carácter alfanumérico no nombra ninguna región."""

    return not any(caracter.isalnum() for caracter in patron)


def cobertura_total(patrones: list[str]) -> bool:
    """¿El conjunto de globs casa con TODAS las sondas del corpus normativo?"""

    expresiones = [_glob_a_regex(patron) for patron in patrones]
    if not expresiones:
        return False
    return all(any(expresion.match(sonda) for expresion in expresiones) for sonda in SONDAS_E11)


def _comprobar_e11(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    accion = "Acota el glob nombrando la región, o declara un océano y asume su coste."
    errores = []
    for nodo in arbol.nodos:
        if nodo.cosmos not in NIVELES_AGUA or nodo.cosmos == "oceano":
            continue
        moja = nodo.datos.get("moja")
        if not isinstance(moja, list) or not all(isinstance(patron, str) and patron for patron in moja):
            continue  # el alcance mal formado lo dice E10
        sin_anclaje = [patron for patron in moja if _sin_anclaje(patron)]
        if sin_anclaje:
            mensaje = f"océano encubierto: {sin_anclaje[0]!r} no nombra ninguna región (ni una letra ni un dígito)"
        elif cobertura_total(moja):
            mensaje = f"océano encubierto: {moja} cubre las {len(SONDAS_E11)} sondas del corpus normativo"
        else:
            continue
        errores.append(_error("E11", nodo, mensaje, accion, campo="moja"))
    return errores


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
    casos = medir_casos(arbol, metodo=config.metodo, presupuesto=config.entrada)
    medicion = casos.peor
    # NUCLEO §3: se compara lo que se paga sin invocar nada, y el agua que entra
    # por `paths:` se paga sin invocarla. Comparar solo `entrada` dejaba fuera del
    # presupuesto todo el coste de los mares (H14).
    if medicion.entrada_con_agua <= config.entrada:
        return []
    partes = list(medicion.detalle_entrada) + list(medicion.detalle_agua)
    caros = ", ".join(
        f"{parte.nombre} ({parte.tokens})"
        for parte in sorted(partes, key=lambda parte: parte.tokens, reverse=True)[:3]
    )
    excede = medicion.entrada_con_agua - config.entrada
    culpable = casos.peor_nicho or "sin nichos"
    return [_error("E16", None, f"peor nicho {culpable}: entrada {medicion.entrada} + agua condicional {medicion.agua} = {medicion.entrada_con_agua} tokens > {config.entrada}; excede en {excede} tokens; más caros: {caros}", "Ejecuta 'cosmos medir --detalle' y reduce las partes más caras del nicho culpable o el cuerpo de los mares.", ruta="presupuesto")]


def _afirmaciones(nodo: Nodo) -> list[tuple[frozenset[str], str]]:
    """Las frases del cuerpo con al menos cuatro palabras con contenido (NUCLEO §10)."""

    texto = MARCAS_MARKDOWN.sub(" ", cuerpo(nodo))
    afirmaciones: list[tuple[frozenset[str], str]] = []
    for frase in CORTES_DE_FRASE.split(texto):
        palabras = frozenset(
            palabra for palabra in _normalizar(frase).split() if palabra not in PALABRAS_VACIAS_E17
        )
        if len(palabras) >= MINIMO_PALABRAS_AFIRMACION:
            afirmaciones.append((palabras, " ".join(frase.split())))
    return afirmaciones


def _co_cargables(arbol: Arbol) -> list[Nodo]:
    """Los nodos que se pagan a la vez sin que nadie los invoque (NUCLEO §10).

    Océanos siempre; mares y lagos en cuanto su `moja` casa con un fichero que se
    toca; estrellas al descender a su sólido. Ciudades y pueblos se invocan y se
    pagan una vez: su duplicación la vigila E18, no esta.
    """

    return sorted(
        (nodo for nodo in arbol.nodos if nodo.cosmos in NIVELES_CO_CARGABLES and cuerpo(nodo)),
        key=lambda nodo: nodo.ruta_relativa,
    )


def solape_de_afirmaciones(primero: Nodo, segundo: Nodo) -> tuple[float, str, str]:
    """La afirmación más repetida entre dos nodos, y las dos frases concretas.

    Se mide afirmación a afirmación, no documento a documento: la duplicación que
    engorda un prólogo es la misma política dicha dos veces con otras palabras, y a
    escala de documento se diluye hasta cero. Solo cuentan los pares que comparten al
    menos tres palabras con contenido; por debajo de eso es coincidencia de
    vocabulario, no política duplicada.
    """

    mejor = (0.0, "", "")
    afirmaciones_segundo = _afirmaciones(segundo)
    for palabras_a, texto_a in _afirmaciones(primero):
        for palabras_b, texto_b in afirmaciones_segundo:
            comunes = palabras_a & palabras_b
            if len(comunes) < MINIMO_PALABRAS_COMPARTIDAS:
                continue
            similitud = len(comunes) / len(palabras_a | palabras_b)
            if similitud > mejor[0]:
                mejor = (similitud, texto_a, texto_b)
    return mejor


def _comprobar_e17(arbol: Arbol, config: Configuracion, __: Path) -> list[ErrorValidacion]:
    nodos = _co_cargables(arbol)
    errores = []
    for indice, primero in enumerate(nodos):
        for segundo in nodos[indice + 1:]:
            similitud, frase_a, frase_b = solape_de_afirmaciones(primero, segundo)
            if similitud > config.umbral_solapamiento:
                errores.append(
                    _error(
                        "E17",
                        segundo,
                        f"solapamiento {similitud:.1%} entre {primero.referencia} y {segundo.referencia}; "
                        f"«{frase_a}» ≈ «{frase_b}»",
                        "Deja la política en un solo nodo co-cargable y que el otro la referencie.",
                    )
                )
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
        nichos=config.nichos,
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


def _comprobar_e20(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    """E20 — `usa:` apunta a un nodo que existe, y no a uno mismo.

    `usa:` es la composición que pide `spec/COMPOSICION.md`: declara con qué se
    trabaja habitualmente **sin arrastrar carga**. Por eso se valida su destino pero
    no se carga nada: una dependencia automática sería una cadena de arrastre —cargas
    uno y vienen cinco— que es como un gestor de paquetes acaba trayendo medio
    internet.

    Lo que sí evita esta comprobación es el fallo silencioso: un `usa:` que apunta a
    un nicho renombrado no da error en ningún sitio y deja al lector buscando algo
    que ya no se llama así.
    """

    rutas = {nodo.referencia for nodo in arbol.nodos}
    rutas |= {nodo.ruta_cosmos for nodo in arbol.nodos if hasattr(nodo, "ruta_cosmos")}
    nombres = {nodo.nombre for nodo in arbol.nodos if nodo.cosmos in NIVELES_SOLIDOS}

    errores: list[ErrorValidacion] = []
    for nodo in arbol.nodos:
        vecinos = nodo.datos.get("usa")
        if vecinos is None:
            continue
        if not isinstance(vecinos, list):
            errores.append(_error("E20", nodo, "'usa' debe ser una lista de rutas",
                                  "Escríbelo como lista, una ruta por línea."))
            continue
        for vecino in vecinos:
            destino = str(vecino).strip()
            if destino == nodo.nombre or destino == nodo.referencia:
                errores.append(_error("E20", nodo, f"'usa' apunta a sí mismo: {destino}",
                                      "Un nodo no se acompaña de sí mismo; quita la línea."))
            elif destino not in rutas and destino not in nombres:
                errores.append(_error("E20", nodo, f"vecino inexistente en 'usa': {destino}",
                                      "Corrige la ruta o quita la línea: un vecino que no existe "
                                      "manda a buscar algo que ya no se llama así."))
    return errores


Comprobacion = Callable[[Arbol, Configuracion, Path], list[ErrorValidacion]]
COMPROBACIONES: tuple[Comprobacion, ...] = (
    _comprobar_e00, _comprobar_e01, _comprobar_e02, _comprobar_e03,
    _comprobar_e05, _comprobar_e06, _comprobar_e07, _comprobar_e08, _comprobar_e09,
    _comprobar_e10, _comprobar_e11, _comprobar_e12, _comprobar_e13, _comprobar_e14,
    _comprobar_e15, _comprobar_e16, _comprobar_e17, _comprobar_e18,
    _comprobar_e19, _comprobar_e20,
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
