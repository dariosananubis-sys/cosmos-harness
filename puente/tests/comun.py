"""Un árbol mínimo y un repo Git de destino, para no depender de la galaxia real."""

from __future__ import annotations

import subprocess
from pathlib import Path

from cosmos.modelo import Arbol, Configuracion, cargar_arbol

GALAXIA = """---
cosmos: galaxia
nombre: prueba
resumen: Galaxia de prueba del puente.
---

Cuerpo de la galaxia.
"""

SISTEMA = """---
cosmos: sistema-solar
nombre: web
padre: ""
resumen: Un sitio que carga y no se cae.
---

Cuerpo del sistema.
"""

OCEANO = """---
cosmos: oceano
nombre: verificar
moja: ["**"]
resumen: Nada se declara hecho sin haberlo visto funcionar.
---

Dos capas: la máquina y los ojos.
"""

PUEBLO = """---
cosmos: pueblo
nombre: {nombre}
padre: web
resumen: Pueblo de prueba {nombre}.
---

Cuerpo del pueblo {nombre}.
"""


def arbol_minimo(base: Path, pueblos: tuple[str, ...] = ("medir-anchos",)) -> Arbol:
    (base / "galaxia.md").write_text(GALAXIA, encoding="utf-8")
    (base / "web.md").write_text(SISTEMA, encoding="utf-8")
    (base / "oceano-verificar.md").write_text(OCEANO, encoding="utf-8")
    for nombre in pueblos:
        directorio = base / "pueblos" / nombre
        directorio.mkdir(parents=True, exist_ok=True)
        (directorio / "SKILL.md").write_text(PUEBLO.format(nombre=nombre), encoding="utf-8")
        (directorio / "referencia.md").write_text(f"Casa de {nombre}.\n", encoding="utf-8")
    return cargar_arbol(base)


def configuracion(base: Path, entrada: int = 4000) -> Configuracion:
    return Configuracion(entrada=entrada, arbol=base, indice=base / "COSMOS.md", ruta=base / "cosmos.toml")


def repo_git(destino: Path) -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "--quiet"], cwd=destino, check=True)
    subprocess.run(["git", "config", "user.email", "puente@example.invalid"], cwd=destino, check=True)
    subprocess.run(["git", "config", "user.name", "puente"], cwd=destino, check=True)
    return destino.resolve()


CONTRATO = """version = 1
nombre = "planeta-de-prueba"
tipo = "generico"
repositorio = "."
nichos = ["web"]

[contexto]
objetivo = "Comprobar la proyeccion"
fuentes_autorizadas = []

[limites]
rutas_escritura = ["src"]
produccion = false
acciones_externas = false

[verificacion]
comandos = ["python3 -m unittest"]
visual = false
"""
