from __future__ import annotations

import io
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import cosmos.validar as validador
from cosmos import medir
from cosmos.generar import generar_indice
from cosmos.modelo import NIVELES_SOLIDOS, Configuracion, Nodo, cargar_arbol


def documento(cosmos: str, nombre: str, resumen: str, cuerpo: str = "Contenido específico del nodo.", **campos: object) -> str:
    lineas = ["---", f"cosmos: {cosmos}", f"nombre: {nombre}", f"resumen: {resumen}"]
    for clave, valor in campos.items():
        if isinstance(valor, list):
            elementos = ", ".join(f'"{item}"' for item in valor)
            lineas.append(f"{clave}: [{elementos}]")
        elif valor == "":
            lineas.append(f'{clave}: ""')
        else:
            lineas.append(f"{clave}: {valor}")
    return "\n".join(lineas + ["---", "", cuerpo, ""])


class PruebasInvariantes(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temporal.name)
        self.indice = self.raiz / "COSMOS.md"
        self.config = Configuracion(
            entrada=4000,
            resumen=120,
            oceanos=7,
            galaxia_lineas=40,
            umbral_solapamiento=0.25,
            arbol=self.raiz,
            indice=self.indice,
            encontrada=True,
        )
        self.escribir("galaxia.md", documento("galaxia", "raiz", "Organiza un árbol sintético para las pruebas."))
        self.escribir(
            "sistema.md",
            documento("sistema-solar", "trabajo", "Agrupa un modo ficticio de trabajo.", padre=""),
        )

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def escribir(self, ruta: str, contenido: str) -> None:
        destino = self.raiz / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(contenido, encoding="utf-8")

    def validar(self, *, sincronizar: bool = True, config: Configuracion | None = None) -> validador.ResultadoValidacion:
        arbol = cargar_arbol(self.raiz, excluir=self.indice)
        if sincronizar:
            self.indice.write_text(generar_indice(arbol), encoding="utf-8")
        return validador.validar_arbol(arbol, configuracion=config or self.config)

    def exigir(self, codigo: str, *, config: Configuracion | None = None) -> validador.ResultadoValidacion:
        resultado = self.validar(config=config)
        self.assertFalse(resultado.valido)
        self.assertIn(codigo, resultado.codigos())
        return resultado

    def test_e00_sintaxis_o_esquema(self) -> None:
        self.escribir("roto.md", "---\ncosmos: [pueblo\n---\n")
        self.exigir("E00")

    def test_e01_nodo_huerfano(self) -> None:
        self.escribir("huerfano.md", documento("pueblo", "huerfano", "Ejecuta una capacidad ficticia sin efectos."))
        self.exigir("E01")

    def test_e02_padre_inexistente(self) -> None:
        self.escribir("sin-padre.md", documento("planeta", "perdido", "Representa un proyecto sintético aislado.", padre="ausente"))
        self.exigir("E02")

    def test_e03_contencion_invertida(self) -> None:
        self.escribir("planeta.md", documento("planeta", "proyecto", "Representa un encargo ficticio comprobable.", padre=""))
        self.escribir("sistema.md", documento("sistema-solar", "trabajo", "Agrupa un modo ficticio de trabajo.", padre="proyecto"))
        self.exigir("E03")

    def test_e04_retirada_ningun_arbol_legal_construye_un_ciclo(self) -> None:
        """H04: E04 era inalcanzable y su test la fingía subclasando Nodo.

        Aquí se construye el cebo por el camino de verdad —ficheros en disco y
        `cargar_arbol`— y se comprueba que lo que sale es la invariante que sí
        vigila el caso, no un ciclo. Con la E04 antigua este árbol tampoco la
        disparaba: por eso se retiró en vez de dejarla de adorno (NUCLEO §1).
        """

        self.escribir("uno.md", documento("planeta", "uno", "Representa la primera rama sintética.", padre="trabajo/dos"))
        self.escribir("dos.md", documento("provincia", "dos", "Representa la segunda rama sintética.", padre="trabajo/uno"))
        resultado = self.validar()
        self.assertFalse(resultado.valido)
        self.assertNotIn("E04", resultado.codigos())
        self.assertIn("E02", resultado.codigos())
        self.assertEqual(
            [],
            [c.__name__ for c in validador.COMPROBACIONES if c.__name__.endswith("e04")],
            "E04 está retirada: su hueco no se reutiliza (NUCLEO §1)",
        )

    def test_e05_varias_galaxias(self) -> None:
        self.escribir("otra-galaxia.md", documento("galaxia", "otra-raiz", "Organiza una instalación sintética alternativa."))
        self.exigir("E05")

    def test_e06_hermanos_homonimos(self) -> None:
        contenido = documento("planeta", "duplicado", "Representa un encargo sintético con final definido.", padre="trabajo")
        self.escribir("uno.md", contenido)
        self.escribir("dos.md", contenido)
        self.exigir("E06")

    def test_e07_resumen_demasiado_largo(self) -> None:
        self.escribir("largo.md", documento("planeta", "extenso", "x" * 121, padre="sistema-solar/trabajo"))
        self.exigir("E07")

    def test_e08_resumen_no_informa(self) -> None:
        self.escribir("vacio.md", documento("planeta", "demo", "la skill de demo", padre="sistema-solar/trabajo"))
        self.exigir("E08")

    def test_e08_resumen_que_no_informa_aunque_no_repita_el_nombre(self) -> None:
        """H16: con la lista de vacías corta, estos dos pasaban en verde."""

        for numero, resumen in enumerate(
            [
                "El pais de calidad",
                "Cosas y mas cosas varias.",
                "La skill de calidad",
                "Calidad.",
                "Cosas generales del mismo tipo.",
            ]
        ):
            with self.subTest(resumen=resumen):
                self.escribir("flojo.md", documento("provincia", "calidad", resumen, padre="trabajo"))
                self.exigir("E08")
        self.escribir(
            "flojo.md",
            documento("provincia", "calidad", "Comprueba el contraste de color en cada pantalla.", padre="trabajo"),
        )
        self.assertNotIn("E08", self.validar().codigos())

    def test_e09_nivel_desconocido(self) -> None:
        self.escribir("nivel.md", documento("asteroide", "roca", "Representa un nivel que no pertenece al esquema."))
        self.exigir("E09")

    def test_e10_agua_sin_alcance(self) -> None:
        self.escribir("mar.md", documento("mar", "regional", "Aplica una regla sintética a una región.", moja=[]))
        self.exigir("E10")

    def test_e10_lluvia_con_alcance_se_cobraria_sin_cargarse(self) -> None:
        """H20: una memoria con `moja` no se carga (GOAL §4) pero sí entra en el presupuesto.

        Medido el 2026-09-01 al conectar el registro al árbol: dos entradas con
        alcance sumaban 7.700 tokens a `agua_condicional`, por ficheros que nunca
        se abren. La regla de `spec/REGISTRO.md` —«ni una línea»— pasa a E10.
        """

        self.escribir("memoria.md", documento("lluvia", "recordada", "Conserva un hecho sintético que se consulta a mano.", moja=["puente/**"]))
        resultado = self.exigir("E10")
        culpables = [error for error in resultado.errores if error.codigo == "E10"]
        self.assertTrue(any("moja" in error.mensaje for error in culpables), culpables)
        # Y con el alcance vacío, la misma memoria pasa: lo que salta es el alcance.
        self.escribir("memoria.md", documento("lluvia", "recordada", "Conserva un hecho sintético que se consulta a mano.", moja=[]))
        self.assertNotIn("E10", self.validar().codigos())

    def test_e11_oceano_encubierto(self) -> None:
        self.escribir("mar.md", documento("mar", "global-disfrazado", "Simula una regla regional demasiado amplia.", moja=["**"]))
        self.exigir("E11")

    def test_e11_oceano_encubierto_con_globs_equivalentes(self) -> None:
        """H08: cinco escrituras que mojan lo mismo que ['**'] y pasaban en verde."""

        for glob in ["**/*", "**/**", "*", "**/*.*", "./**", "*/**", "**/?", "*/*"]:
            with self.subTest(glob=glob):
                self.escribir("mar.md", documento("mar", "disfrazado", "Simula una regla regional demasiado amplia.", moja=[glob]))
                self.exigir("E11")

    def test_verde_e11_un_mar_que_nombra_su_region(self) -> None:
        for globs in ([r"**/*.py", r"**/*.ts"], [r"**/test/**", r"**/conftest.py"], [r"src/**"]):
            with self.subTest(globs=globs):
                self.escribir("mar.md", documento("mar", "acotado", "Aplica una regla sintética a una región concreta.", moja=globs))
                self.assertNotIn("E11", self.validar().codigos())

    def test_e11_conjunto_de_globs_que_entre_todos_lo_cubren_todo(self) -> None:
        """Ninguno solo es global; juntos no dejan fuera ninguna sonda del corpus."""

        self.escribir(
            "mar.md",
            documento("mar", "sumado", "Simula varias reglas que sumadas lo abarcan todo.", moja=[r"**/*.*", r"**/[A-Za-z]", r"**/M*", r"**/L*"]),
        )
        self.exigir("E11")

    def test_e11_cobertura_total_con_todos_los_globs_anclados(self) -> None:
        """F07: `cobertura_total` no tenía ni una prueba que la ejercitara sola.

        Los cebos de arriba llevan `**/*.*` o `**/?`, que no tienen ni una letra:
        los caza `sin_anclaje` y `cobertura_total` nunca llega a decidir. Ponerla a
        `False` dejaba E11 ciega —la invariante que se reescribió para cerrar H08—
        sin que ninguna de las 175 pruebas se pusiera roja.

        Aquí los nueve globs nombran una región cada uno, ninguno es global por sí
        mismo, y juntos cubren las doce sondas del corpus normativo.
        """

        moja = [
            r"**/*.py", r"**/*.html", r"**/*.md", r"**/*.txt", r"**/*.js",
            r"**/Makefile", r"LICENSE", r"**/x", r"**/.gitignore",
        ]
        self.assertEqual([], [patron for patron in moja if validador._sin_anclaje(patron)])
        self.assertTrue(validador.cobertura_total(moja), "el cebo tiene que cubrir las doce sondas")
        self.escribir("mar.md", documento("mar", "sumado-anclado", "Simula reglas ancladas que sumadas lo abarcan todo.", moja=moja))
        self.exigir("E11")

    def test_el_corpus_de_sondas_no_deja_fuera_ninguna_familia(self) -> None:
        """F07: quitar una sonda abría un hueco por el que pasa un océano.

        `SONDAS_E11` es normativo (NUCLEO §9) y su valor está en que ninguna
        familia de ficheros quede sin representar. Amputarlo no rompía nada: con
        solo `main.py`, `['**/*.py']` ya «lo cubriría todo».
        """

        familias = {
            "con extensión en la raíz": lambda s: "/" not in s and "." in s.lstrip("."),
            "con extensión anidada": lambda s: "/" in s and "." in s.rsplit("/", 1)[1],
            "sin extensión en la raíz": lambda s: "/" not in s and "." not in s,
            "sin extensión anidada": lambda s: "/" in s and "." not in s.rsplit("/", 1)[1],
            "oculto": lambda s: s.rsplit("/", 1)[-1].startswith("."),
            "muy anidado": lambda s: s.count("/") >= 3,
        }
        for nombre, cumple in familias.items():
            with self.subTest(familia=nombre):
                self.assertTrue(
                    any(cumple(sonda) for sonda in validador.SONDAS_E11),
                    f"el corpus normativo ya no representa ficheros {nombre}",
                )
        self.assertFalse(
            validador.cobertura_total([r"**/*.py"]),
            "un corpus amputado dejaría que ['**/*.py'] pasara por océano",
        )

    def test_e12_exceso_de_oceanos(self) -> None:
        self.escribir("oceano.md", documento("oceano", "global", "Protege una operación sintética irreversible.", moja=["**"]))
        config = Configuracion(**{**self.config.__dict__, "oceanos": 0})
        self.exigir("E12", config=config)

    def test_e13_adjunto_incorrecto(self) -> None:
        self.escribir("luna.md", documento("luna", "orbita-mal", "Representa un subagente unido al tipo equivocado.", orbita="trabajo"))
        self.exigir("E13")

    def test_e14_dos_estrellas(self) -> None:
        self.escribir("estrella-a.md", documento("estrella", "luz-a", "Aporta contexto sintético al modo de trabajo.", ilumina="trabajo"))
        self.escribir("estrella-b.md", documento("estrella", "luz-b", "Añade otra guía ficticia al mismo dominio.", ilumina="trabajo"))
        self.exigir("E14")

    def test_e15_indice_desincronizado(self) -> None:
        self.validar()
        self.indice.write_text("editado a mano\n", encoding="utf-8")
        resultado = self.validar(sincronizar=False)
        self.assertFalse(resultado.valido)
        self.assertIn("E15", resultado.codigos())

    def test_e16_presupuesto_superado(self) -> None:
        config = Configuracion(**{**self.config.__dict__, "entrada": 1})
        self.exigir("E16", config=config)

    def test_e16_usa_peor_nicho_aunque_el_caso_base_quepa(self) -> None:
        self.escribir("provincia.md", documento("provincia", "calidad", "Agrupa una capacidad web sintética.", padre="trabajo"))
        self.escribir(
            "pueblos/revisar/SKILL.md",
            documento(
                "pueblo",
                "revisar-web",
                "Comprueba una interfaz con múltiples condiciones reproducibles.",
                padre="trabajo/calidad",
            ),
        )
        arbol = cargar_arbol(self.raiz, excluir=self.indice)
        entrada_base = medir.medir_arbol(arbol, metodo="aprox", nichos=None).entrada
        entrada_peor = medir.medir_arbol(arbol, metodo="aprox", nichos=["trabajo"]).entrada
        self.assertLess(entrada_base, entrada_peor)
        config = Configuracion(**{**self.config.__dict__, "entrada": entrada_base})
        resultado = self.exigir("E16", config=config)
        mensaje = next(error.mensaje for error in resultado.errores if error.codigo == "E16")
        self.assertIn("trabajo", mensaje)
        self.assertIn(str(entrada_peor - entrada_base), mensaje)

    def test_e16_cuenta_el_agua_que_se_carga_por_paths(self) -> None:
        """H14: el mar no está en la entrada y se paga igual (NUCLEO §3).

        Con el presupuesto puesto exactamente en la entrada del peor nicho, sin
        contar el agua el árbol quedaba verde. Contándola, es rojo.
        """

        self.escribir("provincia.md", documento("provincia", "calidad", "Agrupa una capacidad sintética comprobable.", padre="trabajo"))
        self.escribir(
            "pueblos/revisar/SKILL.md",
            documento("pueblo", "revisar-web", "Comprueba una interfaz con condiciones reproducibles.", padre="trabajo/calidad"),
        )
        cuerpo_mar = " ".join(f"palabra{numero}" for numero in range(40))
        self.escribir("mar.md", documento("mar", "criterio", "Aplica una regla sintética a los ficheros de código.", cuerpo_mar, moja=[r"**/*.py"]))
        arbol = cargar_arbol(self.raiz, excluir=self.indice)
        casos = medir.medir_casos(arbol, metodo="aprox", presupuesto=4000)
        self.assertGreater(casos.peor.agua, 0, "el mar tiene que contarse como agua condicional")
        self.assertEqual(casos.peor.entrada + casos.peor.agua, casos.peor.entrada_con_agua)
        self.assertLessEqual(casos.peor.entrada_con_agua, casos.peor.universo)

        config = Configuracion(**{**self.config.__dict__, "entrada": casos.peor.entrada})
        resultado = self.exigir("E16", config=config)
        mensaje = next(error.mensaje for error in resultado.errores if error.codigo == "E16")
        self.assertIn("agua", mensaje)

        # «Holgado» = lo que E16 compara de verdad: la estimación MÁS el margen calibrado
        # (auditoría A-10). Con el presupuesto exactamente en la cifra estimada, E16 sigue
        # en rojo, y eso es lo correcto: una estimación sesgada a la baja no cabe por un pelo.
        justo = Configuracion(**{**self.config.__dict__, "entrada": casos.peor.entrada_con_agua})
        self.assertIn("E16", self.validar(config=justo).codigos(),
                      "el presupuesto puesto en la estimación desnuda tiene que seguir en rojo: falta el margen")
        con_margen = medir.veredicto_de_presupuesto(casos, casos.peor.entrada_con_agua).con_margen
        holgado = Configuracion(**{**self.config.__dict__, "entrada": con_margen})
        self.assertNotIn("E16", self.validar(config=holgado).codigos())

    def test_e17_parafrasis_en_contexto_permanente(self) -> None:
        primero = (
            "Antes de modificar archivos sensibles conserva una copia comprobable y registra la ruta de restauración. "
            "Si la comprobación falla detén el cambio y recupera el estado anterior sin continuar."
        )
        segundo = (
            "Para cambios delicados conserva una copia comprobable y registra la ruta de restauración. "
            "Cuando la comprobación falla detén el cambio y recupera el estado anterior antes de seguir."
        )
        self.escribir("oceano-a.md", documento("oceano", "respaldo", "Protege cambios sintéticos mediante restauración.", primero, moja=["**"]))
        self.escribir("oceano-b.md", documento("oceano", "recuperacion", "Detiene operaciones cuando falla una comprobación.", segundo, moja=["**"]))
        self.exigir("E17")

    def test_e17_parafrasis_entre_un_mar_y_una_estrella(self) -> None:
        """H12: E17 solo miraba océano contra océano, y con 4-gramas.

        Sobre la galaxia real daba 0,0000 en los diez pares. Este caso —una
        política repetida entre un mar y una estrella, que se pagan a la vez— era
        invisible dos veces: por alcance y por medida (NUCLEO §10).
        """

        del_mar = "Estar en el arbol de accesibilidad no es estar disponible: se exige tamano y visibilidad reales."
        de_la_estrella = "Lo que existe en el arbol del documento no es lo que se ve: se exige tamano y visibilidad reales."
        self.escribir("mar.md", documento("mar", "accesible", "Exige que la interfaz sintética se pueda usar de verdad.", del_mar, moja=[r"**/*.html"]))
        self.escribir("estrella.md", documento("estrella", "luz", "Aporta contexto sintético sobre interfaces.", de_la_estrella, ilumina="trabajo"))
        resultado = self.exigir("E17")
        mensaje = next(error.mensaje for error in resultado.errores if error.codigo == "E17")
        self.assertIn("mar/accesible", mensaje)
        self.assertIn("estrella/luz", mensaje)
        self.assertIn("visibilidad reales", mensaje)

    def test_verde_e17_una_analogia_no_es_una_duplicacion(self) -> None:
        """Dos frases con la misma forma y distinto contenido comparten 3 palabras."""

        self.escribir("mar.md", documento("mar", "medida", "Exige que la comprobación sintética haya dado rojo.", "Una comprobacion que nunca ha dado rojo no se distingue de una rota.", moja=[r"**/*.py"]))
        self.escribir("estrella.md", documento("estrella", "luz", "Aporta contexto sintético sobre respaldos.", "Una copia que nunca se ha restaurado no se distingue de un fichero.", ilumina="trabajo"))
        self.assertNotIn("E17", self.validar().codigos())

    def test_e18_colision_global_al_aplanar_y_rutas(self) -> None:
        self.escribir("provincia-a.md", documento("provincia", "grupo-a", "Agrupa capacidades sintéticas del primer tipo.", padre="trabajo"))
        self.escribir("provincia-b.md", documento("provincia", "grupo-b", "Agrupa capacidades sintéticas del segundo tipo.", padre="trabajo"))
        self.escribir("skills/a/revisar.md", documento("pueblo", "revisar", "Inspecciona una salida ficticia del primer grupo.", padre="trabajo/grupo-a"))
        self.escribir("skills/b/revisar.md", documento("pueblo", "revisar", "Inspecciona una salida ficticia del segundo grupo.", padre="trabajo/grupo-b"))
        resultado = self.exigir("E18")
        mensaje = next(error.mensaje for error in resultado.errores if error.codigo == "E18")
        self.assertIn("trabajo/grupo-a/revisar", mensaje)
        self.assertIn("trabajo/grupo-b/revisar", mensaje)

    def test_e19_vista_plana_desincronizada(self) -> None:
        self.escribir("provincia.md", documento("provincia", "grupo", "Agrupa una capacidad sintética invocable.", padre="trabajo"))
        self.escribir("skills/revisar/SKILL.md", documento("pueblo", "revisar", "Inspecciona una salida ficticia controlada.", padre="trabajo/grupo"))
        self.exigir("E19")


