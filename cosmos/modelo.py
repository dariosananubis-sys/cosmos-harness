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

    def invalidar(self) -> None:
        """Tras mutar `nodos` en sitio (mismo `len`), tira la caché de nichos (revisión R-41).

        `cargar_arbol` deja el árbol cerrado; quien lo muta a mano —solo las pruebas— lo dice
        aquí. La clave de la caché es (len, id de la lista): sustituir la lista o cambiar su
        tamaño la invalida sola; cambiar un nodo dentro, no, y para eso está esto.
        """

        if hasattr(self, "_nichos_cache"):
            del self._nichos_cache


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
    # `nichos`: la vista son los pueblos de los nichos activos (o todos). `anfitrion`: solo los
    # pueblos con `anfitrion: claude-code` y las `herramientas` elegidas, nunca el catálogo entero —
    # es la vista de un arnés que ya existía y al que COSMOS solo ordena.
    vista_compilacion: str = "nichos"
    # Los otros tres ficheros de runtime que un anfitrión lee: reglas por rutas, agentes y
    # comandos. Solo se generan si se declaran, y solo desde nodos con `anfitrion`.
    rules_compilacion: Path | None = None
    agentes_compilacion: Path | None = None
    comandos_compilacion: Path | None = None
    # La memoria del anfitrión (frontmatter con mapas: no es nodo) que `cosmos memoria` indexa.
    memoria: Path | None = None
    nichos: tuple[str, ...] | None = None
    # Herramientas del perfil local (`cosmos configurar`): acotan el catálogo y la vista del
    # usuario; no tocan el juez del presupuesto, que mira siempre el peor nicho entero.
    herramientas: tuple[str, ...] | None = None
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


def nichos_disponibles(arbol: Arbol) -> frozenset[str]:
    """`nombres_nichos` como conjunto, calculado una vez por árbol.

    `nicho_de_nodo` reconstruía el conjunto entero de nichos en CADA llamada, y se llama
    una vez por nodo y por nicho: `medir_casos` era cúbico y `cosmos validar` tardaba diez
    minutos a 8× la galaxia (auditoría D-01). El árbol se carga una vez y no muta después;
    la caché se invalida sola si cambia el número de nodos, que es lo único que hacen las
    pruebas que construyen un árbol a mano.
    """

    marca = (len(arbol.nodos), id(arbol.nodos))
    cache = getattr(arbol, "_nichos_cache", None)
    if cache is None or cache[0] != marca:
        cache = (marca, frozenset(nombres_nichos(arbol)))
        arbol._nichos_cache = cache
    return cache[1]


def normalizar_nichos(arbol: Arbol, nichos: list[str] | tuple[str, ...] | None) -> tuple[str, ...] | None:
    """Valida una selección explícita y elimina duplicados conservando el orden."""

    if nichos is None:
        return None
    seleccion = tuple(dict.fromkeys(nichos))
    disponibles = nichos_disponibles(arbol)
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
    return candidato if candidato in nichos_disponibles(arbol) else None


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


@dataclass(frozen=True)
class Opaco:
    """Un valor del frontmatter que COSMOS no interpreta: un mapa anidado o un escalar de varias
    líneas, tal como lo escribió el anfitrión.

    El subconjunto normativo no admite mapas (FRONTMATTER.md): un nodo que los lleve es rojo por
    E00... salvo que declare `anfitrion: claude-code`, y entonces esas claves son del runtime,
    viajan intactas al fichero generado y COSMOS solo exige que las suyas sean escalares.
    """

    texto: str


