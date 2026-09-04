from __future__ import annotations

import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from cosmos.cli import ejecutar
from cosmos.compilar import ErrorCompilacion, compilar_arbol
from cosmos.generar import generar_indice
from cosmos.modelo import cargar_arbol, cargar_configuracion
from cosmos.validar import validar_arbol


def documento(cosmos: str, nombre: str, resumen: str, cuerpo: str = "Contenido específico.", **campos: object) -> str:
    lineas = ["---", f"cosmos: {cosmos}", f"nombre: {nombre}", f"resumen: {resumen}"]
    # Un pueblo tiene que nombrar qué ejecutar (E21): estas skills sintéticas son propias,
    # así que lo declaran con `origen: propio` y un bloque de código, como cualquier pueblo real.
    for clave, valor in campos.items():
        if isinstance(valor, list):
            lineas.append(f'{clave}: [{", ".join(f"{item!r}" for item in valor)}]')
        elif valor == "":
            lineas.append(f'{clave}: ""')
        else:
            lineas.append(f"{clave}: {valor}")
    if cosmos == "pueblo" and "github.com" not in cuerpo:
        cuerpo = f"https://github.com/pruebas-sinteticas/{nombre} · MIT · 0★ · último push 2026-01-01 (comprobado 2026-01-01)\n\n" + cuerpo
    if cosmos == "pueblo" and "```" not in cuerpo:
        cuerpo = cuerpo + "\n\n```bash\npython3 -m cosmos abrir " + nombre + "\n```"
    return "\n".join(lineas + ["---", "", cuerpo, ""])


