from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import cosmos.validar as validador
from cosmos.generar import generar_indice
from cosmos.modelo import Configuracion, cargar_arbol


def documento(cosmos: str, nombre: str, resumen: str, cuerpo: str = "Contenido específico del nodo.", **campos: object) -> str:
    lineas = ["---", f"cosmos: {cosmos}", f"nombre: {nombre}", f"resumen: {resumen}"]
    for clave, valor in campos.items():
        if isinstance(valor, list):
            elementos = ", ".join(f'"{item}"' for item in valor)
            lineas.append(f"{clave}: [{elementos}]")
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
            documento("sistema-solar", "trabajo", "Agrupa un modo ficticio de trabajo.", padre="galaxia/raiz"),
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
        self.escribir("sin-padre.md", documento("planeta", "perdido", "Representa un proyecto sintético aislado.", padre="sistema-solar/ausente"))
        self.exigir("E02")

    def test_e03_contencion_invertida(self) -> None:
        self.escribir("planeta.md", documento("planeta", "proyecto", "Representa un encargo ficticio comprobable.", padre="galaxia/raiz"))
        self.escribir("sistema.md", documento("sistema-solar", "trabajo", "Agrupa un modo ficticio de trabajo.", padre="planeta/proyecto"))
        self.exigir("E03")

    def test_e04_ciclo(self) -> None:
        self.escribir("sistema.md", documento("sistema-solar", "trabajo", "Agrupa un modo ficticio de trabajo.", padre="planeta/proyecto"))
        self.escribir("planeta.md", documento("planeta", "proyecto", "Representa un encargo ficticio comprobable.", padre="sistema-solar/trabajo"))
        self.exigir("E04")

    def test_e05_varias_galaxias(self) -> None:
        self.escribir("otra-galaxia.md", documento("galaxia", "otra-raiz", "Organiza una instalación sintética alternativa."))
        self.exigir("E05")

    def test_e06_hermanos_homonimos(self) -> None:
        contenido = documento("planeta", "duplicado", "Representa un encargo sintético con final definido.", padre="sistema-solar/trabajo")
        self.escribir("uno.md", contenido)
        self.escribir("dos.md", contenido)
        self.exigir("E06")

    def test_e07_resumen_demasiado_largo(self) -> None:
        self.escribir("largo.md", documento("planeta", "extenso", "x" * 121, padre="sistema-solar/trabajo"))
        self.exigir("E07")

    def test_e08_resumen_no_informa(self) -> None:
        self.escribir("vacio.md", documento("planeta", "demo", "la skill de demo", padre="sistema-solar/trabajo"))
        self.exigir("E08")

    def test_e09_nivel_desconocido(self) -> None:
        self.escribir("nivel.md", documento("asteroide", "roca", "Representa un nivel que no pertenece al esquema."))
        self.exigir("E09")

    def test_e10_agua_sin_alcance(self) -> None:
        self.escribir("mar.md", documento("mar", "regional", "Aplica una regla sintética a una región.", moja=[]))
        self.exigir("E10")

    def test_e11_oceano_encubierto(self) -> None:
        self.escribir("mar.md", documento("mar", "global-disfrazado", "Simula una regla regional demasiado amplia.", moja=["**"]))
        self.exigir("E11")

    def test_e12_exceso_de_oceanos(self) -> None:
        self.escribir("oceano.md", documento("oceano", "global", "Protege una operación sintética irreversible.", moja=["**"]))
        config = Configuracion(**{**self.config.__dict__, "oceanos": 0})
        self.exigir("E12", config=config)

    def test_e13_adjunto_incorrecto(self) -> None:
        self.escribir("luna.md", documento("luna", "orbita-mal", "Representa un subagente unido al tipo equivocado.", orbita="sistema-solar/trabajo"))
        self.exigir("E13")

    def test_e14_dos_estrellas(self) -> None:
        self.escribir("estrella-a.md", documento("estrella", "luz-a", "Aporta contexto sintético al modo de trabajo.", ilumina="sistema-solar/trabajo"))
        self.escribir("estrella-b.md", documento("estrella", "luz-b", "Añade otra guía ficticia al mismo dominio.", ilumina="sistema-solar/trabajo"))
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

    def test_e18_colision_global_al_aplanar_y_rutas(self) -> None:
        self.escribir("provincia-a.md", documento("provincia", "grupo-a", "Agrupa capacidades sintéticas del primer tipo.", padre="sistema-solar/trabajo"))
        self.escribir("provincia-b.md", documento("provincia", "grupo-b", "Agrupa capacidades sintéticas del segundo tipo.", padre="sistema-solar/trabajo"))
        self.escribir("skills/a/revisar.md", documento("pueblo", "revisar", "Inspecciona una salida ficticia del primer grupo.", padre="provincia/grupo-a"))
        self.escribir("skills/b/revisar.md", documento("pueblo", "revisar", "Inspecciona una salida ficticia del segundo grupo.", padre="provincia/grupo-b"))
        resultado = self.exigir("E18")
        mensaje = next(error.mensaje for error in resultado.errores if error.codigo == "E18")
        self.assertIn("skills/a/revisar.md", mensaje)
        self.assertIn("skills/b/revisar.md", mensaje)


class PruebasValidadorComplementarias(unittest.TestCase):
    def test_ejemplo_completo_es_verde(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        config_path = repo / "cosmos.toml"
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
                "sistema.md": documento("sistema-solar", "modo", "Agrupa capacidades ficticias para comprobar alcance.", padre="galaxia/raiz"),
                "provincia.md": documento("provincia", "grupo", "Reúne dos capacidades atómicas de control.", padre="sistema-solar/modo"),
                "uno.md": documento("pueblo", "primero", "Ejecuta la primera capacidad local de control.", contenido, padre="provincia/grupo"),
                "dos.md": documento("pueblo", "segundo", "Ejecuta la segunda capacidad local de control.", contenido, padre="provincia/grupo"),
            }
            for nombre, texto in archivos.items():
                (raiz / nombre).write_text(texto, encoding="utf-8")
            arbol = cargar_arbol(raiz)
            indice = raiz / "COSMOS.md"
            indice.write_text(generar_indice(arbol), encoding="utf-8")
            config = Configuracion(arbol=raiz, indice=indice, encontrada=True)
            resultado = validador.validar_arbol(arbol, configuracion=config)
            self.assertNotIn("E17", resultado.codigos())

    def test_meta_bateria_rechaza_validador_siempre_verde(self) -> None:
        nombres = sorted(nombre for nombre in unittest.defaultTestLoader.getTestCaseNames(PruebasInvariantes) if nombre.startswith("test_e"))
        suite = unittest.TestSuite(PruebasInvariantes(nombre) for nombre in nombres)
        with mock.patch.object(validador, "COMPROBACIONES", ()), mock.patch.object(validador, "formatear_validacion", return_value="COSMOS verde\n"):
            resultado = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
        self.assertEqual(19, resultado.testsRun)
        self.assertEqual(19, len(resultado.failures), "el mutante siempre-verde no puso roja toda la batería")
        self.assertEqual([], resultado.errors)


if __name__ == "__main__":
    unittest.main()
