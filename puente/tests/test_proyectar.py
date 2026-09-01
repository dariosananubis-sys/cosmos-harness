"""Proyectar sobre un repo ajeno: no pisar nada suyo, y no cambiar nada dos veces."""

from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path

from puente.proyectar import (
    FIN,
    INICIO,
    ErrorProyeccion,
    bloque,
    cargar_contrato,
    problemas,
    pueblos_fuente,
    raiz_del_planeta,
    sincronizar,
)
from puente.tests.comun import CONTRATO, arbol_minimo, configuracion, repo_git

AJENO = "# Instrucciones del equipo\n\nEsto lo escribió una persona y no se toca.\n"


def foto(raiz: Path) -> dict[str, tuple[bytes, int]]:
    return {
        ruta.relative_to(raiz).as_posix(): (ruta.read_bytes(), stat.S_IMODE(ruta.stat().st_mode))
        for ruta in sorted(raiz.rglob("*"))
        if ruta.is_file() and ".git/" not in ruta.relative_to(raiz).as_posix()
    }


class Proyeccion(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="puente-proyectar-")
        base = Path(self.temporal.name)
        self.origen = base / "cosmos"
        self.origen.mkdir()
        self.arbol = arbol_minimo(self.origen)
        self.config = configuracion(self.origen)
        self.destino = repo_git(base / "planeta")
        (self.destino / "planeta.toml").write_text(CONTRATO, encoding="utf-8")
        self.contrato = cargar_contrato(self.destino, self.arbol)

    def tearDown(self) -> None:
        self.temporal.cleanup()

    # ------------------------------------------------------------------ lo ajeno

    def test_no_sobrescribe_una_skill_ajena(self) -> None:
        ajena = self.destino / ".claude" / "skills" / "medir-anchos"
        ajena.mkdir(parents=True)
        (ajena / "SKILL.md").write_text("Skill de otro equipo.\n", encoding="utf-8")
        antes = foto(self.destino)

        with self.assertRaises(ErrorProyeccion) as capturado:
            sincronizar(self.destino, self.contrato, self.arbol, self.config)

        self.assertIn("ajeno", str(capturado.exception))
        self.assertEqual(foto(self.destino), antes, "la proyección tocó el repo ajeno")

    def test_conserva_el_texto_de_fuera_de_los_marcadores(self) -> None:
        (self.destino / "CLAUDE.md").write_text(AJENO, encoding="utf-8")
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        texto = (self.destino / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn(AJENO.strip(), texto)
        self.assertIn(INICIO, texto)
        self.assertLess(texto.index(AJENO.strip()), texto.index(INICIO))

    def test_conserva_las_claves_ajenas_de_settings(self) -> None:
        ajustes = self.destino / ".claude" / "settings.json"
        ajustes.parent.mkdir(parents=True)
        ajustes.write_text(json.dumps({"model": "propio", "autoMemoryEnabled": True}), encoding="utf-8")
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        actuales = json.loads(ajustes.read_text(encoding="utf-8"))
        self.assertEqual(actuales["model"], "propio")
        self.assertFalse(actuales["autoMemoryEnabled"])

    def test_un_fichero_ajeno_cualquiera_sobrevive(self) -> None:
        (self.destino / "README.md").write_text(AJENO, encoding="utf-8")
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        self.assertEqual((self.destino / "README.md").read_text(encoding="utf-8"), AJENO)

    # --------------------------------------------------------------- idempotencia

    def test_la_segunda_proyeccion_no_cambia_nada(self) -> None:
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        primera = foto(self.destino)
        self.assertEqual(problemas(self.destino, self.contrato, self.arbol, self.config), [])

        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        self.assertEqual(foto(self.destino), primera, "la segunda proyección cambió bytes")
        self.assertEqual(problemas(self.destino, self.contrato, self.arbol, self.config), [])

    def test_comprobar_avisa_antes_de_la_primera_proyeccion(self) -> None:
        self.assertTrue(problemas(self.destino, self.contrato, self.arbol, self.config))

    def test_una_edicion_a_mano_se_detecta_y_se_repara(self) -> None:
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        skill = self.destino / ".claude" / "skills" / "medir-anchos" / "SKILL.md"
        skill.write_text("editado a mano\n", encoding="utf-8")
        self.assertTrue(problemas(self.destino, self.contrato, self.arbol, self.config))
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        self.assertEqual(problemas(self.destino, self.contrato, self.arbol, self.config), [])

    # --------------------------------------------------------------------- bloque

    def test_el_bloque_lleva_los_oceanos_y_el_contrato(self) -> None:
        texto = bloque(self.contrato, self.arbol)
        self.assertTrue(texto.startswith(INICIO))
        self.assertTrue(texto.endswith(f"{FIN}\n"))
        self.assertIn("Dos capas: la máquina y los ojos.", texto)
        self.assertIn("planeta-de-prueba", texto)

    def test_el_bloque_no_puede_pasarse_del_presupuesto(self) -> None:
        estrecha = configuracion(self.origen, entrada=10)
        with self.assertRaises(ErrorProyeccion) as capturado:
            sincronizar(self.destino, self.contrato, self.arbol, estrecha)
        self.assertIn("presupuesto", str(capturado.exception))

    # ------------------------------------------------------------------ aplanado

    def test_dos_pueblos_homonimos_nombran_las_dos_rutas(self) -> None:
        gemelo = self.origen / "otros" / "medir-anchos"
        gemelo.mkdir(parents=True)
        (gemelo / "SKILL.md").write_text(
            "---\ncosmos: pueblo\nnombre: medir-anchos\npadre: web\n"
            "resumen: Gemelo en otra provincia.\n---\n\nCuerpo.\n",
            encoding="utf-8",
        )
        from cosmos.modelo import cargar_arbol

        arbol = cargar_arbol(self.origen)
        with self.assertRaises(ErrorProyeccion) as capturado:
            pueblos_fuente(arbol, ("web",))
        mensaje = str(capturado.exception)
        self.assertIn("colisión al aplanar", mensaje)
        self.assertEqual(mensaje.count("web/medir-anchos"), 2)

    def test_no_se_proyecta_sobre_si_mismo(self) -> None:
        with self.assertRaises(ErrorProyeccion):
            raiz_del_planeta(self.destino, propia=self.destino)


if __name__ == "__main__":
    unittest.main()