class PruebasCompilacion(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory()
        self.raiz_repo = Path(self.temporal.name)
        self.arbol_dir = self.raiz_repo / "arbol"
        self.skill_dir = self.arbol_dir / "skills" / "revisar"
        self.skill_dir.mkdir(parents=True)
        archivos = {
            self.arbol_dir / "galaxia.md": documento("galaxia", "raiz", "Organiza un arbol sintetico compilable."),
            self.arbol_dir / "sistema.md": documento("sistema-solar", "modo", "Agrupa capacidades ficticias compilables.", padre=""),
            self.arbol_dir / "provincia.md": documento("provincia", "grupo", "Agrupa una capacidad ficticia invocable.", padre="modo"),
            self.skill_dir / "SKILL.md": documento("pueblo", "revisar", "Inspecciona una salida sintetica controlada.", padre="modo/grupo"),
            # Un fichero de referencia dentro de la skill NO es un nodo (`casa` se
            # retiró en H20): es un fichero suelto que el pueblo abre cuando lo
            # necesita. Aquí se comprueba que `compilar` lo exporta igual.
            self.skill_dir / "referencia.md": "# Referencia interna\n\nDatos que la skill abre cuando hacen falta.\n",
        }
        for ruta, contenido in archivos.items():
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_text(contenido, encoding="utf-8")
        (self.skill_dir / ".oculto").write_text("no copiar\n", encoding="utf-8")
        (self.skill_dir / "__pycache__").mkdir()
        (self.skill_dir / "__pycache__" / "cache.pyc").write_bytes(b"cache")
        self.config_path = self.raiz_repo / "cosmos.toml"
        self.config_path.write_text(
            """[presupuesto]
entrada = 4000
resumen = 120
oceanos = 7
galaxia_lineas = 40
solapamiento = 0.25

[raiz]
arbol = "arbol"
indice = "arbol/COSMOS.md"

[medicion]
metodo = "aprox"

[compilacion]
destino = "plano"
modo = "copia"
manifiesto = ".cosmos/compilado.json"
""",
            encoding="utf-8",
        )
        self.sincronizar_indice()

    def tearDown(self) -> None:
        self.temporal.cleanup()

    @property
    def destino(self) -> Path:
        return self.raiz_repo / "plano"

    @property
    def manifiesto(self) -> Path:
        return self.raiz_repo / ".cosmos" / "compilado.json"

    def arbol(self):
        return cargar_arbol(self.arbol_dir, excluir=self.arbol_dir / "COSMOS.md", excluir_directorios=(self.destino,))

    def sincronizar_indice(self) -> None:
        arbol = cargar_arbol(self.arbol_dir, excluir=self.arbol_dir / "COSMOS.md")
        (self.arbol_dir / "COSMOS.md").write_text(generar_indice(arbol), encoding="utf-8")

    def compilar(self, *, modo: str = "copia", seco: bool = False):
        return compilar_arbol(
            self.arbol(),
            destino=self.destino,
            manifiesto=self.manifiesto,
            modo=modo,
            seco=seco,
            config_path=self.config_path,
        )

    def cli(self, *argumentos: str) -> tuple[int, str]:
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
            codigo = ejecutar([*argumentos, "--config", str(self.config_path)])
        return codigo, salida.getvalue()

    def test_arbol_invalido_no_escribe_en_destino(self) -> None:
        (self.skill_dir / "SKILL.md").write_text(
            documento("pueblo", "revisar", "Inspecciona una salida sintetica controlada.", padre="modo/ausente"),
            encoding="utf-8",
        )
        self.sincronizar_indice()
        codigo, salida = self.cli("compilar")
        self.assertEqual(1, codigo)
        self.assertIn("E02", salida)
        self.assertFalse(self.destino.exists())
        self.assertFalse(self.manifiesto.exists())

    def test_idempotencia_segunda_compilacion_no_cambia(self) -> None:
        primera = self.compilar()
        manifiesto_antes = self.manifiesto.read_bytes()
        segunda = self.compilar()
        self.assertEqual(1, primera.creadas)
        self.assertEqual((0, 0, 1), (segunda.creadas, segunda.actualizadas, segunda.iguales))
        self.assertEqual(manifiesto_antes, self.manifiesto.read_bytes())

    def test_fichero_ajeno_sobrevive_y_se_reporta(self) -> None:
        self.destino.mkdir()
        ajeno = self.destino / "manual.txt"
        ajeno.write_text("conservar\n", encoding="utf-8")
        resultado = self.compilar()
        self.assertEqual(1, resultado.ajenas)
        self.assertEqual("conservar\n", ajeno.read_text(encoding="utf-8"))

    def test_la_vista_huerfana_identica_se_adopta_y_e19_sana(self) -> None:
        """B03: borrar `.cosmos/` (generado, gitignored) dejaba el repo en un callejón.

        Sin manifiesto, `compilar` clasificaba SUS PROPIAS entradas como ajenas y las
        respetaba para siempre; E19 recetaba «ejecuta cosmos compilar», y compilar no
        hacía nada — el único camino de vuelta era borrar a mano lo que el mensaje
        prohíbe tocar a mano. Una entrada idéntica byte a byte a lo que se crearía no
        tiene nada ajeno que perder: se adopta, y la receta del error vuelve a curar.
        """

        self.compilar()
        contenido_antes = (self.destino / "revisar" / "SKILL.md").read_text(encoding="utf-8")
        shutil.rmtree(self.manifiesto.parent)  # el estado que deja «limpiar lo generado»

        resultado = self.compilar()

        self.assertEqual(1, resultado.adoptadas, "la entrada huérfana idéntica no se adoptó")
        self.assertEqual(0, resultado.ajenas)
        self.assertEqual(contenido_antes, (self.destino / "revisar" / "SKILL.md").read_text(encoding="utf-8"))
        config = cargar_configuracion(self.config_path)
        self.assertNotIn("E19", validar_arbol(self.arbol(), configuracion=config).codigos(),
                         "tras seguir la receta del error, E19 sigue en rojo: el callejón vive")

    def test_la_huerfana_divergente_sigue_siendo_ajena(self) -> None:
        """La adopción exige identidad de hash: lo editado a mano no se apropia ni se pisa."""

        self.compilar()
        shutil.rmtree(self.manifiesto.parent)
        (self.destino / "revisar" / "SKILL.md").write_text("editado por otro\n", encoding="utf-8")

        resultado = self.compilar()

        self.assertEqual(0, resultado.adoptadas)
        self.assertEqual(1, resultado.ajenas)
        self.assertEqual("editado por otro\n",
                         (self.destino / "revisar" / "SKILL.md").read_text(encoding="utf-8"))
        config = cargar_configuracion(self.config_path)
        self.assertIn("E19", validar_arbol(self.arbol(), configuracion=config).codigos(),
                      "una vista divergente sin manifiesto tiene que seguir cantando E19")

    def test_el_manifiesto_conserva_sus_permisos_al_reescribirse(self) -> None:
        """A01/B04: el arreglo de permisos solo valía para el 50 % de los escritores.

        `escribir_atomico` (modelo) aprendió a conservar el modo del destino; la copia
        byte a byte que usaba `compilar` para el manifiesto, no — cada recompilación lo
        estrechaba a 0600. Dos escritores idénticos garantizan que la corrección llega
        a uno; ahora hay uno solo y esta prueba lo mide donde dolía.
        """

        self.compilar()
        self.manifiesto.chmod(0o644)
        antes = self.manifiesto.read_bytes()
        (self.skill_dir / "referencia.md").write_text("# Referencia cambiada\n", encoding="utf-8")
        self.compilar()
        self.assertNotEqual(antes, self.manifiesto.read_bytes(),
                            "el manifiesto no se reescribió: la prueba no midió nada")
        self.assertEqual(0o644, self.manifiesto.stat().st_mode & 0o777,
                         "reescribir el manifiesto volvió a estrechar sus permisos")

    def test_editar_copia_a_mano_produce_e19(self) -> None:
        self.compilar()
        (self.destino / "revisar" / "SKILL.md").write_text("editado a mano\n", encoding="utf-8")
        config = cargar_configuracion(self.config_path)
        resultado = validar_arbol(self.arbol(), configuracion=config)
        self.assertIn("E19", resultado.codigos())

    def test_seco_no_escribe_y_anuncia_lo_que_hace_luego(self) -> None:
        seco = self.compilar(seco=True)
        self.assertFalse(self.destino.exists())
        self.assertFalse(self.manifiesto.exists())
        real = self.compilar()
        self.assertEqual(
            (seco.creadas, seco.actualizadas, seco.iguales, seco.ajenas, seco.eliminadas, seco.preservadas, seco.acciones),
            (real.creadas, real.actualizadas, real.iguales, real.ajenas, real.eliminadas, real.preservadas, real.acciones),
        )

    def test_modo_copia_exporta_directorio_y_no_deja_symlinks(self) -> None:
        self.compilar(modo="copia")
        entrada = self.destino / "revisar"
        self.assertTrue((entrada / "SKILL.md").is_file())
        self.assertTrue((entrada / "referencia.md").is_file())
        self.assertFalse((entrada / ".oculto").exists())
        self.assertFalse((entrada / "__pycache__").exists())
        self.assertFalse(any(ruta.is_symlink() for ruta in entrada.rglob("*")))

    def test_obsoleta_intacta_se_borra_por_hash(self) -> None:
        self.compilar()
        shutil.rmtree(self.skill_dir)
        self.sincronizar_indice()
        resultado = self.compilar()
        self.assertEqual(1, resultado.eliminadas)
        self.assertFalse((self.destino / "revisar").exists())

    def test_obsoleta_modificada_se_preserva_y_sale_del_manifiesto(self) -> None:
        self.compilar()
        copia = self.destino / "revisar"
        (copia / "manual.txt").write_text("trabajo ajeno\n", encoding="utf-8")
        shutil.rmtree(self.skill_dir)
        self.sincronizar_indice()
        resultado = self.compilar()
        self.assertEqual(1, resultado.preservadas)
        self.assertTrue((copia / "manual.txt").exists())
        self.assertNotIn('"revisar"', self.manifiesto.read_text(encoding="utf-8"))

    def test_compilar_nicho_aplana_solo_web_y_aplica_hash_a_otros_nichos(self) -> None:
        web = self.arbol_dir / "skills" / "web-only"
        saas = self.arbol_dir / "skills" / "saas-only"
        archivos = {
            self.arbol_dir / "web.md": documento("sistema-solar", "web", "Agrupa capacidades web sinteticas.", padre=""),
            self.arbol_dir / "saas.md": documento("sistema-solar", "saas", "Agrupa capacidades SaaS sinteticas.", padre=""),
            self.arbol_dir / "web-provincia.md": documento("provincia", "calidad-web", "Agrupa una capacidad web invocable.", padre="web"),
            self.arbol_dir / "saas-provincia.md": documento("provincia", "calidad-saas", "Agrupa una capacidad SaaS invocable.", padre="saas"),
            web / "SKILL.md": documento("pueblo", "web-only", "Comprueba una interfaz web sintetica.", padre="web/calidad-web"),
            saas / "SKILL.md": documento("pueblo", "saas-only", "Comprueba un servicio SaaS sintetico.", padre="saas/calidad-saas"),
        }
        for ruta, contenido in archivos.items():
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_text(contenido, encoding="utf-8")
        self.sincronizar_indice()
        self.compilar()
        (self.destino / "saas-only" / "manual.txt").write_text("trabajo ajeno\n", encoding="utf-8")

        resultado = compilar_arbol(
            self.arbol(),
            destino=self.destino,
            manifiesto=self.manifiesto,
            modo="copia",
            nichos=["web"],
            config_path=self.config_path,
        )

        self.assertTrue((self.destino / "web-only" / "SKILL.md").is_file())
        self.assertFalse((self.destino / "revisar").exists(), "la entrada intacta de otro nicho era obsoleta propia")
        self.assertTrue((self.destino / "saas-only" / "manual.txt").is_file(), "la entrada modificada de otro nicho es trabajo ajeno")
        manifiesto = self.manifiesto.read_text(encoding="utf-8")
        self.assertIn('"web-only"', manifiesto)
        self.assertNotIn('"saas-only"', manifiesto)
        self.assertEqual((1, 1), (resultado.eliminadas, resultado.preservadas))

        codigo, salida = self.cli("validar", "--nicho", "web")
        self.assertEqual(0, codigo, salida)
        codigo, salida = self.cli("validar")
        self.assertEqual(1, codigo)
        self.assertIn("E19", salida, "la vista acotada no puede validarse como si fuera completa")
        codigo, salida = self.cli("compilar", "--nicho", "web")
        self.assertEqual(0, codigo, salida)
        self.assertIn("iguales 1", salida)

    def test_compilar_repara_e19_sin_interbloqueo(self) -> None:
        self.compilar()
        (self.destino / "revisar" / "SKILL.md").write_text("desincronizado\n", encoding="utf-8")
        config = cargar_configuracion(self.config_path)
        self.assertIn("E19", validar_arbol(self.arbol(), configuracion=config).codigos())
        codigo, salida = self.cli("compilar")
        self.assertEqual(0, codigo, salida)
        self.assertIn("actualizadas 1", salida)
        self.assertNotIn("E19", validar_arbol(self.arbol(), configuracion=config).codigos())

    def test_generar_repara_e15_y_no_lo_bloquea_una_e19_que_no_puede_reparar(self) -> None:
        """F11: cada comando se eximía de SU invariante, no de la del otro.

        `generar` exigía E19 y `compilar` exigía E15, así que cada uno mandaba al
        otro y un árbol nuevo no tenía camino a verde. `generar` no escribe la
        vista plana: no puede repararla ni romperla, y por tanto no puede quedar
        bloqueado por ella. Lo que sí sigue en rojo es `validar`, que las exige
        todas — el rojo se ve, solo deja de secuestrar al comando equivocado.
        """

        self.compilar()
        indice = self.arbol_dir / "COSMOS.md"
        indice.write_text("desincronizado\n", encoding="utf-8")
        codigo, salida = self.cli("generar")
        self.assertEqual(0, codigo, salida)
        self.assertEqual(generar_indice(self.arbol()), indice.read_text(encoding="utf-8"))

        indice.write_text("desincronizado otra vez\n", encoding="utf-8")
        (self.destino / "revisar" / "SKILL.md").write_text("vista rota\n", encoding="utf-8")
        codigo, salida = self.cli("generar")
        self.assertEqual(0, codigo, salida)
        self.assertEqual(generar_indice(self.arbol()), indice.read_text(encoding="utf-8"))
        codigo, salida = self.cli("validar")
        self.assertEqual(1, codigo)
        self.assertIn("E19", salida)

    def test_generar_no_declara_verde_sin_revalidar_lo_que_acaba_de_escribir(self) -> None:
        """F07: desactivar la revalidación posterior no ponía roja ni una prueba.

        Se dobla el borde más externo —quien escribe el fichero— y se comprueba que
        `generar` NO dice verde con un índice que sigue sin cuadrar. Sin el paso
        posterior, la única señal de que el índice escrito vale desaparece.
        """

        self.sincronizar_indice()
        self.compilar()
        with mock.patch(
            "cosmos.cli.escribir_indice",
            side_effect=lambda arbol, ruta: Path(ruta).write_text("indice que miente\n", encoding="utf-8"),
        ):
            codigo, salida = self.cli("generar")
        self.assertEqual(1, codigo, salida)
        self.assertIn("E15", salida)
        self.assertNotIn("generar  verde", salida)

    def test_un_arbol_nuevo_llega_a_verde_con_un_solo_arrancar(self) -> None:
        """F11: el caso que GOAL §1 vende — clonar COSMOS sobre otro proyecto.

        Ni índice ni vista plana. Antes: `validar` rojo por E15 y E19, `generar`
        rojo por E19, `compilar` rojo por E15 y `arrancar` rojo por E15. Sin salida.
        """

        indice = self.arbol_dir / "COSMOS.md"
        indice.unlink(missing_ok=True)
        shutil.rmtree(self.destino, ignore_errors=True)
        self.manifiesto.unlink(missing_ok=True)

        codigo, salida = self.cli("validar")
        self.assertEqual(1, codigo, "el punto de partida es un árbol nuevo en rojo")

        codigo, salida = self.cli("arrancar")
        self.assertEqual(0, codigo, salida)
        self.assertIn("arrancar  verde", salida)
        self.assertEqual(0, self.cli("validar")[0])

    def test_arrancar_no_repara_un_indice_que_existe_y_miente(self) -> None:
        """La contrapartida: `arrancar` escribe el índice que FALTA, no el que miente.

        Un índice ausente no puede engañar a nadie; uno presente y falso sí, y ahí
        E15 tiene que seguir siendo un rojo de verdad — si no, el bootstrap se
        convertiría en una forma de tapar el fallo que E15 existe para cazar.
        """

        self.sincronizar_indice()
        self.compilar()
        (self.arbol_dir / "COSMOS.md").write_text("# COSMOS — mentira\n", encoding="utf-8")
        codigo, salida = self.cli("arrancar")
        self.assertEqual(1, codigo)
        self.assertIn("E15", salida)
        self.assertEqual("# COSMOS — mentira\n", (self.arbol_dir / "COSMOS.md").read_text(encoding="utf-8"))

    def test_lock_de_un_proceso_vivo_rechaza_la_segunda_compilacion(self) -> None:
        """El contrato cambió a propósito (F09), y esta prueba lo dice.

        Antes bastaba con que el fichero existiera, con cualquier contenido. Eso
        significaba que un proceso muerto sin llegar a su `finally` —`kill -9`, batería,
        terminal cerrada— dejaba el repositorio sin poder compilar **para siempre**. Ahora
        el cerrojo lleva dentro el PID y se pregunta: si su dueño vive, esto rechaza; si
        no, se retoma. Un cerrojo del que no se puede salir no protege nada.
        """

        import os

        lock = self.manifiesto.parent / "compilar.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text(f"{os.getppid()}\n", encoding="utf-8")  # un PID que existe de verdad
        with self.assertRaisesRegex(ErrorCompilacion, "en curso"):
            self.compilar()
        self.assertFalse(self.destino.exists())

    def test_un_lock_rancio_no_deja_el_repositorio_inservible(self) -> None:
        lock = self.manifiesto.parent / "compilar.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text("999999\n", encoding="utf-8")  # PID que no existe
        self.compilar()
        self.assertTrue(self.destino.exists(), "un cerrojo rancio bloqueó una compilación válida")
        self.assertFalse(lock.exists())

    def test_editar_por_symlink_edita_la_verdad_y_no_rompe_e19(self) -> None:
        self.compilar(modo="symlink")
        enlace = self.destino / "revisar"
        self.assertTrue(enlace.is_symlink())
        (enlace / "nota.txt").write_text("verdad compartida\n", encoding="utf-8")
        self.assertEqual("verdad compartida\n", (self.skill_dir / "nota.txt").read_text(encoding="utf-8"))
        config = cargar_configuracion(self.config_path)
        config = type(config)(**{**config.__dict__, "modo_compilacion": "symlink"})
        self.assertNotIn("E19", validar_arbol(self.arbol(), configuracion=config).codigos())


if __name__ == "__main__":
    unittest.main()
