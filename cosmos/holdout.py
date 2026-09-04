"""Holdout externo con encargos que el árbol no ha podido aprender.

Vive fuera del repositorio versionado porque quien tiene el repositorio tendría
también el examen. Su procedencia se contrasta con toda la historia de Git: un
fichero borrado sigue siendo legible con ``git show``.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from puente.lluvia import normalizar


VARIABLE_ENTORNO = "COSMOS_HOLDOUT"
RUTA_POR_DEFECTO = Path.home() / ".cosmos" / "holdout" / "encargos-validacion.json"


def ruta_por_defecto() -> Path:
    """Devuelve la ruta externa configurada o la convencional."""
    valor = os.environ.get(VARIABLE_ENTORNO)
    return Path(os.path.expanduser(valor)) if valor else RUTA_POR_DEFECTO


def intervalo_wilson(aciertos: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Calcula el intervalo de Wilson en puntos porcentuales."""
    if total <= 0 or not 0 <= aciertos <= total:
        raise ValueError("aciertos debe estar entre cero y total, y total debe ser positivo")
    proporcion = aciertos / total
    z2 = z * z
    denominador = 1 + z2 / total
    centro = (proporcion + z2 / (2 * total)) / denominador
    radicando = proporcion * (1 - proporcion) / total + z2 / (4 * total * total)
    semi = z * math.sqrt(radicando) / denominador
    limites = (100 * (centro - semi), 100 * (centro + semi))
    return tuple(round(min(100.0, max(0.0, limite)), 1) for limite in limites)


def normalizar_peticion(texto: str) -> str:
    """Lleva una petición a la forma comparable del árbol."""
    return " ".join(normalizar(texto))


@dataclass(frozen=True)
class Procedencia:
    comprobada: bool | None
    quemadas: tuple[str, ...]
    blobs_revisados: int
    motivo: str

    @property
    def limpia(self) -> bool:
        return self.comprobada is True and not self.quemadas


def _peticiones_json(contenido: bytes) -> set[str]:
    try:
        datos = json.loads(contenido)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return set()
    if not isinstance(datos, list):
        return set()
    return {
        normalizar_peticion(elemento["peticion"])
        for elemento in datos
        if isinstance(elemento, dict) and isinstance(elemento.get("peticion"), str)
    }


def _leer_lote(salida: bytes) -> tuple[set[str], int]:
    flujo = BytesIO(salida)
    peticiones: set[str] = set()
    revisados = 0
    while cabecera := flujo.readline():
        campos = cabecera.split()
        if len(campos) >= 2 and campos[1] == b"missing":
            continue
        if len(campos) != 3:
            break
        try:
            tamano = int(campos[2])
        except ValueError:
            break
        contenido = flujo.read(tamano)
        flujo.read(1)
        if len(contenido) != tamano:
            break
        if campos[1] == b"blob":
            revisados += 1
            peticiones.update(_peticiones_json(contenido))
    return peticiones, revisados


def es_superficial(raiz_repo: Path) -> bool | None:
    """`True` si el clon es superficial (`--depth`): su historia no es la historia."""
    try:
        r = subprocess.run(["git", "-C", str(raiz_repo), "rev-parse", "--is-shallow-repository"],
                           capture_output=True, check=False, text=True)
    except FileNotFoundError:
        return None
    if r.returncode != 0:
        return None
    return r.stdout.strip() == "true"


