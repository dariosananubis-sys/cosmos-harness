from __future__ import annotations

import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from cosmos.cli import ejecutar
from cosmos.compilar import ErrorCompilacion, compilar_arbol
from cosmos.generar import generar_indice
from cosmos.modelo import cargar_arbol, cargar_configuracion
from cosmos.validar import validar_arbol


def documento(cosmos: str, nombre: str, resumen: str, cuerpo: str = "Contenido específico.", **campos: object) -> str:
    lineas = ["---", f"cosmos: {cosmos}", f"nombre: {nombre}", f"resumen: {resumen}"]
    for clave, valor in campos.items():
        if isinstance(valor, list):
            lineas.append(f'{clave}: [{", ".join(f"{item!r}" for item in valor)}]')
        elif valor == "":
            lineas.append(f'{clave}: ""')
        else:
            lineas.append(f"{clave}: {valor}")
    return "\n".join(lineas + ["---", "", cuerpo, ""])


class PruebasCompilacion(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory()
        self.raiz_repo = Path(self.temporal.name)
        self.arbol_dir = self.raiz_repo / "arbol"
        self.skill_dir = self.arbol_dir / "skills" / "revisar"
        self.skill_dir.mkdir(parents=True)
        archivos = {
            self.arbol_dir / "galaxia.md": documento("galaxia", "raiz", "Organiza un árbol sintético compilable."),
            self.arbol_dir / "sistema.md": documento("sistema-solar", "modo", "Agrupa capacidades ficticias compilables.", padre=""),
            self.arbol_dir / "provincia.md": documento("provincia", "grupo", "Agrupa una capacidad ficticia invocable.", padre="modo"),
            self.skill_dir / "SKILL.md": documento("pueblo", "revisar", "Inspecciona una salida sintética controlada.", padre="modo/grupo"),
            self.skill_dir / "referencia.md": documento("casa", "referencia", "Documenta una referencia interna de la skill.", padre="modo/grupo/revisar"),
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
            documento("pueblo", "revisar", "Inspecciona una salida sintética controlada.", padre="modo/ausente"),
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

    def test_compilar_repara_e19_sin_interbloqueo(self) -> None:
        self.compilar()
        (self.destino / "revisar" / "SKILL.md").write_text("desincronizado\n", encoding="utf-8")
        config = cargar_configuracion(self.config_path)
        self.assertIn("E19", validar_arbol(self.arbol(), configuracion=config).codigos())
        codigo, salida = self.cli("compilar")
        self.assertEqual(0, codigo, salida)
        self.assertIn("actualizadas 1", salida)
        self.assertNotIn("E19", validar_arbol(self.arbol(), configuracion=config).codigos())

    def test_generar_repara_e15_pero_no_ignora_e19(self) -> None:
        self.compilar()
        indice = self.arbol_dir / "COSMOS.md"
        indice.write_text("desincronizado\n", encoding="utf-8")
        codigo, salida = self.cli("generar")
        self.assertEqual(0, codigo, salida)
        self.assertEqual(generar_indice(self.arbol()), indice.read_text(encoding="utf-8"))

        indice.write_text("desincronizado otra vez\n", encoding="utf-8")
        (self.destino / "revisar" / "SKILL.md").write_text("vista rota\n", encoding="utf-8")
        codigo, salida = self.cli("generar")
        self.assertEqual(1, codigo)
        self.assertIn("E19", salida)
        self.assertEqual("desincronizado otra vez\n", indice.read_text(encoding="utf-8"))

    def test_lock_exclusivo_rechaza_segunda_compilacion(self) -> None:
        lock = self.manifiesto.parent / "compilar.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text("ocupado\n", encoding="utf-8")
        with self.assertRaisesRegex(ErrorCompilacion, "otra compilación"):
            self.compilar()
        self.assertFalse(self.destino.exists())

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
