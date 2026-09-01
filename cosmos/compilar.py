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

from .modelo import Arbol, Nodo


NIVELES_APLANADOS = frozenset({"ciudad", "pueblo"})
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
    seco: bool = False
    acciones: tuple[str, ...] = field(default_factory=tuple)


def _resueltos(config_path: Path | None, arbol: Arbol, ruta: Path) -> Path:
    if ruta.is_absolute():
        return ruta.resolve()
    base = config_path.parent if config_path is not None else arbol.raiz
    return (base / ruta).resolve()


def rutas_compilacion(arbol: Arbol, destino: Path, manifiesto: Path, config_path: Path | None = None) -> tuple[Path, Path]:
    return _resueltos(config_path, arbol, destino), _resueltos(config_path, arbol, manifiesto)


def _skills(arbol: Arbol) -> dict[str, Nodo]:
    return {
        nodo.nombre: nodo
        for nodo in sorted(arbol.nodos, key=lambda item: (item.nombre, item.ruta_cosmos, item.ruta_relativa))
        if nodo.cosmos in NIVELES_APLANADOS
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


def _hash_directorio(raiz: Path, *, filtrar: bool) -> str:
    digest = hashlib.sha256()
    for ruta in _elementos(raiz, filtrar=filtrar):
        relativa = ruta.relative_to(raiz).as_posix().encode("utf-8")
        if ruta.is_symlink():
            clase = b"L"
            contenido = os.readlink(ruta).encode("utf-8")
        elif ruta.is_file():
            clase = b"F"
            contenido = ruta.read_bytes()
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
    return _hash_directorio(origen, filtrar=True)


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


def _serializar_manifiesto(destino: Path, manifiesto: Path, entradas: dict[str, dict[str, str]]) -> str:
    return json.dumps(
        {
            "destino": os.path.relpath(destino, start=manifiesto.parent),
            "entradas": entradas,
            "version": VERSION_MANIFIESTO,
        },
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def _escribir_atomico(ruta: Path, contenido: str) -> None:
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
        os.replace(temporal, entrada)
    finally:
        if temporal_raiz.exists():
            shutil.rmtree(temporal_raiz)


def errores_vista(arbol: Arbol, destino: Path, manifiesto: Path, modo: str, *, config_path: Path | None = None) -> list[str]:
    destino, manifiesto = rutas_compilacion(arbol, destino, manifiesto, config_path)
    esperadas = _skills(arbol)
    try:
        datos = _leer_manifiesto(manifiesto)
    except ErrorCompilacion as exc:
        return [str(exc)]
    if datos is None:
        return [f"falta el manifiesto {manifiesto}"] if esperadas else []
    if _destino_declarado(manifiesto, datos["destino"]) != destino:
        return [f"el manifiesto apunta a {datos['destino']} y no a {destino}"]
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
    config_path: Path | None = None,
    _bloqueado: bool = False,
) -> ResultadoCompilacion:
    if modo not in {"symlink", "copia"}:
        raise ErrorCompilacion("modo debe ser 'symlink' o 'copia'")
    destino, manifiesto = rutas_compilacion(arbol, destino, manifiesto, config_path)
    if not seco and not _bloqueado:
        manifiesto.parent.mkdir(parents=True, exist_ok=True)
        lock = manifiesto.parent / "compilar.lock"
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError as exc:
            raise ErrorCompilacion(f"otra compilación está en curso: {lock}") from exc
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as fichero:
                fichero.write(f"{os.getpid()}\n")
            return compilar_arbol(
                arbol,
                destino=destino,
                manifiesto=manifiesto,
                modo=modo,
                seco=False,
                _bloqueado=True,
            )
        finally:
            lock.unlink(missing_ok=True)
    datos = _leer_manifiesto(manifiesto)
    if datos is not None and _destino_declarado(manifiesto, datos["destino"]) != destino:
        raise ErrorCompilacion(f"el manifiesto pertenece a otro destino: {datos['destino']}")
    antiguas: dict[str, dict[str, str]] = datos["entradas"] if datos else {}
    esperadas = _skills(arbol)
    existentes = {ruta.name for ruta in destino.iterdir()} if destino.is_dir() else set()
    ajenas_nombres = existentes - set(antiguas)
    acciones: list[str] = []
    creadas = actualizadas = iguales = eliminadas = preservadas = 0
    nuevas: dict[str, dict[str, str]] = {}

    for nombre, nodo in esperadas.items():
        entrada = destino / nombre
        origen = nodo.ruta.parent.resolve()
        hash_esperado = _hash_esperado(origen, entrada, modo)
        registro = antiguas.get(nombre)
        if registro is None and (entrada.exists() or entrada.is_symlink()):
            acciones.append(f"AJENA {entrada}")
            continue
        correcto = _hash_actual(entrada, modo) == hash_esperado
        if correcto and isinstance(registro, dict) and registro.get("modo") == modo:
            iguales += 1
            acciones.append(f"IGUAL {entrada}")
        else:
            if registro is None:
                creadas += 1
                acciones.append(f"CREAR {entrada}")
            else:
                actualizadas += 1
                acciones.append(f"ACTUALIZAR {entrada}")
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
            acciones.append(f"ELIMINAR {entrada}")
        else:
            preservadas += 1
            ajenas_nombres.add(nombre)
            acciones.append(f"PRESERVAR {entrada}")

    resultado = ResultadoCompilacion(
        creadas=creadas,
        actualizadas=actualizadas,
        iguales=iguales,
        ajenas=len(ajenas_nombres),
        eliminadas=eliminadas,
        preservadas=preservadas,
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
    contenido = _serializar_manifiesto(destino, manifiesto, nuevas)
    actual_manifest = manifiesto.read_text(encoding="utf-8") if manifiesto.exists() else None
    if actual_manifest != contenido:
        _escribir_atomico(manifiesto, contenido)
    return resultado


def formatear_compilacion(resultado: ResultadoCompilacion) -> str:
    modo = "seco" if resultado.seco else "verde"
    lineas = [
        f"COSMOS  compilar  {modo}",
        "",
        (
            f"Creadas {resultado.creadas}; actualizadas {resultado.actualizadas}; "
            f"iguales {resultado.iguales}; ajenas respetadas {resultado.ajenas}; "
            f"obsoletas eliminadas {resultado.eliminadas}; obsoletas preservadas {resultado.preservadas}."
        ),
    ]
    lineas.extend(resultado.acciones)
    return "\n".join(lineas) + "\n"
