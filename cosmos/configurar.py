"""Alta local de COSMOS y descubrimiento de las credenciales necesarias.

El fichero de claves vive FUERA del repositorio, en un directorio con permisos
700 y con permisos 600 para el propio fichero. Dentro del repositorio solo se
guarda la plantilla vacía, nunca sus valores.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from cosmos.modelo import Arbol, cuerpo


DIRECTORIO = Path.home() / ".cosmos"
PERFIL = DIRECTORIO / "perfil.toml"
CREDENCIALES = DIRECTORIO / "credenciales.txt"
# Respaldo byte a byte de los ajustes de usuario del runtime antes de fijar el grado de
# autonomía (`configurar --autonomia`). Vive fuera del repositorio, como el perfil.
RESPALDO_AUTONOMIA = DIRECTORIO / "autonomia.json"
# El lanzador `cosmos` en el PATH: un shim de cuatro líneas que apunta al clon.
LANZADOR = Path.home() / ".local" / "bin" / "cosmos"
MARCA_LANZADOR = "generado-por-cosmos-configurar"
PATRON_VARIABLE = re.compile(r"\b([A-Z][A-Z0-9_]{3,})=")
NOMBRES_NO_CREDENCIAL = frozenset({
    "PATH", "PYTHONPATH", "HOME", "LANG", "LC_ALL", "CLAUDE_PROJECT_DIR", "COSMOS_HOLDOUT",
    "COSMOS_EXIGE_TOKENIZADOR", "OPENCLAW_SIN_PERMISOS", "PWD", "SHELL", "TERM", "USER", "EDITOR",
})


@dataclass(frozen=True)
class Credencial:
    variable: str
    pueblo: str
    de_donde: str


def credenciales_de(arbol: Arbol, herramientas: Iterable[str]) -> list[Credencial]:
    """Extrae las credenciales mencionadas por las herramientas elegidas."""
    elegidas = set(herramientas)
    encontradas: dict[str, Credencial] = {}
    indicadores = (
        "TOKEN", "KEY", "SECRET", "PASSWORD", "PASS", "API",
        "CREDENTIAL", "AUTH", "USER_ID", "DSN",
    )
    for nodo in arbol.nodos:
        if nodo.cosmos != "pueblo" or nodo.nombre not in elegidas:
            continue
        for linea in cuerpo(nodo).splitlines():
            for coincidencia in PATRON_VARIABLE.finditer(linea):
                variable = coincidencia.group(1)
                if variable in NOMBRES_NO_CREDENCIAL:
                    continue
                if not any(indicador in variable for indicador in indicadores):
                    continue
                encontradas.setdefault(variable, Credencial(variable, nodo.nombre, linea.strip()[:100]))
    return [encontradas[variable] for variable in sorted(encontradas)]


def _valor_toml(valor: object) -> str:
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, (int, float)):
        return str(valor)
    if isinstance(valor, (list, tuple)):
        return "[" + ", ".join(_valor_toml(v) for v in valor) + "]"
    return json.dumps(str(valor), ensure_ascii=False)


def perfil_toml(oficios: Iterable[str], herramientas: Iterable[str], comprobadas: bool = False,
                modelos: dict | None = None) -> str:
    """Serializa el perfil local en TOML.

    La tabla opcional ``[modelos]`` (la escribe el usuario a mano: qué ``.claude.json`` vigilar
    y qué modelo duro usan los atajos) se CONSERVA al reescribir el perfil. Sin esto, la
    siguiente alta borraba lo que alguien había puesto, que es la clase de sorpresa por la
    que se desinstala un sistema.
    """
    lista_oficios = ", ".join(json.dumps(oficio) for oficio in oficios)
    lista_herramientas = ", ".join(json.dumps(herramienta) for herramienta in herramientas)
    comprobacion = "true" if comprobadas else "false"
    texto = (
        "# Perfil local de COSMOS. Vive fuera del repositorio.\n"
        "# Dentro del repositorio solo se conserva una plantilla vacía.\n\n"
        "[perfil]\n"
        f"oficios = [{lista_oficios}]\n"
        f"herramientas = [{lista_herramientas}]\n"
        f"credenciales_comprobadas = {comprobacion}\n"
    )
    if modelos:
        texto += (
            "\n# Opcional: qué .claude.json vigila el reponedor de modelos además del global y del de\n"
            "# CLAUDE_CONFIG_DIR (un directorio se expande a sus */.claude.json), y el modelo duro de\n"
            "# los atajos maxcode/ultracode. Lo lee `cosmos configurar --modelos`.\n"
            "[modelos]\n"
        )
        for clave, valor in modelos.items():
            texto += f"{clave} = {_valor_toml(valor)}\n"
    return texto


def _leer_toml(ruta: Path) -> dict:
    try:
        datos = tomllib.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return {}
    return datos if isinstance(datos, dict) else {}


def leer_perfil(ruta: Path = PERFIL) -> dict | None:
    """Lee la tabla de perfil; devuelve ``None`` si no existe o no es válida."""
    perfil = _leer_toml(ruta).get("perfil")
    return perfil if isinstance(perfil, dict) else None


def leer_modelos(ruta: Path = PERFIL) -> dict:
    """La tabla opcional ``[modelos]`` del perfil; vacía si no está."""
    modelos = _leer_toml(ruta).get("modelos")
    return modelos if isinstance(modelos, dict) else {}


def plantilla_credenciales(credenciales: Iterable[Credencial]) -> str:
    """Construye la plantilla externa sin incluir ningún secreto."""
    lineas = [
        "# Credenciales de COSMOS. Este fichero vive FUERA del repositorio, con permisos 600. Rellena los valores y guarda; cosmos configurar --comprobar lo lee y lo deja aqui. Con --llavero pasan al llavero de macOS y este fichero se vacia."
    ]
    for credencial in credenciales:
        lineas.extend([f"# {credencial.pueblo}: {credencial.de_donde}", f"{credencial.variable}="])
    return "\n".join(lineas) + "\n"


def escribir_privado(ruta: Path, contenido: str) -> None:
    """Escribe un fichero privado sin atravesar enlaces simbólicos."""
    if ruta.is_symlink():
        raise ValueError(f"no se escribe sobre un enlace simbólico: {ruta}")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.parent.chmod(0o700)
    ruta.write_text(contenido, encoding="utf-8")
    ruta.chmod(0o600)


def leer_credenciales(ruta: Path = CREDENCIALES) -> dict[str, str]:
    """Lee asignaciones ``VARIABLE=valor`` de un fichero de credenciales."""
    try:
        lineas = ruta.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return {}
    resultado: dict[str, str] = {}
    for linea in lineas:
        limpia = linea.strip()
        if not limpia or limpia.startswith("#") or "=" not in limpia:
            continue
        variable, valor = limpia.split("=", 1)
        variable = variable.strip()
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in {"'", '"'}:
            valor = valor[1:-1]
        if variable:
            resultado[variable] = valor
    return resultado


def comprobar_credenciales(esperadas: Iterable[Credencial], leidas: dict[str, str]) -> tuple[list[str], list[str]]:
    """Separa las credenciales ausentes de las que parecen marcadores."""
    faltan: list[str] = []
    sospechosas: list[str] = []
    vistas: set[str] = set()
    for credencial in esperadas:
        variable = credencial.variable
        if variable in vistas:
            continue
        vistas.add(variable)
        valor = leidas.get(variable, "").strip()
        if not valor:
            faltan.append(variable)
            continue
        minusculas = valor.lower()
        if (len(valor) < 8 or "<" in valor or ">" in valor
                or minusculas.startswith("tu_")
                or minusculas in {"change-me", "changeme", "xxx", "..."}):
            sospechosas.append(variable)
    return faltan, sospechosas


def ordenes_llavero(leidas: dict[str, str], cuenta: str) -> list[list[str]]:
    """Prepara, sin ejecutarlas, las órdenes para el llavero de macOS."""
    return [[
        "security", "add-generic-password", "-a", cuenta,
        "-s", f"cosmos/{variable}", "-w", valor, "-U",
    ] for variable, valor in leidas.items() if valor]


def vaciar_valores(ruta: Path = CREDENCIALES) -> int:
    """Vacía los valores del fichero conservando su estructura y comentarios."""
    if ruta.is_symlink():
        raise ValueError(f"no se lee un enlace simbólico: {ruta}")
    contenido = ruta.read_text(encoding="utf-8")
    lineas: list[str] = []
    vaciadas = 0
    for linea in contenido.splitlines():
        izquierda, separador, valor = linea.partition("=")
        variable = izquierda.strip()
        if separador and re.fullmatch(r"[A-Z][A-Z0-9_]*", variable):
            if valor.strip():
                vaciadas += 1
            lineas.append(f"{variable}=")
        else:
            lineas.append(linea)
    final = "\n".join(lineas) + ("\n" if contenido.endswith("\n") else "")
    escribir_privado(ruta, final)
    return vaciadas


def abrir_en_editor(ruta: Path) -> bool:
    """Abre el fichero con el editor de texto convencional del sistema."""
    orden = ["open", "-t", str(ruta)] if sys.platform == "darwin" else ["xdg-open", str(ruta)]
    try:
        resultado = subprocess.run(orden, check=False)
    except FileNotFoundError:
        return False
    return resultado.returncode == 0


def elegir(opciones: list[str], pregunta: str,
           entrada: Callable[[str], str] = input) -> list[str]:
    """Pide una selección por número, nombre exacto o la palabra ``todos``."""
    for indice, opcion in enumerate(opciones, start=1):
        print(f"{indice}. {opcion}", file=sys.stdout)
    respuesta = entrada(pregunta).strip()
    if not respuesta:
        return []
    if respuesta.lower() == "todos":
        return list(opciones)

    elegidas: set[str] = set()
    for fragmento in respuesta.split(","):
        fragmento = fragmento.strip()
        if fragmento in opciones:
            elegidas.add(fragmento)
            continue
        for valor in fragmento.split():
            if valor.isdigit() and 1 <= int(valor) <= len(opciones):
                elegidas.add(opciones[int(valor) - 1])
            elif valor in opciones:
                elegidas.add(valor)
    return [opcion for opcion in opciones if opcion in elegidas]


# --- Los ajustes de usuario del runtime: escribir sin pisar, deshacer byte a byte ----------
#
# Dos caras del alta de máquina escriben en el `settings.json` de USUARIO de Claude Code —el
# grado de autonomía y el hook del reponedor de modelos— y las dos usan el mismo mecanismo,
# calcado de `guardarrailes.enganchar_sesion`: se guardan los bytes exactos del fichero
# anterior y solo se quita lo que se puso, con su valor; lo que alguien cambió a mano no se
# toca y se dice.


def abreviar_home(ruta: Path | str) -> str:
    """La carpeta de casa pasa a `~` en lo que se imprime: legible, y sin rutas de máquina en un informe."""
    texto = str(ruta)
    casa = str(Path.home())
    return "~" + texto[len(casa):] if texto == casa or texto.startswith(casa + os.sep) else texto


def ajustes_usuario() -> Path:
    """El `settings.json` de ámbito USUARIO: el único desde el que el runtime acepta el modo.

    `permissions.defaultMode` en `auto` o `bypassPermissions` se IGNORA en silencio desde el
    `.claude/settings.json` de un repositorio (Claude Code 2.1.257+): fijarlo ahí sería un
    verde que miente. `CLAUDE_CONFIG_DIR` primero, que es donde el runtime guarda los ajustes
    cuando está definida.
    """
    base = os.environ.get("CLAUDE_CONFIG_DIR")
    return (Path(base).expanduser() if base else Path.home() / ".claude") / "settings.json"


def _obtener(datos: dict, clave: str) -> tuple[bool, object]:
    actual: object = datos
    for tramo in clave.split("."):
        if not isinstance(actual, dict) or tramo not in actual:
            return False, None
        actual = actual[tramo]
    return True, actual


def _poner(datos: dict, clave: str, valor: object) -> None:
    tramos = clave.split(".")
    actual = datos
    for tramo in tramos[:-1]:
        siguiente = actual.get(tramo)
        if not isinstance(siguiente, dict):
            siguiente = {}
            actual[tramo] = siguiente
        actual = siguiente
    actual[tramos[-1]] = valor


def _quitar(datos: dict, clave: str) -> None:
    tramos = clave.split(".")
    pila: list[tuple[dict, str]] = []
    actual = datos
    for tramo in tramos[:-1]:
        siguiente = actual.get(tramo)
        if not isinstance(siguiente, dict):
            return
        pila.append((actual, tramo))
        actual = siguiente
    actual.pop(tramos[-1], None)
    # Un `permissions` que se queda vacío se elimina entero, como `podar_sesion` con `hooks`.
    for padre, tramo in reversed(pila):
        if not padre[tramo]:
            del padre[tramo]
        else:
            break


def leer_ajustes(ruta: Path) -> dict | None:
    """El JSON del fichero, o ``None`` si no existe, no es JSON o no es un objeto."""
    if not ruta.is_file():
        return None
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return None
    return datos if isinstance(datos, dict) else None


def podar_claves(datos: dict, escritas: dict[str, object]) -> tuple[dict, list[str]]:
    """Quita de una copia las claves escritas por COSMOS cuyo valor sigue siendo el nuestro.

    Regla de `spec/NUCLEO.md` §7 aplicada a los ajustes: una clave con nuestro valor es nuestra
    y se quita; una clave con OTRO valor la cambió alguien a mano y no se toca — se devuelve en
    la lista para decirlo. Nunca se pisa la decisión de otro.
    """
    copia = json.loads(json.dumps(datos))
    ajenas: list[str] = []
    for clave, valor in escritas.items():
        esta, actual = _obtener(copia, clave)
        if not esta:
            continue
        if actual == valor:
            _quitar(copia, clave)
        else:
            ajenas.append(clave)
    return copia, ajenas


def fijar_claves(ruta: Path, respaldo: Path, claves: dict[str, object], *, marca: str) -> list[tuple[str, object, str]]:
    """Escribe claves en un fichero de ajustes guardando antes los bytes exactos del anterior.

    Devuelve `(clave, valor, estado)` con estado `nuevo`, `ya estaba` o `cambiado desde X`.
    El respaldo conserva el original de la PRIMERA escritura aunque se repita con otro grado;
    `escritas` es siempre lo que COSMOS tiene puesto ahora.
    """
    if ruta.is_symlink():
        raise ValueError(f"no se escribe sobre un enlace simbólico: {ruta}")
    existia = ruta.is_file()
    original = ruta.read_text(encoding="utf-8") if existia else None
    datos = leer_ajustes(ruta)
    if existia and datos is None:
        raise ValueError(f"{ruta} no es un objeto JSON legible; no se ha tocado nada")
    datos = datos or {}

    guardado = leer_ajustes(respaldo) or {}
    previas: dict[str, object] = guardado.get("escritas", {}) if guardado.get("marca") == marca else {}
    if guardado.get("marca") == marca and "original" in guardado:
        existia, original = bool(guardado.get("existia")), guardado.get("original")
        creo_directorio = bool(guardado.get("creo_directorio"))
    else:
        creo_directorio = not ruta.parent.exists()
    # Lo que se puso en una vuelta anterior y ya no toca, fuera (p. ej. de `libre` a `auto`).
    datos, _ = podar_claves(datos, {k: v for k, v in previas.items() if k not in claves})

    informe: list[tuple[str, object, str]] = []
    for clave, valor in claves.items():
        esta, actual = _obtener(datos, clave)
        if esta and actual == valor:
            informe.append((clave, valor, "ya estaba"))
        elif esta:
            informe.append((clave, valor, f"cambiado desde {json.dumps(actual, ensure_ascii=False)}"))
        else:
            informe.append((clave, valor, "nuevo"))
        _poner(datos, clave, valor)

    escribir_privado(respaldo, json.dumps({
        "esquema": 1, "marca": marca, "existia": existia, "creo_directorio": creo_directorio,
        "original": original, "escritas": claves,
    }, ensure_ascii=False, indent=2) + "\n")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return informe


def retirar_claves(ruta: Path, respaldo: Path, *, marca: str) -> tuple[str, list[str]]:
    """Deshace `fijar_claves`. Devuelve `(estado, claves_que_no_se_tocaron)`.

    Estados: `ausente` (COSMOS no escribió nada), `restaurado` (fichero devuelto byte a byte),
    `eliminado` (no existía antes), `podado` (el resto lo cambió alguien: se quita solo lo
    nuestro) o `ilegible` (no es JSON: no se toca).
    """
    guardado = leer_ajustes(respaldo) or {}
    if guardado.get("marca") != marca or "escritas" not in guardado:
        return "ausente", []
    if not ruta.is_file():
        respaldo.unlink(missing_ok=True)
        return "ausente", []
    datos = leer_ajustes(ruta)
    if datos is None:
        return "ilegible", []
    escritas = guardado["escritas"] if isinstance(guardado["escritas"], dict) else {}
    podado, ajenas = podar_claves(datos, escritas)
    original = guardado.get("original")
    try:
        previo = podar_claves(json.loads(original), escritas)[0] if isinstance(original, str) else {}
    except ValueError:
        previo = None
    intacto = previo is not None and podado == previo and not ajenas
    if intacto and guardado.get("existia") and isinstance(original, str):
        ruta.write_text(original, encoding="utf-8")
        respaldo.unlink(missing_ok=True)
        return "restaurado", []
    if intacto and not guardado.get("existia"):
        ruta.unlink()
        respaldo.unlink(missing_ok=True)
        if guardado.get("creo_directorio") and not any(ruta.parent.iterdir()):
            ruta.parent.rmdir()
        return "eliminado", []
    ruta.write_text(json.dumps(podado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    respaldo.unlink(missing_ok=True)
    return "podado", ajenas


# --- El grado de autonomía de la máquina --------------------------------------------------
#
# El océano `autonomia` promete que no se pide permiso. Que el runtime cumpla esa promesa es
# una decisión DE MÁQUINA (ajustes de usuario), no de proyecto, y por eso vive en el alta.
# Tres grados y ni uno más: `auto` (sin preguntas, con el clasificador del runtime detrás),
# `libre` (sin comprobación ninguna) y `manual` (deshacer, dejar el fichero como estaba).

MARCA_AUTONOMIA = "cosmos-configurar-autonomia"
GRADOS: dict[str, dict[str, object]] = {
    "auto": {"permissions.defaultMode": "auto"},
    # La segunda clave es la aceptación guardada del diálogo de responsabilidad: sin ella la
    # primera sesión interactiva de una máquina nueva se para a preguntar y `claude --bg` se
    # niega hasta que alguien conteste. No está documentada; si el runtime la renombra, el
    # diálogo vuelve una vez y `--autonomia libre` la reescribe.
    "libre": {"permissions.defaultMode": "bypassPermissions", "skipDangerousModePermissionPrompt": True},
}
MODOS_SIN_PREGUNTAS = frozenset({"auto", "bypassPermissions"})


def grado_vigente(ruta: Path | None = None) -> tuple[str, str]:
    """`(grado, detalle)` leído de los ajustes de usuario: trivalente, nunca adivina.

    `auto` / `libre` / `manual` cuando `permissions.defaultMode` está y se puede leer;
    `desconocido` cuando el fichero no existe, no es JSON o no lleva la clave (ahí el defecto
    lo decide el runtime, que en algunos planes ya arranca sin preguntar; no se afirma).
    """
    ruta = ruta or ajustes_usuario()
    if not ruta.is_file():
        return "desconocido", f"{ruta} no existe"
    datos = leer_ajustes(ruta)
    if datos is None:
        return "desconocido", f"{ruta} no es JSON legible"
    esta, modo = _obtener(datos, "permissions.defaultMode")
    if not esta or not isinstance(modo, str):
        return "desconocido", "sin permissions.defaultMode en los ajustes de usuario (el defecto lo decide el runtime)"
    if modo == "bypassPermissions":
        return "libre", "permissions.defaultMode = bypassPermissions"
    if modo == "auto":
        return "auto", "permissions.defaultMode = auto"
    return "manual", f"permissions.defaultMode = {modo}"


def fijar_autonomia(grado: str, ruta: Path | None = None, respaldo: Path | None = None) -> list[tuple[str, object, str]]:
    if grado not in GRADOS:
        raise ValueError(f"grado desconocido: {grado}; vale auto, libre o manual")
    return fijar_claves(ruta or ajustes_usuario(), respaldo or RESPALDO_AUTONOMIA, GRADOS[grado], marca=MARCA_AUTONOMIA)


def retirar_autonomia(ruta: Path | None = None, respaldo: Path | None = None) -> tuple[str, list[str]]:
    return retirar_claves(ruta or ajustes_usuario(), respaldo or RESPALDO_AUTONOMIA, marca=MARCA_AUTONOMIA)


# --- El lanzador `cosmos` en el PATH ------------------------------------------------------
#
# El bloque que `proyectar` escribe en un repositorio ajeno manda ejecutar `cosmos abrir …`, y
# ahí eso daba «command not found» (auditoría E-01). Un shim de cuatro líneas lo arregla sin
# meter el paquete en el repo ajeno. Su límite se declara: ata el PATH a la ruta de ESTE clon,
# y `cosmos estado --maquina` dice si el clon al que apunta ya no existe.


def contenido_lanzador(raiz: Path, interprete: str | None = None) -> str:
    python = interprete or sys.executable
    return (
        "#!/usr/bin/env bash\n"
        f"# {MARCA_LANZADOR}: lo escribe 'cosmos configurar --lanzador' y lo quita '--lanzador quitar'.\n"
        f"COSMOS_RAIZ={json.dumps(str(raiz))}\n"
        f"exec env PYTHONPATH=\"$COSMOS_RAIZ${{PYTHONPATH:+:$PYTHONPATH}}\" {json.dumps(python)} -m cosmos \"$@\"\n"
    )


def es_lanzador_nuestro(ruta: Path) -> bool:
    try:
        return MARCA_LANZADOR in ruta.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False


def raiz_del_lanzador(ruta: Path) -> Path | None:
    """A qué clon apunta el shim; ``None`` si no es nuestro o no se puede leer."""
    if not es_lanzador_nuestro(ruta):
        return None
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.startswith("COSMOS_RAIZ="):
            try:
                return Path(json.loads(linea.split("=", 1)[1]))
            except ValueError:
                return None
    return None


def instalar_lanzador(raiz: Path, ruta: Path | None = None, *, forzar: bool = False) -> tuple[Path, str]:
    """Escribe el shim. No pisa un `cosmos` ajeno: lo dice y devuelve `ajeno`."""
    ruta = ruta or LANZADOR
    if ruta.exists() and not es_lanzador_nuestro(ruta) and not forzar:
        return ruta, "ajeno"
    existia = ruta.exists()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido_lanzador(raiz.resolve()), encoding="utf-8")
    ruta.chmod(0o755)
    return ruta, "actualizado" if existia else "creado"


def quitar_lanzador(ruta: Path | None = None) -> tuple[Path, str]:
    ruta = ruta or LANZADOR
    if not ruta.exists():
        return ruta, "ausente"
    if not es_lanzador_nuestro(ruta):
        return ruta, "ajeno"
    ruta.unlink()
    return ruta, "eliminado"


def en_el_path(ruta: Path) -> bool:
    return str(ruta.parent) in os.environ.get("PATH", "").split(os.pathsep)
