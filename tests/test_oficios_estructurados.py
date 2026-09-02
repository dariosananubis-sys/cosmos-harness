"""Un oficio no es una lista de herramientas: es un mapa por el que se baja.

Lo señaló Darío mirando `trading`, cuyo resumen decía *«Bots que operan solos»* — un
oficio entero reducido a una de sus ramas, con sus siete países colgando en plano. Al
medirlo salió que era sistémico: **14 de los 21 oficios estaban planos** y ocho de ellos
tenían TODAS sus herramientas colgando directamente del oficio, sin un solo nivel
intermedio. Solo `ciberseguridad` y `rendimiento` tenían estructura.

Eso rompe la promesa del árbol por los dos lados. Quien busca no ve por dónde bajar —
veinte nombres al mismo nivel no son un mapa—, y el catálogo del nicho activo se paga
entero sin que ninguna línea agrupe nada.

Este canario fija las dos mitades: que ningún oficio vuelva a quedar en plano, y que la
estructura que se añada **agrupe de verdad** — un nivel con un solo hijo no organiza
nada, solo cobra su resumen (`spec/TAXONOMIA.md`, antipatrones).
"""

from __future__ import annotations

import unittest
from collections import defaultdict
from pathlib import Path

from cosmos.modelo import cargar_arbol

RAIZ = Path(__file__).resolve().parent.parent
ARBOL = cargar_arbol(RAIZ / "galaxia")

# Un puñado de herramientas colgando del oficio es sano: son las que no agrupan con nada
# todavía. Lo que no puede volver a pasar es un oficio ENTERO en plano.
SUELTOS_TOLERADOS = 2


def _hijos() -> dict[str, list]:
    hijos = defaultdict(list)
    for nodo in ARBOL.nodos:
        padre = nodo.datos.get("padre")
        if isinstance(padre, str) and padre:
            hijos[padre].append(nodo)
    return hijos


class NingunOficioEnPlano(unittest.TestCase):
    def test_las_herramientas_cuelgan_de_un_nivel_que_agrupa(self) -> None:
        hijos = _hijos()
        planos = {}
        for oficio in (n for n in ARBOL.nodos if n.cosmos == "sistema-solar"):
            sueltos = [h.nombre for h in hijos.get(oficio.nombre, []) if h.cosmos == "pueblo"]
            if len(sueltos) > SUELTOS_TOLERADOS:
                planos[oficio.nombre] = sueltos
        self.assertEqual(
            planos, {},
            "oficios en plano: sus herramientas cuelgan del oficio sin nivel que las agrupe",
        )

    def test_todo_oficio_tiene_por_donde_bajar(self) -> None:
        """Un oficio sin ningún hijo intermedio es una lista, no un mapa."""

        hijos = _hijos()
        sin_mapa = [
            o.nombre
            for o in ARBOL.nodos
            if o.cosmos == "sistema-solar"
            and not any(h.cosmos in {"continente", "pais"} for h in hijos.get(o.nombre, []))
        ]
        self.assertEqual(sin_mapa, [], "oficios sin un solo nivel intermedio")


class LoQueAgrupaTieneQueAgrupar(unittest.TestCase):
    def test_ningun_nivel_intermedio_con_un_solo_hijo(self) -> None:
        """El antipatrón contrario: llenar de niveles que no organizan nada."""

        hijos = _hijos()
        relleno = {
            n.referencia: [h.nombre for h in hijos.get(n.referencia, [])]
            for n in ARBOL.nodos
            if n.cosmos in {"continente", "pais", "provincia"}
            and len(hijos.get(n.referencia, [])) == 1
        }
        self.assertEqual(relleno, {}, "niveles que no agrupan: un solo hijo, y su resumen se paga")


# NO hay canario para «el resumen reduce el oficio a una de sus ramas», que es el defecto
# original de `trading`. Se intentó por léxico —la primera palabra no puede ser el nombre
# de una rama— y se midió antes de dejarlo: marcaba en rojo a `audiovisual` («Video, audio
# y voz…»), `blockchain` y `ciberseguridad`, que no reducen nada, **enumeran** sus ramas.
# Y no cazaba el caso real: «Bots que operan solos: exchanges, ejecucion, backtest y
# riesgo» menciona dos de las cuatro ramas de trading, así que cualquier umbral por
# recuento lo dejaba pasar.
#
# Distinguir «enumera sus partes» de «llama al todo por una parte» es semántica, y la
# semántica necesita un modelo (`GOAL.md` §5). Se declara el límite en vez de publicar un
# canario que miente: esto lo sigue cazando una persona leyendo, como pasó aquí.


if __name__ == "__main__":
    unittest.main()
