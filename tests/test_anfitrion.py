"""`anfitrion: claude-code`: el nodo es el fichero del runtime más las claves de COSMOS, y compilar
es quitarlas. Todo lo que hace reversible organizar un arnés con COSMOS, visto funcionar y fallar.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from cosmos import validar as validador
from cosmos.compilar import (ErrorCompilacion, _skills, compilar_arbol, compilar_runtime, errores_runtime,
                             nodos_runtime)
from cosmos.generar import generar_indice
from cosmos.modelo import Configuracion, Opaco, cargar_arbol, parsear_frontmatter, sin_claves_cosmos

RULE = """---
name: seo-wordpress
description: "Reglas duras del SEO: listón perfecto, acceso por vault."
paths:
  - "src/deploy/wpcli/**"
  - '.claude/skills/seo/**'
---

# SEO WordPress

Lo que no se negocia.
"""

AGENTE = """---
name: reviewer
description: Strict reviewer.
model: inherit
skills:
  - code-review
mcpServers:
  playwright:
    command: npx
---

Eres un revisor estricto.
"""

COMANDO_SIN_FRONTMATTER = "# Quality gate\n\nValida el DoD antes de cerrar.\n"

SKILL = """---
name: web-cero-fallos
description: Puerta única de las webs de cliente.
allowed-tools: Bash, Read
metadata:
  version: 3
---

# Web cero fallos

