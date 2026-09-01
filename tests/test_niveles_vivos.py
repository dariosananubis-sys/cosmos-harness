"""Un nivel de la taxonomía existe cuando alguien lo usa, y eso se cuenta, no se recuerda.

Nace del hallazgo H20, que midió `cosmos estado` sobre la galaxia y concluyó que
ocho de dieciséis niveles no tenían «un solo nodo vivo». Seis de esos ocho sí lo
tenían: estaban en `ejemplo/`, que es un árbol completo y validado en cada push.
El inventario no mentía —carga la raíz que le pasan— pero **no podía distinguir un
nivel muerto de uno que este árbol no necesita**, y de esa confusión salió la idea
de retirar media taxonomía.

Aquí se cuenta sobre TODOS los árboles del repositorio a la vez. Si un nivel se
queda sin un solo nodo en todos ellos, es que la spec lo define y nadie lo
ejercita: o se usa, o se retira (`spec/TAXONOMIA.md`). Y esto es un test y no un
párrafo pidiendo disciplina, porque una regla que hay que recordar ya está mal
puesta (`GOAL.md` §2).
"""

from __future__ import annotations

import unittest
from collections import Counter
from pathlib import Path

from cosmos.modelo import NIVELES_VALIDOS, Arbol, cargar_arbol, cargar_configuracion


REPO = Path(__file__).resolve().parent.parent
CONFIGURACIONES = ("cosmos.toml", "ejemplo.toml")


def arboles_del_repositorio() -> list[Arbol]:
    """Cada árbol declarado por una configuración del repositorio, con su registro."""

    arboles = []
    for nombre in CONFIGURACIONES:
        config = cargar_configuracion(REPO / nombre)
        arboles.append(
            cargar_arbol(
                config.arbol,
                excluir=config.indice,
                excluir_directorios=(config.destino_compilacion,),
                tambien=(config.registro,) if config.registro else (),
            )
        )
    return arboles


def censo(arboles: list[Arbol]) -> Counter[str]:
    cuenta: Counter[str] = Counter()
    for arbol in arboles:
        cuenta.update(nodo.cosmos for nodo in arbol.nodos)
    return cuenta


def niveles_muertos(arboles: list[Arbol], niveles: frozenset[str] = NIVELES_VALIDOS) -> list[str]:
    vivos = censo(arboles)
    return sorted(nivel for nivel in niveles if not vivos.get(nivel))


class PruebasNivelesVivos(unittest.TestCase):
    def setUp(self) -> None:
        self.arboles = arboles_del_repositorio()

    def test_todo_nivel_de_la_taxonomia_tiene_al_menos_un_nodo(self) -> None:
        muertos = niveles_muertos(self.arboles)
        self.assertEqual(
            [],
            muertos,
            "niveles definidos por la spec y sin un solo nodo en ningún árbol: "
            f"{', '.join(muertos)}. O se usan con un nodo real, o se retiran de "
            "NIVELES_SOLIDOS/NIVELES_AGUA y de las specs (spec/TAXONOMIA.md).",
        )

    def test_el_censo_cubre_los_dos_arboles_y_el_registro(self) -> None:
        """El canario solo vale si de verdad mira más de un árbol.

        `planeta`, `provincia`, `luna` y `lago` viven únicamente en `ejemplo/`, y
        parte de la `lluvia` vive en `registro/`, que no cuelga de ninguna galaxia.
        Si alguna de esas dos fuentes dejara de cargarse, el test de arriba seguiría
        pasando por casualidad o fallaría sin decir por qué.
        """

        solo_ejemplo = niveles_muertos(self.arboles[:1])
        self.assertIn("luna", solo_ejemplo)
        self.assertIn("provincia", solo_ejemplo)
        cuenta = censo(self.arboles)
        self.assertGreaterEqual(cuenta["lluvia"], 2, "el registro no se está cargando")

    def test_meta_el_canario_se_pone_rojo_cuando_un_nivel_pierde_su_ultimo_nodo(self) -> None:
        """Un verde que nunca ha dado rojo no se distingue de uno roto (`GOAL.md` §7).

        Se le quita al censo el único nivel que solo sostiene un nodo del ejemplo y
        se exige que el canario lo nombre.
        """

        for nivel in ("luna", "lago", "rio", "lluvia"):
            with self.subTest(nivel=nivel):
                mermados = [
                    Arbol(raiz=arbol.raiz, nodos=[n for n in arbol.nodos if n.cosmos != nivel])
                    for arbol in self.arboles
                ]
                self.assertIn(nivel, niveles_muertos(mermados))


if __name__ == "__main__":
    unittest.main()
