"""Modelo de nodos y parser restringido de frontmatter.

El parser acepta únicamente claves de primer nivel, escalares y listas de
escalares (en línea o en bloque). No intenta completar ni reinterpretar YAML.
"""

from __future__ import annotations

import ast
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


NIVELES_SOLIDOS = (
    "galaxia",
    "sistema-solar",
    "planeta",
    "continente",
    "pais",
    "provincia",
    "ciudad",
    "pueblo",
    "casa",
)
NIVELES_ADJUNTOS = ("estrella", "luna")
NIVELES_AGUA = ("oceano", "mar", "lago", "rio", "lluvia")
NIVELES_VALIDOS = frozenset(NIVELES_SOLIDOS + NIVELES_ADJUNTOS + NIVELES_AGUA)
RANGOS = {nivel: indice for indice, nivel in enumerate(NIVELES_SOLIDOS, start=1)}
PATRON_NOMBRE = re.compile(r"^[a-z0-9-]+$")


@dataclass(frozen=True)
class ErrorCarga:
    ruta: str
    linea: int | None
    mensaje: str


@dataclass
class Nodo:
    ruta: Path
    ruta_relativa: str
    datos: dict[str, Any]
    lineas: dict[str, int]
    contenido: str

    @property
    def cosmos(self) -> str:
        valor = self.datos.get("cosmos", "")
        return valor if isinstance(valor, str) else ""

    @property
    def nombre(self) -> str:
        valor = self.datos.get("nombre", "")
        return valor if isinstance(valor, str) else ""

    @property
    def resumen(self) -> str:
        valor = self.datos.get("resumen", "")
        return valor if isinstance(valor, str) else ""

    @property
    def referencia(self) -> str:
        return f"{self.cosmos}/{self.nombre}"

    def linea(self, campo: str) -> int | None:
        return self.lineas.get(campo)


@dataclass
class Arbol:
    raiz: Path
    nodos: list[Nodo] = field(default_factory=list)
    errores: list[ErrorCarga] = field(default_factory=list)

    def buscar(self, referencia: str) -> list[Nodo]:
        return [nodo for nodo in self.nodos if nodo.referencia == referencia]


@dataclass(frozen=True)
class Configuracion:
    entrada: int = 4000
    resumen: int = 120
    oceanos: int = 7
    galaxia_lineas: int = 40
    arbol: Path = Path(".")
    indice: Path = Path("COSMOS.md")
    encontrada: bool = False
    ruta: Path | None = None


class ErrorConfiguracion(ValueError):
    pass


def _quitar_comentario(texto: str) -> str:
    comilla: str | None = None
    escapado = False
    for indice, caracter in enumerate(texto):
        if escapado:
            escapado = False
            continue
        if caracter == "\\" and comilla == '"':
            escapado = True
            continue
        if caracter in ("'", '"'):
            if comilla is None:
                comilla = caracter
            elif comilla == caracter:
                comilla = None
            continue
        if caracter == "#" and comilla is None:
            return texto[:indice].rstrip()
    return texto.rstrip()


def _escalar(texto: str, ruta: str, linea: int) -> str:
    texto = texto.strip()
    if not texto:
        raise ValueError(f"{ruta}:{linea}: escalar vacío")
    if texto[0] in "[{" or texto[-1:] in "]}":
        raise ValueError(f"{ruta}:{linea}: estructura no permitida")
    if texto[0] in ("'", '"'):
        if len(texto) < 2 or texto[-1] != texto[0]:
            raise ValueError(f"{ruta}:{linea}: comilla sin cerrar")
        try:
            valor = ast.literal_eval(texto)
        except (SyntaxError, ValueError) as exc:
            raise ValueError(f"{ruta}:{linea}: escalar entrecomillado inválido") from exc
        if not isinstance(valor, str):
            raise ValueError(f"{ruta}:{linea}: solo se admiten escalares de texto")
        return valor
    return texto


def _separar_lista(texto: str, ruta: str, linea: int) -> list[str]:
    interior = texto[1:-1].strip()
    if not interior:
        return []
    partes: list[str] = []
    inicio = 0
    comilla: str | None = None
    escapado = False
    for indice, caracter in enumerate(interior):
        if escapado:
            escapado = False
            continue
        if caracter == "\\" and comilla == '"':
            escapado = True
            continue
        if caracter in ("'", '"'):
            if comilla is None:
                comilla = caracter
            elif comilla == caracter:
                comilla = None
        elif caracter == "," and comilla is None:
            partes.append(interior[inicio:indice])
            inicio = indice + 1
        elif caracter in "[{}]" and comilla is None:
            raise ValueError(f"{ruta}:{linea}: listas anidadas o mapas no permitidos")
    if comilla is not None:
        raise ValueError(f"{ruta}:{linea}: comilla sin cerrar")
    partes.append(interior[inicio:])
    if any(not parte.strip() for parte in partes):
        raise ValueError(f"{ruta}:{linea}: elemento vacío en lista")
    return [_escalar(parte, ruta, linea) for parte in partes]


