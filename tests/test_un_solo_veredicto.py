"""Tres comparaciones sobre el mismo árbol, publicadas con la misma etiqueta.

`E16` (el gate) medía el peor nicho **con** su agua. `cosmos medir` devolvía su código de
salida sobre el nicho activo con agua. Y los guards de sesión comparaban el nicho activo
**sin** agua, con un comentario encima que afirmaba usar «el mismo criterio que `cosmos
medir`». No lo usaba.

Con `[nichos] activos` puesto, el mismo árbol daba «quedan 325» en el comando mientras el
gate vigilaba 119, y el guard un número aún más holgado. Ninguno estaba mal por separado:
el fallo es que se publicaban como si fueran la misma cifra, y cada uno parecía confirmar
a los otros.

Lo que el presupuesto promete es que **cualquier sesión quepa**, así que el juez es el peor
nicho con toda su agua, y vive en un solo sitio.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from cosmos.medir import medir_casos, veredicto_de_presupuesto
from cosmos.modelo import cargar_arbol, cargar_configuracion

RAIZ = Path(__file__).resolve().parent.parent


class ElJuezEsUnoSolo(unittest.TestCase):
    def setUp(self) -> None:
        self.config = cargar_configuracion(RAIZ / "cosmos.toml")
        self.arbol = cargar_arbol(RAIZ / "galaxia")

    def test_el_veredicto_no_depende_del_nicho_activo(self) -> None:
        """Elegir un nicho barato no puede poner verde un árbol que no cabe."""

        sin_seleccion = medir_casos(self.arbol, metodo=self.config.metodo,
                                    presupuesto=self.config.entrada)
        barato = medir_casos(self.arbol, metodo=self.config.metodo,
                             presupuesto=self.config.entrada, nichos=["juegos"])
        self.assertEqual(
            veredicto_de_presupuesto(sin_seleccion, self.config.entrada).evaluado,
            veredicto_de_presupuesto(barato, self.config.entrada).evaluado,
        )

    def test_juzga_el_peor_caso_con_agua_y_no_la_entrada_pelada(self) -> None:
        casos = medir_casos(self.arbol, metodo=self.config.metodo, presupuesto=self.config.entrada)
        v = veredicto_de_presupuesto(casos, self.config.entrada)
        self.assertEqual(v.evaluado, casos.peor.entrada_con_agua)
        self.assertNotEqual(v.evaluado, casos.peor.entrada, "el agua volvió a quedar fuera")

    def test_dice_de_que_nicho_habla(self) -> None:
        """Un número sin su nicho obliga a adivinar dónde recortar."""

        casos = medir_casos(self.arbol, metodo=self.config.metodo, presupuesto=self.config.entrada)
        v = veredicto_de_presupuesto(casos, self.config.entrada)
        self.assertEqual(v.nicho, casos.peor_nicho)
        self.assertIn(v.nicho, v.como_linea())


class LosTresLlamantesDicenLoMismo(unittest.TestCase):
    def test_validar_y_medir_coinciden_en_el_veredicto(self) -> None:
        validar = subprocess.run([sys.executable, "-m", "cosmos", "validar"],
                                 capture_output=True, text=True, cwd=RAIZ)
        medir = subprocess.run([sys.executable, "-m", "cosmos", "medir"],
                               capture_output=True, text=True, cwd=RAIZ)
        cabe_validar = "E16" not in validar.stdout + validar.stderr
        cabe_medir = medir.returncode == 0
        self.assertEqual(cabe_validar, cabe_medir,
                         "el gate y el comando discrepan sobre el mismo árbol")

    def test_el_guard_de_sesion_usa_el_mismo_juez(self) -> None:
        fuente = (RAIZ / "puente/sesion.py").read_text(encoding="utf-8")
        self.assertIn("veredicto_de_presupuesto(medicion, config.entrada)", fuente)
        self.assertNotIn("medicion.evaluada.entrada\n", fuente,
                         "el guard volvió a comparar la entrada sin agua")


if __name__ == "__main__":
    unittest.main()


class LaDescargaNoSubeSolaPorEscribirDocumentacion(unittest.TestCase):
    """F23: el universo incluía los partes de commit del propio COSMOS.

    `resto` sumaba el cuerpo de todo nodo no-océano, y los partes viven en el árbol como
    `lluvia`. Eran 17.263 tokens —el 11 % del universo— de historia interna que ningún
    agente carga para resolver un encargo: `rio/memoria` los busca y devuelve dónde mirar,
    nunca el cuerpo.

    El efecto medido era de dos décimas (98,42 % contra 98,24 %), pero el defecto no es el
    tamaño: es que la métrica **subía sola**. Cada parte nuevo mejoraba la descarga sin que
    el sistema descargara nada, y este repositorio escribe un parte por tanda de trabajo.
    """

    def test_la_lluvia_no_cuenta_en_el_universo(self) -> None:
        from cosmos.medir import medir_arbol

        # El árbol se carga como lo hace el CLI: con el registro dentro. Cargando solo
        # `galaxia/` no hay ni una lluvia y la prueba pasaría sin medir nada.
        config = cargar_configuracion(RAIZ / "cosmos.toml")
        arbol = cargar_arbol(config.arbol, tambien=(config.registro,))
        medicion = medir_arbol(arbol)
        nombres = {parte.nombre for parte in medicion.detalle_arbol}
        lluvias = [n.referencia for n in arbol.nodos if n.cosmos == "lluvia"]
        self.assertTrue(lluvias, "no hay partes en el árbol: la prueba no está midiendo nada")
        for parte in lluvias:
            self.assertNotIn(parte, nombres)

    def test_escribir_un_parte_nuevo_no_mejora_la_descarga(self) -> None:
        """La propiedad que importa, ejercitada: se añade un parte y la cifra no se mueve."""

        from tempfile import TemporaryDirectory

        from cosmos.medir import medir_arbol

        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "galaxia.md").write_text(
                "---\ncosmos: galaxia\nnombre: t\nresumen: Arbol de prueba.\n---\n", encoding="utf-8")
            (base / "sistemas").mkdir()
            (base / "sistemas/web.md").write_text(
                "---\ncosmos: sistema-solar\nnombre: web\npadre: \"\"\nresumen: Sitios que cargan.\n---\n"
                "Cuerpo del oficio, con la longitud tipica de uno real y algo mas de texto.\n",
                encoding="utf-8")
            antes = medir_arbol(cargar_arbol(base)).descarga

            (base / "registro").mkdir()
            (base / "registro/parte.md").write_text(
                "---\ncosmos: lluvia\nnombre: parte\nmoja: []\nresumen: Un parte de commit.\n---\n"
                + ("Texto largo del parte que no lo carga nadie para trabajar. " * 40),
                encoding="utf-8")
            despues = medir_arbol(cargar_arbol(base)).descarga

        self.assertEqual(antes, despues, "la descarga subió sola por escribir documentación")


class ElPeorNichoEsElPeorDeVerdad(unittest.TestCase):
    """T02: `max` por `min` en `medir_casos` y la suite entera seguía verde.

    El comando publicaba «Peor nicho ... 1.528 tokens (juegos, 7 pueblos)» —el más barato
    del árbol, con la etiqueta del peor— y el presupuesto daba 1.126 tokens de margen que
    no existen. Todo el sistema de garantías descansa en esa palabra: el presupuesto
    promete que **cualquier** sesión cabe, y solo lo promete si se mide la más cara.
    """

    def test_ningun_nicho_del_arbol_es_mas_caro_que_el_declarado_peor(self) -> None:
        from cosmos.medir import medir_casos

        config = cargar_configuracion(RAIZ / "cosmos.toml")
        arbol = cargar_arbol(config.arbol)
        casos = medir_casos(arbol, metodo=config.metodo, presupuesto=config.entrada)

        oficios = [n.nombre for n in arbol.nodos if n.cosmos == "sistema-solar"]
        self.assertGreater(len(oficios), 1, "con un solo oficio la prueba no distingue nada")

        peor_medido = max(
            medir_casos(arbol, metodo=config.metodo, presupuesto=config.entrada,
                        nichos=[oficio]).evaluada.entrada
            for oficio in oficios
        )
        self.assertEqual(casos.peor.entrada, peor_medido,
                         "el 'peor nicho' publicado no es el más caro del árbol")

    def test_el_peor_nicho_declarado_existe(self) -> None:
        from cosmos.medir import medir_casos

        config = cargar_configuracion(RAIZ / "cosmos.toml")
        arbol = cargar_arbol(config.arbol)
        casos = medir_casos(arbol, metodo=config.metodo, presupuesto=config.entrada)
        oficios = {n.nombre for n in arbol.nodos if n.cosmos == "sistema-solar"}
        self.assertIn(casos.peor_nicho, oficios)