def parsear_frontmatter(contenido: str, ruta: str) -> tuple[dict[str, Any], dict[str, int]]:
    """Parsea el subconjunto normativo o levanta ``ValueError`` con línea.

    Lo que el subconjunto no cubre (mapas, escalares plegados) no rompe el parseo: queda como
    `Opaco` y es E00 quien decide si el nodo puede llevarlo (solo con `anfitrion`).
    """

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
    ultima_clave: str | None = None
    for indice in range(1, cierre):
        numero = indice + 1
        original = lineas_texto[indice]
        sin_comentario = _quitar_comentario(original)
        if not sin_comentario.strip():
            continue

        indentacion = len(sin_comentario) - len(sin_comentario.lstrip(" "))
        texto = sin_comentario.strip()
        if indentacion:
            if lista_pendiente is not None and texto.startswith("-") and not isinstance(datos.get(lista_pendiente), Opaco):
                resto = texto[1:].strip()
                datos[lista_pendiente].append(_escalar(resto, ruta, numero))
                continue
            if ultima_clave is None:
                raise ValueError(f"{ruta}:{numero}: anidamiento o mapa no permitido")
            # Un bloque anidado bajo la última clave: opaco. La lista que hubiera empezado a
            # llenarse se convierte entera en texto crudo, línea a línea, sin interpretarla.
            previo = datos.get(ultima_clave)
            acumulado = previo.texto if isinstance(previo, Opaco) else ""
            datos[ultima_clave] = Opaco(acumulado + original + "\n")
            continue

        lista_pendiente = None
        if texto.startswith("-"):
            raise ValueError(f"{ruta}:{numero}: elemento de lista sin clave")
        if ":" not in texto:
            raise ValueError(f"{ruta}:{numero}: se esperaba 'clave: valor'")
        clave, valor_bruto = texto.split(":", 1)
        clave = clave.strip()
        # Minúsculas y guiones para lo de COSMOS; el anfitrión escribe también `mcpServers` o
        # `allowed-tools`, y esas claves se aceptan aquí para que E00 las juzgue con contexto.
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", clave):
            raise ValueError(f"{ruta}:{numero}: clave inválida {clave!r}")
        if clave in datos:
            raise ValueError(f"{ruta}:{numero}: clave duplicada {clave!r}")
        valor_bruto = valor_bruto.strip()
        numeros[clave] = numero
        ultima_clave = clave
        if not valor_bruto:
            datos[clave] = []
            lista_pendiente = clave
        elif valor_bruto.startswith("["):
            if not valor_bruto.endswith("]"):
                raise ValueError(f"{ruta}:{numero}: lista en línea sin cerrar")
            datos[clave] = _separar_lista(valor_bruto, ruta, numero)
        elif valor_bruto.startswith(("{", ">", "|")):
            datos[clave] = Opaco(original + "\n")
        else:
            datos[clave] = _escalar(valor_bruto, ruta, numero)
    return datos, numeros


# Las claves que son de COSMOS y no del anfitrión. `compilar` las quita al materializar un nodo
# con `anfitrion: claude-code` en su fichero de runtime: lo que queda es, byte a byte, lo que el
# anfitrión tenía antes de que COSMOS lo organizara.
CLAVES_COSMOS = frozenset({
    "cosmos", "nombre", "resumen", "padre", "moja", "invoca", "momento", "ilumina", "orbita", "usa",
    "origen", "anfitrion",
})


