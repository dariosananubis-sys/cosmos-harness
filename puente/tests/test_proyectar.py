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
    ContratoPlaneta,
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
        # Revisión C-03: una clave presente es del anfitrión aunque se llame como una nuestra.
        self.assertTrue(actuales["autoMemoryEnabled"], "proyectar pisó un ajuste del anfitrión")
        self.assertFalse(actuales["includeGitInstructions"], "la clave ausente sí se añade")

    def test_un_ajuste_del_anfitrion_no_se_pisa_ni_comprobar_lo_exige(self) -> None:
        ajustes = self.destino / ".claude" / "settings.json"
        ajustes.parent.mkdir(parents=True)
        ajustes.write_text(json.dumps({"attribution": {"commit": "Firmado por mí", "mio": 1}}), encoding="utf-8")
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        actuales = json.loads(ajustes.read_text(encoding="utf-8"))
        self.assertEqual(actuales["attribution"]["commit"], "Firmado por mí")
        self.assertEqual(actuales["attribution"]["mio"], 1)
        self.assertEqual(actuales["attribution"]["pr"], "", "dentro del mismo objeto, lo ausente se añade")
        self.assertEqual(problemas(self.destino, self.contrato, self.arbol, self.config), [])

    def test_el_bloque_se_sustituye_donde_estaba(self) -> None:
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        agentes = self.destino / "AGENTS.md"
        agentes.write_text(agentes.read_text(encoding="utf-8") + "\n## Mis notas al final\n", encoding="utf-8")
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        texto = agentes.read_text(encoding="utf-8")
        self.assertLess(texto.index(FIN), texto.index("## Mis notas al final"), "el bloque se movió al final (C-15)")
        self.assertTrue(texto.endswith("## Mis notas al final\n"))
        self.assertEqual(problemas(self.destino, self.contrato, self.arbol, self.config), [])

    def test_un_claude_md_con_crlf_conserva_su_final_de_linea(self) -> None:
        ruta = self.destino / "CLAUDE.md"
        ruta.write_bytes(b"# Mi proyecto\r\n\r\nReglas mias.\r\n")
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        crudo = ruta.read_bytes()
        self.assertIn(b"Reglas mias.\r\n", crudo)
        self.assertNotIn(b"\n\n", crudo.replace(b"\r\n", b""), "quedaron saltos LF sueltos en un fichero CRLF")
        self.assertIn(INICIO.encode(), crudo)
        self.assertEqual(problemas(self.destino, self.contrato, self.arbol, self.config), [])

    def test_una_skill_enlazada_del_anfitrion_no_aborta_la_proyeccion(self) -> None:
        propias = self.destino / "skills-propias" / "mia"
        propias.mkdir(parents=True)
        (propias / "SKILL.md").write_text("---\nname: mia\ndescription: mia\n---\n", encoding="utf-8")
        base = self.destino / ".claude" / "skills"
        base.mkdir(parents=True)
        (base / "mia").symlink_to(propias)
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        self.assertTrue((base / "mia").is_symlink(), "el enlace del anfitrión tiene que seguir ahí")
        self.assertEqual(problemas(self.destino, self.contrato, self.arbol, self.config), [])

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




