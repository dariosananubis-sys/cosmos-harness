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

Y las pruebas de este fichero ejercitan **la configuración que produjo el fallo**: un
tercer revisor demostró (T03) que ninguna ponía `[nichos] activos` con contenido — que es
justo la condición bajo la cual el fallo original aparecía — y que el «test del guard» era
un grep de una cadena en el fuente (T04), incapaz de distinguir «no existe» de «existe y
hay otro juez al lado». Aquí se elige un presupuesto ENTRE el nicho más barato y el más
caro, para que un juez que cobre sobre la selección dé la respuesta contraria al bueno.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.medir import formatear_casos, medir_arbol, medir_casos, veredicto_de_presupuesto
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


def _costes_por_nicho(arbol, metodo: str) -> dict[str, int]:
    return {
        nombre: medir_arbol(arbol, metodo=metodo, nichos=[nombre]).entrada_con_agua
        for nombre in sorted({n.nombre for n in arbol.nodos if n.cosmos == "sistema-solar"})
    }


class ElJuezCobraSobreElPeorAunqueHayaSeleccion(unittest.TestCase):
    """T03: la configuración que produjo el fallo, por fin ejercitada.

    El sabotaje que sobrevivía (M02): `cabe` calculado sobre `casos.evaluada` —la
    selección— en vez de sobre `casos.peor`. Con `activos = []` los dos coinciden y
    ningún test lo distinguía. Se elige un presupuesto ESTRICTAMENTE entre el nicho
    más barato y el más caro: el juez bueno dice «no cabe» (el peor no cabe) y el
    saboteado diría «cabe» (la selección barata sí). Medido antes de afirmar.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = cargar_configuracion(RAIZ / "cosmos.toml")
        cls.arbol = cargar_arbol(
            cls.config.arbol,
            excluir=cls.config.indice,
            excluir_directorios=(cls.config.destino_compilacion,),
            tambien=(cls.config.registro,) if cls.config.registro else (),
        )
        costes = _costes_por_nicho(cls.arbol, cls.config.metodo)
        cls.barato = min(costes, key=costes.get)
        cls.coste_barato = costes[cls.barato]
        cls.coste_caro = max(costes.values())
        cls.presupuesto = (cls.coste_barato + cls.coste_caro) // 2

    def test_el_presupuesto_elegido_distingue_los_dos_jueces(self) -> None:
        """Si el árbol degenera (todos los nichos cuestan igual), la prueba lo canta."""

        self.assertLess(self.coste_barato, self.presupuesto,
                        "no hay hueco entre nichos: esta clase ya no distingue nada")
        self.assertGreater(self.coste_caro, self.presupuesto)

    def test_cabe_es_falso_con_la_seleccion_barata_activa(self) -> None:
        casos = medir_casos(self.arbol, metodo=self.config.metodo,
                            presupuesto=self.presupuesto, nichos=[self.barato])
        v = veredicto_de_presupuesto(casos, self.presupuesto)
        self.assertIs(v.cabe, False,
                      "el juez cobró sobre la selección: elegir un nicho barato puso verde "
                      "un árbol cuyo peor caso no cabe")
        self.assertEqual(v.evaluado, casos.peor.entrada_con_agua)

    def test_la_linea_que_lee_una_persona_dice_lo_mismo_que_el_codigo_de_salida(self) -> None:
        """B02: «OK, quedan 93» impreso y exit 1 en la misma ejecución. Nunca más."""

        casos = medir_casos(self.arbol, metodo=self.config.metodo,
                            presupuesto=self.presupuesto, nichos=[self.barato])
        texto = formatear_casos(casos)
        self.assertIn("ROJO, excede", texto)
        self.assertNotIn("OK, quedan", texto)


class LosCuatroLlamantesDicenLoMismo(unittest.TestCase):
    """T04: la igualdad de veredictos se ejercita, no se grepea.

    El test anterior comprobaba que la cadena `veredicto_de_presupuesto(medicion,
    config.entrada)` aparecía en el texto de `puente/sesion.py`. Un grep no distingue
    «no existe» de «existe con otro nombre» ni de «existe y además hay otro juez al
    lado» — y había otro juez al lado (B02). Aquí los llamantes se EJECUTAN sobre la
    misma configuración con selección activa y presupuesto entre nichos, y se exige
    que los cuatro den rojo: E16, el código de salida de `medir`, su línea impresa y
    el guard de sesión.
    """

    @classmethod
    def setUpClass(cls) -> None:
        base = ElJuezCobraSobreElPeorAunqueHayaSeleccion
        base.setUpClass()
        cls.barato = base.barato
        cls.presupuesto = base.presupuesto
        cls.tmp = TemporaryDirectory()
        cls.toml = Path(cls.tmp.name, "cosmos.toml")
        cls.toml.write_text(
            f"""[presupuesto]
