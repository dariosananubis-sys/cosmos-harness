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
from .medir import medir_casos, veredicto_de_presupuesto
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
    "continente", "continentes", "cosmos",
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
NIVELES_APLANADOS = frozenset({"pueblo"})
# Campos permitidos pero nunca obligatorios. 'usa' declara con qué se trabaja junto
# (spec/COMPOSICION.md): un nodo sin vecinos es perfectamente válido, y forzarlo
# llenaría el árbol de relaciones inventadas para rellenar un campo.
CAMPOS_OPCIONALES = {nivel: {"usa"} for nivel in NIVELES_SOLIDOS}
# `origen: propio` declara que el pueblo es una herramienta propia (guion dentro del
# directorio), no una de GitHub: es la única excepción a la URL obligatoria de E21.
CAMPOS_OPCIONALES["pueblo"] = {"usa", "origen"}
# 'momento' separa el verbo que resuelve el encargo del que cuida el repositorio.
# Los dos existen igual y los dos se abren igual; lo que cambia es si su resumen se paga
# en cada sesión. Sin este campo, `enganchar` o `proyectar` cobraban su línea en todos
# los turnos de la vida del proyecto para ejecutarse una vez.
CAMPOS_OPCIONALES["rio"] = {"momento"}
MOMENTOS_DE_RIO = frozenset({"trabajo", "mantenimiento"})


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
        momento = nodo.datos.get("momento")
        if momento is not None and momento not in MOMENTOS_DE_RIO:
            errores.append(_error(
                "E00", nodo, f"'momento' inválido: {momento!r}",
                f"Usa uno de {sorted(MOMENTOS_DE_RIO)}, o quita el campo (por defecto 'trabajo').",
                campo="momento"))
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
    """E07 — `resumen` presente, ≤ N caracteres y en ASCII.

    Lo tercero era costumbre, no norma: 453 de 454 resúmenes iban sin acentos y uno no, en un
    océano (revisión B-29). El resumen es la línea que se paga en cada sesión y el tokenizador
    BPE parte cada carácter acentuado en una pieza aparte (`docs/CALIBRACION.md`); el cuerpo,
    que solo se paga al abrir el nodo, sí lleva acentos.
    """
    errores = []
    for nodo in arbol.nodos:
        if not nodo.resumen:
            errores.append(_error("E07", nodo, "resumen ausente", "Añade un resumen informativo.", campo="resumen"))
        elif len(nodo.resumen) > config.resumen:
            errores.append(_error("E07", nodo, f"resumen de {len(nodo.resumen)} caracteres; máximo {config.resumen}", "Recorta el resumen sin describir a los hijos.", campo="resumen"))
        elif not nodo.resumen.isascii():
            raros = "".join(sorted({c for c in nodo.resumen if not c.isascii()}))
            errores.append(_error("E07", nodo, f"resumen con caracteres fuera de ASCII ({raros}); se paga en cada sesión y cada acento cuesta una pieza más",
                                  "Escribe el resumen sin acentos ni signos especiales; el cuerpo sí los lleva.", campo="resumen"))
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
        _error("E09", nodo, f"nivel desconocido: {nodo.datos.get('cosmos')!r}", "Usa uno de los 14 niveles definidos por COSMOS.", campo="cosmos")
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
        elif nodo.cosmos == "lluvia" and moja:
            # La memoria se consulta, no se carga (GOAL §4). Un `moja` no vacío no
            # la hace aparecer sola, pero sí la mete en `agua_condicional` y la cobra:
            # dos entradas del registro sumaban 7.700 tokens al presupuesto de cada
            # sesión que tocara su terreno, sin cargarse nunca (H20).
            errores.append(
                _error(
                    "E10",
                    nodo,
                    "la memoria no se carga sola: 'moja' de una lluvia debe ser []",
                    "Deja 'moja: []'. El registro se consulta con rio/memoria; con alcance se paga y no se lee.",
                    campo="moja",
                )
            )
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


# La invariante del presupuesto, nombrada donde se define: el CLI necesita saber
# cuál es para consultar su válvula, y escribir "E16" en otro fichero es la clase
# de número a mano que este repositorio persigue.
INVARIANTE_PRESUPUESTO = "E16"


