"""La lluvia dice dónde mirar. Si devolviera el cuerpo, sería otra fuga de contexto."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from puente.lluvia import MIN_SALIDA, como_json, como_texto, indexar, ordenar

TESTIGO = "TESTIGOQUENUNCASALE"

CON_FRONTMATTER = """---
cosmos: lluvia
nombre: backtest-sin-comisiones-miente
moja:
  - "trading/**"
resumen: Un backtest sin comisiones ni deslizamiento infla el resultado hasta invertirlo.
---

# Detalle

{testigo}. Aquí va el cuerpo largo con la explicación completa, que es justo lo que
esta herramienta existe para no traerse al contexto.
""".format(testigo=TESTIGO)

SIN_FRONTMATTER = """# Cierre de la tanda de despliegue

{testigo}. Nota escrita a mano, sin frontmatter, como las que deja cualquiera al
cerrar un trabajo.
""".format(testigo=TESTIGO)


def registro_de_prueba(base: Path, extras: int = 0) -> Path:
    entradas = base / "registro"
    (entradas / "lluvia" / "trading").mkdir(parents=True)
    (entradas / "commits" / "infraestructura" / "2026" / "09").mkdir(parents=True)
    (entradas / "lluvia" / "trading" / "backtest-sin-comisiones-miente.md").write_text(
        CON_FRONTMATTER, encoding="utf-8"
    )
    (entradas / "commits" / "infraestructura" / "2026" / "09" / "cierre-despliegue.md").write_text(
        SIN_FRONTMATTER, encoding="utf-8"
    )
    for indice in range(extras):
        (entradas / "lluvia" / "trading" / f"relleno-{indice:02d}.md").write_text(
            "---\ncosmos: lluvia\nnombre: relleno-{i:02d}\nmoja:\n  - \"trading/**\"\n"
            "resumen: Un backtest de relleno numero {i} que habla de comisiones y deslizamiento.\n"
            "---\n\n{t}. Cuerpo de relleno.\n".format(i=indice, t=TESTIGO),
            encoding="utf-8",
        )
    return base


class NuncaElCuerpo(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="puente-lluvia-")
        self.base = registro_de_prueba(Path(self.temporal.name), extras=12)
        self.entradas = indexar(self.base)

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_el_indice_lee_el_cuerpo_para_puntuar(self) -> None:
        self.assertTrue(any(TESTIGO in entrada.cuerpo for entrada in self.entradas))

    def test_la_salida_de_texto_nunca_lleva_el_cuerpo(self) -> None:
        resultados = ordenar("backtest comisiones deslizamiento", self.entradas)
        self.assertTrue(resultados)
        salida = como_texto(resultados, 100_000, explicar=True)
        self.assertIn("backtest-sin-comisiones-miente", salida)
        self.assertNotIn(TESTIGO, salida)

    def test_la_salida_json_nunca_lleva_el_cuerpo(self) -> None:
        resultados = ordenar("backtest comisiones deslizamiento", self.entradas)
        salida = como_json(resultados, 100_000)
        self.assertNotIn(TESTIGO, salida)
        for fila in json.loads(salida):
            self.assertNotIn("cuerpo", fila)
            self.assertEqual(
                set(fila) - {"puntuacion"}, {"ruta", "nombre", "resumen", "carpeta", "nicho"}
            )

    def test_una_consulta_por_el_cuerpo_tampoco_lo_devuelve(self) -> None:
        resultados = ordenar(TESTIGO, self.entradas)
        self.assertTrue(resultados, "el cuerpo debe puntuar aunque no se muestre")
        self.assertNotIn(TESTIGO, como_texto(resultados, 100_000))


class Presupuesto(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="puente-lluvia-")
        self.base = registro_de_prueba(Path(self.temporal.name), extras=40)
        self.entradas = indexar(self.base)
        self.resultados = ordenar("backtest comisiones deslizamiento relleno", self.entradas)

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_el_texto_respeta_el_presupuesto_de_bytes(self) -> None:
        self.assertGreater(len(self.resultados), 10)
        for maximo in (MIN_SALIDA, 512, 1_000, 4_000):
            with self.subTest(maximo=maximo):
                salida = como_texto(self.resultados, maximo)
                self.assertLessEqual(len(salida.encode("utf-8")), maximo)

    def test_el_json_respeta_el_presupuesto_de_bytes(self) -> None:
        for maximo in (MIN_SALIDA, 512, 1_000, 4_000):
            with self.subTest(maximo=maximo):
                salida = como_json(self.resultados, maximo)
                self.assertLessEqual(len((salida + "\n").encode("utf-8")), maximo)
                json.loads(salida)

    def test_un_presupuesto_mayor_no_devuelve_menos(self) -> None:
        corto = como_texto(self.resultados, 512).splitlines()
        largo = como_texto(self.resultados, 4_000).splitlines()
        self.assertGreaterEqual(len(largo), len(corto))


class Indexado(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="puente-lluvia-")
        self.base = registro_de_prueba(Path(self.temporal.name))
        self.entradas = indexar(self.base)

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def test_indexa_tambien_lo_que_no_tiene_frontmatter(self) -> None:
        nombres = {entrada.nombre for entrada in self.entradas}
        self.assertIn("cierre-despliegue", nombres)
        deducida = next(e for e in self.entradas if e.nombre == "cierre-despliegue")
        self.assertEqual(deducida.resumen, "Cierre de la tanda de despliegue")
        self.assertEqual(deducida.nicho, "infraestructura")
        self.assertEqual(deducida.carpeta, "commits")

    def test_el_nicho_sale_de_la_carpeta(self) -> None:
        memoria = next(e for e in self.entradas if e.carpeta == "lluvia")
        self.assertEqual(memoria.nicho, "trading")

    def test_sin_registro_no_hay_indice(self) -> None:
        with tempfile.TemporaryDirectory() as vacio:
            self.assertEqual(indexar(vacio), [])


if __name__ == "__main__":
    unittest.main()
