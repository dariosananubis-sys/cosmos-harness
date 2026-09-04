from __future__ import annotations

import json
import os
import re
import tempfile
import unittest
from pathlib import Path

from cosmos import medir
from cosmos.modelo import Arbol, Nodo, cargar_arbol, cuerpo

RAIZ = Path(__file__).resolve().parent.parent


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
        # Formato de arbol indentado (2026-09-02): el pueblo paga su nombre bajo su
        # familia, no la ruta entera — el ancla del nicho la pone el hijo del sistema.
        contexto = medir.contexto_inicial(self.arbol_dos_nichos(), nichos=["web"], indice="")
        self.assertIn("web/calidad-web: Agrupa controles web.", contexto)
        self.assertIn("\n  web-tool: Comprueba una interfaz web.", contexto)
        self.assertNotIn("web/calidad-web/web-tool", contexto, "volvio la ruta completa por linea")
        self.assertNotIn("saas-tool", contexto)

    def test_arbol_de_tokens_conocidos_a_mano(self) -> None:
        """Cuentas a mano, con los DOS factores de calibración.

        El índice se cuenta con `FACTOR_GENERADO` (1.381) y el cuerpo con
        `FACTOR_CALIBRACION` (1.204). No es un capricho: medido el 2026-09-02, las
        listas de `ruta: resumen` tokenizan un 15 % peor que la prosa, y usar el
        factor de prosa para ellas ponía verde un árbol que estaba en rojo (F01).
        """

        nodo = Nodo(Path("galaxia.md"), "galaxia.md", {"cosmos": "galaxia", "nombre": "raiz", "resumen": "explica"}, {}, "alpha beta")
        resultado = medir.medir_arbol(Arbol(Path("."), [nodo]), metodo="aprox", indice="uno dos")
        self.assertEqual(round(2 * medir.FACTOR_GENERADO), resultado.entrada)      # índice
        self.assertEqual(round(2 * medir.FACTOR_CALIBRACION), resultado.resto)     # cuerpo
        self.assertEqual(resultado.entrada + resultado.resto, resultado.universo)
        self.assertTrue(0 <= resultado.descarga <= 1)

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

    def test_los_factores_publicados_son_los_que_documenta_la_calibracion(self) -> None:
        """Los tres números de la calibración, atados a `docs/CALIBRACION.md`.

        Corre SIEMPRE, con tokenizador o sin él, porque cierra el agujero de F07:
        `FACTOR_CALIBRACION = 1.0` revertía un 20 % de todas las cifras publicadas
        y `MARGEN_ERROR = None` devolvía el «±desconocido» que la documentación da
        por cerrado — y ninguna de las dos ponía roja una sola prueba.
        """

        doc = (RAIZ / "docs" / "CALIBRACION.md").read_text(encoding="utf-8")

        def publicado(patron: str) -> float:
            hallado = re.search(patron, doc)
            self.assertIsNotNone(hallado, f"docs/CALIBRACION.md ya no publica {patron!r}")
            return float(hallado.group(1).replace(",", "."))

        self.assertEqual(publicado(r"`FACTOR_CALIBRACION` *= *([0-9.]+)"), medir.FACTOR_CALIBRACION)
        self.assertEqual(publicado(r"`FACTOR_GENERADO` *= *([0-9.]+)"), medir.FACTOR_GENERADO)
        self.assertIsNotNone(medir.MARGEN_ERROR, "el margen publicado no puede volver a ±desconocido")
        self.assertAlmostEqual(publicado(r"error medio ([0-9,]+) %") / 100, medir.MARGEN_ERROR, places=4)

    def test_aproximado_y_exacto_respetan_margen_publicado(self) -> None:
        """El margen se comprueba sobre lo que el medidor cuenta de verdad.

        Antes esta prueba comparaba siete líneas de juguete y divergía un 19,05 %
        contra el 5,2 % publicado: estaba en verde **solo** porque esta máquina no
        tiene tokenizador (F03). Un `skip` silencioso sobre la única prueba de la
        métrica principal es un verde comprado.

        Ahora el corpus es el árbol real —los cuerpos que el medidor suma y los dos
        bloques generados que forman la entrada—, que es lo que `FACTOR_CALIBRACION`
        se calibró para contar. Sobre un árbol de juguete la divergencia media es
        del 27,9 %: la representatividad del corpus no era un detalle.
        """

        exacto = medir._contador_exacto()
        if exacto is None:
            aviso = (
                "SIN TOKENIZADOR: el margen publicado (±5,2 %) NO se ha verificado en esta "
                "ejecución. Instálalo en un venv temporal (docs/CALIBRACION.md) o exige el fallo "
                "con COSMOS_EXIGE_TOKENIZADOR=1."
            )
            if os.environ.get("COSMOS_EXIGE_TOKENIZADOR"):
                self.fail(aviso)
            print(f"\n  AVISO  {aviso}")
            self.skipTest(aviso)

        contar_exacto = exacto[0]
        arbol = cargar_arbol(RAIZ / "galaxia")
        cuerpos = [cuerpo(nodo) for nodo in arbol.nodos]
        divergencias = [
            abs(medir.contar_aprox(texto) - contar_exacto(texto)) / contar_exacto(texto)
            for texto in cuerpos
            if contar_exacto(texto) >= 20
        ]
        self.assertGreater(len(divergencias), 100, "el corpus de calibración se ha vaciado")
        media = sum(divergencias) / len(divergencias)
        self.assertLessEqual(
            media, medir.MARGEN_ERROR,
            f"la divergencia media real ({media:.2%}) supera el margen publicado; recalibra el factor "
            "y actualiza docs/CALIBRACION.md, no bajes esta prueba",
        )

        # Y el número que decide el presupuesto, que es el que no puede mentir.
        entrada_exacta = contar_exacto(medir.contexto_inicial(arbol, None))
        entrada_aprox = medir.medir_arbol(arbol, metodo="aprox").entrada
        self.assertLessEqual(
            abs(entrada_aprox - entrada_exacta) / entrada_exacta, medir.MARGEN_ERROR,
            f"la entrada publicada ({entrada_aprox}) se aleja del conteo real ({entrada_exacta}) "
            "más de lo que declara el margen",
        )

    def test_el_veredicto_exacto_y_el_aproximado_coinciden_sobre_la_galaxia(self) -> None:
        """Sustituye al canario F01, que pedía borrarse el día que el exacto diera verde.

        Ese día llegó el 2026-09-02 (el commit que adelgazó el contenido) y nadie lo
        oyó, porque el canario solo hablaba con tokenizador y ninguna instalación por
        defecto lo tiene (auditoría E-11 / D-08). Medido el 2026-09-03 con
        `~/.cosmos/calib/bin/python -m cosmos medir --metodo exacto`: 3.654 ≤ 4.000.

        Lo que sí se exige desde hoy: los dos métodos dan el MISMO veredicto sobre el
        árbol real, y la desviación agregada aprox↔exacto queda dentro del margen que
        el medidor publica y aplica al presupuesto. Si divergen, o el contenido creció
        hasta el borde o la calibración caducó; en los dos casos es un rojo.
        """

        if medir._contador_exacto() is None:
            if os.environ.get("COSMOS_EXIGE_TOKENIZADOR"):
                self.fail("COSMOS_EXIGE_TOKENIZADOR=1 y no hay tokenizador: instala tiktoken (docs/CALIBRACION.md)")
            self.skipTest("sin tokenizador no se puede medir el veredicto exacto")
        arbol = cargar_arbol(RAIZ / "galaxia")
        aprox = medir.medir_casos(arbol, metodo="aprox", presupuesto=4000)
        exacto = medir.medir_casos(arbol, metodo="exacto", presupuesto=4000)
        self.assertEqual(
            medir.veredicto_de_presupuesto(aprox, 4000).cabe,
            medir.veredicto_de_presupuesto(exacto, 4000).cabe,
            "el contador aproximado y el tokenizador real discrepan sobre si el árbol cabe",
        )
        desvio = abs(exacto.peor.entrada_con_agua - aprox.peor.entrada_con_agua) / exacto.peor.entrada_con_agua
        self.assertLessEqual(
            desvio, medir.MARGEN_ERROR,
            f"la desviación agregada aprox↔exacto ({desvio:.1%}) supera el margen publicado "
            f"({medir.MARGEN_ERROR:.1%}): recalibra (docs/CALIBRACION.md)",
        )

    def test_no_medido_nunca_se_convierte_en_cero(self) -> None:
        resultado = medir.medir_arbol(Arbol(Path(".")), metodo="aprox", indice="")
        self.assertEqual("no_medido", resultado.fuera_cosmos)
        serializado = json.dumps(resultado.como_dict(), ensure_ascii=False, indent=2, sort_keys=True)
        self.assertIn('"fuera_cosmos": "no_medido"', serializado)
        self.assertNotIn('"fuera_cosmos": 0', serializado)

    def test_el_agua_condicional_no_entra_en_la_entrada_pero_si_en_el_presupuesto(self) -> None:
        """H14: el mar se carga por `paths:` y no aparecía en ningún número.

        `entrada` no lo cuenta —es correcto, no está en `contexto_inicial`— pero
        `entrada_con_agua` sí, porque se paga igual sin que nadie lo invoque
        (NUCLEO §3). Y como el agua ya vive dentro de `resto`, no se puede colar
        dos veces: `entrada_con_agua` nunca pasa de `universo`.
        """

        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            (raiz / "galaxia.md").write_text(
                "---\ncosmos: galaxia\nnombre: prueba\nresumen: Galaxia de prueba.\n---\n",
                encoding="utf-8",
            )
            (raiz / "oceano.md").write_text(
                '---\ncosmos: oceano\nnombre: seguridad\nmoja: ["**"]\nresumen: Regla global de prueba.\n---\nRegla global corta.\n',
                encoding="utf-8",
            )
            (raiz / "rio.md").write_text(
                '---\ncosmos: rio\nnombre: comprobar\nmoja: []\ninvoca: comprobar\nresumen: Comando de prueba invocado a mano.\n---\nCuerpo del comando que solo se paga al invocarlo.\n',
                encoding="utf-8",
            )
            sin_mar = medir.medir_arbol(cargar_arbol(raiz), metodo="aprox")
            (raiz / "mar.md").write_text(
                '---\ncosmos: mar\nnombre: criterio\nmoja: ["**/*.py"]\nresumen: Regla regional de prueba.\n---\n'
                + " ".join(f"palabra{numero}" for numero in range(30))
                + "\n",
                encoding="utf-8",
            )
            con_mar = medir.medir_arbol(cargar_arbol(raiz), metodo="aprox")

        self.assertEqual(0, sin_mar.agua)
        self.assertEqual(sin_mar.entrada, con_mar.entrada, "el mar no está en contexto_inicial")
        self.assertGreater(con_mar.agua, 0, "el mar se carga por paths: y tiene que contarse")
        self.assertEqual(con_mar.entrada + con_mar.agua, con_mar.entrada_con_agua)
        self.assertLessEqual(con_mar.entrada_con_agua, con_mar.universo, "el agua no se puede contar dos veces")
        self.assertEqual(["mar/criterio"], [parte.nombre for parte in con_mar.detalle_agua], "el río se invoca: no es agua condicional")
        self.assertIn('"agua"', json.dumps(con_mar.como_dict()))

    @staticmethod
    def _escribir_arbol(raiz: Path, aguas: dict[str, list[str]]) -> None:
        (raiz / "galaxia.md").write_text(
            "---\ncosmos: galaxia\nnombre: agua\nresumen: Galaxia mínima para medir el agua condicional.\n---\n\nCuerpo.\n",
            encoding="utf-8",
        )
        for nombre, moja in aguas.items():
            (raiz / f"mar-{nombre}.md").write_text(
                f'---\ncosmos: mar\nnombre: {nombre}\nresumen: Reglas del alcance {nombre} para esta prueba.\n'
                f"moja: {moja!r}\n---\n\n" + " ".join(f"palabra{numero}" for numero in range(60)) + "\n",
                encoding="utf-8",
            )

    def test_dos_aguas_que_mojan_el_mismo_fichero_se_cobran_las_dos(self) -> None:
        """F06: el medidor publicaba la mitad del coste real de un solo fichero.

        `**/*.spec.*` y `**/*.ts` casan los dos `src/app.spec.ts`, pero el cálculo
        «por extensión» los metía en grupos distintos —`.*` y `.ts`— y se quedaba
        con el más caro. Medido antes del arreglo: publicaba 120 tokens donde ese
        fichero carga 240.
        """

        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            self._escribir_arbol(raiz, {"specs": ["**/*.spec.*"], "tipado": ["**/*.ts"]})
            resultado = medir.medir_arbol(cargar_arbol(raiz), metodo="aprox", indice="")

        nombres = sorted(parte.nombre for parte in resultado.detalle_agua)
        self.assertEqual(["mar/specs", "mar/tipado"], nombres, "las dos mojan src/app.spec.ts")
        self.assertEqual(sum(parte.tokens for parte in resultado.detalle_agua), resultado.agua)
        self.assertEqual(2 * resultado.detalle_agua[0].tokens, resultado.agua)

    def test_un_agua_que_no_solapa_con_la_mas_cara_tambien_se_cobra(self) -> None:
        """F06: el agua de marcado y hojas de estilo desaparecía del número.

        El cálculo «por extensión» se quedaba con el grupo más caro, así que un mar
        que moja `.css` y no coincide con el de `.py` no se cobraba nunca. En la
        galaxia real eso dejaba fuera `mar/accesibilidad` (101 tok): una sesión de
        React + Python toca las dos cosas y paga las dos.

        Además `**/tests/**` no tiene extensión: `rfind('.')` lo volvía «todas», y
        el alcance por directorio dejaba de distinguirse de un océano.
        """

        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            self._escribir_arbol(raiz, {
                "accesible": ["**/*.css"], "codigo": ["**/*.py"], "pruebas": ["**/tests/**"],
            })
            resultado = medir.medir_arbol(cargar_arbol(raiz), metodo="aprox", indice="")

        self.assertEqual(
            ["mar/accesible", "mar/codigo", "mar/pruebas"],
            sorted(parte.nombre for parte in resultado.detalle_agua),
            "ninguna se puede caer del número por no solapar con la más cara",
        )
        self.assertEqual(3 * resultado.detalle_agua[0].tokens, resultado.agua)

    def test_el_recuento_publicado_es_el_numero_real_de_aguas(self) -> None:
        """F06: la línea decía «5 aguas por paths:» habiendo seis.

        El «5» era el tamaño del grupo ganador, no cuánta agua condicional existe.
        Un rótulo que cuenta otra cosa que el número que acompaña miente dos veces.
        """

        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            self._escribir_arbol(raiz, {
                "uno": ["**/*.py"], "dos": ["**/*.ts"], "tres": ["**/*.css"],
                "cuatro": ["**/tests/**"], "cinco": ["**/*.md"], "seis": ["**/*.go"],
            })
            arbol = cargar_arbol(raiz)
            resultado = medir.medir_arbol(arbol, metodo="aprox", indice="")
            salida = medir.formatear_casos(medir.medir_casos(arbol, metodo="aprox", indice=""))

        self.assertEqual(6, len(medir.agua_condicional(arbol)))
        self.assertEqual(6, len(resultado.detalle_agua))
        self.assertIn("(6 aguas por paths:", salida)

    def test_arbol_vacio_no_publica_descarga_perfecta(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            resultado = medir.medir_arbol(Arbol(Path(temporal)), metodo="aprox", indice="")
        self.assertEqual(0, resultado.entrada)
        self.assertEqual(0, resultado.arbol)
        self.assertEqual("no_definida", resultado.descarga)


if __name__ == "__main__":
    unittest.main()