def _comprobar_e16(arbol: Arbol, config: Configuracion, _: Path) -> list[ErrorValidacion]:
    casos = medir_casos(arbol, metodo=config.metodo, presupuesto=config.entrada)
    medicion = casos.peor
    # NUCLEO §3: se compara lo que se paga sin invocar nada, y el agua que entra
    # por `paths:` se paga sin invocarla. Comparar solo `entrada` dejaba fuera del
    # presupuesto todo el coste de los mares (H14). El juez es único y vive en
    # `medir.veredicto_de_presupuesto`: aquí, en el CLI y en los guards de sesión.
    veredicto = veredicto_de_presupuesto(casos, config.entrada)
    # Trivalente de punta a punta (auditoría D-03). `cabe` es `True` / `False` / `None`,
    # y `None` —no había nada que medir— caía aquí por la rama de «excede» porque es
    # falsy: sobre un árbol vacío E16 afirmaba «0 tokens > 4000; excede en -4000». Un
    # «no lo sé» no es un exceso: el árbol vacío ya lo denuncia E05 (ninguna galaxia) y
    # `cosmos medir` sale 1 diciendo SIN MEDIR. E16 solo habla cuando ha medido.
    if veredicto.cabe is None or veredicto.cabe:
        return []
    partes = list(medicion.detalle_entrada) + list(medicion.detalle_agua)
    caros = ", ".join(
        f"{parte.nombre} ({parte.tokens})"
        for parte in sorted(partes, key=lambda parte: parte.tokens, reverse=True)[:3]
    )
    # El mensaje compara LO MISMO que el veredicto: la estimación más el margen calibrado.
    # Restar en crudo publicaba «3715 > 3800; excede en -85» mientras `medir` decía «+109»
    # sobre el mismo hecho (revisión R-06) — la rama hermana del D-03 que se arregló arriba.
    excede = veredicto.con_margen - config.entrada
    culpable = casos.peor_nicho or "sin nichos"
    margen = f" (estimación {medicion.entrada_con_agua} + margen calibrado {veredicto.margen_error * 100:.1f} %)".replace(".", ",") if veredicto.margen_error else ""
    return [_error("E16", None, f"peor nicho {culpable}: entrada {medicion.entrada} + agua condicional {medicion.agua} = {veredicto.con_margen} tokens{margen} > {config.entrada}; excede en {excede} tokens; más caros: {caros}", "Ejecuta 'cosmos medir --detalle' y reduce las partes más caras del nicho culpable o el cuerpo de los mares.", ruta="presupuesto")]


# Una URL de REPOSITORIO en la primera línea no vacía del cuerpo: esquema https, host con punto y
# al menos dos tramos de ruta (organización/proyecto). La versión anterior aceptaba la cadena
# `https://` en cualquier prosa y 10 pueblos pasaban por accidente (revisión R-18).
PATRON_URL = re.compile(r"^https://[A-Za-z0-9.-]+\.[A-Za-z]{2,}/[^/\s]+/[^/\s]+")
MARCADORES_URL = ("usuario/repo", "<", ">", "example.", "ejemplo.", "localhost", "127.0.0.1", "dominio.", "tu-")
VALORES_ORIGEN = frozenset({"propio"})


def url_de_repositorio(texto: str) -> str | None:
    """La URL de repositorio que exige `spec/PUEBLO.md` regla 1, o `None` si no la hay donde toca."""

    primera = next((linea.strip() for linea in texto.splitlines() if linea.strip()), "")
    coincidencia = PATRON_URL.match(primera)
    if coincidencia is None:
        return None
    url = coincidencia.group(0)
    if any(marcador in url.lower() for marcador in MARCADORES_URL):
        return None
    return url