class LoProyectadoLoVeElAnfitrion(unittest.TestCase):
    """Auditoría E-01 / E-02 / E-15: 22 de 22 pueblos proyectados invisibles para Claude Code
    con `comprobar` en verde; el bloque mandaba ejecutar un `cosmos` que el repo ajeno no
    tiene; y `.claude/settings.json` se reordenaba sin cambiar nada."""

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="puente-anfitrion-")
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

    def _skill(self) -> Path:
        skills = [p for p in (self.destino / ".claude" / "skills").iterdir() if p.is_dir()]
        self.assertTrue(skills, "no se proyectó ningún pueblo")
        return skills[0] / "SKILL.md"

    def test_el_skill_proyectado_lleva_name_y_description(self) -> None:
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        texto = self._skill().read_text(encoding="utf-8")
        cabecera = texto.split("\n---", 1)[0]
        import re

        self.assertIsNotNone(re.search(r"^name: [a-z0-9-]+$", cabecera, re.M), cabecera)
        self.assertIsNotNone(re.search(r"^description: \"Pueblo de prueba", cabecera, re.M), cabecera)
        self.assertIn("cosmos: pueblo", cabecera, "los campos de COSMOS se conservan")
        self.assertEqual(problemas(self.destino, self.contrato, self.arbol, self.config), [])

    def test_comprobar_verifica_el_contrato_del_anfitrion_no_el_de_cosmos(self) -> None:
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        skill = self._skill()
        sin_campos = "\n".join(l for l in skill.read_text(encoding="utf-8").splitlines()
                               if not l.startswith(("name:", "description:"))) + "\n"
        skill.write_text(sin_campos, encoding="utf-8")
        encontrados = problemas(self.destino, self.contrato, self.arbol, self.config)
        self.assertTrue(any("invisible para el anfitrión" in p for p in encontrados), encontrados)

    def test_el_bloque_no_manda_ejecutar_un_verbo_que_el_repo_no_tiene(self) -> None:
        texto = bloque(self.contrato, self.arbol)
        self.assertNotIn("rio/", texto)
        self.assertNotIn("cosmos abrir rio", texto)
        self.assertIn("Cómo se baja desde aquí", texto)
        self.assertIn("NO están en este repositorio", texto)

    def test_settings_no_se_reordena_si_no_cambia_nada(self) -> None:
        ajustes = self.destino / ".claude" / "settings.json"
        ajustes.parent.mkdir(parents=True, exist_ok=True)
        original = '{\n  "zeta": 1,\n  "alfa": 2\n}\n'
        ajustes.write_text(original, encoding="utf-8")
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        primera = ajustes.read_text(encoding="utf-8")
        self.assertLess(primera.index('"zeta"'), primera.index('"alfa"'), "se reordenaron las claves ajenas")
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        self.assertEqual(ajustes.read_text(encoding="utf-8"), primera)
        mtime = ajustes.stat().st_mtime_ns
        sincronizar(self.destino, self.contrato, self.arbol, self.config)
        self.assertEqual(ajustes.stat().st_mtime_ns, mtime, "se reescribió sin cambiar nada")




class ElBloqueRealNoMandaEjecutarCosmos(unittest.TestCase):
    """R-20: el fix de A-11 metió `cosmos buscar`/`abrir` en un océano que se inyecta verbatim en
    repos donde `cosmos` no existe. El doble sintético no tenía océanos reales: se prueba con el árbol real."""

    def test_los_oceanos_reales_no_nombran_verbos_de_cosmos(self) -> None:
        from cosmos.modelo import cargar_arbol, cuerpo

        raiz = Path(__file__).resolve().parent.parent.parent
        arbol = cargar_arbol(raiz / "galaxia")
        for oceano in (n for n in arbol.nodos if n.cosmos == "oceano"):
            with self.subTest(oceano.nombre):
                self.assertNotIn("cosmos ", cuerpo(oceano).lower(),
                                 f"oceano/{oceano.nombre} manda ejecutar un verbo que el repo proyectado no tiene")

    def test_el_bloque_real_solo_nombra_cosmos_en_la_seccion_de_como_se_baja(self) -> None:
        from cosmos.modelo import cargar_arbol

        raiz = Path(__file__).resolve().parent.parent.parent
        arbol = cargar_arbol(raiz / "galaxia")
        contrato = ContratoPlaneta("p", "generico", ("trading",), "", (), (), False, False, (), False)
        texto = bloque(contrato, arbol)
        antes, _, despues = texto.partition("## Cómo se baja desde aquí")
        self.assertEqual(antes.lower().count("cosmos abrir") + antes.lower().count("cosmos buscar"), 0,
                         "el bloque manda ejecutar cosmos antes de explicar que no existe aquí")
        self.assertIn("NO están en este repositorio", despues)


if __name__ == "__main__":
    unittest.main()
