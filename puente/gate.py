#!/usr/bin/env python3
"""Gate local: verifica la instantánea del índice, nunca el árbol de trabajo."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Git exporta su estado al proceso hijo por entorno. Si no se limpia, el hook
# contamina cualquier repositorio que se cree dentro de la instantánea.
ENTORNO_GIT_LOCAL = (
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_CONFIG",
    "GIT_CONFIG_COUNT",
    "GIT_CONFIG_PARAMETERS",
    "GIT_DIR",
    "GIT_GRAFT_FILE",
    "GIT_IMPLICIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_INTERNAL_SUPER_PREFIX",
    "GIT_NO_REPLACE_OBJECTS",
    "GIT_OBJECT_DIRECTORY",
    "GIT_PREFIX",
    "GIT_REPLACE_REF_BASE",
    "GIT_SHALLOW_FILE",
    "GIT_WORK_TREE",
)
VARIABLES_COSMOS = ("COSMOS_NICHOS", "COSMOS_CONFIG")


def raiz_repositorio(inicio: str | Path | None = None) -> Path:
    """El repositorio que se verifica es donde se está, no donde vive este fichero.

    Anclarlo en `__file__` hacía que COSMOS instalado sobre otro proyecto —vía
    PYTHONPATH, que es como lo engancha `cosmos enganchar`— verificase su propio
    árbol y dejase pasar el ajeno. Un gate que mira al repositorio equivocado
    tranquiliza sin comprobar nada.
    """

    base = Path(inicio) if inicio is not None else Path.cwd()
    resultado = subprocess.run(
        ["git", "-C", str(base), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado.returncode or not resultado.stdout.strip():
        return base
    return Path(resultado.stdout.strip()).resolve()


def _entorno_limpio(*, conservar_indice: bool) -> dict[str, str]:
    entorno = os.environ.copy()
    indice = entorno.get("GIT_INDEX_FILE") if conservar_indice else None
    for variable in tuple(entorno):
        if variable.startswith("GIT_"):
            entorno.pop(variable, None)
    if indice is not None:
        entorno["GIT_INDEX_FILE"] = indice
    for variable in VARIABLES_COSMOS:
        entorno.pop(variable, None)
    entorno["PYTHONDONTWRITEBYTECODE"] = "1"
    return entorno


def entorno_de_origen() -> dict[str, str]:
    """Aísla Git conservando solo el índice efectivo que disparó el hook."""

    return _entorno_limpio(conservar_indice=True)


def entorno_aislado() -> dict[str, str]:
    """Evita que el Git del hook contamine el repositorio de la instantánea."""

    return _entorno_limpio(conservar_indice=False)


SUITES = ("tests", "puente/tests")

# --- Canario de vaciado de resumen (P01) ------------------------------------
#
# «La manera más barata de pasar el presupuesto es escribir resúmenes peores»
# (cosmos/acertar.py). La auditoría B-01 lo llevó al extremo: reescribir veinte
# resúmenes con las palabras del examen dejó `validar` verde, `medir` 204 tokens más
# barato y la contra-métrica en 100 %, con el árbol estrictamente peor. Ninguna
# invariante mira la DIFERENCIA entre dos versiones del árbol; esto sí. Un resumen
# que mejora casi nunca se vacía: si pierde más del umbral de sus términos distintos
# respecto a HEAD, el commit se para y pide revisión humana. La válvula es `cosmos
# saltar P01 --motivo "..." --caduca 1d`, como en cualquier otro guardarraíl.
UMBRAL_VACIADO = 0.4
CODIGO_VACIADO = "P01"


def _resumen_de(texto: str) -> str | None:
    if not texto.startswith("---"):
        return None
    cabecera = texto.split("\n---", 1)[0]
    for linea in cabecera.splitlines()[1:]:
        if linea.startswith("resumen:"):
            return linea[len("resumen:"):].strip().strip("\"'")
    return None


def _git(base: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=base, env=entorno_de_origen(),
                          capture_output=True, check=False).stdout


def resumenes_vaciados(base: Path, umbral: float = UMBRAL_VACIADO) -> list[str]:
    """Nodos cuyo `resumen` pierde más de `umbral` de sus términos distintos entre HEAD y el índice."""

    from puente.lluvia import normalizar

    cambiados = _git(base, "diff", "--cached", "--name-only", "--diff-filter=M", "-z", "--", "*.md")
    hallazgos: list[str] = []
    for ruta in filter(None, cambiados.decode("utf-8", "replace").split("\0")):
        antes = _resumen_de(_git(base, "show", f"HEAD:{ruta}").decode("utf-8", "replace"))
        despues = _resumen_de(_git(base, "show", f":{ruta}").decode("utf-8", "replace"))
        if not antes or despues is None:
            continue
        terminos_antes = set(normalizar(antes))
        perdidos = terminos_antes - set(normalizar(despues))
        if terminos_antes and len(perdidos) / len(terminos_antes) > umbral:
            hallazgos.append(
                f"{ruta}: el resumen pierde {len(perdidos)} de {len(terminos_antes)} términos "
                f"distintos ({len(perdidos) / len(terminos_antes):.0%})"
            )
    return hallazgos


def _terminos_del_examen(holdout: Path) -> dict[str, set[str]]:
    """Términos de cada petición del holdout, por nodo esperado (y sus ancestros).

    El ataque B-01 en su dirección de AÑADIR (revisión R-14): meter las palabras del
    examen en el resumen del nodo que espera sube la validación sin vaciar nada, y P01
    solo miraba pérdidas. Si el holdout está en esta máquina —y lo está en la del que
    ajusta— se lee aquí para vigilar la ganancia. En CI no está y esta guarda no ve
    nada: se dice en vez de fingir.
    """

    import json

    from puente.lluvia import normalizar

    try:
        datos = json.loads(holdout.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    por_nodo: dict[str, set[str]] = {}
    for dato in datos if isinstance(datos, list) else []:
        if not isinstance(dato, dict) or not isinstance(dato.get("peticion"), str):
            continue
        terminos = set(normalizar(dato["peticion"]))
        espera = str(dato.get("espera", ""))
        partes = espera.split("/")
        for i in range(1, len(partes) + 1):
            por_nodo.setdefault("/".join(partes[:i]), set()).update(terminos)
    return por_nodo


def _ruta_cosmos_de(texto: str) -> str | None:
    if not texto.startswith("---"):
        return None
    cabecera = texto.split("\n---", 1)[0]
    nombre = padre = None
    for linea in cabecera.splitlines()[1:]:
        if linea.startswith("nombre:"):
            nombre = linea[len("nombre:"):].strip().strip("\"'")
        elif linea.startswith("padre:"):
            padre = linea[len("padre:"):].strip().strip("\"'")
    if nombre is None:
        return None
    return f"{padre}/{nombre}" if padre else nombre


def resumenes_calcados(base: Path, holdout: Path | None = None) -> list[str]:
    """Resúmenes modificados que GANAN términos de las peticiones del examen que los espera."""

    from cosmos.holdout import ruta_por_defecto
    from puente.lluvia import normalizar

    examen = _terminos_del_examen(holdout or ruta_por_defecto())
    if not examen:
        return []
    cambiados = _git(base, "diff", "--cached", "--name-only", "--diff-filter=M", "-z", "--", "*.md")
    hallazgos: list[str] = []
    for ruta in filter(None, cambiados.decode("utf-8", "replace").split("\0")):
        despues_texto = _git(base, "show", f":{ruta}").decode("utf-8", "replace")
        antes = _resumen_de(_git(base, "show", f"HEAD:{ruta}").decode("utf-8", "replace"))
        despues = _resumen_de(despues_texto)
        nodo = _ruta_cosmos_de(despues_texto)
        if antes is None or despues is None or nodo is None or nodo not in examen:
            continue
        ganados = set(normalizar(despues)) - set(normalizar(antes))
        del_examen = sorted(ganados & examen[nodo])
        if del_examen:
            hallazgos.append(f"{ruta}: el resumen de {nodo} gana términos del examen que lo espera: {', '.join(del_examen)}")
    return hallazgos


def pueblos_retirados(base: Path) -> list[str]:
    """Pueblos que el índice borra respecto a HEAD (baja neta del catálogo).

    Revisión R-02: borrar 40 herramientas subía la contra-métrica (30 → 55 %) y ensanchaba el
    presupuesto (91 → 167 tokens) con `validar` en verde. GOAL §2: lo que falta también es
    un fallo. Toda baja de pueblo pasa por la válvula `cosmos saltar P02`, como E16.
    """

    borrados = _git(base, "diff", "--cached", "--name-only", "--diff-filter=D", "-z", "--", "*.md")
    retirados: list[str] = []
    for ruta in filter(None, borrados.decode("utf-8", "replace").split("\0")):
        antes = _git(base, "show", f"HEAD:{ruta}").decode("utf-8", "replace")
        if antes.startswith("---") and "\ncosmos: pueblo" in antes.split("\n---", 1)[0]:
            retirados.append(ruta)
    return retirados


CODIGO_BAJA = "P02"


def comprobar_bajas(base: Path) -> int:
    """Rojo si se retira algún pueblo y la válvula P02 no está abierta."""

    from cosmos.guardarrailes import estado_saltos, ruta_saltos

    retirados = pueblos_retirados(base)
    if not retirados:
        return 0
    activos, _ = estado_saltos(ruta_saltos(base))
    if any(salto.codigo == CODIGO_BAJA for salto in activos):
        sys.stderr.write(f"COSMOS  gate  {CODIGO_BAJA} saltado: {len(retirados)} pueblo(s) retirado(s) pasan con la válvula abierta\n")
        return 0
    sys.stderr.write(
        "\nCOSMOS  gate  rojo — commit bloqueado: se retiran pueblos.\n"
        + "".join(f"  {ruta}\n" for ruta in retirados)
        + "Lo que falta también es un fallo (GOAL §2): retirar herramientas sube la contra-métrica y\n"
        "ensancha el presupuesto sin mejorar nada (R-02). Si la retirada es a propósito:\n"
        f"  cosmos saltar {CODIGO_BAJA} --motivo \"...\" --caduca 7d\n"
    )
    return 1


def comprobar_vaciado(base: Path) -> int:
    """Rojo si algún resumen se vacía y la válvula P01 no está abierta."""

    from cosmos.guardarrailes import estado_saltos, ruta_saltos

    hallazgos = resumenes_vaciados(base) + resumenes_calcados(base)
    if not hallazgos:
        return 0
    activos, _ = estado_saltos(ruta_saltos(base))
    if any(salto.codigo == CODIGO_VACIADO for salto in activos):
        sys.stderr.write(f"COSMOS  gate  {CODIGO_VACIADO} saltado: {len(hallazgos)} resumen(es) sospechoso(s) pasan con la válvula abierta\n")
        return 0
    sys.stderr.write(
        "\nCOSMOS  gate  rojo — commit bloqueado: resúmenes que se vacían o que copian el examen.\n"
        + "".join(f"  {hallazgo}\n" for hallazgo in hallazgos)
        + "Un resumen que pierde más del 40 % de sus términos casi nunca mejora: es la palanca\n"
        "más barata para abaratar el presupuesto o inflar la contra-métrica (B-01). Si es a\n"
        f"propósito: cosmos saltar {CODIGO_VACIADO} --motivo \"...\" --caduca 1d\n"
    )
    return 1


def _ordenes(con_pruebas: bool, base: Path | None = None) -> list[list[str]]:
    ordenes = [
        # El escaneo se repite dentro: fuera mira el índice real, aquí los bytes
        # exactos que se van a commitear, ya materializados.
        [sys.executable, "-m", "puente.secretos", "--todo"],
        # 'arrancar' y no 'validar': la vista plana es un artefacto generado que no
        # se versiona, así que la instantánea del índice la tiene ausente igual que
        # un clon recién bajado. Verificar aquí es verificar que ese clon arranca.
        [sys.executable, "-m", "cosmos", "arrancar"],
    ]
    if con_pruebas:
        for suite in SUITES:
            if base is None or (base / suite).is_dir():
                ordenes.append([sys.executable, "-m", "unittest", "discover", "-s", suite, "-t", "."])
    return ordenes


def verificar_instantanea(
    *, con_pruebas: bool = True, silencioso: bool = False, raiz: Path | None = None
) -> int:
    """Exporta el índice a un temporal y verifica ahí, no sobre lo que hay en disco."""

    base = raiz or raiz_repositorio()
    with tempfile.TemporaryDirectory(prefix="cosmos-gate-") as directorio:
        instantanea = Path(directorio).resolve() / "repo"
        instantanea.mkdir()
        exportacion = subprocess.run(
            ["git", "checkout-index", "--all", f"--prefix={instantanea}{os.sep}"],
            cwd=base,
            env=entorno_de_origen(),
            capture_output=True,
            check=False,
        )
        if exportacion.returncode:
            print("ERROR: no se pudo exportar el índice Git", file=sys.stderr)
            return 1

        entorno = entorno_aislado()
        for preparacion in (["git", "init", "--quiet"], ["git", "add", "--force", "--all"]):
            if subprocess.run(
                preparacion,
                cwd=instantanea,
                env=entorno,
                capture_output=silencioso,
                check=False,
            ).returncode:
                print("ERROR: no se pudo preparar la instantánea del índice", file=sys.stderr)
                return 1

        # La válvula de escape vive fuera del control de versiones, así que hay
        # que traerla a mano: sin esto un salto legítimo no llegaría al hook.
        saltos = base / ".cosmos" / "saltos.log"
        if saltos.is_file():
            destino_saltos = instantanea / ".cosmos"
            destino_saltos.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(saltos, destino_saltos / "saltos.log")

        for orden in _ordenes(con_pruebas, instantanea):
            resultado = subprocess.run(
                orden, cwd=instantanea, env=entorno, capture_output=silencioso, check=False
            )
            if resultado.returncode:
                # Un gate que bloquea sin decir por qué se desinstala el mismo día.
                # En modo silencioso la salida se guarda, no se tira: al fallar se
                # publica entera, con el comando exacto para reproducirlo.
                if silencioso:
                    for flujo in (resultado.stdout, resultado.stderr):
                        if flujo:
                            sys.stderr.write(flujo.decode("utf-8", "replace"))
                sys.stderr.write(
                    "\nCOSMOS  gate  rojo — commit bloqueado.\n"
                    f"Falló: {' '.join(orden)}\n"
                    "Repítelo a mano para ver el detalle, o usa la válvula acotada:\n"
                    "  cosmos saltar <codigo> --motivo \"...\" --caduca 7d\n"
                )
                return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sin-pruebas", action="store_true", help="omite las suites de tests")
    parser.add_argument("--silencioso", action="store_true")
    args = parser.parse_args(argv)
    base = raiz_repositorio()
    previo = subprocess.run(
        [sys.executable, "-m", "puente.secretos", "--indice"],
        cwd=base,
        env=entorno_de_origen(),
        check=False,
    )
    if previo.returncode:
        return 1
    if comprobar_vaciado(base):
        return 1
    if comprobar_bajas(base):
        return 1
    return verificar_instantanea(
        con_pruebas=not args.sin_pruebas, silencioso=args.silencioso, raiz=base
    )


if __name__ == "__main__":
    raise SystemExit(main())
