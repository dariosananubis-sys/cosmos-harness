from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cosmos import medir
from cosmos.modelo import Arbol, Nodo, cargar_arbol, cuerpo


class PruebasMedidor(unittest.TestCase):
    @staticmethod
    def arbol_dos_nichos() -> Arbol:
        nodos = [
            Nodo(Path("galaxia.md"), "galaxia.md", {"cosmos": "galaxia", "nombre": "raiz", "resumen": "Organiza dos nichos sintéticos."}, {}, ""),
            Nodo(Path("web.md"), "web.md", {"cosmos": "sistema-solar", "nombre": "web", "resumen": "Construye sitios sintéticos.", "padre": ""}, {}, ""),
            Nodo(Path("saas.md"), "saas.md", {"cosmos": "sistema-solar", "nombre": "saas", "resumen": "Construye servicios sintéticos.", "padre": ""}, {}, ""),
            Nodo(Path("web-provincia.md"), "web-provincia.md", {"cosmos": "provincia", "nombre": "calidad-web", "resumen": "Agrupa controles web.", "padre": "web"}, {}, ""),
            Nodo(Path("saas-provincia.md"), "saas-provincia.md", {"cosmos": "provincia", "nombre": "calidad-saas", "resumen": "Agrupa controles SaaS.", "padre": "saas"}, {}, ""),
            Nodo(Path("web-tool.md"), "web-tool.md", {"cosmos": "pueblo", "nombre": "web-tool", "resumen": "Comprueba una interfaz web.", "padre": "web/calidad-web"}, {}, ""),
            Nodo(Path("saas-tool.md"), "saas-tool.md", {"cosmos": "pueblo", "nombre": "saas-tool", "resumen": "Comprueba un servicio SaaS.", "padre": "saas/calidad-saas"}, {}, ""),
        ]
        return Arbol(Path("."), nodos)

    def test_catalogo_base_no_contiene_ningun_pueblo(self) -> None:
        contexto = medir.contexto_inicial(self.arbol_dos_nichos(), indice="")
        self.assertNotIn("web-tool", contexto)
        self.assertNotIn("saas-tool", contexto)

    def test_catalogo_web_contiene_solo_pueblos_de_web(self) -> None:
        contexto = medir.contexto_inicial(self.arbol_dos_nichos(), nichos=["web"], indice="")
        self.assertIn("web/calidad-web/web-tool: Comprueba una interfaz web.", contexto)
        self.assertNotIn("saas-tool", contexto)

    def test_arbol_de_tokens_conocidos_a_mano(self) -> None:
        nodo = Nodo(Path("galaxia.md"), "galaxia.md", {"cosmos": "galaxia", "nombre": "raiz", "resumen": "explica"}, {}, "alpha beta")
        resultado = medir.medir_arbol(Arbol(Path("."), [nodo]), metodo="aprox", indice="uno dos")
        self.assertEqual(2, resultado.entrada)
        self.assertEqual(4, resultado.universo)
        self.assertEqual(2, resultado.resto)
        self.assertEqual(0.5, resultado.descarga)

    def test_regresion_descarga_nunca_sale_de_cero_uno(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            (raiz / "galaxia.md").write_text(
                "---\ncosmos: galaxia\nnombre: prueba\nresumen: Galaxia de prueba.\n---\n",
                encoding="utf-8",
            )
            (raiz / "oceano.md").write_text(
                '---\ncosmos: oceano\nnombre: seguridad\nmoja: ["**"]\nresumen: No borrar nada sin permiso.\n---\nRegla corta.\n',
                encoding="utf-8",
            )
            resultado = medir.medir_arbol(cargar_arbol(raiz), metodo="aprox")
        self.assertLessEqual(resultado.entrada, resultado.universo)
        self.assertIsInstance(resultado.descarga, float)
        self.assertGreaterEqual(float(resultado.descarga), 0.0)
        self.assertLessEqual(float(resultado.descarga), 1.0)

    def test_contexto_y_medidor_usan_el_cuerpo_sin_frontmatter(self) -> None:
        nodo = Nodo(
            Path("oceano.md"),
            "oceano.md",
            {"cosmos": "oceano", "nombre": "global", "resumen": "Protege el ejemplo.", "moja": ["**"]},
            {},
            '---\ncosmos: oceano\nnombre: global\nresumen: Protege el ejemplo.\nmoja: ["**"]\n---\n\n  Solo este cuerpo.  \n',
        )
        arbol = Arbol(Path("."), [nodo])
        self.assertEqual("Solo este cuerpo.", cuerpo(nodo))
        self.assertEqual("Solo este cuerpo.", medir.contexto_inicial(arbol, indice=""))
        self.assertEqual(medir.contar_aprox("Solo este cuerpo."), medir.medir_arbol(arbol, metodo="aprox", indice="").entrada)

    def test_aproximado_y_exacto_respetan_margen_publicado(self) -> None:
        exacto = medir._contador_exacto()
        if exacto is None:
            self.skipTest("tokenizador exacto local no disponible; comparación declaradamente omitida")
        self.assertIsNotNone(medir.MARGEN_ERROR, "hay tokenizador exacto pero no existe margen publicado")
        corpus = "# Prueba\n\nTexto en castellano and English.\n\n```python\nprint('ok')\n```\n"
        esperado = exacto[0](corpus)
        aproximado = medir.contar_aprox(corpus)
        divergencia = abs(aproximado - esperado) / esperado
        self.assertLessEqual(divergencia, medir.MARGEN_ERROR)

    def test_no_medido_nunca_se_convierte_en_cero(self) -> None:
        resultado = medir.medir_arbol(Arbol(Path(".")), metodo="aprox", indice="")
        self.assertEqual("no_medido", resultado.fuera_cosmos)
        serializado = medir.medicion_json(resultado)
        self.assertIn('"fuera_cosmos": "no_medido"', serializado)
        self.assertNotIn('"fuera_cosmos": 0', serializado)

    def test_arbol_vacio_no_publica_descarga_perfecta(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            resultado = medir.medir_arbol(Arbol(Path(temporal)), metodo="aprox", indice="")
        self.assertEqual(0, resultado.entrada)
        self.assertEqual(0, resultado.arbol)
        self.assertEqual("no_definida", resultado.descarga)


if __name__ == "__main__":
    unittest.main()
