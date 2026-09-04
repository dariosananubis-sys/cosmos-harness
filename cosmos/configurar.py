"""Alta local de COSMOS y descubrimiento de las credenciales necesarias.

El fichero de claves vive FUERA del repositorio, en un directorio con permisos
700 y con permisos 600 para el propio fichero. Dentro del repositorio solo se
guarda la plantilla vacía, nunca sus valores.
"""

from __future__ import annotations

import json
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


def perfil_toml(oficios: Iterable[str], herramientas: Iterable[str], comprobadas: bool = False) -> str:
    """Serializa el perfil local en TOML."""
    lista_oficios = ", ".join(json.dumps(oficio) for oficio in oficios)
    lista_herramientas = ", ".join(json.dumps(herramienta) for herramienta in herramientas)
    comprobacion = "true" if comprobadas else "false"
    return (
        "# Perfil local de COSMOS. Vive fuera del repositorio.\n"
        "# Dentro del repositorio solo se conserva una plantilla vacía.\n\n"
        "[perfil]\n"
        f"oficios = [{lista_oficios}]\n"
        f"herramientas = [{lista_herramientas}]\n"
        f"credenciales_comprobadas = {comprobacion}\n"
    )


def leer_perfil(ruta: Path = PERFIL) -> dict | None:
    """Lee la tabla de perfil; devuelve ``None`` si no existe o no es válida."""
    try:
        datos = tomllib.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return None
    perfil = datos.get("perfil")
    return perfil if isinstance(perfil, dict) else None


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