entrada = {cls.presupuesto}
resumen = 120
oceanos = 7
galaxia_lineas = 40
solapamiento = 0.25

[raiz]
arbol = "{RAIZ}/galaxia"
indice = "{RAIZ}/galaxia/COSMOS.md"
registro = "{RAIZ}/registro"

[medicion]
metodo = "aprox"

[nichos]
activos = ["{cls.barato}"]
""",
            encoding="utf-8",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def _correr(self, *orden: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-m", "cosmos", *orden, "--config", str(self.toml)],
                              capture_output=True, text=True, cwd=RAIZ)

    def test_medir_sale_1_y_su_linea_dice_rojo(self) -> None:
        medir = self._correr("medir")
        self.assertEqual(medir.returncode, 1,
                         "con la selección barata activa, medir puso verde el peor caso")
        self.assertIn("ROJO, excede", medir.stdout)
        self.assertNotIn("OK, quedan", medir.stdout)

    def test_validar_canta_e16_sobre_la_misma_configuracion(self) -> None:
        validar = self._correr("validar")
        self.assertEqual(validar.returncode, 1)
        self.assertIn("E16", validar.stdout + validar.stderr,
                      "el gate discrepa del comando sobre el mismo árbol")

    def test_el_guard_de_sesion_da_el_mismo_rojo_ejecutandolo(self) -> None:
        from puente.sesion import revisar_arbol

        config = replace(cargar_configuracion(self.toml), nichos=(self.barato,))
        revision = revisar_arbol(config, frozenset())
        self.assertFalse(revision.verde)
        self.assertIn("EXCEDIDO", revision.titulo,
                      "el guard no cobró el presupuesto sobre el peor caso")


class ElVeredictoEsTrivalente(unittest.TestCase):
    """B10: «cabe» no puede salir de no haber medido nada.

    Sobre un árbol vacío —o un `--config` cuyo `arbol` resuelve a un directorio que
    no existe— el juez decía «OK, quedan 4.000 tokens»: `0 <= presupuesto` es verdad,
    pero un cero que sale de cero observaciones es «no lo sé», no un verde. Es el
    mismo patrón que `descarga` ya publicaba como `no_definida` — el módulo conocía
    la regla y la aplicaba a una cifra de las dos.
    """

    def test_sobre_un_arbol_vacio_cabe_es_none_y_la_linea_no_dice_ok(self) -> None:
        with TemporaryDirectory() as tmp:
            vacio = cargar_arbol(Path(tmp))
            casos = medir_casos(vacio, metodo="aprox", presupuesto=4000)
        v = veredicto_de_presupuesto(casos, 4000)
        self.assertIsNone(v.cabe, "un veredicto sobre nada volvió a ser un OK")
        self.assertIn("SIN MEDIR", v.como_linea())
        self.assertNotIn("OK, quedan", v.como_linea())

    def test_medir_sale_1_cuando_la_raiz_del_arbol_no_existe(self) -> None:
        """El caso alcanzable de verdad: un `--config` movido de sitio (rutas relativas)."""

        with TemporaryDirectory() as tmp:
            toml = Path(tmp, "cosmos.toml")
            toml.write_text(
                (RAIZ / "cosmos.toml").read_text(encoding="utf-8"), encoding="utf-8"
            )
            r = subprocess.run([sys.executable, "-m", "cosmos", "medir", "--config", str(toml)],
                               capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 1, "verde sobre un directorio que no existe")
        self.assertIn("no existe", r.stderr)

    def test_el_guard_de_sesion_tampoco_da_verde_sin_nada_que_medir(self) -> None:
        from puente.sesion import revisar_arbol

        with TemporaryDirectory() as tmp:
            config = replace(
                cargar_configuracion(RAIZ / "cosmos.toml"),
                arbol=Path(tmp), indice=Path(tmp, "COSMOS.md"), registro=None,
            )
            revision = revisar_arbol(config, frozenset())
        self.assertFalse(revision.verde)
        self.assertIn("SIN MEDIR", revision.titulo)


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


# T05: `unittest.main()` vivía a media altura del fichero, con clases definidas después.
# `python3 tests/test_un_solo_veredicto.py` ejecutaba 5 pruebas de 7 y terminaba en OK:
# un verde que no había ejercitado dos tercios del fichero. Va al final, siempre.
if __name__ == "__main__":
    unittest.main()
