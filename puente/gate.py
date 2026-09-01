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
    return verificar_instantanea(
        con_pruebas=not args.sin_pruebas, silencioso=args.silencioso, raiz=base
    )


if __name__ == "__main__":
    raise SystemExit(main())
