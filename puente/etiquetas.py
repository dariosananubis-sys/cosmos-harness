#!/usr/bin/env python3
"""Etiquetas opacas: un diagnóstico nombra una ruta sin filtrar la ruta."""

from __future__ import annotations

import hashlib
import os
import re
from os import PathLike

PREFIJO = "ruta#"
LONGITUD = 12
INTENTOS = 8
_TRAMO = re.compile(r"[0-9a-z]{3,}")


def _tramos(crudo: bytes) -> frozenset[str]:
    """Los tramos alfanuméricos de la ruta que la etiqueta no puede contener."""

    texto = crudo.decode("utf-8", errors="replace").lower()
    return frozenset(coincidencia.group(0) for coincidencia in _TRAMO.finditer(texto))


def etiqueta_de_ruta(ruta: str | bytes | PathLike[str] | PathLike[bytes]) -> str:
    """Identificador estable y opaco de una ruta, sin ningún tramo suyo dentro.

    El resumen es hexadecimal, así que por azar puede contener un tramo de la ruta
    original ('cafe', 'dead', 'ab1'...). Eso rompería la única razón de ser de esta
    función, así que se comprueba y se vuelve a resumir hasta que no ocurra. Si ni
    así (ruta patológica, imposible en la práctica), se emite en pares separados:
    esa forma no tiene ninguna secuencia alfanumérica de tres caracteres.
    """

    crudo = ruta if isinstance(ruta, bytes) else os.fsencode(ruta)
    prohibidos = _tramos(crudo)
    for intento in range(INTENTOS):
        resumen = hashlib.sha256(crudo + b"\0" * intento).hexdigest()[:LONGITUD]
        if not any(tramo in resumen for tramo in prohibidos):
            return f"{PREFIJO}{resumen}"
    resumen = hashlib.sha256(crudo).hexdigest()[:LONGITUD]
    return PREFIJO + "-".join(resumen[indice : indice + 2] for indice in range(0, LONGITUD, 2))