def _comprobar_e21(arbol: Arbol, _: Configuracion, __: Path) -> list[ErrorValidacion]:
    """E21 — un pueblo nombra qué ejecutar: URL de repositorio (o `origen: propio`) y un bloque de código.

    `spec/PUEBLO.md` se titula «normativo», dice «si falta una, no está terminado» y nadie lo
    comprobaba: 28 de 247 pueblos no nombraban ningún repositorio y el criterio 1 de
    `spec/UNIVERSO.md` («se ejecuta») es eliminatorio (auditoría A-06). Es la infracción
    literal del corolario 1 de GOAL §2: una regla que hay que recordar está mal puesta. Las
    herramientas propias —guion en el directorio, sin GitHub— son legítimas y la spec no las
    contemplaba: lo declaran con `origen: propio` en vez de fingir una URL. La comparación
    con el rival y el apartado de avisos siguen siendo prosa: `cosmos estado` los cuenta.
    """

    errores = []
    for nodo in arbol.nodos:
        if nodo.cosmos != "pueblo":
            continue
        origen = nodo.datos.get("origen")
        if origen is not None and origen not in VALORES_ORIGEN:
            errores.append(_error("E21", nodo, f"origen desconocido: {origen!r}; solo se admite 'propio'",
                                  "Quita el campo o escribe 'origen: propio' si la herramienta no vive en un repositorio ajeno.",
                                  campo="origen"))
            continue
        texto = cuerpo(nodo)
        if origen != "propio" and url_de_repositorio(texto) is None:
            errores.append(_error("E21", nodo, "el pueblo no nombra qué ejecutar: sin URL de repositorio en la primera línea del cuerpo ni 'origen: propio'",
                                  "Pon la URL literal del repositorio (https://host/organizacion/proyecto) en la primera línea del cuerpo (spec/PUEBLO.md), o declara 'origen: propio' si el guion vive aquí."))
        if origen == "propio" and not any(p.is_file() and p.name != "SKILL.md" for p in nodo.ruta.parent.rglob("*")):
            # R-37: `origen: propio` era un indulto autodeclarado. La spec lo define como «un guion
            # que vive en el directorio del pueblo»: sin ningún fichero al lado, no hay guion.
            errores.append(_error("E21", nodo, "'origen: propio' sin ningún guion en el directorio del pueblo: prosa que no se ejecuta",
                                  "Deja el guion junto al SKILL.md (scripts/...) o cataloga la herramienta con su URL.", campo="origen"))
        if "```" not in texto:
            errores.append(_error("E21", nodo, "sin bloque de código: no hay nada que copiar y pegar",
                                  "Añade la instalación y un uso mínimo en bloques de código (spec/PUEBLO.md, reglas 2 y 3)."))
    return errores


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
    toca; estrellas al descender a su sólido. Los pueblos se invocan y se
    pagan una vez: su duplicación la vigila E18, no esta.
    """

    return sorted(
        (nodo for nodo in arbol.nodos if nodo.cosmos in NIVELES_CO_CARGABLES and cuerpo(nodo)),
        key=lambda nodo: nodo.ruta_relativa,
    )


def solape_de_afirmaciones(
    primero: Nodo, segundo: Nodo, afirmaciones: dict[int, list[tuple[frozenset[str], str]]] | None = None
) -> tuple[float, str, str]:
    """La afirmación más repetida entre dos nodos, y las dos frases concretas.

    Se mide afirmación a afirmación, no documento a documento: la duplicación que
    engorda un prólogo es la misma política dicha dos veces con otras palabras, y a
    escala de documento se diluye hasta cero. Solo cuentan los pares que comparten al
    menos tres palabras con contenido; por debajo de eso es coincidencia de
    vocabulario, no política duplicada.
    """

    mejor = (0.0, "", "")
    # `afirmaciones` es la caché por nodo que construye E17: sin ella, cada pareja
    # re-parseaba los dos cuerpos (regex + Unicode + casefold) y a 5× la galaxia eran
    # 20.880 parseos donde hacen falta 145 (auditoría D-06).
    if afirmaciones is None:
        afirmaciones = {}
    # `dict.setdefault(k, f(x))` evalúa f(x) SIEMPRE: la primera versión de esta caché hacía
    # 33 parseos MÁS que sin caché, y las 320 pruebas lo firmaron (revisión R-47 / D-06).
    # Desde hoy hay una prueba de conteo de llamadas (`tests/test_escala.py`).
    if id(segundo) not in afirmaciones:
        afirmaciones[id(segundo)] = _afirmaciones(segundo)
    if id(primero) not in afirmaciones:
        afirmaciones[id(primero)] = _afirmaciones(primero)
    afirmaciones_segundo = afirmaciones[id(segundo)]
    for palabras_a, texto_a in afirmaciones[id(primero)]:
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
    cache: dict[int, list[tuple[frozenset[str], str]]] = {id(n): _afirmaciones(n) for n in nodos}
    for indice, primero in enumerate(nodos):
        for segundo in nodos[indice + 1:]:
            similitud, frase_a, frase_b = solape_de_afirmaciones(primero, segundo, cache)
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
    _comprobar_e19, _comprobar_e20, _comprobar_e21,
)


def codigos_comprobados() -> tuple[str, ...]:
    """Los códigos que `validar` recorre, sacados de las propias comprobaciones.

    La ayuda del CLI y el README decían «E00-E19» con E20 ya existiendo, y el
    desfase estaba anotado en un parte de commit desde hacía días sin cerrarse
    (F14). Un número copiado a mano envejece en silencio: se genera.
    """

    return tuple(sorted(f"E{c.__name__.removeprefix('_comprobar_e')}" for c in COMPROBACIONES))


def rango_comprobado() -> str:
    """`E00–E20`: el intervalo que la ayuda muestra, sin escribirlo a mano."""

    codigos = codigos_comprobados()
    return f"{codigos[0]}–{codigos[-1]}"


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