def comprobar_procedencia(raiz_repo: Path, peticiones: Iterable[str]) -> Procedencia:
    """Busca si alguna petición del examen ya apareció en el repositorio.

    Trivalente de verdad (auditoría R-17): sobre un clon superficial —el defecto de
    `actions/checkout`— o cuando no se ha revisado ni un blob, la respuesta es «no lo
    sé», nunca «limpia». `AUSENTE == AUSENTE` no es una comprobación.
    """
    originales = tuple(peticiones)
    try:
        historia = subprocess.run(
            ["git", "-C", str(raiz_repo), "rev-list", "--all", "--objects"],
            capture_output=True, check=False, text=True,
        )
    except FileNotFoundError:
        return Procedencia(None, (), 0, "git no está disponible; procedencia no comprobada")
    if historia.returncode != 0:
        return Procedencia(None, (), 0, "la ruta no es un repositorio git; procedencia no comprobada")
    if es_superficial(raiz_repo):
        return Procedencia(None, (), 0, "clon superficial: la historia no está entera; procedencia no comprobada (fetch-depth: 0)")

    lineas_json = (
        linea.split(" ", 1)[0]
        for linea in historia.stdout.splitlines()
        if " " in linea and linea.split(" ", 1)[1].endswith(".json")
    )
    shas = list(dict.fromkeys(lineas_json))
    encontradas: set[str] = set()
    revisados = 0
    if shas:
        lote = subprocess.run(
            ["git", "-C", str(raiz_repo), "cat-file", "--batch"],
            input=("\n".join(shas) + "\n").encode(), capture_output=True, check=False,
        )
        encontradas, revisados = _leer_lote(lote.stdout)

    arbol = subprocess.run(
        ["git", "-C", str(raiz_repo), "ls-files", "-z", "--", "*.json"],
        capture_output=True, check=False,
    )
    if arbol.returncode == 0:
        for nombre in filter(None, arbol.stdout.split(b"\0")):
            try:
                contenido = (raiz_repo / os.fsdecode(nombre)).read_bytes()
            except OSError:
                continue
            encontradas.update(_peticiones_json(contenido))

    quemadas = tuple(
        original for original in originales if normalizar_peticion(original) in encontradas
    )
    if quemadas:
        return Procedencia(True, quemadas, revisados,
                           f"{len(quemadas)} de {len(originales)} peticiones ya están en el repositorio: examen visto")
    if revisados == 0:
        return Procedencia(None, (), 0, "ningún blob .json en la historia: no hay contra qué comprobar; procedencia no comprobada")
    return Procedencia(True, (), revisados, f"{revisados} blobs .json revisados en la historia; 0 coincidencias")


def esta_dentro(raiz_repo: Path, ruta: Path) -> bool:
    """Si la ruta vive bajo la raíz del repositorio (resuelta). Fuera del repo no hay nada que versionar."""
    try:
        return Path(ruta).resolve().is_relative_to(Path(raiz_repo).resolve())
    except (OSError, RuntimeError):
        return False


@dataclass(frozen=True)
class Compromiso:
    """Cuándo quedó fijado el examen en la historia versionada, si es que quedó.

    El sello dice de qué contenido se fía; el compromiso dice DESDE CUÁNDO: el primer
    commit que versiona el `.SELLO` con este mismo sha256. No prueba ceguera —quien
    escribe el examen puede leer el árbol—, pero sí prueba que el examen no cambió
    después, y permite contar cuántos resúmenes se tocaron desde entonces (R-01).
    """

    commit: str | None
    fecha: str | None
    commits_despues: int | None
    resumenes_cambiados_despues: int | None
    motivo: str