class PruebasValidadorComplementarias(unittest.TestCase):
    def test_ejemplo_completo_es_verde(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        # cosmos.toml pasa a apuntar al árbol real; el ejemplo tiene su propia
        # configuración desde el arreglo de H02. Esta prueba es la del ejemplo.
        config_path = repo / "ejemplo.toml"
        from cosmos.modelo import cargar_configuracion

        config = cargar_configuracion(config_path)
        arbol = cargar_arbol(config.arbol, excluir=config.indice)
        resultado = validador.validar_arbol(arbol, configuracion=config)
        self.assertTrue(resultado.valido, validador.formatear_validacion(resultado))

    def test_e17_no_compara_nodos_que_no_coinciden(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            contenido = "Conserva una copia comprobable registra restauración completa antes de modificar archivos delicados."
            archivos = {
                "galaxia.md": documento("galaxia", "raiz", "Organiza un árbol sintético de control."),
                "sistema.md": documento("sistema-solar", "modo", "Agrupa capacidades ficticias para comprobar alcance.", padre=""),
                "provincia.md": documento("provincia", "grupo", "Reúne dos capacidades atómicas de control.", padre="modo"),
                "uno.md": documento("pueblo", "primero", "Ejecuta la primera capacidad local de control.", contenido, padre="modo/grupo"),
                "dos.md": documento("pueblo", "segundo", "Ejecuta la segunda capacidad local de control.", contenido, padre="modo/grupo"),
            }
            for nombre, texto in archivos.items():
                (raiz / nombre).write_text(texto, encoding="utf-8")
            arbol = cargar_arbol(raiz)
            indice = raiz / "COSMOS.md"
            indice.write_text(generar_indice(arbol), encoding="utf-8")
            config = Configuracion(arbol=raiz, indice=indice, encontrada=True)
            resultado = validador.validar_arbol(arbol, configuracion=config)
            self.assertNotIn("E17", resultado.codigos())

    def test_identidad_completa_desambigua_provincias_homonimas(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            archivos = {
                "galaxia.md": documento("galaxia", "raiz", "Organiza un árbol sintético de identidad."),
                "sistema.md": documento("sistema-solar", "modo", "Agrupa proyectos ficticios de identidad.", padre=""),
                "planeta-a.md": documento("planeta", "uno", "Representa la primera rama ficticia.", padre="modo"),
                "planeta-b.md": documento("planeta", "dos", "Representa la segunda rama ficticia.", padre="modo"),
                "provincia-a.md": documento("provincia", "revision", "Agrupa referencias de la primera rama.", padre="modo/uno"),
                "provincia-b.md": documento("provincia", "revision", "Agrupa referencias de la segunda rama.", padre="modo/dos"),
                # Las hojas eran dos `casa` homónimas, y `casa` se retiró en H20. No se
                # sustituyen por pueblos: el único nivel que cuelga de una provincia es
                # `pueblo`, que se aplana, y dos pueblos homónimos son E18 —una colisión
                # real— mientras que dos provincias homónimas son legales. El sujeto del
                # test son ellas, y siguen aquí.
            }
            for nombre, texto in archivos.items():
                (raiz / nombre).write_text(texto, encoding="utf-8")
            arbol = cargar_arbol(raiz)
            indice = raiz / "COSMOS.md"
            indice.write_text(generar_indice(arbol), encoding="utf-8")
            config = Configuracion(arbol=raiz, indice=indice, encontrada=True)
            resultado = validador.validar_arbol(arbol, configuracion=config)
            self.assertTrue(resultado.valido, validador.formatear_validacion(resultado))
            self.assertEqual(1, len(arbol.buscar("modo/uno/revision")))
            self.assertEqual(1, len(arbol.buscar("modo/dos/revision")))
            self.assertNotEqual(
                arbol.buscar("modo/uno/revision")[0].ruta_relativa,
                arbol.buscar("modo/dos/revision")[0].ruta_relativa,
            )

    def test_validar_no_depende_de_que_exista_tokenizador(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            (raiz / "galaxia.md").write_text(documento("galaxia", "raiz", "Organiza un árbol sintético reproducible."), encoding="utf-8")
            arbol = cargar_arbol(raiz)
            indice = raiz / "COSMOS.md"
            indice.write_text(generar_indice(arbol), encoding="utf-8")
            config = Configuracion(arbol=raiz, indice=indice, metodo="aprox", encontrada=True)
            with mock.patch("cosmos.medir._contador_exacto", return_value=None):
                sin_tokenizador = validador.validar_arbol(arbol, configuracion=config)
            falso = (lambda texto: len(texto.encode("utf-8")), "tokenizador/falso")
            with mock.patch("cosmos.medir._contador_exacto", return_value=falso):
                con_tokenizador = validador.validar_arbol(arbol, configuracion=config)
            self.assertEqual(sin_tokenizador.errores, con_tokenizador.errores)
            self.assertEqual(sin_tokenizador.valido, con_tokenizador.valido)

    def test_meta_bateria_rechaza_validador_siempre_verde(self) -> None:
        # Solo las que EXIGEN un rojo. Las que comprueban que algo sigue en verde
        # (prefijo `test_verde_`) pasan con el mutante y deben pasar: exigirles un
        # fallo convertiría la meta-prueba en una mentira en sentido contrario.
        nombres = sorted(
            nombre
            for nombre in unittest.defaultTestLoader.getTestCaseNames(PruebasInvariantes)
            if re.fullmatch(r"test_e\d\d_.*", nombre)
        )
        suite = unittest.TestSuite(PruebasInvariantes(nombre) for nombre in nombres)
        with mock.patch.object(validador, "COMPROBACIONES", ()), mock.patch.object(validador, "formatear_validacion", return_value="COSMOS verde\n"):
            resultado = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
        # Un test con subTest deja un registro de fallo por subcaso: lo que hay que
        # contar son las pruebas distintas que se pusieron rojas, no los registros.
        rojas = {caso.id().split(" ")[0] for caso, _ in resultado.failures}
        self.assertEqual(len(nombres), resultado.testsRun)
        self.assertEqual(len(nombres), len(rojas), "el mutante siempre-verde no puso roja toda la batería")
        self.assertEqual([], resultado.errors)


class PruebasAciclicidad(unittest.TestCase):
    """El canario que sustituye a E04, y la meta-prueba que lo ve fallar.

    E04 se retiró porque ningún árbol legal puede disparar un ciclo (NUCLEO §1).
    Eso solo es cierto mientras la identidad de un sólido sea su ruta completa, y
    esa es la premisa que se vigila aquí: si alguien la cambia, los ciclos vuelven
    a ser posibles y la retirada deja de estar justificada.
    """

    @staticmethod
    def arbol_profundo(raiz: Path) -> object:
        archivos = {
            "galaxia.md": documento("galaxia", "raiz", "Organiza un árbol sintético profundo."),
            "sistema.md": documento("sistema-solar", "modo", "Agrupa proyectos ficticios encadenados.", padre=""),
            "planeta.md": documento("planeta", "uno", "Representa la primera rama ficticia.", padre="modo"),
            "provincia.md": documento("provincia", "revision", "Agrupa referencias de la rama ficticia.", padre="modo/uno"),
            "pueblo.md": documento("pueblo", "detalle", "Inspecciona una salida ficticia de la rama.", padre="modo/uno/revision"),
        }
        for nombre, texto in archivos.items():
            (raiz / nombre).write_text(texto, encoding="utf-8")
        return cargar_arbol(raiz)

    def test_canario_la_identidad_es_la_ruta_completa(self) -> None:
        """La ruta crece estrictamente al bajar, luego un ciclo se contradice.

        Es el paso que sostiene el teorema de NUCLEO §1: si `len(ruta(hijo)) >
        len(ruta(padre))` siempre, recorrer un ciclo devolvería la longitud a su
        punto de partida habiendo crecido. Imposible.
        """

        with tempfile.TemporaryDirectory() as temporal:
            arbol = self.arbol_profundo(Path(temporal))
        solidos = [
            nodo
            for nodo in arbol.nodos
            if nodo.cosmos in NIVELES_SOLIDOS and nodo.cosmos != "galaxia"
        ]
        self.assertEqual(4, len(solidos))
        for nodo in solidos:
            with self.subTest(nodo=nodo.nombre):
                self.assertGreater(
                    len(nodo.ruta_cosmos),
                    len(str(nodo.datos["padre"])),
                    "la identidad ha dejado de ser la ruta completa: los ciclos vuelven a ser posibles",
                )

    def test_meta_el_canario_de_aciclicidad_salta_si_la_identidad_cambia(self) -> None:
        """Una guarda que nunca se ha visto fallar es decorativa.

        Se sustituye la identidad por la que usaba el test falso de E04 —un campo
        cualquiera en vez de la ruta— y se exige que el canario se ponga rojo.
        """

        suite = unittest.TestSuite([PruebasAciclicidad("test_canario_la_identidad_es_la_ruta_completa")])
        identidad_plana = property(lambda self: "" if self.cosmos == "galaxia" else self.nombre)
        with mock.patch.object(Nodo, "ruta_cosmos", identidad_plana):
            resultado = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
        self.assertEqual([], resultado.errors)
        self.assertEqual(
            3,
            len(resultado.failures),
            "el canario no vio caer la identidad por ruta completa: con la ruta plana, "
            "los tres sólidos anidados dejan de crecer respecto de su padre",
        )


if __name__ == "__main__":
    unittest.main()
