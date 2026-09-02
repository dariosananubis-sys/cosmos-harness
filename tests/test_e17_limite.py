"""La tabla de E17 en la spec la escribe el código, no la memoria de nadie.

`spec/GUARDARRAILES.md` publica cinco cifras de similitud para justificar qué caza E17
y qué no. Antes de esta prueba, dos de ellas eran erróneas y el «mecanismo» descrito
—n-gramas de cuatro palabras— no era el implementado: E17 compara **conjuntos de
palabras con contenido, frase contra frase**. La motivación citaba además, como ejemplo
a cazar, justo el caso que la invariante deja pasar.

Un límite declarado se puede tener en cuenta; uno declarado con el número equivocado es
peor que ninguno, porque invita a confiar. Esta prueba fija las dos cosas: que las
cifras publicadas salen de la función, y que el límite es exactamente donde se dice.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from cosmos.modelo import Nodo
from cosmos.validar import solape_de_afirmaciones

RAIZ = Path(__file__).resolve().parent.parent
UMBRAL = 0.25


def _nodo(texto: str) -> Nodo:
    return Nodo(
        ruta=Path("x.md"),
        ruta_relativa="x.md",
        datos={"cosmos": "pueblo", "nombre": "x", "resumen": "r"},
        lineas=3,
        contenido="---\ncosmos: pueblo\nnombre: x\nresumen: r\n---\n\n" + texto + "\n",
    )


def _similitud(a: str, b: str) -> float:
    return solape_de_afirmaciones(_nodo(a), _nodo(b))[0]


CAZADOS = [
    (
        "copia literal",
        "No se toca produccion sin escribir antes como deshacer el cambio.",
        "No se toca produccion sin escribir antes como deshacer el cambio.",
    ),
    (
        "reedicion con sinonimos y otro orden",
        "Los secretos nunca se copian en claro dentro del repositorio por seguridad.",
        "Por seguridad, los secretos jamas se copian dentro del repositorio en claro.",
    ),
]

NO_CAZADOS = [
    (
        "vocabulario distinto: rollback",
        "Antes de tocar produccion se deja escrito el camino de vuelta.",
        "No se modifica un entorno vivo sin haber redactado antes como deshacerlo.",
    ),
    (
        "vocabulario distinto: secretos",
        "Los secretos jamas se escriben en claro dentro del repositorio.",
        "Las credenciales nunca van sin cifrar en el codigo versionado.",
    ),
]


class E17CazaLaReedicion(unittest.TestCase):
    def test_los_pares_reeditados_superan_el_umbral(self) -> None:
        for nombre, a, b in CAZADOS:
            with self.subTest(nombre):
                self.assertGreater(_similitud(a, b), UMBRAL)

    def test_el_orden_de_las_palabras_no_la_despista(self) -> None:
        """Reordenar es la forma más barata de esquivar un detector literal."""

        recta = "El despliegue se detiene cuando la comprobacion de integridad falla."
        vuelta = "Cuando falla la comprobacion de integridad, el despliegue se detiene."
        self.assertEqual(_similitud(recta, vuelta), 1.0)


class E17NoCazaLaReformulacion(unittest.TestCase):
    """El límite, medido. Si algún día lo cazara, esta prueba avisa para subir la spec."""

    def test_sin_palabras_en_comun_la_similitud_es_cero_exacto(self) -> None:
        for nombre, a, b in NO_CAZADOS:
            with self.subTest(nombre):
                self.assertEqual(_similitud(a, b), 0.0)

    def test_una_frase_corta_no_cuenta_como_afirmacion(self) -> None:
        self.assertEqual(_similitud("No se toca.", "No se toca."), 0.0)


class LaSpecPublicaLasCifrasDelCodigo(unittest.TestCase):
    def test_la_tabla_de_la_spec_sale_de_la_funcion(self) -> None:
        texto = (RAIZ / "spec/GUARDARRAILES.md").read_text(encoding="utf-8")
        publicadas = re.findall(r"^\| ([01],\d{3}) \| \*{0,2}(salta|pasa)\*{0,2} \|", texto, flags=re.M)
        self.assertTrue(publicadas, "desapareció la tabla de similitudes de E17")

        medidas = [(f"{_similitud(a, b):.3f}".replace(".", ","), "salta") for _, a, b in CAZADOS]
        medidas += [(f"{_similitud(a, b):.3f}".replace(".", ","), "pasa") for _, a, b in NO_CAZADOS]
        self.assertEqual(publicadas, medidas)


if __name__ == "__main__":
    unittest.main()