def compromiso_del_sello(raiz_repo: Path, sello: Path, sha256: str, arbol_dir: Path | None = None) -> Compromiso:
    def git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", "-C", str(raiz_repo), *args], capture_output=True, check=False, text=True)

    if not esta_dentro(raiz_repo, sello):
        return Compromiso(None, None, None, None, "el sello no está dentro del repositorio: sin compromiso")
    try:
        relativa = Path(sello).resolve().relative_to(Path(raiz_repo).resolve()).as_posix()
        historial = git("log", "--format=%H %cI", "--reverse", "--", relativa)
    except (FileNotFoundError, ValueError):
        return Compromiso(None, None, None, None, "git no disponible: sin compromiso")
    if historial.returncode != 0:
        return Compromiso(None, None, None, None, "sin historia git: sin compromiso")
    primero: tuple[str, str] | None = None
    for linea in historial.stdout.splitlines():
        commit, _, fecha = linea.partition(" ")
        contenido = git("show", f"{commit}:{relativa}")
        if contenido.returncode != 0:
            continue
        try:
            datos = json.loads(contenido.stdout)
        except ValueError:
            continue
        if isinstance(datos, dict) and datos.get("sha256") == sha256:
            primero = (commit, fecha)
            break
    if primero is None:
        return Compromiso(None, None, None, None, "el sello con este contenido no está commiteado: sin compromiso previo")
    commit, fecha = primero
    despues = git("rev-list", "--count", f"{commit}..HEAD")
    cuantos = int(despues.stdout.strip() or 0) if despues.returncode == 0 else None
    cambiados: int | None = None
    if arbol_dir is not None:
        try:
            rel_arbol = Path(arbol_dir).resolve().relative_to(Path(raiz_repo).resolve()).as_posix()
        except ValueError:
            rel_arbol = None
        if rel_arbol:
            diff = git("diff", "-U0", f"{commit}", "HEAD", "--", rel_arbol)
            if diff.returncode == 0:
                cambiados = sum(1 for l in diff.stdout.splitlines() if l.startswith("+resumen:") or l.startswith("-resumen:")) // 2
    return Compromiso(commit[:12], fecha, cuantos, cambiados,
                      f"sello commiteado en {commit[:12]} ({fecha[:10]}); {cuantos} commit(s) después"
                      + (f"; {cambiados} resumen(es) cambiado(s) desde entonces" if cambiados is not None else ""))


def solape_examen_catalogo(pares: Iterable[tuple[str, str]]) -> float | None:
    """Solape medio (Jaccard) entre cada petición y la línea del nodo que espera.

    Un examen fabricado a partir de las líneas del catálogo —el ataque R-01— comparte
    casi todo su vocabulario con la línea esperada; un encargo escrito por alguien que no
    ha visto el árbol, casi nada. Se publica como señal y, por encima de `SOLAPE_CALCADO`,
    invalida la integridad: no es un examen, es una copia.
    """

    valores: list[float] = []
    for peticion, linea in pares:
        a, b = set(normalizar(peticion)), set(normalizar(linea))
        if not a or not b:
            continue
        valores.append(len(a & b) / len(a | b))
    return round(sum(valores) / len(valores), 3) if valores else None


# Calibrado el 2026-09-03 sobre la galaxia: el holdout v1 (escrito por una persona) da 6 %; un
# examen fabricado con tres palabras distintivas de cada línea, 23 %; con la línea entera, 100 %.
# Es una señal contra la fabricación burda, no una prueba de ceguera: lo dice NUCLEO §11.
SOLAPE_CALCADO = 0.2


def esta_versionado(raiz_repo: Path, ruta: Path) -> bool | None:
    """Indica si Git rastrea la ruta, o si no pudo comprobarse."""
    try:
        resultado = subprocess.run(
            ["git", "-C", str(raiz_repo), "ls-files", "--error-unmatch", "--", str(ruta)],
            capture_output=True, check=False,
        )
    except FileNotFoundError:
        return None
    return True if resultado.returncode == 0 else False if resultado.returncode == 1 else None


@dataclass(frozen=True)
class Cobertura:
    oficios_cubiertos: tuple[str, ...]
    oficios_sin_encargo: tuple[str, ...]
    profundos: int
    total: int


def cobertura(oficios: Iterable[str], esperas: Iterable[str]) -> Cobertura:
    """Resume los oficios y la profundidad cubiertos por los encargos."""
    disponibles = set(oficios)
    rutas = tuple(esperas)
    presentes = {ruta.split("/")[0] for ruta in rutas}
    cubiertos = tuple(sorted(disponibles & presentes))
    sin_encargo = tuple(sorted(disponibles - presentes))
    return Cobertura(cubiertos, sin_encargo, sum(ruta.count("/") >= 2 for ruta in rutas), len(rutas))


def formatear_intervalo(aciertos: int, total: int) -> str:
    """Da al intervalo el formato compacto del informe."""
    inferior, superior = intervalo_wilson(aciertos, total)
    return f"IC95 {round(inferior)}–{round(superior)} %"
