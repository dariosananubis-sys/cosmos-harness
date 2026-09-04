"""Los arreglos de código de la auditoría 360 (P3), cada uno visto fallar antes de cerrarse.

Cada clase nombra el hallazgo que cierra. Todo corre sobre árboles sintéticos en un temporal:
nada toca el repositorio real (auditoría D-02).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.guardarrailes import instalacion, orden_sesion
from cosmos.modelo import cargar_arbol

RAIZ = Path(__file__).resolve().parent.parent

GALAXIA = "---\ncosmos: galaxia\nnombre: prueba\nresumen: Nada se carga hasta entrar en ello.\n---\n\nCuerpo.\n"
SISTEMA = '---\ncosmos: sistema-solar\nnombre: web\npadre: ""\nresumen: Un sitio que carga y no se cae.\n---\n\nCuerpo.\n'


def _config(directorio: Path, arbol: str = "arbol") -> Path:
    config = directorio / "cosmos.toml"
    config.write_text(
        (RAIZ / "cosmos.toml").read_text(encoding="utf-8")
        .replace('arbol = "galaxia"', f'arbol = "{arbol}"')
        .replace('indice = "galaxia/COSMOS.md"', f'indice = "{arbol}/COSMOS.md"')
        .replace('registro = "registro"', ""),
        encoding="utf-8",
    )
    return config


def _cosmos(*args: str, config: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "cosmos", *args, "--config", str(config)],
                          capture_output=True, text=True, cwd=RAIZ)


def _config_compilacion(directorio: Path, modo: str = "symlink") -> Path:
    """Config sobre la galaxia real, con destino y manifiesto de la vista en el temporal."""

    config = directorio / "cosmos.toml"
    config.write_text(
        (RAIZ / "cosmos.toml").read_text(encoding="utf-8")
        .replace('arbol = "galaxia"', f'arbol = "{RAIZ}/galaxia"')
        .replace('indice = "galaxia/COSMOS.md"', f'indice = "{RAIZ}/galaxia/COSMOS.md"')
        .replace('registro = "registro"', f'registro = "{RAIZ}/registro"')
        .replace('manifiesto = ".cosmos/compilado-galaxia.json"', f'manifiesto = "{directorio}/compilado.json"'),
        encoding="utf-8",
    )
    # el espaciado de `destino` en cosmos.toml no es estable: se sustituye por expresión
    texto = re.sub(r'^destino\s*=\s*".*?"', f'destino = "{directorio}/vista"', config.read_text(encoding="utf-8"), count=1, flags=re.M)
    texto = re.sub(r'^modo\s*=\s*".*?"', f'modo = "{modo}"', texto, count=1, flags=re.M)
    config.write_text(texto, encoding="utf-8")
    return config


from tests._integrado import solo_en_el_origen

solo_en_el_origen()  # cifras y listas del catálogo del origen, no del motor


class D04_UnBomNoHaceDesaparecerUnNodo(unittest.TestCase):
    def test_el_nodo_con_bom_se_carga(self) -> None:
        with TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "galaxia.md").write_bytes(b"\xef\xbb\xbf" + GALAXIA.encode("utf-8"))
            arbol = cargar_arbol(raiz)
        self.assertEqual([n.cosmos for n in arbol.nodos], ["galaxia"], "el BOM descartó el nodo en silencio")
        self.assertEqual(arbol.errores, [])


class D11_UnEnlaceFueraDelArbolNoEntraComoNodo(unittest.TestCase):
    def test_se_denuncia_en_vez_de_cargarse(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "arbol").mkdir()
            (base / "arbol" / "galaxia.md").write_text(GALAXIA, encoding="utf-8")
            (base / "fuera.md").write_text(SISTEMA, encoding="utf-8")
            os.symlink(base / "fuera.md", base / "arbol" / "web.md")
            arbol = cargar_arbol(base / "arbol")
        self.assertEqual([n.cosmos for n in arbol.nodos], ["galaxia"], "un symlink de fuera entró como nodo")
        self.assertTrue(any("fuera del árbol" in e.mensaje for e in arbol.errores), arbol.errores)
        self.assertEqual(arbol.errores[0].ruta, "web.md", "la ruta del error tiene que ser relativa (D-10)")


class D05_EstadoYMapaNoDanVerdeSobreUnaRaizQueNoExiste(unittest.TestCase):
    def test_los_dos_verbos_salen_1(self) -> None:
        with TemporaryDirectory() as tmp:
            config = _config(Path(tmp), arbol="no-existe")
            for verbo in ("estado", "mapa"):
                with self.subTest(verbo):
                    r = _cosmos(verbo, config=config)
                    self.assertEqual(r.returncode, 1, r.stdout)
                    self.assertIn("la raíz del árbol no existe", r.stderr)


class E03_CompilarNoListaLoQueNoCambia(unittest.TestCase):
    def test_sin_detalle_no_hay_lineas_igual(self) -> None:
        with TemporaryDirectory() as tmp:
            config = _config_compilacion(Path(tmp))
            r = _cosmos("compilar", "--modo", "copia", config=config)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertNotIn("\nCREAR ", r.stdout)
            r = _cosmos("compilar", "--modo", "copia", config=config)
            self.assertNotIn("IGUAL ", r.stdout)
            self.assertLess(len(r.stdout.splitlines()), 12, "el segundo arranque vuelve a costar 250 líneas")
            r = _cosmos("compilar", "--modo", "copia", "--detalle", config=config)
            self.assertIn("IGUAL ", r.stdout)


class E08_ArrancarDejaUnArbolNuevoEnVerde(unittest.TestCase):
    def test_directorio_vacio_mas_config_sale_verde(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "arbol").mkdir()
            config = _config(base)
            r = _cosmos("arrancar", config=config)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("Galaxia creada", r.stdout)
            self.assertTrue((base / "arbol" / "galaxia.md").is_file())
            self.assertEqual(_cosmos("validar", config=config).returncode, 0)

    def test_con_nodos_pero_sin_galaxia_no_se_inventa_nada(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "arbol").mkdir()
            (base / "arbol" / "web.md").write_text(SISTEMA, encoding="utf-8")
            r = _cosmos("arrancar", config=_config(base))
            self.assertEqual(r.returncode, 1)
            self.assertNotIn("Galaxia creada", r.stdout)
            self.assertFalse((base / "arbol" / "galaxia.md").exists())


class E06_LaOrdenDelHookEsPortableCuandoPuede(unittest.TestCase):
    def test_sobre_el_propio_repositorio_no_lleva_rutas_de_esta_maquina(self) -> None:
        orden = orden_sesion(None, instalacion())
        self.assertIn("${CLAUDE_PROJECT_DIR", orden)
        self.assertNotIn(str(instalacion()), orden)
        self.assertNotIn(sys.executable, orden)

    def test_instalado_en_otra_parte_sigue_funcionando(self) -> None:
        with TemporaryDirectory() as tmp:
            orden = orden_sesion(None, Path(tmp))
        self.assertIn(str(instalacion()), orden)


class E14_AbrirNombraLosOficiosQueUsa(unittest.TestCase):
    def test_solo_nombres(self) -> None:
        r = subprocess.run([sys.executable, "-m", "cosmos", "abrir", "trading"], capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 0)
        self.assertIn("oficios que este usa", r.stdout)
        self.assertIn("ingenieria-datos", r.stdout)
        self.assertNotIn("dbt", r.stdout, "usa: arrastró carga: apareció un pueblo del oficio vecino")


class A12_UnNivelRetiradoNoSeNombraComoVivo(unittest.TestCase):
    PERMITIDOS = {"GOAL.md", "spec/TAXONOMIA.md", "spec/FRONTMATTER.md", "spec/NUCLEO.md", "cosmos/modelo.py"}

    def test_ciudad_solo_aparece_donde_se_documenta_su_retirada(self) -> None:
        import re

        culpables = []
        for patron in ("README.md", "PROGRESS.md", "spec/*.md", "cosmos/*.py", "puente/*.py", "galaxia/*.md",
                       "galaxia/agua/*.md", "galaxia/sistemas/*.md", "galaxia/estrellas/*.md", "galaxia/paises/*.md",
                       "galaxia/continentes/*.md", "galaxia/pueblos/*/SKILL.md"):
            for ruta in RAIZ.glob(patron):
                relativa = ruta.relative_to(RAIZ).as_posix()
                if relativa in self.PERMITIDOS:
                    continue
                if re.search(r"\bciudad(es)?\b", ruta.read_text(encoding="utf-8")):
                    culpables.append(relativa)
        self.assertEqual(culpables, [], "un nivel retirado sigue nombrado como si existiera")




class A06_E21_UnPuebloNombraQueEjecutar(unittest.TestCase):
    """spec/PUEBLO.md era normativo y no lo comprobaba nadie: 28 de 247 pueblos sin URL."""

    PUEBLO = "---\ncosmos: pueblo\nnombre: cosa\npadre: web\nresumen: Hace una cosa concreta y distinta.\n{extra}---\n\n{cuerpo}\n"

    def _errores(self, extra: str, cuerpo: str, guion: bool = True) -> list[str]:
        from cosmos.validar import _comprobar_e21
        from cosmos.modelo import Configuracion

        with TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "galaxia.md").write_text(GALAXIA, encoding="utf-8")
            (raiz / "web.md").write_text(SISTEMA, encoding="utf-8")
            (raiz / "cosa").mkdir()
            (raiz / "cosa" / "SKILL.md").write_text(self.PUEBLO.format(extra=extra, cuerpo=cuerpo), encoding="utf-8")
            if guion:
                (raiz / "cosa" / "scripts").mkdir()
                (raiz / "cosa" / "scripts" / "cosa.sh").write_text("#!/bin/sh\necho cosa\n", encoding="utf-8")
            arbol = cargar_arbol(raiz)
            return [e.mensaje for e in _comprobar_e21(arbol, Configuracion(), raiz)]

    def test_sin_url_ni_origen_es_rojo(self) -> None:
        errores = self._errores("", "Una herramienta estupenda.\n\n```bash\nhacer cosa\n```")
        self.assertEqual(len(errores), 1, errores)
        self.assertIn("sin URL de repositorio", errores[0])

    def test_con_url_y_bloque_pasa(self) -> None:
        self.assertEqual(self._errores("", "https://github.com/x/cosa · MIT\n\n```bash\ncosa\n```"), [])

    def test_origen_propio_sustituye_a_la_url(self) -> None:
        self.assertEqual(self._errores("origen: propio\n", "herramienta propia, no de GitHub\n\n```bash\ncosa\n```"), [])

    def test_la_url_tiene_que_ser_de_repositorio_y_en_la_primera_linea(self) -> None:
        """R-18: la cadena `https://` en prosa satisfacía E21; 10 pueblos pasaban por accidente."""

        prosa = "Esto fuerza `https://`, y no nombra ningun repositorio.\n\n```bash\ncosa\n```"
        self.assertTrue(any("sin URL de repositorio" in e for e in self._errores("", prosa)))
        marcador = "https://github.com/usuario/repo · MIT\n\n```bash\ncosa\n```"
        self.assertTrue(any("sin URL de repositorio" in e for e in self._errores("", marcador)))
        docs = "https://learn.microsoft.com/en-us/bingwebmaster/getting-access\n\n```bash\ncosa\n```"
        self.assertEqual(self._errores("", docs), [], "una URL con organización/proyecto en la primera línea vale; el marcador y la prosa no")
        segunda = "Texto.\nhttps://github.com/x/cosa · MIT\n\n```bash\ncosa\n```"
        self.assertTrue(any("sin URL de repositorio" in e for e in self._errores("", segunda)), "la URL tiene que ir en la PRIMERA línea")

    def test_origen_propio_exige_un_guion_en_el_directorio(self) -> None:
        """R-37: `origen: propio` era un indulto autodeclarado."""

        errores = self._errores("origen: propio\n", "herramienta propia\n\n```bash\ncosa\n```", guion=False)
        self.assertTrue(any("sin ningún guion" in e for e in errores), errores)

    def test_sin_bloque_de_codigo_es_rojo(self) -> None:
        errores = self._errores("", "https://github.com/x/cosa · MIT\n\nSe instala con brew.")
        self.assertTrue(any("sin bloque de código" in e for e in errores), errores)

    def test_un_origen_desconocido_es_rojo(self) -> None:
        errores = self._errores("origen: ajeno\n", "https://github.com/x/cosa\n\n```bash\ncosa\n```")
        self.assertTrue(any("origen desconocido" in e for e in errores), errores)

    def test_e21_esta_viva_y_tiene_valvula(self) -> None:
        from cosmos.guardarrailes import CODIGOS_INVARIANTES
        from cosmos.validar import codigos_comprobados

        self.assertIn("E21", codigos_comprobados())
        self.assertIn("E21", CODIGOS_INVARIANTES)

    def test_la_galaxia_real_cumple_el_contrato(self) -> None:
        from cosmos.validar import _comprobar_e21
        from cosmos.modelo import Configuracion

        arbol = cargar_arbol(RAIZ / "galaxia")
        self.assertEqual([e.mensaje for e in _comprobar_e21(arbol, Configuracion(), RAIZ / "galaxia")], [])




class R40_UnEnlaceDentroDelArbolNoDuplicaElNodo(unittest.TestCase):
    def test_se_denuncia_el_enlace_no_la_victima(self) -> None:
        with TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "galaxia.md").write_text(GALAXIA, encoding="utf-8")
            (raiz / "web.md").write_text(SISTEMA, encoding="utf-8")
            os.symlink(raiz / "web.md", raiz / "clon.md")
            arbol = cargar_arbol(raiz)
        self.assertEqual(sorted(n.cosmos for n in arbol.nodos), ["galaxia", "sistema-solar"], "el enlace duplicó el nodo")
        enlace = [e for e in arbol.errores if "dentro del árbol" in e.mensaje]
        self.assertEqual([e.ruta for e in enlace], ["clon.md"], "el error tiene que señalar al enlace, no al original")


class R41_LaCacheDeNichosSeInvalidaPorContenido(unittest.TestCase):
    def test_sustituir_la_lista_o_invalidar_la_refresca(self) -> None:
        from cosmos.modelo import Arbol, Nodo, nichos_disponibles

        def sistema(nombre: str) -> Nodo:
            return Nodo(Path(f"{nombre}.md"), f"{nombre}.md", {"cosmos": "sistema-solar", "nombre": nombre, "resumen": "x", "padre": ""}, {}, "")

        arbol = Arbol(Path("."), [sistema("juegos")])
        self.assertEqual(nichos_disponibles(arbol), frozenset({"juegos"}))
        arbol.nodos[0] = sistema("oficio-nuevo")          # mismo len, misma lista: la caché queda vieja...
        arbol.invalidar()                                  # ...y esto es lo que la refresca
        self.assertEqual(nichos_disponibles(arbol), frozenset({"oficio-nuevo"}))
        arbol.nodos = [sistema("otro")]                    # lista nueva: se invalida sola
        self.assertEqual(nichos_disponibles(arbol), frozenset({"otro"}))




class E13_AbrirDescribeLasHojasYNombraLosIntermedios(unittest.TestCase):
    """La regla está escrita en COMPOSICION.md; sin test era el corolario 1 de GOAL §2 incumplido."""

    def test_un_continente_nombra_sin_describir_y_una_provincia_describe_sus_pueblos(self) -> None:
        from cosmos.abrir import abrir, formatear
        from cosmos.modelo import cargar_arbol

        arbol = cargar_arbol(RAIZ / "galaxia")
        salida_intermedio = formatear(abrir(arbol, "ciberseguridad/ofensiva"))
        hijos = [n for n in arbol.nodos if n.datos.get("padre") == "ciberseguridad/ofensiva"]
        self.assertTrue(hijos)
        for hijo in hijos:
            self.assertIn(hijo.referencia, salida_intermedio)
            self.assertNotIn(hijo.resumen, salida_intermedio, f"abrir describió al intermedio {hijo.nombre}")
        salida_hoja = formatear(abrir(arbol, "ciberseguridad/ofensiva/reconocimiento"))
        pueblos = [n for n in arbol.nodos if n.cosmos == "pueblo" and n.datos.get("padre") == "ciberseguridad/ofensiva/reconocimiento"]
        self.assertTrue(pueblos)
        for pueblo in pueblos:
            self.assertIn(pueblo.resumen, salida_hoja, f"abrir no describió la hoja {pueblo.nombre}")




class R22_LaVistaCompiladaLaVeElRuntime(unittest.TestCase):
    """306 de 306 entradas compiladas sin `name`: invisibles para el runtime que la spec invoca."""

    def test_en_copia_el_skill_lleva_name_y_description_y_e19_queda_verde(self) -> None:
        import re

        with TemporaryDirectory() as tmp:
            config = _config_compilacion(Path(tmp), modo="copia")
            r = _cosmos("compilar", "--nicho", "juegos", config=config)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            skills = sorted((Path(tmp) / "vista").glob("*/SKILL.md"))
            self.assertTrue(skills)
            for skill in skills:
                cabecera = skill.read_text(encoding="utf-8").split("\n---", 1)[0]
                self.assertIsNotNone(re.search(r"^name: ", cabecera, re.M), skill)
                self.assertIsNotNone(re.search(r"^description: ", cabecera, re.M), skill)
            r = _cosmos("validar", "--nicho", "juegos", config=config)
            self.assertNotIn("E19", r.stdout, "la traducción se tomó por una edición a mano")

    def test_symlink_hacia_un_directorio_escaneado_se_niega(self) -> None:
        from cosmos.compilar import ErrorCompilacion, compilar_arbol
        from cosmos.modelo import cargar_arbol

        with TemporaryDirectory() as tmp:
            arbol = cargar_arbol(RAIZ / "galaxia")
            destino = Path(tmp) / ".claude" / "skills"
            with self.assertRaises(ErrorCompilacion) as caso:
                compilar_arbol(arbol, destino=destino, manifiesto=Path(tmp) / "m.json", modo="symlink", nichos=["juegos"])
            self.assertIn("--modo copia", str(caso.exception))

    def test_la_vista_completa_en_un_directorio_escaneado_exige_todos(self) -> None:
        from cosmos.compilar import ErrorCompilacion, compilar_arbol
        from cosmos.modelo import cargar_arbol

        with TemporaryDirectory() as tmp:
            arbol = cargar_arbol(RAIZ / "galaxia")
            destino = Path(tmp) / ".agents" / "skills"
            with self.assertRaises(ErrorCompilacion) as caso:
                compilar_arbol(arbol, destino=destino, manifiesto=Path(tmp) / "m.json", modo="copia")
            self.assertIn("--todos", str(caso.exception))
            resultado = compilar_arbol(arbol, destino=destino, manifiesto=Path(tmp) / "m.json", modo="copia", todos=True)
            self.assertGreater(resultado.creadas, 200)

    def test_nichos_none_ya_no_es_todos_en_la_api(self) -> None:
        """A-04 cerrado de verdad: el mismo centinela significa lo mismo en los dos subsistemas."""

        from cosmos.compilar import _skills
        from cosmos.medir import nodos_de_catalogo
        from cosmos.modelo import cargar_arbol

        arbol = cargar_arbol(RAIZ / "galaxia")
        self.assertEqual(_skills(arbol, None), {})
        self.assertEqual([n for n in nodos_de_catalogo(arbol, None) if n.cosmos == "pueblo"], [])
        self.assertGreater(len(_skills(arbol, None, todos=True)), 200)


class F09_ElPrePushRepiteElEscaneo(unittest.TestCase):
    def test_enganchar_escribe_pre_push_y_desenganchar_lo_quita(self) -> None:
        from cosmos.guardarrailes import contenido_hook_push, desenganchar, enganchar

        self.assertIn("puente.secretos --todo", contenido_hook_push())
        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
            enganchar(repo)
            push = repo / ".git" / "hooks" / "pre-push"
            self.assertTrue(push.is_file())
            self.assertTrue(os.access(push, os.X_OK))
            desenganchar(repo)
            self.assertFalse(push.exists())

    def test_un_pre_push_ajeno_no_se_pisa(self) -> None:
        from cosmos.guardarrailes import enganchar

        with TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
            ajeno = repo / ".git" / "hooks" / "pre-push"
            ajeno.write_text("#!/bin/sh\necho ajeno\n", encoding="utf-8")
            enganchar(repo)
            self.assertEqual(ajeno.read_text(encoding="utf-8"), "#!/bin/sh\necho ajeno\n")


if __name__ == "__main__":
    unittest.main()
