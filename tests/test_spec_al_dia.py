"""La spec dice lo que hay, no lo que había.

`mar/revision` vivió semanas en el árbol sin figurar en `spec/UNIVERSO.md`, que seguía
anunciando cinco mares. Nadie mintió: se añadió el sexto y la tabla se quedó donde
estaba. Es el mismo fallo que COSMOS ya resuelve generando el índice y el inventario —
lo que se escribe a mano se desincroniza— y aquí no se puede generar, porque la columna
«qué impone» la escribe una persona.

Lo que sí se puede es **exigir que coincidan**. Este canario no redacta la tabla: cuenta
las filas y las compara con el disco. Si aparece un mar nuevo, esta prueba se pone roja
hasta que alguien escriba su fila.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _mares_en_disco() -> list[str]:
    return sorted(f.stem.removeprefix("mar-") for f in (RAIZ / "galaxia/agua").glob("mar-*.md"))


def _mares_en_la_spec() -> list[str]:
    texto = (RAIZ / "spec/UNIVERSO.md").read_text(encoding="utf-8")
    tabla = texto[texto.index("| Mar | Qué impone |") :]
    tabla = tabla[: tabla.index("\n\n")]
    return sorted(re.findall(r"^\| `([a-z-]+)` \|", tabla, flags=re.M))


from tests._integrado import solo_en_el_origen

solo_en_el_origen()  # cifras y listas del catálogo del origen, no del motor


class LaSpecCuadraConElArbol(unittest.TestCase):
    def test_los_mares_de_la_spec_son_los_del_disco(self) -> None:
        disco, spec = _mares_en_disco(), _mares_en_la_spec()
        sobran = sorted(set(spec) - set(disco))
        faltan = sorted(set(disco) - set(spec))
        self.assertEqual(
            (faltan, sobran),
            ([], []),
            f"spec/UNIVERSO.md no cuadra con galaxia/agua: faltan {faltan}, sobran {sobran}",
        )

    def test_el_recuento_escrito_en_prosa_es_el_de_la_tabla(self) -> None:
        """La frase «Seis aguas que mojan…» también envejece, y nadie la mira."""

        cardinales = {
            "Tres": 3, "Cuatro": 4, "Cinco": 5, "Seis": 6, "Siete": 7,
            "Ocho": 8, "Nueve": 9, "Diez": 10,
        }
        texto = (RAIZ / "spec/UNIVERSO.md").read_text(encoding="utf-8")
        escrito = re.search(r"^(\w+) aguas que mojan", texto, flags=re.M)
        self.assertIsNotNone(escrito, "desapareció la frase que cuenta los mares")
        self.assertEqual(cardinales[escrito.group(1)], len(_mares_en_la_spec()))


if __name__ == "__main__":
    unittest.main()
