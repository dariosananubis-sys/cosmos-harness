"""Modelo de nodos y parser restringido de frontmatter.

El parser acepta únicamente claves de primer nivel, escalares y listas de
escalares (en línea o en bloque). No intenta completar ni reinterpretar YAML.
"""

from __future__ import annotations

from contextlib import contextmanager

import tempfile

import os

import ast
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Siete sólidos. `ciudad` y `casa` se retiraron el 2026-09-01 (H20): ni un nodo en
# la galaxia ni en el ejemplo, ni un test que los creara, y 209 skills atómicas de
# un solo fichero. Un nivel que nunca ha agrupado nada no es una reserva, es spec
# sin ejercitar. Si vuelve a hacer falta una skill con partes que se cargan por
# separado, se reintroduce con el nodo que lo justifique delante, no antes.
NIVELES_SOLIDOS = (
    "galaxia",
    "sistema-solar",
    "planeta",
    "continente",
    "pais",
    "provincia",
    "pueblo",
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
        if self.cosmos in NIVELES_SOLIDOS:
            return self.ruta_cosmos
        return f"{self.cosmos}/{self.nombre}"

    @property
    def ruta_cosmos(self) -> str:
        """Ruta normativa del sólido; el agua conserva identidad nivel/nombre."""

        if self.cosmos == "galaxia":
            return ""
        padre = self.datos.get("padre")
        if self.cosmos in NIVELES_SOLIDOS and isinstance(padre, str):
            return f"{padre}/{self.nombre}" if padre else self.nombre
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
    umbral_solapamiento: float = 0.25
    metodo: str = "aprox"
    arbol: Path = Path(".")
    indice: Path = Path("COSMOS.md")
    # Raíz hermana opcional. El registro no cuelga de la galaxia (es otra puerta),
    # pero sus entradas son nodos y el validador tiene que verlas.
    registro: Path | None = None
    destino_compilacion: Path = Path(".claude/skills")
    modo_compilacion: str = "symlink"
    manifiesto_compilacion: Path = Path(".cosmos/compilado.json")
    nichos: tuple[str, ...] | None = None
    encontrada: bool = False
    ruta: Path | None = None


class ErrorConfiguracion(ValueError):
    pass


class ErrorCerrojo(RuntimeError):
    """Otro proceso vivo tiene el cerrojo. Distinto de uno rancio, que se retoma solo."""


class ErrorNicho(ValueError):
    pass


def nombres_nichos(arbol: Arbol) -> tuple[str, ...]:
    """Nombres canónicos de los sistemas solares disponibles."""

    return tuple(sorted({nodo.nombre for nodo in arbol.nodos if nodo.cosmos == "sistema-solar" and nodo.nombre}))


def normalizar_nichos(arbol: Arbol, nichos: list[str] | tuple[str, ...] | None) -> tuple[str, ...] | None:
    """Valida una selección explícita y elimina duplicados conservando el orden."""

    if nichos is None:
        return None
    seleccion = tuple(dict.fromkeys(nichos))
    disponibles = set(nombres_nichos(arbol))
    desconocidos = [nicho for nicho in seleccion if nicho not in disponibles]
    if desconocidos:
        lista = ", ".join(desconocidos)
        opciones = ", ".join(sorted(disponibles)) or "ninguno"
        raise ErrorNicho(f"nicho desconocido: {lista}; disponibles: {opciones}")
    return seleccion


def nicho_de_nodo(arbol: Arbol, nodo: Nodo) -> str | None:
    """Devuelve el sistema solar que contiene al nodo sólido."""

    if nodo.cosmos not in NIVELES_SOLIDOS or nodo.cosmos == "galaxia":
        return None
    candidato = nodo.ruta_cosmos.split("/", 1)[0]
    return candidato if candidato in set(nombres_nichos(arbol)) else None


def cuerpo(nodo: Nodo) -> str:
    """Contenido Markdown sin frontmatter ni su delimitador de cierre."""

    lineas = nodo.contenido.splitlines(keepends=True)
    if not lineas or lineas[0].strip() != "---":
        return nodo.contenido.strip()
    for indice, linea in enumerate(lineas[1:], start=1):
        if linea.strip() == "---":
            return "".join(lineas[indice + 1 :]).strip()
    return nodo.contenido.strip()


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


def cargar_arbol(
    raiz: str | Path,
    *,
    excluir: str | Path | None = None,
    excluir_directorios: tuple[str | Path, ...] = (),
    tambien: tuple[str | Path, ...] = (),
) -> Arbol:
    """Carga el árbol; `tambien` añade raíces hermanas, como el registro.

    El registro vive fuera de la galaxia a propósito (`spec/REGISTRO.md`: una
    puerta por fuera), pero sus entradas **son nodos** y la spec promete que el
    validador las comprueba. Mientras el cargador miraba una sola raíz, esa
    promesa era falsa: la memoria estaba escrita y el árbol no la veía (H20).
    Las rutas de una raíz añadida se nombran desde su directorio padre, para que
    `registro/lluvia/x.md` se lea igual en un error que en el disco.
    """

    raiz_path = Path(raiz).resolve()
    arbol = Arbol(raiz=raiz_path)
    excluir_path = Path(excluir).resolve() if excluir is not None else None
    directorios_excluidos = tuple(Path(ruta).resolve() for ruta in excluir_directorios)
    if not raiz_path.exists():
        arbol.errores.append(ErrorCarga(str(raiz_path), None, "la raíz del árbol no existe"))
        return arbol

    origenes = [(raiz_path, raiz_path)]
    for extra in tambien:
        extra_path = Path(extra).resolve()
        if not extra_path.is_dir():
            arbol.errores.append(ErrorCarga(str(extra_path), None, "la raíz añadida no existe"))
            continue
        origenes.append((extra_path, extra_path.parent))

    for origen, base_relativa in origenes:
        _cargar_desde(arbol, origen, base_relativa, excluir_path, directorios_excluidos)
    return arbol


def _cargar_desde(
    arbol: Arbol,
    raiz_path: Path,
    base_relativa: Path,
    excluir_path: Path | None,
    directorios_excluidos: tuple[Path, ...],
) -> None:
    for ruta in sorted(raiz_path.rglob("*.md")):
        if excluir_path is not None and ruta.resolve() == excluir_path:
            continue
        ruta_resuelta = ruta.resolve()
        if any(ruta_resuelta == directorio or directorio in ruta_resuelta.parents for directorio in directorios_excluidos):
            continue
        try:
            contenido = ruta.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            arbol.errores.append(ErrorCarga(str(ruta), None, f"no se puede leer: {exc}"))
            continue
        if not contenido.startswith("---"):
            continue
        relativa = ruta.relative_to(base_relativa).as_posix()
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


def cargar_configuracion(ruta: str | Path | None = None) -> Configuracion:
    ruta_path = Path(ruta or "cosmos.toml").resolve()
    if not ruta_path.exists():
        base = ruta_path.parent
        return Configuracion(
            arbol=base,
            indice=base / "COSMOS.md",
            destino_compilacion=base / ".claude/skills",
            manifiesto_compilacion=base / ".cosmos/compilado.json",
            ruta=ruta_path,
        )
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
        umbral_solapamiento = presupuesto.get("solapamiento", 0.25)
        arbol_rel = raiz["arbol"]
        indice_rel = raiz["indice"]
        registro_rel = raiz.get("registro")
        medicion = datos.get("medicion", {})
        compilacion = datos.get("compilacion", {})
        if not isinstance(medicion, dict) or not isinstance(compilacion, dict):
            raise ErrorConfiguracion("medicion y compilacion deben ser tablas TOML")
        metodo = medicion.get("metodo", "aprox")
        destino_rel = compilacion.get("destino", ".claude/skills")
        modo_compilacion = compilacion.get("modo", "symlink")
        manifiesto_rel = compilacion.get("manifiesto", ".cosmos/compilado.json")
    except (KeyError, TypeError) as exc:
        raise ErrorConfiguracion(f"falta un umbral o ruta obligatoria en {ruta_path}: {exc}") from exc
    if any(not isinstance(valor, int) or isinstance(valor, bool) or valor < 0 for valor in valores.values()):
        raise ErrorConfiguracion("los umbrales deben ser enteros no negativos")
    if (
        not isinstance(umbral_solapamiento, (int, float))
        or isinstance(umbral_solapamiento, bool)
        or not 0 <= float(umbral_solapamiento) <= 1
    ):
        raise ErrorConfiguracion("presupuesto.solapamiento debe estar entre 0 y 1")
    if metodo not in {"aprox", "exacto"}:
        raise ErrorConfiguracion("medicion.metodo debe ser 'aprox' o 'exacto'")
    if modo_compilacion not in {"symlink", "copia"}:
        raise ErrorConfiguracion("compilacion.modo debe ser 'symlink' o 'copia'")
    rutas_texto = (arbol_rel, indice_rel, destino_rel, manifiesto_rel)
    if any(not isinstance(valor, str) for valor in rutas_texto):
        raise ErrorConfiguracion("las rutas de raiz y compilacion deben ser texto")
    if registro_rel is not None and not isinstance(registro_rel, str):
        raise ErrorConfiguracion("raiz.registro debe ser texto")
    base = ruta_path.parent
    return Configuracion(
        **valores,
        umbral_solapamiento=float(umbral_solapamiento),
        metodo=metodo,
        arbol=(base / arbol_rel).resolve(),
        indice=(base / indice_rel).resolve(),
        registro=(base / registro_rel).resolve() if registro_rel else None,
        destino_compilacion=(base / destino_rel).resolve(),
        modo_compilacion=modo_compilacion,
        manifiesto_compilacion=(base / manifiesto_rel).resolve(),
        encontrada=True,
        ruta=ruta_path,
    )


def escribir_atomico(ruta: Path, contenido: str) -> None:
    """Escribe entero o no escribe. Vivía solo en `compilar`, y el índice lo necesita igual.

    `NUCLEO.md` §7 exige atomicidad para el manifiesto porque «un manifiesto truncado es
    peor que ninguno». El argumento vale más para el índice, que **es** el contexto de
    entrada: si se corta a medias, el árbol queda rojo por E15 y G03 impide arreglarlo a
    mano, que es un callejón sin salida.
    """

    ruta.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporal = tempfile.mkstemp(prefix=f".{ruta.name}.", dir=ruta.parent)
    temporal_path = Path(temporal)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as fichero:
            fichero.write(contenido)
            fichero.flush()
            os.fsync(fichero.fileno())
        os.replace(temporal_path, ruta)
    finally:
        if temporal_path.exists():
            temporal_path.unlink()


def _proceso_vivo(pid: int) -> bool:
    """¿Sigue ahí el que dejó el cerrojo? `signal 0` pregunta sin tocar nada."""

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # existe, pero es de otro usuario
    return True


@contextmanager
def cerrojo(ruta: Path, *, que_hace: str = "escritura"):
    """Cerrojo de fichero que sabe distinguir «ocupado» de «alguien murió aquí».

    El cerrojo anterior era `O_EXCL` a secas: si el proceso moría sin llegar al `finally`
    —`kill -9`, batería, terminal cerrada—, el fichero quedaba y **toda ejecución futura
    fallaba para siempre** con «otra compilación está en curso». Un cerrojo que no se
    puede abrir no protege nada, solo rompe el repositorio.

    Dentro va el PID, así que se puede preguntar. Si su dueño ya no existe, el cerrojo
    está rancio y se retoma diciéndolo; si vive, el error es legítimo.
    """

    ruta.parent.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            descriptor = os.open(ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            break
        except FileExistsError as exc:
            try:
                pid = int(ruta.read_text(encoding="utf-8").split()[0])
            except (OSError, ValueError, IndexError):
                pid = None
            if pid is not None and pid != os.getpid() and _proceso_vivo(pid):
                raise ErrorCerrojo(
                    f"otra {que_hace} está en curso (proceso {pid}): {ruta}"
                ) from exc
            # Rancio: su dueño no existe o el fichero está ilegible.
            ruta.unlink(missing_ok=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as fichero:
            fichero.write(f"{os.getpid()}\n")
        yield
    finally:
        ruta.unlink(missing_ok=True)
