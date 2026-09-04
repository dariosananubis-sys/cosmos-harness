"""¿Vive COSMOS integrado en el arnés de un anfitrión?

Una parte de la suite no prueba el motor: afirma cifras, listas y bloques del catálogo del
ORIGEN (los mares de `galaxia/agua`, las cifras de las specs, el bloque de `PROGRESS.md`, el
presupuesto de 4.000). Cuando COSMOS organiza el arnés de un anfitrión (`[compilacion]
vista = "anfitrion"` en `cosmos.toml`), el árbol es el de ese arnés y esas afirmaciones dejan de
tener sentido; medido el 2026-09-04: 18 rojos en 10 módulos sin un solo defecto del motor. Esos
módulos saltan enteros, con motivo, y siguen corriendo en el origen.
"""

from __future__ import annotations

import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def integrado_en_un_anfitrion() -> bool:
    try:
        from cosmos.modelo import cargar_configuracion

        return cargar_configuracion(RAIZ / "cosmos.toml").vista_compilacion == "anfitrion"
    except Exception:  # noqa: BLE001 - sin configuración legible, se asume el origen
        return False


def solo_en_el_origen() -> None:
    """Llamar en la cabecera del módulo: salta el módulo entero fuera del origen."""

    if integrado_en_un_anfitrion():
        raise unittest.SkipTest("COSMOS vive integrado en el arnés de un anfitrión: este módulo afirma cifras y listas del catálogo del origen")