Este playbook se lee antes de tocar una web. Tiene que tener al menos cuarenta palabras para que la
guía cuente como guía y no como un título suelto: por eso este párrafo se alarga hasta llegar a las
cuarenta con holgura, una tras otra, sin decir nada nuevo.
"""


def _con_cosmos(original: str, claves: str) -> str:
    """El nodo: las claves de COSMOS delante del frontmatter original (o un frontmatter nuevo)."""

    if original.startswith("---\n"):
        return "---\n" + claves + original[4:]
    return "---\n" + claves + "---\n\n" + original


class ElParserTolera(unittest.TestCase):
    def test_un_mapa_anidado_queda_opaco_y_no_rompe(self) -> None:
        datos, _ = parsear_frontmatter(AGENTE, "a.md")
        self.assertIsInstance(datos["mcpServers"], Opaco)
        self.assertIn("playwright", datos["mcpServers"].texto)
        self.assertEqual(datos["skills"], ["code-review"])
        self.assertEqual(datos["name"], "reviewer")

    def test_sin_claves_cosmos_devuelve_el_original_byte_a_byte(self) -> None:
        for original, claves in ((RULE, "cosmos: lago\nnombre: seo-wordpress\nmoja: [\"src/deploy/wpcli/**\"]\nresumen: Reglas duras del SEO.\nanfitrion: claude-code\n"),
                                 (AGENTE, "cosmos: luna\nnombre: reviewer\norbita: web/arnes\nresumen: Revisor estricto.\nanfitrion: claude-code\n"),
                                 (COMANDO_SIN_FRONTMATTER, "cosmos: rio\nnombre: quality-gate\nmoja: []\ninvoca: /quality-gate\nresumen: Valida el DoD.\nanfitrion: claude-code\n"),
                                 (SKILL, "cosmos: pueblo\nnombre: web-cero-fallos\npadre: web\nresumen: Puerta unica de las webs.\norigen: guia\nanfitrion: claude-code\n")):
            with self.subTest(original[:20]):
                self.assertEqual(sin_claves_cosmos(_con_cosmos(original, claves)), original)

    def test_sin_claves_cosmos_no_toca_un_fichero_sin_frontmatter(self) -> None:
        self.assertEqual(sin_claves_cosmos(COMANDO_SIN_FRONTMATTER), COMANDO_SIN_FRONTMATTER)


class Arbol(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="anfitrion-")
        self.raiz = Path(self.temporal.name)
        self.arbol_dir = self.raiz / "arbol"
        self.arbol_dir.mkdir()
        self.config = Configuracion(
            entrada=4000, resumen=120, oceanos=7, galaxia_lineas=40, umbral_solapamiento=0.25,
            arbol=self.arbol_dir, indice=self.arbol_dir / "COSMOS.md",
            destino_compilacion=self.raiz / ".claude/skills", modo_compilacion="copia",
            manifiesto_compilacion=self.raiz / ".cosmos/compilado.json",
            rules_compilacion=self.raiz / ".claude/rules", agentes_compilacion=self.raiz / ".claude/agents",
            comandos_compilacion=self.raiz / ".claude/commands", nichos=("web",), encontrada=True,
            ruta=self.raiz / "cosmos.toml",
        )
        (self.arbol_dir / "galaxia.md").write_text("---\ncosmos: galaxia\nnombre: raiz\nresumen: Arbol sintetico de un arnes.\n---\n\nCuerpo.\n", encoding="utf-8")
        (self.arbol_dir / "web.md").write_text('---\ncosmos: sistema-solar\nnombre: web\npadre: ""\nresumen: Un sitio que carga y no se cae.\n---\n\nCuerpo.\n', encoding="utf-8")
        (self.arbol_dir / "arnes.md").write_text("---\ncosmos: planeta\nnombre: arnes\npadre: web\nresumen: El arnes de trabajo: lo que orbita aqui opera en cualquier encargo.\n---\n\nCuerpo.\n", encoding="utf-8")
        (self.arbol_dir / "lago-seo.md").write_text(_con_cosmos(RULE, 'cosmos: lago\nnombre: seo-wordpress\nmoja: ["src/deploy/wpcli/**", ".claude/skills/seo/**"]\nresumen: Reglas duras del SEO de webs cliente.\nanfitrion: claude-code\n'), encoding="utf-8")
        (self.arbol_dir / "luna-reviewer.md").write_text(_con_cosmos(AGENTE, "cosmos: luna\nnombre: reviewer\norbita: web/arnes\nresumen: Revisor estricto de errores y pruebas.\nanfitrion: claude-code\n"), encoding="utf-8")
        (self.arbol_dir / "rio-quality-gate.md").write_text(_con_cosmos(COMANDO_SIN_FRONTMATTER, "cosmos: rio\nnombre: quality-gate\nmoja: []\ninvoca: /quality-gate\nresumen: Valida el DoD antes de dar por terminado.\nanfitrion: claude-code\n"), encoding="utf-8")
        (self.arbol_dir / "rio-validar.md").write_text("---\ncosmos: rio\nnombre: validar\nmoja: []\ninvoca: python3 -m cosmos validar\nresumen: Comprueba las invariantes del arbol.\n---\n\nUn rio de COSMOS, sin anfitrion: no se materializa como comando.\n", encoding="utf-8")
        pueblo = self.arbol_dir / "pueblos" / "web-cero-fallos"
        pueblo.mkdir(parents=True)
        (pueblo / "SKILL.md").write_text(_con_cosmos(SKILL, "cosmos: pueblo\nnombre: web-cero-fallos\npadre: web\nresumen: Puerta unica de las webs de cliente.\norigen: guia\nanfitrion: claude-code\n"), encoding="utf-8")
        generico = self.arbol_dir / "pueblos" / "toxiproxy"
        generico.mkdir()
        (generico / "SKILL.md").write_text("---\ncosmos: pueblo\nnombre: toxiproxy\npadre: web\nresumen: Proxy que rompe la red a proposito.\n---\n\nhttps://github.com/Shopify/toxiproxy · MIT · 1★ · último push 2026-01-01 (comprobado 2026-01-01)\n\n```bash\ntoxiproxy-server\n```\n", encoding="utf-8")
        self.arbol = cargar_arbol(self.arbol_dir, excluir=self.config.indice)
        self.config.indice.write_text(generar_indice(self.arbol), encoding="utf-8")

    def tearDown(self) -> None:
        self.temporal.cleanup()

    def _validar(self, omitir: set[str] = frozenset()):
        return validador.validar_arbol(self.arbol, configuracion=self.config, omitir_codigos=frozenset(omitir) | {"E16"})

    def test_e00_acepta_las_claves_del_anfitrion_solo_con_la_declaracion(self) -> None:
        codigos = self._validar({"E19", "E22"}).codigos()
        self.assertNotIn("E00", codigos, self._validar({"E19", "E22"}).errores)
        sin = (self.arbol_dir / "luna-reviewer.md").read_text(encoding="utf-8").replace("anfitrion: claude-code\n", "")
        (self.arbol_dir / "luna-reviewer.md").write_text(sin, encoding="utf-8")
        self.arbol = cargar_arbol(self.arbol_dir, excluir=self.config.indice)
        errores = [e for e in self._validar({"E15", "E19", "E22"}).errores if e.codigo == "E00"]
        self.assertTrue(errores, "sin 'anfitrion', mcpServers y model tienen que ser E00")
        self.assertTrue(any("mcpServers" in e.mensaje for e in errores))

    def test_e00_rechaza_un_anfitrion_desconocido(self) -> None:
        texto = (self.arbol_dir / "lago-seo.md").read_text(encoding="utf-8").replace("anfitrion: claude-code", "anfitrion: cursor")
        (self.arbol_dir / "lago-seo.md").write_text(texto, encoding="utf-8")
        self.arbol = cargar_arbol(self.arbol_dir, excluir=self.config.indice)
        self.assertIn("E00", self._validar({"E15", "E19", "E22"}).codigos())

    def test_e21_admite_una_guia_con_cuerpo_y_rechaza_una_vacia(self) -> None:
        self.assertNotIn("E21", self._validar({"E19", "E22"}).codigos())
        corta = self.arbol_dir / "pueblos" / "web-cero-fallos" / "SKILL.md"
        corta.write_text(corta.read_text(encoding="utf-8").split("# Web cero fallos")[0] + "# Web cero fallos\n\nPoco.\n", encoding="utf-8")
        self.arbol = cargar_arbol(self.arbol_dir, excluir=self.config.indice)
        self.assertIn("E21", self._validar({"E15", "E19", "E22"}).codigos())

    def test_los_pueblos_del_anfitrion_entran_siempre_en_la_vista(self) -> None:
        self.assertIn("web-cero-fallos", _skills(self.arbol, None, todos=False))
        self.assertNotIn("toxiproxy", _skills(self.arbol, None, todos=False))
        self.assertIn("toxiproxy", _skills(self.arbol, None, todos=False, herramientas=("toxiproxy",)))

    def test_compilar_devuelve_el_runtime_byte_a_byte_y_e22_lo_vigila(self) -> None:
        for tipo, destino in (("rules", self.config.rules_compilacion), ("agentes", self.config.agentes_compilacion), ("comandos", self.config.comandos_compilacion)):
            manifiesto = self.raiz / ".cosmos" / f"compilado-{tipo}.json"
            resultado = compilar_runtime(self.arbol, tipo, destino, manifiesto)
            self.assertEqual(resultado.creadas, 1, (tipo, resultado.acciones))
        self.assertEqual((self.config.rules_compilacion / "seo-wordpress.md").read_text(encoding="utf-8"), RULE)
        self.assertEqual((self.config.agentes_compilacion / "reviewer.md").read_text(encoding="utf-8"), AGENTE)
        self.assertEqual((self.config.comandos_compilacion / "quality-gate.md").read_text(encoding="utf-8"), COMANDO_SIN_FRONTMATTER)
        self.assertFalse((self.config.comandos_compilacion / "validar.md").exists(), "un rio sin anfitrion no es un comando del runtime")
        compilar_arbol(self.arbol, destino=self.config.destino_compilacion, manifiesto=self.config.manifiesto_compilacion, modo="copia", nichos=("web",))
        self.assertEqual((self.config.destino_compilacion / "web-cero-fallos" / "SKILL.md").read_text(encoding="utf-8"), SKILL)
        generico = (self.config.destino_compilacion / "toxiproxy" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: toxiproxy", generico, "un pueblo sin anfitrion sigue traduciéndose para el runtime")
        self.assertEqual(self._validar().codigos(), [])
        # E22 en rojo si alguien edita el fichero generado a mano, y verde tras compilar
        (self.config.rules_compilacion / "seo-wordpress.md").write_text(RULE + "\nAñadido a mano.\n", encoding="utf-8")
        self.assertIn("E22", self._validar().codigos())
        resultado = compilar_runtime(self.arbol, "rules", self.config.rules_compilacion, self.raiz / ".cosmos/compilado-rules.json")
        self.assertEqual(resultado.preservadas, 1, "lo editado a mano se preserva, no se pisa")
        self.assertIn("E22", self._validar().codigos(), "preservar no es sincronizar: sigue en rojo hasta que alguien decida")

    def test_lo_ajeno_no_se_toca_y_lo_identico_se_adopta(self) -> None:
        destino = self.config.rules_compilacion
        destino.mkdir(parents=True)
        (destino / "ajena.md").write_text("---\npaths:\n  - \"x/**\"\n---\nRegla de otro.\n", encoding="utf-8")
        (destino / "seo-wordpress.md").write_text(RULE, encoding="utf-8")  # idéntica a lo que se crearía
        resultado = compilar_runtime(self.arbol, "rules", destino, self.raiz / ".cosmos/compilado-rules.json")
        self.assertEqual((resultado.adoptadas, resultado.ajenas, resultado.creadas), (1, 1, 0), resultado.acciones)
        self.assertEqual((destino / "ajena.md").read_text(encoding="utf-8"), "---\npaths:\n  - \"x/**\"\n---\nRegla de otro.\n")
        # el nodo desaparece: lo que COSMOS escribió (o adoptó) se retira; lo ajeno sigue
        (self.arbol_dir / "lago-seo.md").unlink()
        self.arbol = cargar_arbol(self.arbol_dir, excluir=self.config.indice)
        resultado = compilar_runtime(self.arbol, "rules", destino, self.raiz / ".cosmos/compilado-rules.json")
        self.assertEqual(resultado.eliminadas, 1)
        self.assertFalse((destino / "seo-wordpress.md").exists())
        self.assertTrue((destino / "ajena.md").exists())

    def test_e22_sin_manifiesto_pero_con_nodos_es_rojo(self) -> None:
        self.assertEqual(errores_runtime(self.arbol, "rules", self.config.rules_compilacion, self.raiz / ".cosmos/compilado-rules.json"),
                         [f"falta el manifiesto {self.raiz / '.cosmos/compilado-rules.json'}"])
        self.assertEqual(nodos_runtime(self.arbol, "comandos").keys(), {"quality-gate.md"})
        with self.assertRaises(ErrorCompilacion):
            compilar_runtime(self.arbol, "inventado", self.raiz / "x", self.raiz / "y.json")


class LaMemoriaDelAnfitrionSeIndexaDondeEsta(unittest.TestCase):
    def test_indexa_name_y_description_con_mapas_anidados(self) -> None:
        from puente.lluvia import indexar, ordenar

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "memory").mkdir()
            (base / "memory" / "reference-wp-cli-remoto.md").write_text(
                '---\nname: reference-wp-cli-remoto\ndescription: "WP-CLI remoto: el socket cambia de ruta en cada despliegue."\nmetadata:\n  type: reference\n  modified: 2026-09-01\n---\n\nEl socket vive en /run/mysqld.\n', encoding="utf-8")
            (base / "memory" / "MEMORY.md").write_text("- indice\n", encoding="utf-8")
            entradas = indexar(base, memoria="memory")
            self.assertEqual([e.nombre for e in entradas], ["reference-wp-cli-remoto"])
            self.assertEqual(entradas[0].ruta, "memory/reference-wp-cli-remoto.md")
            self.assertIn("socket", entradas[0].resumen)
            self.assertEqual(entradas[0].publico().keys(), {"ruta", "nombre", "resumen", "carpeta", "nicho"}, "nunca el cuerpo")
            self.assertTrue(ordenar("socket de wp-cli en el despliegue", entradas))
            self.assertEqual(indexar(base), [], "sin declararla, la memoria del anfitrion no se indexa")



class LosMdDeApoyoDeUnPuebloNoSonNodos(unittest.TestCase):
    def test_referencias_y_subpaquetes_viajan_con_el_pueblo_sin_ser_nodos(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "galaxia.md").write_text("---\ncosmos: galaxia\nnombre: g\nresumen: Arbol de prueba de carga.\n---\n", encoding="utf-8")
            (base / "web.md").write_text('---\ncosmos: sistema-solar\nnombre: web\npadre: ""\nresumen: Un sitio que carga.\n---\n', encoding="utf-8")
            pueblo = base / "pueblos" / "paquete"
            (pueblo / "references").mkdir(parents=True)
            (pueblo / "sub").mkdir()
            (pueblo / "SKILL.md").write_text("---\ncosmos: pueblo\nnombre: paquete\npadre: web\nresumen: Un paquete con sub-skills y referencias.\norigen: guia\nanfitrion: claude-code\n---\n\n" + "palabra " * 45 + "\n", encoding="utf-8")
            (pueblo / "references" / "nota.md").write_text("# Nota sin frontmatter\n", encoding="utf-8")
            (pueblo / "README.md").write_text("---\ntitle: paquete\nauthor: alguien\n---\nlibre\n", encoding="utf-8")
            (pueblo / "sub" / "SKILL.md").write_text("---\nname: sub-skill\ndescription: anidada\nmetadata:\n  version: 1\n---\n", encoding="utf-8")
            arbol = cargar_arbol(base)
            self.assertEqual(sorted(n.nombre for n in arbol.nodos), ["g", "paquete", "web"])
            self.assertEqual(arbol.errores, [])
            resultado = validador.validar_arbol(arbol, configuracion=Configuracion(arbol=base, indice=base / "COSMOS.md"), omitir_codigos={"E15", "E16", "E19", "E22"})
            self.assertEqual(resultado.codigos(), [])


if __name__ == "__main__":
    unittest.main()
