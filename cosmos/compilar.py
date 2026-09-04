"""Compilación segura del árbol a la vista plana de skills."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .modelo import (ErrorCerrojo, cerrojo, escribir_atomico, Arbol, Nodo, nicho_de_nodo, normalizar_nichos,
                     parsear_frontmatter, sin_claves_cosmos)


NIVELES_APLANADOS = frozenset({"pueblo"})
VERSION_MANIFIESTO = 1


class ErrorCompilacion(RuntimeError):
    pass


@dataclass(frozen=True)
class ResultadoCompilacion:
    creadas: int = 0
    actualizadas: int = 0
    iguales: int = 0
    ajenas: int = 0
    eliminadas: int = 0
    preservadas: int = 0
    adoptadas: int = 0
    seco: bool = False
    acciones: tuple[str, ...] = field(default_factory=tuple)


def _resueltos(config_path: Path | None, arbol: Arbol, ruta: Path) -> Path:
    if ruta.is_absolute():
        return ruta.resolve()
    base = config_path.parent if config_path is not None else arbol.raiz
    return (base / ruta).resolve()


def rutas_compilacion(arbol: Arbol, destino: Path, manifiesto: Path, config_path: Path | None = None) -> tuple[Path, Path]:
    return _resueltos(config_path, arbol, destino), _resueltos(config_path, arbol, manifiesto)


# Directorios que un runtime de agentes escanea al arrancar: cada entrada que se materialice ahí
# inyecta su nombre y su descripción en el prompt de TODAS las sesiones (auditoría A-02). La
# vista completa (306 resúmenes, más que el presupuesto entero) solo entra ahí con `--todos`.
DESTINOS_ESCANEADOS = (".claude/skills", ".agents/skills")


def destino_escaneado(destino: Path) -> bool:
    ruta = destino.as_posix()
    return any(ruta.endswith(sufijo) for sufijo in DESTINOS_ESCANEADOS)


def _del_anfitrion(nodo: Nodo) -> bool:
    return nodo.datos.get("anfitrion") == "claude-code"


def _skills(arbol: Arbol, nichos: list[str] | tuple[str, ...] | None = None, *, todos: bool = False,
            herramientas: tuple[str, ...] | None = None, solo_anfitrion: bool = False) -> dict[str, Nodo]:
    """Los pueblos que se aplanan. `nichos=None` es NINGUNO, como en el catálogo (NUCLEO §2);
    la vista completa se pide explícita con `todos=True` (auditoría A-04: un mismo centinela
    significaba «nada» en un subsistema y «todo» en el otro).

    Dos entradas más, y las dos son del que usa el árbol, no del árbol: las `herramientas`
    elegidas (perfil o `[nichos] herramientas`) entran aunque su nicho duerma, y los pueblos con
    `anfitrion: claude-code` entran SIEMPRE, porque son las skills que el anfitrión ya tenía y
    COSMOS solo ordena; dejarlas fuera de la vista sería quitárselas.
    """

    seleccion = normalizar_nichos(arbol, nichos)
    if solo_anfitrion:
        seleccion, todos = None, False
    elegidas = set(herramientas or ())
    ordenados = sorted(arbol.nodos, key=lambda item: (item.nombre, item.ruta_cosmos, item.ruta_relativa))
    return {
        nodo.nombre: nodo
        for nodo in ordenados
        if nodo.cosmos in NIVELES_APLANADOS
        and (
            _del_anfitrion(nodo)
            or nodo.nombre in elegidas
            or (todos or (seleccion is not None and nicho_de_nodo(arbol, nodo) in seleccion))
        )
    }


def _ignorado(nombre: str) -> bool:
    return nombre.startswith(".") or nombre in {".git", "__pycache__"}


def _elementos(raiz: Path, *, filtrar: bool) -> list[Path]:
    if not raiz.exists():
        return []
    elementos: list[Path] = []
    for directorio, nombres_dir, nombres_fichero in os.walk(raiz, followlinks=False):
        if filtrar:
            nombres_dir[:] = sorted(nombre for nombre in nombres_dir if not _ignorado(nombre))
            nombres_fichero = [nombre for nombre in nombres_fichero if not _ignorado(nombre)]
        else:
            nombres_dir.sort()
        base = Path(directorio)
        for nombre in sorted(nombres_dir):
            ruta = base / nombre
            if ruta.is_symlink():
                elementos.append(ruta)
        for nombre in sorted(nombres_fichero):
            elementos.append(base / nombre)
    return sorted(elementos, key=lambda ruta: ruta.relative_to(raiz).as_posix())


def _traducido(relativa: bytes, contenido: bytes) -> bytes:
    """El SKILL.md raíz de una copia lleva `name`/`description` para el anfitrión (R-22).

    Si el pueblo declara `anfitrion: claude-code`, la copia es el fichero ORIGINAL del anfitrión
    byte a byte: se quitan las claves de COSMOS y no se añade nada. Es lo que hace reversible
    organizar un arnés con COSMOS: `git diff` sobre la vista tiene que dar vacío.
    """

    if relativa == b"SKILL.md":
        texto = contenido.decode("utf-8-sig", errors="replace")
        try:
            datos, _ = parsear_frontmatter(texto, "SKILL.md")
        except ValueError:
            datos = {}
        if datos.get("anfitrion") == "claude-code":
            return sin_claves_cosmos(texto).encode("utf-8")
        from puente.proyectar import para_el_anfitrion

        return para_el_anfitrion(contenido)
    return contenido


# --- Los otros ficheros de runtime: reglas, agentes y comandos ---------------------------
#
# El anfitrión lee cuatro cosas: skills (la vista plana de arriba), reglas por rutas, agentes y
# comandos. Las tres últimas se generan desde nodos con `anfitrion: claude-code` —un lago o un mar
# es una regla, una luna es un agente, un río con `invoca: /x` es un comando— quitando las claves
# de COSMOS. Un manifiesto por destino: lo que COSMOS escribió se actualiza o se retira; lo que
# no escribió (ajeno) no se toca nunca, y lo que alguien editó después de escribirlo se preserva.

TIPOS_RUNTIME = {
    "rules": frozenset({"oceano", "mar", "lago"}),
    "agentes": frozenset({"luna"}),
    "comandos": frozenset({"rio"}),
}


def manifiesto_runtime(config: Any, tipo: str) -> Path:
    base = Path(config.manifiesto_compilacion)
    return base.with_name(f"{base.stem}-{tipo}{base.suffix}")


def nodos_runtime(arbol: Arbol, tipo: str) -> dict[str, Nodo]:
    niveles = TIPOS_RUNTIME[tipo]
    elegidos = {}
    for nodo in sorted(arbol.nodos, key=lambda n: (n.nombre, n.ruta_relativa)):
        if nodo.cosmos not in niveles or not _del_anfitrion(nodo):
            continue
        if tipo == "comandos" and not str(nodo.datos.get("invoca", "")).startswith("/"):
            continue
        elegidos[f"{nodo.nombre}.md"] = nodo
    return elegidos


def contenido_runtime(nodo: Nodo) -> str:
    return sin_claves_cosmos(nodo.contenido)


def _hash_texto(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _leer_manifiesto_runtime(ruta: Path) -> dict[str, Any] | None:
    if not ruta.is_file():
        return None
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ErrorCompilacion(f"manifiesto ilegible: {ruta} ({exc})") from exc
    if not isinstance(datos, dict) or not isinstance(datos.get("entradas"), dict):
        raise ErrorCompilacion(f"manifiesto con forma inesperada: {ruta}")
    return datos


def compilar_runtime(arbol: Arbol, tipo: str, destino: Path, manifiesto: Path, *, seco: bool = False) -> ResultadoCompilacion:
    """Materializa un tipo de runtime en su destino. Misma política que la vista plana."""

    if tipo not in TIPOS_RUNTIME:
        raise ErrorCompilacion(f"tipo de runtime desconocido: {tipo}")
    destino = Path(destino)
    manifiesto = Path(manifiesto)
    datos = _leer_manifiesto_runtime(manifiesto)
    antiguas: dict[str, dict[str, str]] = datos["entradas"] if datos else {}
    esperadas = nodos_runtime(arbol, tipo)
    existentes = {p.name for p in destino.iterdir() if p.is_file()} if destino.is_dir() else set()
    ajenas_nombres = existentes - set(antiguas)
    acciones: list[str] = []
    creadas = actualizadas = iguales = eliminadas = preservadas = adoptadas = 0
    nuevas: dict[str, dict[str, str]] = {}

    def _rel(ruta: Path) -> str:
        try:
            return os.path.relpath(ruta)
        except ValueError:
            return str(ruta)

    def _actual(ruta: Path) -> str | None:
        if ruta.is_symlink() or not ruta.is_file():
            return None
        return _hash_texto(ruta.read_text(encoding="utf-8", errors="replace"))

    for nombre, nodo in esperadas.items():
        entrada = destino / nombre
        esperado = _hash_texto(contenido_runtime(nodo))
        registro = antiguas.get(nombre)
        if registro is None and entrada.exists():
            if _actual(entrada) == esperado:
                adoptadas += 1
                ajenas_nombres.discard(nombre)
                acciones.append(f"ADOPTAR {_rel(entrada)}")
                nuevas[nombre] = {"hash": esperado, "origen": os.path.relpath(nodo.ruta, start=manifiesto.parent)}
                continue
            acciones.append(f"AJENA {_rel(entrada)}")
            continue
        if _actual(entrada) == esperado:
            iguales += 1
            acciones.append(f"IGUAL {_rel(entrada)}")
        elif registro is None:
            creadas += 1
            acciones.append(f"CREAR {_rel(entrada)}")
        elif _actual(entrada) != registro.get("hash"):
            # Lo que COSMOS escribió y alguien cambió después: no se pisa, se dice.
            preservadas += 1
            ajenas_nombres.add(nombre)
            acciones.append(f"PRESERVAR {_rel(entrada)}")
            continue
        else:
            actualizadas += 1
            acciones.append(f"ACTUALIZAR {_rel(entrada)}")
        nuevas[nombre] = {"hash": esperado, "origen": os.path.relpath(nodo.ruta, start=manifiesto.parent)}

    for nombre, registro in sorted(antiguas.items()):
        if nombre in esperadas:
            continue
        entrada = destino / nombre
        if _actual(entrada) == registro.get("hash"):
            eliminadas += 1
            acciones.append(f"ELIMINAR {_rel(entrada)}")
        elif entrada.exists():
            preservadas += 1
            ajenas_nombres.add(nombre)
            acciones.append(f"PRESERVAR {_rel(entrada)}")

    resultado = ResultadoCompilacion(creadas=creadas, actualizadas=actualizadas, iguales=iguales, ajenas=len(ajenas_nombres),
                                     eliminadas=eliminadas, preservadas=preservadas, adoptadas=adoptadas, seco=seco,
                                     acciones=tuple(acciones))
    if seco:
        return resultado
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, nodo in esperadas.items():
        if nombre not in nuevas:
            continue
        entrada = destino / nombre
        texto = contenido_runtime(nodo)
        if _actual(entrada) != _hash_texto(texto):
            escribir_atomico(entrada, texto)
    for nombre, registro in sorted(antiguas.items()):
        if nombre in esperadas:
            continue
        entrada = destino / nombre
        if _actual(entrada) == registro.get("hash"):
            entrada.unlink()
    contenido = json.dumps({"esquema": 1, "tipo": tipo, "destino": os.path.relpath(destino, start=manifiesto.parent),
                            "entradas": nuevas}, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if not manifiesto.exists() or manifiesto.read_text(encoding="utf-8") != contenido:
        escribir_atomico(manifiesto, contenido)
    return resultado


def errores_runtime(arbol: Arbol, tipo: str, destino: Path, manifiesto: Path) -> list[str]:
    """Lo que E22 comprueba: cada nodo del anfitrión tiene su fichero generado, igual a él."""

    esperadas = nodos_runtime(arbol, tipo)
    try:
        datos = _leer_manifiesto_runtime(Path(manifiesto))
    except ErrorCompilacion as exc:
        return [str(exc)]
    if datos is None:
        return [f"falta el manifiesto {manifiesto}"] if esperadas else []
    entradas = datos["entradas"]
    errores: list[str] = []
    for nombre, nodo in esperadas.items():
        entrada = Path(destino) / nombre
        esperado = _hash_texto(contenido_runtime(nodo))
        if not entrada.is_file():
            errores.append(f"falta {entrada}")
            continue
        actual = _hash_texto(entrada.read_text(encoding="utf-8", errors="replace"))
        if actual != esperado:
            errores.append(f"{entrada} no coincide con su nodo {nodo.ruta_relativa}")
        elif not isinstance(entradas.get(nombre), dict):
            errores.append(f"{entrada} no está en el manifiesto")
    for nombre in sorted(set(entradas) - set(esperadas)):
        entrada = Path(destino) / nombre
        if entrada.exists():
            errores.append(f"{entrada} está en el manifiesto y ya no tiene nodo")
    return errores


def _hash_directorio(raiz: Path, *, filtrar: bool, traducir: bool = False) -> str:
    digest = hashlib.sha256()
    for ruta in _elementos(raiz, filtrar=filtrar):
        relativa = ruta.relative_to(raiz).as_posix().encode("utf-8")
        if ruta.is_symlink():
            clase = b"L"
            contenido = os.readlink(ruta).encode("utf-8")
        elif ruta.is_file():
            clase = b"F"
            contenido = ruta.read_bytes()
            if traducir:
                contenido = _traducido(relativa, contenido)
        else:
            continue
        digest.update(clase + b"\0" + relativa + b"\0" + contenido + b"\0")
    return digest.hexdigest()


def _hash_symlink(enlace: Path) -> str | None:
    if not enlace.is_symlink():
        return None
    return hashlib.sha256(("symlink\0" + os.readlink(enlace)).encode("utf-8")).hexdigest()


def _objetivo_relativo(origen: Path, entrada: Path) -> str:
    return os.path.relpath(origen.resolve(), start=entrada.parent.resolve())


def _hash_esperado(origen: Path, entrada: Path, modo: str) -> str:
    if modo == "symlink":
        objetivo = _objetivo_relativo(origen, entrada)
        return hashlib.sha256(("symlink\0" + objetivo).encode("utf-8")).hexdigest()
    # La copia que se materializa lleva el SKILL.md traducido: el hash esperado también.
    return _hash_directorio(origen, filtrar=True, traducir=True)


def _hash_actual(entrada: Path, modo: str) -> str | None:
    if modo == "symlink":
        return _hash_symlink(entrada)
    if entrada.is_symlink() or not entrada.is_dir():
        return None
    return _hash_directorio(entrada, filtrar=False)


def _leer_manifiesto(ruta: Path) -> dict[str, Any] | None:
    if not ruta.exists():
        return None
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ErrorCompilacion(f"manifiesto ilegible {ruta}: {exc}") from exc
    if (
        not isinstance(datos, dict)
        or datos.get("version") != VERSION_MANIFIESTO
        or not isinstance(datos.get("entradas"), dict)
        or not isinstance(datos.get("destino"), str)
    ):
        raise ErrorCompilacion(f"manifiesto inválido {ruta}")
    return datos


def _destino_declarado(manifiesto: Path, valor: str) -> Path:
    ruta = Path(valor)
    return ruta.resolve() if ruta.is_absolute() else (manifiesto.parent / ruta).resolve()


def _serializar_manifiesto(
    destino: Path,
    manifiesto: Path,
    entradas: dict[str, dict[str, str]],
    nichos: tuple[str, ...] | None,
) -> str:
    return json.dumps(
        {
            "destino": os.path.relpath(destino, start=manifiesto.parent),
            "entradas": entradas,
            "nichos": list(nichos) if nichos is not None else None,
            "version": VERSION_MANIFIESTO,
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def _borrar_entrada(ruta: Path) -> None:
    if ruta.is_symlink() or ruta.is_file():
        ruta.unlink()
    elif ruta.is_dir():
        shutil.rmtree(ruta)


def _ignorar_copia(_: str, nombres: list[str]) -> set[str]:
    return {nombre for nombre in nombres if _ignorado(nombre)}


def _crear_entrada(origen: Path, entrada: Path, modo: str) -> None:
    entrada.parent.mkdir(parents=True, exist_ok=True)
    if modo == "symlink":
        descriptor, nombre_temporal = tempfile.mkstemp(prefix=f".{entrada.name}.", dir=entrada.parent)
        os.close(descriptor)
        temporal = Path(nombre_temporal)
        temporal.unlink()
        try:
            temporal.symlink_to(_objetivo_relativo(origen, entrada), target_is_directory=True)
            os.replace(temporal, entrada)
        finally:
            temporal.unlink(missing_ok=True)
        return
    temporal_raiz = Path(tempfile.mkdtemp(prefix=f".{entrada.name}.", dir=entrada.parent))
    temporal = temporal_raiz / entrada.name
    try:
        shutil.copytree(origen, temporal, symlinks=True, ignore=_ignorar_copia)
        # La vista compilada en copia es lo que un runtime escanea: 306 de 306 entradas iban sin
        # `name`/`description` y ningún runtime las veía (revisión R-22). Misma traducción que
        # `proyectar`, y el hash esperado la incluye, así que E19 no la confunde con una edición.
        skill = temporal / "SKILL.md"
        if skill.is_file() and not skill.is_symlink():
            skill.write_bytes(_traducido(b"SKILL.md", skill.read_bytes()))
        os.replace(temporal, entrada)
    finally:
        if temporal_raiz.exists():
            shutil.rmtree(temporal_raiz)


def errores_vista(
    arbol: Arbol,
    destino: Path,
    manifiesto: Path,
    modo: str,
    *,
    nichos: list[str] | tuple[str, ...] | None = None,
    config_path: Path | None = None,
    herramientas: tuple[str, ...] | None = None,
    solo_anfitrion: bool = False,
) -> list[str]:
    destino, manifiesto = rutas_compilacion(arbol, destino, manifiesto, config_path)
    seleccion = normalizar_nichos(arbol, nichos)
    # Sin selección en `cosmos.toml`, la vista que se valida es la completa: es la que deja el
    # bootstrap de un clon, y el manifiesto la registra como `nichos: null`.
    esperadas = _skills(arbol, seleccion, todos=seleccion is None and not solo_anfitrion, herramientas=herramientas, solo_anfitrion=solo_anfitrion)
    try:
        datos = _leer_manifiesto(manifiesto)
    except ErrorCompilacion as exc:
        return [str(exc)]
    if datos is None:
        return [f"falta el manifiesto {manifiesto}"] if esperadas else []
    if _destino_declarado(manifiesto, datos["destino"]) != destino:
        return [f"el manifiesto apunta a {datos['destino']} y no a {destino}"]
    nichos_declarados = list(seleccion) if seleccion is not None else None
    if datos.get("nichos") != nichos_declarados:
        return [f"el manifiesto declara nichos {datos.get('nichos')!r} y se validan {nichos_declarados!r}"]
    entradas = datos["entradas"]
    errores: list[str] = []
    for nombre, nodo in esperadas.items():
        entrada = destino / nombre
        registrada = entradas.get(nombre)
        if not isinstance(registrada, dict):
            errores.append(f"{nombre}: no figura en el manifiesto")
            continue
        if registrada.get("modo") != modo:
            errores.append(f"{nombre}: modo distinto del configurado")
            continue
        esperado = _hash_esperado(nodo.ruta.parent, entrada, modo)
        if registrada.get("hash") != esperado:
            errores.append(f"{nombre}: hash desincronizado en el manifiesto")
            continue
        if _hash_actual(entrada, modo) != esperado:
            errores.append(f"{nombre}: contenido o enlace distinto del árbol")
    for nombre in sorted(set(entradas) - set(esperadas)):
        errores.append(f"{nombre}: entrada obsoleta en el manifiesto")
    return errores


def compilar_arbol(
    arbol: Arbol,
    *,
    destino: Path,
    manifiesto: Path,
    modo: str = "symlink",
    seco: bool = False,
    nichos: list[str] | tuple[str, ...] | None = None,
    config_path: Path | None = None,
    todos: bool | None = None,
    herramientas: tuple[str, ...] | None = None,
    solo_anfitrion: bool = False,
    _bloqueado: bool = False,
) -> ResultadoCompilacion:
    if modo not in {"symlink", "copia"}:
        raise ErrorCompilacion("modo debe ser 'symlink' o 'copia'")
    destino, manifiesto = rutas_compilacion(arbol, destino, manifiesto, config_path)
    seleccion = normalizar_nichos(arbol, nichos)
    # Compatibilidad del manifiesto: sin selección, la vista es la completa y se registra como
    # `nichos: null`. Pero materializarla en un directorio que un runtime escanea es la fuga
    # que COSMOS existe para eliminar: ahí hace falta `--todos` explícito (auditoría A-02).
    explicito = todos is True
    if todos is None:
        todos = seleccion is None and not solo_anfitrion
    if modo == "symlink" and destino_escaneado(destino) and not _bloqueado and not seco:
        raise ErrorCompilacion(
            f"{destino} es un directorio que el runtime escanea y en modo symlink las entradas apuntan al "
            "SKILL.md original, sin `name`/`description`: el anfitrión no las ve (R-22). Usa --modo copia."
        )
    if todos and not explicito and destino_escaneado(destino) and not _bloqueado and not seco:
        raise ErrorCompilacion(
            f"{destino} es un directorio que el runtime escanea: aplanar TODOS los pueblos ahí inyecta cada "
            "resumen en cada sesión (más que el presupuesto entero). Acota con --nicho o [nichos] activos, "
            "o pide la vista completa a propósito con --todos."
        )
    if not seco and not _bloqueado:
        # El cerrojo compartido sabe distinguir «ocupado» de «alguien murió aquí»: antes,
        # un proceso muerto sin llegar al `finally` dejaba el fichero y toda compilación
        # futura fallaba para siempre.
        try:
            with cerrojo(manifiesto.parent / "compilar.lock", que_hace="compilación"):
                return compilar_arbol(
                    arbol,
                    destino=destino,
                    manifiesto=manifiesto,
                    modo=modo,
                    seco=False,
                    nichos=seleccion,
                    todos=todos,
                    herramientas=herramientas,
                    solo_anfitrion=solo_anfitrion,
                    _bloqueado=True,
                )
        except ErrorCerrojo as exc:
            raise ErrorCompilacion(str(exc)) from exc
    datos = _leer_manifiesto(manifiesto)
    if datos is not None and _destino_declarado(manifiesto, datos["destino"]) != destino:
        raise ErrorCompilacion(f"el manifiesto pertenece a otro destino: {datos['destino']}")
    antiguas: dict[str, dict[str, str]] = datos["entradas"] if datos else {}
    esperadas = _skills(arbol, seleccion, todos=todos, herramientas=herramientas, solo_anfitrion=solo_anfitrion)
    existentes = {ruta.name for ruta in destino.iterdir()} if destino.is_dir() else set()
    ajenas_nombres = existentes - set(antiguas)
    acciones: list[str] = []
    creadas = actualizadas = iguales = eliminadas = preservadas = adoptadas = 0

    def _rel(ruta: Path) -> str:
        # Relativas al directorio actual (R-50): las absolutas eran material para el escáner de
        # secretos y 40 KB de ruido en el primer comando del README.
        try:
            return os.path.relpath(ruta)
        except ValueError:
            return str(ruta)
    nuevas: dict[str, dict[str, str]] = {}

    for nombre, nodo in esperadas.items():
        entrada = destino / nombre
        origen = nodo.ruta.parent.resolve()
        hash_esperado = _hash_esperado(origen, entrada, modo)
        registro = antiguas.get(nombre)
        if registro is None and (entrada.exists() or entrada.is_symlink()):
            # La ausencia del manifiesto NO convierte lo propio en ajeno. Sin esta
            # rama, borrar `.cosmos/` (un artefacto generado, gitignored) dejaba la
            # vista plana huérfana para siempre: `compilar` clasificaba sus propias
            # entradas como ajenas, E19 mandaba a ejecutar `compilar`, y `compilar`
            # las respetaba — el único camino de vuelta era borrar a mano lo que el
            # mensaje prohíbe tocar a mano. Se adopta SOLO lo idéntico byte a byte
            # (o el symlink con el mismo objetivo) a lo que se crearía: con hash
            # igual no hay nada ajeno que perder. Lo que difiere sigue siendo ajeno.
            if _hash_actual(entrada, modo) == hash_esperado:
                adoptadas += 1
                ajenas_nombres.discard(nombre)
                acciones.append(f"ADOPTAR {_rel(entrada)}")
                nuevas[nombre] = {
                    "hash": hash_esperado,
                    "modo": modo,
                    "origen": os.path.relpath(origen, start=manifiesto.parent),
                }
                continue
            acciones.append(f"AJENA {_rel(entrada)}")
            continue
        correcto = _hash_actual(entrada, modo) == hash_esperado
        if correcto and isinstance(registro, dict) and registro.get("modo") == modo:
            iguales += 1
            acciones.append(f"IGUAL {_rel(entrada)}")
        else:
            if registro is None:
                creadas += 1
                acciones.append(f"CREAR {_rel(entrada)}")
            else:
                actualizadas += 1
                acciones.append(f"ACTUALIZAR {_rel(entrada)}")
        nuevas[nombre] = {
            "hash": hash_esperado,
            "modo": modo,
            "origen": os.path.relpath(origen, start=manifiesto.parent),
        }

    for nombre, registro in sorted(antiguas.items()):
        if nombre in esperadas:
            continue
        entrada = destino / nombre
        actual = _hash_actual(entrada, str(registro.get("modo", "")))
        if actual == registro.get("hash"):
            eliminadas += 1
            acciones.append(f"ELIMINAR {_rel(entrada)}")
        else:
            preservadas += 1
            ajenas_nombres.add(nombre)
            acciones.append(f"PRESERVAR {_rel(entrada)}")

    resultado = ResultadoCompilacion(
        creadas=creadas,
        actualizadas=actualizadas,
        iguales=iguales,
        ajenas=len(ajenas_nombres),
        eliminadas=eliminadas,
        preservadas=preservadas,
        adoptadas=adoptadas,
        seco=seco,
        acciones=tuple(acciones),
    )
    if seco:
        return resultado

    destino.mkdir(parents=True, exist_ok=True)
    for nombre, nodo in esperadas.items():
        entrada = destino / nombre
        registro = antiguas.get(nombre)
        if registro is None and (entrada.exists() or entrada.is_symlink()):
            continue
        esperado = _hash_esperado(nodo.ruta.parent.resolve(), entrada, modo)
        if _hash_actual(entrada, modo) != esperado or not isinstance(registro, dict) or registro.get("modo") != modo:
            _borrar_entrada(entrada)
            _crear_entrada(nodo.ruta.parent.resolve(), entrada, modo)
    for nombre, registro in sorted(antiguas.items()):
        if nombre in esperadas:
            continue
        entrada = destino / nombre
        if _hash_actual(entrada, str(registro.get("modo", ""))) == registro.get("hash"):
            _borrar_entrada(entrada)
    contenido = _serializar_manifiesto(destino, manifiesto, nuevas, seleccion)
    actual_manifest = manifiesto.read_text(encoding="utf-8") if manifiesto.exists() else None
    if actual_manifest != contenido:
        escribir_atomico(manifiesto, contenido)
    return resultado


def formatear_compilacion(resultado: ResultadoCompilacion, *, detalle: bool = False) -> str:
    """El resumen siempre; las acciones una a una solo con `--detalle` o en seco.

    Sin esto `arrancar` —el primer comando del README— costaba 247 líneas de `CREAR
    <ruta absoluta>` (≈9.900 tokens), y la segunda vez, sin cambiar nada, 247 de `IGUAL`:
    5,7 veces el recorrido guiado entero, en un proyecto cuya tesis es no gastar de más
    (auditoría E-03). `IGUAL` no se imprime nunca sin pedirlo.
    """

    modo = "seco" if resultado.seco else "verde"
    lineas = [
        f"COSMOS  compilar  {modo}",
        "",
        (
            f"Creadas {resultado.creadas}; actualizadas {resultado.actualizadas}; "
            f"iguales {resultado.iguales}; adoptadas {resultado.adoptadas}; "
            f"ajenas respetadas {resultado.ajenas}; "
            f"obsoletas eliminadas {resultado.eliminadas}; obsoletas preservadas {resultado.preservadas}."
        ),
    ]
    if detalle or resultado.seco:
        lineas.extend(resultado.acciones)
    elif resultado.acciones:
        cambios = [accion for accion in resultado.acciones if not accion.startswith("IGUAL ")]
        if cambios:
            lineas.append(f"({len(cambios)} cambio(s); 'cosmos compilar --detalle' o '--seco' los lista uno a uno)")
    return "\n".join(lineas) + "\n"