def sin_claves_cosmos(contenido: str) -> str:
    """El fichero del nodo sin las claves de COSMOS; si el frontmatter queda vacío, sin él.

    Es textual a propósito —no se re-serializa nada—: el runtime recibe sus claves con el mismo
    orden, las mismas comillas y los mismos comentarios que escribió su autor. Una línea indentada
    pertenece a la clave que la precede, y se va o se queda con ella.
    """

    lineas = contenido.splitlines(keepends=True)
    if not lineas or lineas[0].strip() != "---":
        return contenido
    cierre = next((i for i, l in enumerate(lineas[1:], start=1) if l.strip() == "---"), None)
    if cierre is None:
        return contenido
    conservadas: list[str] = []
    quitando = False
    for linea in lineas[1:cierre]:
        despojada = linea.lstrip(" ")
        indentada = len(despojada) != len(linea) and linea.strip() != ""
        if indentada or not linea.strip():
            if not quitando:
                conservadas.append(linea)
            continue
        clave = linea.split(":", 1)[0].strip() if ":" in linea else ""
        quitando = clave in CLAVES_COSMOS
        if not quitando:
            conservadas.append(linea)
    resto = "".join(lineas[cierre + 1:])
    if not any(l.strip() for l in conservadas):
        return resto.lstrip("\n")
    return "---\n" + "".join(conservadas) + "---\n" + resto


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
    raiz_resuelta = raiz_path.resolve()
    for ruta in sorted(raiz_path.rglob("*.md")):
        if excluir_path is not None and ruta.resolve() == excluir_path:
            continue
        ruta_resuelta = ruta.resolve()
        if any(ruta_resuelta == directorio or directorio in ruta_resuelta.parents for directorio in directorios_excluidos):
            continue
        # La misma ruta —relativa a la raíz— en los dos errores de carga: la de lectura
        # salía absoluta y la de parseo relativa, en la misma salida (auditoría D-10).
        relativa = ruta.relative_to(base_relativa).as_posix()
        # Dentro de un pueblo —un directorio con `SKILL.md`— los demás `.md` son carga del pueblo
        # (referencias, guías, la `SKILL.md` de un sub-paquete), no nodos: viajan con él al
        # compilarlo y no se validan como frontmatter de COSMOS. Un nodo por pueblo, como dice
        # `spec/PUEBLO.md`; sin esto, una skill del anfitrión con `references/` era E00 por
        # cada fichero de apoyo. Va ANTES de mirar los enlaces: la carga de un pueblo puede
        # ser un enlace a una guía de fuera del árbol (una skill que enlaza el manual de la
        # raíz del repositorio) y sigue sin ser un nodo; `compilar` copia el enlace tal cual.
        if _es_carga_de_pueblo(ruta, raiz_path):
            continue
        # La frontera del árbol es la raíz que declara `cosmos.toml`. Un enlace simbólico
        # que apunta fuera de ella entraba como nodo de pleno derecho (auditoría D-11):
        # lo que se mide y se aplana tiene que estar dentro de lo que se declara. Se
        # dice, no se calla: un nodo que desaparece sin ruido es peor que un error.
        if not ruta_resuelta.is_relative_to(raiz_resuelta):
            arbol.errores.append(ErrorCarga(relativa, None, f"enlace simbólico fuera del árbol: apunta a {ruta_resuelta}"))
            continue
        # Y dentro tampoco (revisión R-40): un enlace a otro nodo del árbol lo cargaba dos veces —
        # `pueblo 306 → 307`, +29 tokens de presupuesto— y el rojo que salía (E06/E18) señalaba al
        # ORIGINAL, no al enlace. Se denuncia el enlace y no se carga: un nodo vive en un sitio.
        if ruta.is_symlink() or any(padre.is_symlink() for padre in ruta.relative_to(raiz_path).parents
                                   if (raiz_path / padre).is_symlink()):
            arbol.errores.append(ErrorCarga(relativa, None, f"enlace simbólico dentro del árbol: apunta a {ruta_resuelta}; un nodo vive en un solo sitio"))
            continue
        try:
            # `utf-8-sig`: un BOM (Windows, editores con la codificación heredada) hacía
            # que el fichero no empezara por `---` y el nodo desaparecía en silencio, con
            # E05 o E02 culpando a un fichero inocente (auditoría D-04).
            contenido = ruta.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            arbol.errores.append(ErrorCarga(relativa, None, f"no se puede leer: {exc}"))
            continue
        if not contenido.startswith("---"):
            continue
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


