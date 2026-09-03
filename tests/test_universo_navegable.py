"""El mapa de oficios se puede navegar, y sus decisiones no se deshacen en silencio.

Tres canarios de la revisión C01/C03 (2026-09-02), con la decisión delegada por Darío:

1. **El cardinal del título de UNIVERSO es el del disco.** «21 oficios» se escribió a mano
   y nada lo vigilaba — el mismo defecto que ya mordió con los mares, los nodos y los
   pares co-cargables. Ahora, añadir o quitar un sistema sin tocar la spec se pone rojo.
2. **Ningún oficio queda sin que nadie lo cite, salvo los declarados terminales.** El grafo
   `usa:` era una estrella: 7 oficios a los que ningún vecino mandaba. Se añadieron las
   aristas que son verdad sobre cómo se cruza el trabajo real (cada una con su historia en
   el parte `taxonomia-c01-c03`), y quedó UNO deliberado: `juegos` es nicho destino — se
   llega a él por el encargo, no desde otro oficio. Si un sistema nuevo aparece sin que
   nadie lo cite, esto exige o una arista verdadera o declararlo aquí como terminal.
3. **La partición de `rendimiento` no se refunde.** «Que vaya rápido» y «entrar en código
   ajeno y dejarlo mejor» son dos contratos con herramientas disjuntas (medido: 8 y 10,
   cero solapamiento). Volver a fundirlos —o mover sus pueblos de vuelta— es deshacer una
   decisión de diseño registrada, y tiene que doler en rojo, no pasar en un commit.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from cosmos.modelo import cargar_arbol

RAIZ = Path(__file__).resolve().parent.parent
ARBOL = cargar_arbol(RAIZ / "galaxia")

# Oficios a los que se llega por el encargo, nunca enviados desde otro oficio.
# Añadir aquí un nombre exige la justificación en el parte correspondiente.
TERMINALES = {"juegos"}


def _sistemas() -> dict[str, object]:
    return {n.nombre: n for n in ARBOL.nodos if n.cosmos == "sistema-solar"}


class ElCardinalDelTituloEsElDelDisco(unittest.TestCase):
    def test_universo_anuncia_los_oficios_que_hay(self) -> None:
        texto = (RAIZ / "spec/UNIVERSO.md").read_text(encoding="utf-8")
        titulo = re.search(r"^# El universo — (\d+) oficios", texto)
        self.assertIsNotNone(titulo, "desapareció el título con el cardinal; actualiza este canario")
        self.assertEqual(int(titulo.group(1)), len(_sistemas()),
                         "el título de UNIVERSO anuncia un número de oficios que el disco no tiene")

    def test_la_tabla_tiene_una_fila_por_oficio(self) -> None:
        texto = (RAIZ / "spec/UNIVERSO.md").read_text(encoding="utf-8")
        tabla = texto[texto.index("## Los ") :]
        tabla = tabla[: tabla.index("### ")]
        filas = set(re.findall(r"^\| \d+ \| `([a-z-]+)` \|", tabla, flags=re.M))
        en_disco = set(_sistemas())
        self.assertEqual(
            (sorted(en_disco - filas), sorted(filas - en_disco)), ([], []),
            "la tabla de UNIVERSO no cuadra con galaxia/sistemas",
        )


class ElGrafoUsaLlegaATodosSalvoLosTerminales(unittest.TestCase):
    def test_ningun_oficio_sin_citar_salvo_los_declarados(self) -> None:
        sistemas = _sistemas()
        entrada = {nombre: 0 for nombre in sistemas}
        for nodo in sistemas.values():
            for destino in nodo.datos.get("usa") or []:
                if destino in entrada:
                    entrada[destino] += 1
        huerfanos = {nombre for nombre, veces in entrada.items() if veces == 0}
        self.assertEqual(
            huerfanos, TERMINALES,
            "un oficio se quedó sin que nadie lo cite (o un terminal declarado ya no lo es): "
            "o existe una arista verdadera hacia él, o se declara terminal con su porqué",
        )


class LaParticionDeRendimientoNoSeRefunde(unittest.TestCase):
    def test_los_dos_oficios_existen_y_cada_mitad_esta_en_el_suyo(self) -> None:
        sistemas = _sistemas()
        self.assertIn("rendimiento", sistemas)
        self.assertIn("refactorizacion", sistemas)
        rutas = {n.nombre: n.ruta_cosmos for n in ARBOL.nodos if n.cosmos == "pueblo"}
        # Un representante medido de cada mitad; si alguien los recuelga, esto canta.
        self.assertTrue(rutas["py-spy"].startswith("rendimiento/"),
                        "el perfilado salió de rendimiento")
        self.assertTrue(rutas["mutmut"].startswith("refactorizacion/"),
                        "la calidad de código volvió a rendimiento: la partición se deshizo")

    def test_los_vecinos_se_citan_mutuamente(self) -> None:
        """La pareja medir↔arreglar es recíproca a propósito: el uno limita al otro."""

        sistemas = _sistemas()
        self.assertIn("refactorizacion", sistemas["rendimiento"].datos.get("usa") or [])
        self.assertIn("rendimiento", sistemas["refactorizacion"].datos.get("usa") or [])


if __name__ == "__main__":
    unittest.main()
