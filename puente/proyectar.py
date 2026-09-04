#!/usr/bin/env python3
"""Proyecta COSMOS sobre un repo Git ajeno sin pisar nada que no sea suyo."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path

from cosmos.medir import contar_aprox, contexto_inicial
from cosmos.modelo import (
    Arbol,
    Configuracion,
    cargar_arbol,
    cargar_configuracion,
    nicho_de_nodo,
    nombres_nichos,
    parsear_frontmatter,
)

INICIO = "<!-- cosmos:inicio -->"
FIN = "<!-- cosmos:fin -->"
MARCA = ".generado-por-cosmos"
CONTENIDO_MARCA = "Generado por COSMOS; no editar.\n"
CONTRATO = "planeta.toml"
FICHEROS_RAIZ = ("AGENTS.md", "CLAUDE.md")
DESTINOS = (".agents", ".claude")
PARTES_IGNORADAS = {"__pycache__", ".DS_Store", ".git", ".pytest_cache"}
NIVELES_APLANADOS = frozenset({"pueblo"})
AJUSTES_CLAUDE = {
    "autoCompactEnabled": True,
    "autoMemoryEnabled": False,
    "includeGitInstructions": False,
    "preferredNotifChannel": "notifications_disabled",
    "attribution": {"commit": "", "pr": "", "sessionUrl": False},
    "enableAllProjectMcpServers": False,
}


class ErrorProyeccion(RuntimeError):
    pass


@dataclass(frozen=True)
class ContratoPlaneta:
    nombre: str
    tipo: str
    nichos: tuple[str, ...]
    objetivo: str
    fuentes_autorizadas: tuple[str, ...]
    rutas_escritura: tuple[str, ...]
    produccion: bool
    acciones_externas: bool
    comandos: tuple[str, ...]
    visual: bool


# --------------------------------------------------------------------------- rutas


def _ruta_del_planeta(raiz: Path, relativa: Path) -> Path:
    if relativa.is_absolute() or ".." in relativa.parts:
        raise ErrorProyeccion("ruta de planeta no portable")
    ruta = raiz / relativa
    actual = raiz
    for parte in relativa.parts:
        actual /= parte
        if actual.is_symlink():
            raise ErrorProyeccion(f"ancestro symlink prohibido: {relativa.as_posix()}")
    if not ruta.resolve(strict=False).is_relative_to(raiz.resolve()):
        raise ErrorProyeccion("una ruta de planeta escapa del repositorio")
    return ruta


def raiz_del_planeta(destino: Path, *, propia: Path) -> Path:
    if destino.is_symlink() or not destino.is_dir():
        raise ErrorProyeccion("el destino debe ser un directorio real")
    resultado = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=destino,
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado.returncode or not resultado.stdout.strip():
        raise ErrorProyeccion("el destino no es un repositorio Git")
    raiz = Path(resultado.stdout.strip()).resolve()
    if raiz != destino.resolve():
        raise ErrorProyeccion("indica la raíz exacta del repositorio Git")
    if raiz == propia.resolve():
        raise ErrorProyeccion("COSMOS no se proyecta sobre sí mismo")
    return raiz


# ------------------------------------------------------------------------ contrato


def _lista(tabla: dict, clave: str) -> tuple[str, ...]:
    valor = tabla.get(clave, [])
    if not isinstance(valor, list) or not all(isinstance(item, str) for item in valor):
        raise ErrorProyeccion(f"{clave} debe ser una lista de texto")
    limpia = tuple(dict.fromkeys(item.strip() for item in valor if item.strip()))
    if any(
        len(item) > 1_000 or "\n" in item or "\r" in item or INICIO in item or FIN in item
        for item in limpia
    ):
        raise ErrorProyeccion(f"{clave} contiene un valor no portable")
    return limpia


def _booleano(tabla: dict, clave: str) -> bool:
    valor = tabla.get(clave, False)
    if not isinstance(valor, bool):
        raise ErrorProyeccion(f"{clave} debe ser booleano")
    return valor


def cargar_contrato(raiz: Path, arbol: Arbol) -> ContratoPlaneta:
    ruta = _ruta_del_planeta(raiz, Path(CONTRATO))
    if ruta.is_symlink() or not ruta.is_file():
        raise ErrorProyeccion(f"falta {CONTRATO} regular en el repo destino")
    datos = tomllib.loads(ruta.read_text(encoding="utf-8"))
    permitidas = {"version", "nombre", "tipo", "repositorio", "nichos", "contexto", "limites", "verificacion"}
    desconocidas = sorted(set(datos) - permitidas)
    if desconocidas:
        raise ErrorProyeccion(f"claves desconocidas en {CONTRATO}: {', '.join(desconocidas)}")
    if datos.get("version") != 1:
        raise ErrorProyeccion(f"{CONTRATO} necesita version = 1")
    nombre = datos.get("nombre")
    tipo = datos.get("tipo")
    if (
        not isinstance(nombre, str)
        or not nombre.strip()
        or len(nombre) > 120
        or "\n" in nombre
        or "\r" in nombre
        or INICIO in nombre
        or FIN in nombre
    ):
        raise ErrorProyeccion("nombre debe ser texto no vacío de hasta 120 caracteres")
    if not isinstance(tipo, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", tipo):
        raise ErrorProyeccion("tipo no es portable")
    if datos.get("repositorio") != ".":
        raise ErrorProyeccion('repositorio debe ser "." dentro del repo del planeta')
    nichos = _lista(datos, "nichos")
    disponibles = set(nombres_nichos(arbol))
    inexistentes = sorted(set(nichos) - disponibles)
    if inexistentes:
        raise ErrorProyeccion(f"nichos inexistentes: {', '.join(inexistentes)}")

    contexto = datos.get("contexto", {})
    limites = datos.get("limites", {})
    verificacion = datos.get("verificacion", {})
    if not all(isinstance(seccion, dict) for seccion in (contexto, limites, verificacion)):
        raise ErrorProyeccion("contexto, limites y verificacion deben ser tablas")
    objetivo = contexto.get("objetivo", "")
    if not isinstance(objetivo, str) or len(objetivo) > 2_000 or INICIO in objetivo or FIN in objetivo:
        raise ErrorProyeccion("objetivo debe ser texto portable de hasta 2000 caracteres")
    rutas_escritura = _lista(limites, "rutas_escritura")
    for valor in rutas_escritura:
        candidata = Path(valor)
        if candidata.is_absolute() or ".." in candidata.parts:
            raise ErrorProyeccion("rutas_escritura debe contener rutas relativas sin ..")

    return ContratoPlaneta(
        nombre=nombre.strip(),
        tipo=tipo,
        nichos=nichos,
        objetivo=objetivo.strip(),
        fuentes_autorizadas=_lista(contexto, "fuentes_autorizadas"),
        rutas_escritura=rutas_escritura,
        produccion=_booleano(limites, "produccion"),
        acciones_externas=_booleano(limites, "acciones_externas"),
        comandos=_lista(verificacion, "comandos"),
        visual=_booleano(verificacion, "visual"),
    )


def _contrato_en_blanco(nombre: str, tipo: str, nichos: list[str]) -> str:
    valores = ", ".join(json.dumps(nicho, ensure_ascii=False) for nicho in nichos)
    return (
        "version = 1\n"
        f"nombre = {json.dumps(nombre, ensure_ascii=False)}\n"
        f"tipo = {json.dumps(tipo, ensure_ascii=False)}\n"
        'repositorio = "."\n'
        f"nichos = [{valores}]\n\n"
        "[contexto]\n"
        'objetivo = ""\n'
        "fuentes_autorizadas = []\n\n"
        "[limites]\n"
        "rutas_escritura = []\n"
        "produccion = false\n"
        "acciones_externas = false\n\n"
        "[verificacion]\n"
        "comandos = []\n"
        "visual = false\n"
    )


# ------------------------------------------------------------------------------ pueblos


def pueblos_fuente(arbol: Arbol, nichos: tuple[str, ...]) -> dict[str, Path]:
    """Los pueblos de los nichos del contrato, indexados por nombre.

    Aquí vive E18 aplicada al repo ajeno: al aplanar se pierde la jerarquía, así que
    dos nombres iguales colapsan en la misma entrada y una gana en silencio. El
    mensaje nombra las dos rutas, que es lo único que se arregla en diez segundos.
    """

    if not nichos:
        return {}
    fuentes: dict[str, Path] = {}
    rutas: dict[str, str] = {}
    for nodo in sorted(arbol.nodos, key=lambda n: n.ruta_relativa):
        if nodo.cosmos not in NIVELES_APLANADOS or nicho_de_nodo(arbol, nodo) not in nichos:
            continue
        if nodo.ruta.name != "SKILL.md":
            raise ErrorProyeccion(f"{nodo.ruta_cosmos} no vive en un SKILL.md; no se puede aplanar")
        directorio = nodo.ruta.parent
        if directorio.is_symlink():
            raise ErrorProyeccion(f"{nodo.ruta_cosmos} es un symlink; no se proyecta")
        if nodo.nombre != directorio.name:
            raise ErrorProyeccion(
                f"{nodo.ruta_cosmos} vive en un directorio llamado {directorio.name!r}"
            )
        if nodo.nombre in fuentes:
            raise ErrorProyeccion(
                f"colisión al aplanar {nodo.nombre!r}: {rutas[nodo.nombre]} y {nodo.ruta_cosmos}"
            )
        fuentes[nodo.nombre] = directorio
        rutas[nodo.nombre] = nodo.ruta_cosmos
    return fuentes


CAMPOS_ANFITRION = ("name", "description")


def para_el_anfitrion(contenido: bytes) -> bytes:
    """Traduce el frontmatter de un pueblo a lo que el agente anfitrión sabe leer.

    Claude Code (y los agentes que siguen su convención) descubren una skill por `name:`
    y `description:`; COSMOS escribe `cosmos:`, `nombre:`, `padre:` y `resumen:`. Copiar el
    fichero tal cual dejaba 22 de 22 pueblos proyectados invisibles, con `comprobar` en
    verde (auditoría E-02). Los campos de COSMOS se conservan: no estorban y son los que
    `comprobar` compara con el origen. Si ya trae `name` y `description`, no se toca.
    """

    # `utf-8-sig`: un pueblo con BOM cargaba y validaba dentro de COSMOS y llegaba al anfitrión
    # sin `name`/`description` reconocibles (revisión R-43, la puerta que D-04 no cerró).
    texto = contenido.decode("utf-8-sig")
    try:
        datos, _ = parsear_frontmatter(texto, "SKILL.md")
    except ValueError:
        return contenido
    if all(campo in datos for campo in CAMPOS_ANFITRION):
        return contenido
    nombre, resumen = str(datos.get("nombre", "")), str(datos.get("resumen", ""))
    if not nombre:
        return contenido
    cabecera, resto = texto.split("\n", 1)
    extra = f"name: {nombre}\ndescription: {json.dumps(resumen, ensure_ascii=False)}\n"
    return f"{cabecera}\n{extra}{resto}".encode("utf-8")


def _ficheros_fuente(origen: Path) -> dict[Path, tuple[bytes, int]]:
    ficheros: dict[Path, tuple[bytes, int]] = {}
    for ruta in sorted(origen.rglob("*")):
        if ruta.is_symlink():
            raise ErrorProyeccion("un pueblo fuente contiene un symlink")
        if not ruta.is_file() or any(parte in PARTES_IGNORADAS for parte in ruta.parts):
            continue
        modo = 0o755 if ruta.stat().st_mode & 0o111 else 0o644
        contenido = ruta.read_bytes()
        if ruta.parent == origen and ruta.name == "SKILL.md":
            contenido = para_el_anfitrion(contenido)
        ficheros[ruta.relative_to(origen)] = (contenido, modo)
    ficheros[Path(MARCA)] = (CONTENIDO_MARCA.encode("utf-8"), 0o644)
    return ficheros


def invisibles_para_el_anfitrion(base: Path, nombres: list[str]) -> list[str]:
    """Skills proyectadas cuyo `SKILL.md` no lleva los campos que el anfitrión exige.

    Es el contrato del ANFITRIÓN, no el de COSMOS consigo mismo: `comprobar` verificaba que
    el destino coincidía con el origen y daba verde sobre 22 ficheros que Claude Code no
    veía. Se lee el fichero que hay en el destino, no lo que se esperaba escribir.
    """

    invisibles: list[str] = []
    for nombre in nombres:
        skill = base / nombre / "SKILL.md"
        if not skill.is_file():
            continue
        texto = skill.read_text(encoding="utf-8", errors="replace")
        cabecera = texto.split("\n---", 1)[0]
        if not all(re.search(rf"^{campo}:\s*\S", cabecera, re.M) for campo in CAMPOS_ANFITRION):
            invisibles.append(nombre)
    return invisibles


def _gestionados(base: Path) -> dict[str, Path]:
    if not base.exists():
        return {}
    if base.is_symlink() or not base.is_dir():
        raise ErrorProyeccion("el directorio de skills del destino no es seguro")
    resultado = {}
    for hijo in base.iterdir():
        if hijo.is_symlink():
            raise ErrorProyeccion("una skill del destino no puede ser symlink")
        marca = hijo / MARCA
        if hijo.is_dir() and marca.is_file() and not marca.is_symlink():
            if marca.read_text(encoding="utf-8") == CONTENIDO_MARCA:
                resultado[hijo.name] = hijo
    return resultado


def _coincide(destino: Path, esperado: dict[Path, tuple[bytes, int]]) -> bool:
    if not destino.is_dir() or destino.is_symlink():
        return False
    actual = {
        ruta.relative_to(destino)
        for ruta in destino.rglob("*")
        if ruta.is_file() and not any(parte in PARTES_IGNORADAS for parte in ruta.parts)
    }
    if actual != set(esperado):
        return False
    for relativa, (contenido, modo) in esperado.items():
        ruta = destino / relativa
        if ruta.is_symlink() or ruta.read_bytes() != contenido:
            return False
        if stat.S_IMODE(ruta.stat().st_mode) != modo:
            return False
    return True


# --------------------------------------------------------------------------- bloque


def bloque(contrato: ContratoPlaneta, arbol: Arbol) -> str:
    """El contexto de entrada de COSMOS más el contrato, entre marcadores.

    El original leía un fichero fijo de política. Aquí el bloque es exactamente
    'contexto_inicial' (NUCLEO §2): índice, océanos y catálogo del nicho activo. Lo
    que se proyecta es lo mismo que se mide, así que el presupuesto de entrada
    significa lo mismo dentro y fuera.
    """

    nichos = contrato.nichos or None
    # Sin ríos: el repo ajeno no tiene el paquete `cosmos` y el bloque mandaba ejecutar
    # `cosmos abrir rio/x` donde eso da «command not found» (auditoría E-01).
    entrada = contexto_inicial(arbol, nichos, con_rios=False).rstrip()
    fuentes = ", ".join(contrato.fuentes_autorizadas) or "por completar; no asumir"
    escrituras = ", ".join(contrato.rutas_escritura) or "por completar; no ampliar alcance"
    comandos = "; ".join(contrato.comandos) or "por completar"
    lista_nichos = ", ".join(contrato.nichos) or "ninguno activo"
    objetivo = contrato.objetivo or "por completar antes de tocar el planeta"
    return (
        f"{INICIO}\n"
        "# COSMOS\n\n"
        f"{entrada}\n\n"
        "## Contrato del planeta\n\n"
        f"- Nombre: {contrato.nombre}; tipo: {contrato.tipo}; objetivo: {objetivo}.\n"
        f"- Fuentes autorizadas: {fuentes}.\n"
        f"- Escritura declarada: {escrituras}.\n"
        f"- Incluye producción: {'sí' if contrato.produccion else 'no'}; "
        f"acciones externas: {'sí' if contrato.acciones_externas else 'no'}. "
        "Describen alcance; no sustituyen a los océanos.\n"
        f"- Verificación: {comandos}; visual: {'sí' if contrato.visual else 'no'}.\n"
        f"- Nichos proyectados: {lista_nichos}.\n\n"
        "## Cómo se baja desde aquí\n\n"
        "- Los pueblos de los nichos proyectados son skills nativas de este repositorio "
        "(`.claude/skills/`, `.agents/skills/`): se invocan por su nombre y su cuerpo se "
        "carga solo al invocarlas. Eso es la carga perezosa aquí.\n"
        "- Los verbos de COSMOS (`buscar`, `abrir`, `acertar`…) NO están en este repositorio: "
        "viven en el repositorio COSMOS de origen (el que tiene `cosmos.toml`). Para bajar por "
        "otro oficio, añade su nicho a `planeta.toml` y ejecuta desde el origen "
        "`python3 -m cosmos proyectar sincronizar <ruta de este repositorio>`.\n"
        f"{FIN}\n"
    )


def _fusionar(existente: str, nuevo: str) -> str:
    """Sustituye solo lo que está entre marcadores; lo de fuera se conserva entero."""

    inicios = [c.start() for c in re.finditer(re.escape(INICIO), existente)]
    finales = [c.end() for c in re.finditer(re.escape(FIN), existente)]
    if not inicios and not finales:
        if not existente:
            return nuevo
        separador = "" if existente.endswith("\n\n") else "\n" if existente.endswith("\n") else "\n\n"
        return f"{existente}{separador}{nuevo}"
    if len(inicios) != 1 or len(finales) != 1 or inicios[0] >= finales[0]:
        raise ErrorProyeccion("marcadores de COSMOS inválidos en las instrucciones del planeta")
    prefijo = existente[: inicios[0]]
    corte = finales[0] + (1 if existente[finales[0] :].startswith("\n") else 0)
    fuera = prefijo + existente[corte:]
    if not fuera:
        return nuevo
    separador = "" if fuera.endswith("\n\n") else "\n" if fuera.endswith("\n") else "\n\n"
    return f"{fuera}{separador}{nuevo}"


def ficheros_raiz_esperados(
    raiz: Path, contrato: ContratoPlaneta, arbol: Arbol, config: Configuracion
) -> dict[Path, bytes]:
    texto = bloque(contrato, arbol)
    tokens = contar_aprox(texto)
    if tokens > config.entrada:
        raise ErrorProyeccion(
            f"el bloque proyectado son {tokens} tokens y el presupuesto de entrada es "
            f"{config.entrada}; reduce nichos o resúmenes"
        )
    esperados: dict[Path, bytes] = {}
    for nombre in FICHEROS_RAIZ:
        ruta = _ruta_del_planeta(raiz, Path(nombre))
        if ruta.is_symlink():
            raise ErrorProyeccion(f"{nombre} no puede ser symlink")
        existente = ruta.read_text(encoding="utf-8") if ruta.exists() else ""
        esperados[ruta] = _fusionar(existente, texto).encode("utf-8")
    return esperados


def ajustes_claude_esperados(raiz: Path) -> dict:
    ruta = _ruta_del_planeta(raiz, Path(".claude/settings.json"))
    if ruta.is_symlink():
        raise ErrorProyeccion(".claude/settings.json no puede ser symlink")
    if ruta.exists():
        try:
            actual = json.loads(ruta.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ErrorProyeccion(".claude/settings.json no contiene JSON válido") from exc
        if not isinstance(actual, dict):
            raise ErrorProyeccion(".claude/settings.json debe contener un objeto JSON")
    else:
        actual = {}
    return _fusionar_ajustes(actual, AJUSTES_CLAUDE)


def _fusionar_ajustes(actual: dict, nuestros: dict) -> dict:
    """Fusión recursiva: `actual | nuestros` era superficial y borraba `attribution.miCampoPropio`
    del `settings.json` de un repositorio AJENO (revisión R-46). Lo nuestro manda en su clave; lo
    del anfitrión dentro del mismo objeto se conserva. El orden de claves del anfitrión se respeta."""

    resultado = dict(actual)
    for clave, valor in nuestros.items():
        previo = resultado.get(clave)
        if isinstance(valor, dict) and isinstance(previo, dict):
            resultado[clave] = _fusionar_ajustes(previo, valor)
        else:
            resultado[clave] = valor
    return resultado


# ------------------------------------------------------------------------ comprobar


def problemas(
    raiz: Path, contrato: ContratoPlaneta, arbol: Arbol, config: Configuracion
) -> list[str]:
    """Lista todo lo que está desactualizado o en conflicto, sin arreglar nada."""

    encontrados: list[str] = []
    try:
        esperados = ficheros_raiz_esperados(raiz, contrato, arbol, config)
    except ErrorProyeccion as exc:
        return [str(exc)]
    for ruta, contenido in esperados.items():
        if not ruta.is_file() or ruta.read_bytes() != contenido:
            encontrados.append(f"desactualizado {ruta.name}")
    ruta_ajustes = _ruta_del_planeta(raiz, Path(".claude/settings.json"))
    ajustes_claude_esperados(raiz)
    if not ruta_ajustes.is_file():
        encontrados.append("desactualizado .claude/settings.json")
    else:
        actuales = json.loads(ruta_ajustes.read_text(encoding="utf-8"))
        if _fusionar_ajustes(actuales, AJUSTES_CLAUDE) != actuales:
            encontrados.append("desactualizado .claude/settings.json")
    fuentes = pueblos_fuente(arbol, contrato.nichos)
    for destino in DESTINOS:
        base = _ruta_del_planeta(raiz, Path(destino) / "skills")
        gestionados = _gestionados(base)
        for nombre, origen in fuentes.items():
            entrada = base / nombre
            if entrada.exists() and nombre not in gestionados:
                encontrados.append(f"conflicto ajeno {destino}/skills/{nombre}")
            elif not _coincide(entrada, _ficheros_fuente(origen)):
                encontrados.append(f"desactualizado {destino}/skills/{nombre}")
        for obsoleta in sorted(set(gestionados) - set(fuentes)):
            encontrados.append(f"obsoleta {destino}/skills/{obsoleta}")
        for nombre in invisibles_para_el_anfitrion(base, sorted(fuentes)):
            encontrados.append(f"invisible para el anfitrión (sin name/description) {destino}/skills/{nombre}")
    return encontrados


# ------------------------------------------------------------------------ escribir


def _escritura_atomica(ruta: Path, contenido: bytes) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    modo = stat.S_IMODE(ruta.stat().st_mode) if ruta.exists() else 0o644
    descriptor, temporal_nombre = tempfile.mkstemp(prefix=f".{ruta.name}.", dir=ruta.parent)
    temporal = Path(temporal_nombre)
    try:
        with os.fdopen(descriptor, "wb") as manejador:
            manejador.write(contenido)
        temporal.chmod(modo)
        os.replace(temporal, ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def _reemplazar(destino: Path, ficheros: dict[Path, tuple[bytes, int]]) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    montaje = Path(tempfile.mkdtemp(prefix=f".{destino.name}.", dir=destino.parent))
    respaldo = destino.parent / f".{destino.name}.cosmos-respaldo"
    try:
        for relativa, (contenido, modo) in ficheros.items():
            ruta = montaje / relativa
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_bytes(contenido)
            ruta.chmod(modo)
        if respaldo.exists():
            raise ErrorProyeccion("hay un respaldo pendiente de una proyección anterior")
        if destino.exists():
            destino.rename(respaldo)
        montaje.rename(destino)
        if respaldo.exists():
            shutil.rmtree(respaldo)
    except Exception:
        if not destino.exists() and respaldo.exists():
            respaldo.rename(destino)
        raise
    finally:
        if montaje.exists():
            shutil.rmtree(montaje)


def sincronizar(
    raiz: Path, contrato: ContratoPlaneta, arbol: Arbol, config: Configuracion
) -> int:
    ficheros_raiz = ficheros_raiz_esperados(raiz, contrato, arbol, config)
    ajustes = ajustes_claude_esperados(raiz)
    fuentes = pueblos_fuente(arbol, contrato.nichos)
    esperado = {nombre: _ficheros_fuente(origen) for nombre, origen in fuentes.items()}

    for destino in DESTINOS:
        base = _ruta_del_planeta(raiz, Path(destino) / "skills")
        gestionados = _gestionados(base)
        for nombre in fuentes:
            if (base / nombre).exists() and nombre not in gestionados:
                raise ErrorProyeccion(f"no se sobrescribe lo ajeno: {destino}/skills/{nombre}")

    for ruta, contenido in ficheros_raiz.items():
        if not ruta.is_file() or ruta.read_bytes() != contenido:
            _escritura_atomica(ruta, contenido)
    # Solo si cambia algo efectivo, y sin reordenar: reescribir `.claude/settings.json` de
    # un repo ajeno con las mismas claves en orden alfabético ensuciaba su diff con ruido
    # cosmético (auditoría E-15). `actual | AJUSTES` conserva el orden de lo que había.
    ruta_ajustes = _ruta_del_planeta(raiz, Path(".claude/settings.json"))
    actuales = json.loads(ruta_ajustes.read_text(encoding="utf-8")) if ruta_ajustes.is_file() else None
    if actuales != ajustes:
        _escritura_atomica(
            ruta_ajustes,
            (json.dumps(ajustes, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
    for destino in DESTINOS:
        base = _ruta_del_planeta(raiz, Path(destino) / "skills")
        gestionados = _gestionados(base)
        for nombre, ficheros in esperado.items():
            _reemplazar(base / nombre, ficheros)
        for obsoleta in sorted(set(gestionados) - set(esperado)):
            shutil.rmtree(gestionados[obsoleta])
    return len(fuentes)


def iniciar(raiz: Path, arbol: Arbol, nombre: str | None, tipo: str, nichos: list[str]) -> None:
    ruta = _ruta_del_planeta(raiz, Path(CONTRATO))
    if ruta.exists() or ruta.is_symlink():
        raise ErrorProyeccion(f"{CONTRATO} ya existe; usa sincronizar")
    inexistentes = sorted(set(nichos) - set(nombres_nichos(arbol)))
    if inexistentes:
        raise ErrorProyeccion(f"nichos inexistentes: {', '.join(inexistentes)}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", tipo):
        raise ErrorProyeccion("tipo no es portable")
    _escritura_atomica(ruta, _contrato_en_blanco(nombre or raiz.name, tipo, nichos).encode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cosmos proyectar", description=__doc__)
    parser.add_argument("--config", default=None, help="cosmos.toml a usar")
    subparsers = parser.add_subparsers(dest="orden", required=True)
    ayudas = {
        "sincronizar": "inyecta el bloque marcado en CLAUDE.md/AGENTS.md del repo destino y sus pueblos como skills nativas",
        "comprobar": "rojo si el bloque o las skills del repo destino se desincronizaron con el contrato",
    }
    for orden in ("sincronizar", "comprobar"):
        hijo = subparsers.add_parser(orden, help=ayudas[orden])
        hijo.add_argument("repo", type=Path, help="raíz del repositorio Git ajeno")
    iniciar_parser = subparsers.add_parser(
        "iniciar", help="escribe planeta.toml en el repo destino; luego edítalo y ejecuta sincronizar"
    )
    iniciar_parser.add_argument("repo", type=Path, help="raíz del repositorio Git ajeno")
    iniciar_parser.add_argument("--nombre", help="nombre del planeta (por defecto, el del directorio)")
    iniciar_parser.add_argument("--tipo", default="generico", help="tipo de proyecto, minúsculas y guiones")
    iniciar_parser.add_argument("--nicho", action="append", default=[],
                                help="oficio a proyectar (repetible); sin ninguno, el contrato nace vacío")
    args = parser.parse_args(argv)

    try:
        config = cargar_configuracion(args.config)
        arbol = cargar_arbol(config.arbol, excluir=config.indice)
        propia = Path(config.ruta or Path.cwd()).parent
        raiz = raiz_del_planeta(Path(os.path.abspath(os.fspath(args.repo))), propia=propia)
        if args.orden == "iniciar":
            iniciar(raiz, arbol, args.nombre, args.tipo, list(dict.fromkeys(args.nicho)))
        contrato = cargar_contrato(raiz, arbol)
        lista = ",".join(contrato.nichos) or "ninguno"
        if args.orden == "iniciar" and not contrato.nichos:
            # Verde con cero proyectado es un verde que no dice nada (auditoría E-04).
            print(f"AVISO: contrato creado con 0 oficios proyectados: declara `nichos` en {CONTRATO} "
                  "y ejecuta sincronizar", file=sys.stderr)
        if args.orden == "comprobar":
            encontrados = problemas(raiz, contrato, arbol, config)
            if encontrados:
                for problema in encontrados:
                    print(f"ERROR: {problema}")
                return 1
            print(f"proyección correcta · nichos={lista}")
            return 0
        cuantos = sincronizar(raiz, contrato, arbol, config)
        print(f"proyección sincronizada · {cuantos} skills · nichos={lista}")
        return 0
    except (OSError, ErrorProyeccion, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