def _es_carga_de_pueblo(ruta: Path, raiz: Path) -> bool:
    """¿Vive este `.md` por debajo de un `SKILL.md` que no es él mismo?"""

    for padre in ruta.parents:
        if padre == raiz or not padre.is_relative_to(raiz):
            return False
        skill = padre / "SKILL.md"
        if skill.is_file() and skill != ruta:
            return True
    return False


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
        vista_compilacion = compilacion.get("vista", "nichos")
        # `[nichos] activos` vivía solo en el CLI (`nichos_de_configuracion`): un llamante de la
        # librería que validaba un config con nichos activos veía E19 contra un manifiesto que sí
        # los declaraba (el test del árbol de ejemplo, ciclo 2). Un solo lector del TOML.
        nichos_tabla = datos.get("nichos", {})
        if not isinstance(nichos_tabla, dict):
            raise ErrorConfiguracion("[nichos] debe ser una tabla TOML")
        activos = nichos_tabla.get("activos", [])
        if not isinstance(activos, list) or any(not isinstance(valor, str) for valor in activos):
            raise ErrorConfiguracion("[nichos].activos debe ser una lista de nombres")
        # `[nichos] herramientas`: la selección por herramienta del perfil (`cosmos configurar`),
        # pero versionada con el repositorio para un arnés que quiere la misma vista en todas sus
        # máquinas. Vacía = sin selección (manda el perfil local si lo hay).
        herramientas_cfg = nichos_tabla.get("herramientas", [])
        if not isinstance(herramientas_cfg, list) or any(not isinstance(v, str) for v in herramientas_cfg):
            raise ErrorConfiguracion("[nichos].herramientas debe ser una lista de nombres")
        rules_rel = compilacion.get("rules")
        agentes_rel = compilacion.get("agentes")
        comandos_rel = compilacion.get("comandos")
        memoria_rel = raiz.get("memoria")
        for etiqueta, valor in (("compilacion.rules", rules_rel), ("compilacion.agentes", agentes_rel),
                                ("compilacion.comandos", comandos_rel), ("raiz.memoria", memoria_rel)):
            if valor is not None and not isinstance(valor, str):
                raise ErrorConfiguracion(f"{etiqueta} debe ser texto")
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
    if vista_compilacion not in {"nichos", "anfitrion"}:
        raise ErrorConfiguracion("compilacion.vista debe ser 'nichos' o 'anfitrion'")
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
        vista_compilacion=vista_compilacion,
        manifiesto_compilacion=(base / manifiesto_rel).resolve(),
        rules_compilacion=(base / rules_rel).resolve() if rules_rel else None,
        agentes_compilacion=(base / agentes_rel).resolve() if agentes_rel else None,
        comandos_compilacion=(base / comandos_rel).resolve() if comandos_rel else None,
        memoria=(base / memoria_rel).resolve() if memoria_rel else None,
        nichos=tuple(dict.fromkeys(activos)) or None,
        herramientas=tuple(dict.fromkeys(herramientas_cfg)) or None,
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
    # `mkstemp` crea en 0600 por seguridad, y como el temporal SUSTITUYE al destino, el
    # índice pasaba de 644 a 600 cada vez que se regeneraba: la escritura atómica cambiaba
    # en silencio quién puede leer el fichero. Se conservan los permisos que tenía; si no
    # existía, los que daría una creación normal con la máscara del proceso.
    try:
        permisos = ruta.stat().st_mode & 0o777
    except OSError:
        mascara = os.umask(0)
        os.umask(mascara)
        permisos = 0o666 & ~mascara

    descriptor, temporal = tempfile.mkstemp(prefix=f".{ruta.name}.", dir=ruta.parent)
    temporal_path = Path(temporal)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as fichero:
            fichero.write(contenido)
            fichero.flush()
            os.fsync(fichero.fileno())
        os.chmod(temporal_path, permisos)
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

    **No es reentrante, y lo dice.** La condición de robo llevaba un `pid != os.getpid()`
    que convertía el propio cerrojo en «rancio» para el mismo proceso: un `with` anidado
    sobre la misma ruta lo robaba, y al salir el interior borraba el fichero — el exterior
    seguía creyendo que tenía la exclusión y ya no la tenía nadie. Una exclusión que se
    evapora sin decirlo es peor que un interbloqueo, porque nada se pone rojo. Ahora el
    mismo proceso recibe un `ErrorCerrojo` explícito, y el cerrojo exterior sobrevive.
    """

    ruta.parent.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            descriptor = os.open(ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError as exc:
            try:
                pid = int(ruta.read_text(encoding="utf-8").split()[0])
            except (OSError, ValueError, IndexError):
                pid = None
            if pid is not None and _proceso_vivo(pid):
                quien = (
                    "este mismo proceso ya tiene el cerrojo (reentrada no soportada)"
                    if pid == os.getpid()
                    else f"otra {que_hace} está en curso (proceso {pid})"
                )
                raise ErrorCerrojo(f"{quien}: {ruta}") from exc
            # Rancio: su dueño no existe o el fichero está ilegible.
            ruta.unlink(missing_ok=True)
        else:
            # El PID se escribe ANTES de ceder el control: un fichero vacío se
            # clasifica como rancio, y entre el open y la escritura otro proceso
            # podía robar un cerrojo vivo. La ventana no desaparece del todo, pero
            # pasa de «lo que tarde el cuerpo» a dos llamadas al sistema seguidas.
            os.write(descriptor, f"{os.getpid()}\n".encode("utf-8"))
            os.close(descriptor)
            break
    try:
        yield
    finally:
        ruta.unlink(missing_ok=True)