def parsear_frontmatter(contenido: str, ruta: str) -> tuple[dict[str, Any], dict[str, int]]:
    """Parsea el subconjunto normativo o levanta ``ValueError`` con línea."""

    lineas_texto = contenido.splitlines()
    if not lineas_texto or lineas_texto[0].strip() != "---":
        raise ValueError(f"{ruta}:1: falta el delimitador inicial '---'")
    cierre = next(
        (i for i, texto in enumerate(lineas_texto[1:], start=1) if texto.strip() == "---"),
        None,
    )
    if cierre is None:
        raise ValueError(f"{ruta}:1: frontmatter sin delimitador de cierre")

    datos: dict[str, Any] = {}
    numeros: dict[str, int] = {}
    lista_pendiente: str | None = None
    for indice in range(1, cierre):
        numero = indice + 1
        original = lineas_texto[indice]
        sin_comentario = _quitar_comentario(original)
        if not sin_comentario.strip():
            continue

        indentacion = len(sin_comentario) - len(sin_comentario.lstrip(" "))
        texto = sin_comentario.strip()
        if indentacion:
            if lista_pendiente is None or not texto.startswith("-"):
                raise ValueError(f"{ruta}:{numero}: anidamiento o mapa no permitido")
            resto = texto[1:].strip()
            datos[lista_pendiente].append(_escalar(resto, ruta, numero))
            continue

        lista_pendiente = None
        if texto.startswith("-"):
            raise ValueError(f"{ruta}:{numero}: elemento de lista sin clave")
        if ":" not in texto:
            raise ValueError(f"{ruta}:{numero}: se esperaba 'clave: valor'")
        clave, valor_bruto = texto.split(":", 1)
        clave = clave.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", clave):
            raise ValueError(f"{ruta}:{numero}: clave inválida {clave!r}")
        if clave in datos:
            raise ValueError(f"{ruta}:{numero}: clave duplicada {clave!r}")
        valor_bruto = valor_bruto.strip()
        numeros[clave] = numero
        if not valor_bruto:
            datos[clave] = []
            lista_pendiente = clave
        elif valor_bruto.startswith("["):
            if not valor_bruto.endswith("]"):
                raise ValueError(f"{ruta}:{numero}: lista en línea sin cerrar")
            datos[clave] = _separar_lista(valor_bruto, ruta, numero)
        else:
            datos[clave] = _escalar(valor_bruto, ruta, numero)
    return datos, numeros


def cargar_arbol(raiz: str | Path, *, excluir: str | Path | None = None) -> Arbol:
    raiz_path = Path(raiz).resolve()
    arbol = Arbol(raiz=raiz_path)
    excluir_path = Path(excluir).resolve() if excluir is not None else None
    if not raiz_path.exists():
        arbol.errores.append(ErrorCarga(str(raiz_path), None, "la raíz del árbol no existe"))
        return arbol

    for ruta in sorted(raiz_path.rglob("*.md")):
        if excluir_path is not None and ruta.resolve() == excluir_path:
            continue
        try:
            contenido = ruta.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            arbol.errores.append(ErrorCarga(str(ruta), None, f"no se puede leer: {exc}"))
            continue
        if not contenido.startswith("---"):
            continue
        relativa = ruta.relative_to(raiz_path).as_posix()
        try:
            datos, lineas = parsear_frontmatter(contenido, relativa)
        except ValueError as exc:
            mensaje = str(exc)
            coincidencia = re.match(r"^.*?:(\d+):\s*(.*)$", mensaje)
            linea = int(coincidencia.group(1)) if coincidencia else None
            detalle = coincidencia.group(2) if coincidencia else mensaje
            arbol.errores.append(ErrorCarga(relativa, linea, detalle))
            continue
        arbol.nodos.append(Nodo(ruta, relativa, datos, lineas, contenido))
    return arbol


def cargar_configuracion(ruta: str | Path | None = None) -> Configuracion:
    ruta_path = Path(ruta or "cosmos.toml").resolve()
    if not ruta_path.exists():
        base = ruta_path.parent
        return Configuracion(arbol=base, indice=base / "COSMOS.md", ruta=ruta_path)
    try:
        datos = tomllib.loads(ruta_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ErrorConfiguracion(f"no se puede leer {ruta_path}: {exc}") from exc

    try:
        presupuesto = datos["presupuesto"]
        raiz = datos["raiz"]
        valores = {
            "entrada": presupuesto["entrada"],
            "resumen": presupuesto["resumen"],
            "oceanos": presupuesto["oceanos"],
            "galaxia_lineas": presupuesto["galaxia_lineas"],
        }
        arbol_rel = raiz["arbol"]
        indice_rel = raiz["indice"]
    except (KeyError, TypeError) as exc:
        raise ErrorConfiguracion(f"falta un umbral o ruta obligatoria en {ruta_path}: {exc}") from exc
    if any(not isinstance(valor, int) or valor < 0 for valor in valores.values()):
        raise ErrorConfiguracion("los umbrales deben ser enteros no negativos")
    if not isinstance(arbol_rel, str) or not isinstance(indice_rel, str):
        raise ErrorConfiguracion("raiz.arbol y raiz.indice deben ser texto")
    base = ruta_path.parent
    return Configuracion(
        **valores,
        arbol=(base / arbol_rel).resolve(),
        indice=(base / indice_rel).resolve(),
        encontrada=True,
        ruta=ruta_path,
    )
