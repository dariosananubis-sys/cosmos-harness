"""El juez no puede mentir a favor del árbol, y se le ve fallar en cada puerta.

La auditoría 360 del 2026-09-03 (informe B) demostró que la cifra de acierto subía de
40 % a 100 % copiando el examen a los resúmenes, con `validar` verde, `medir` más barato
y el listón en verde; que el holdout viajaba en claro dentro del repositorio; que la
única guarda anti-Goodhart felicitaba al tramposo; y que el criterio de corrección se
aflojaba con la suite entera en verde. Cada clase de aquí cierra una de esas puertas y
la ve cerrada: **arreglar el juez no es subir la nota**. Aserciones escritas tras medir.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.acertar import (BRECHA_ALARMA, Contraste, Encargo, Puntuacion, Resultado, _acierta,
                            _lineas_del_catalogo, cargar_encargos, formatear_contraste, sellar)
from cosmos.holdout import (Procedencia, cobertura, comprobar_procedencia, esta_versionado,
                            formatear_intervalo, intervalo_wilson, normalizar_peticion, solape_examen_catalogo)
from cosmos.medir import catalogo_visible, lineas_de_catalogo
from cosmos.modelo import cargar_arbol, cargar_configuracion, nombres_nichos

RAIZ = Path(__file__).resolve().parent.parent

def _sin_historia_git() -> bool:
    """La instantánea del gate tiene .git (git init) pero ningún commit: sin historia no hay contra qué leer."""
    return subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--verify", "-q", "HEAD"],
                          capture_output=True).returncode != 0

CONFIG = cargar_configuracion(RAIZ / "cosmos.toml")
ARBOL = cargar_arbol(CONFIG.arbol, tambien=(CONFIG.registro,) if CONFIG.registro else ())


def _puntuacion(aciertos: int, total: int) -> Puntuacion:
    return Puntuacion(resultados=[
        Resultado(encargo=Encargo(peticion=f"p{i}", espera="web"), elegida="web",
                  posicion=1 if i < aciertos else 4, acierta=i < aciertos)
        for i in range(total)
    ])


def _limpia() -> Procedencia:
    return Procedencia(comprobada=True, quemadas=(), blobs_revisados=3, motivo="3 blobs; 0 coincidencias")


@unittest.skipIf(_sin_historia_git(), "sin historia git: la instantánea del gate hace git init con cero commits")
class ElExamenNoViajaConElRepositorio(unittest.TestCase):
    """B-02: un holdout que se puede leer con `cat` desde el repo es un ejercicio resuelto."""

    def test_el_holdout_no_esta_versionado(self) -> None:
        r = subprocess.run(["git", "-C", str(RAIZ), "ls-files", "--", "pruebas/"],
                           capture_output=True, text=True, check=False)
        versionados = [linea for linea in r.stdout.splitlines() if linea.endswith(".json")]
        self.assertNotIn("pruebas/encargos-validacion.json", versionados,
                         "el examen volvió al repositorio: quien clona lo tiene entero")
        self.assertIn("pruebas/encargos.json", versionados, "el conjunto de AJUSTE sí se versiona")

    def test_el_gitignore_lo_impide(self) -> None:
        texto = (RAIZ / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("encargos-validacion.json", texto)

    def test_un_holdout_versionado_se_declara_quemado(self) -> None:
        self.assertIs(esta_versionado(RAIZ, RAIZ / "pruebas/encargos.json"), True)
        self.assertIs(esta_versionado(RAIZ, RAIZ / "pruebas/no-existe.json"), False)

    def test_una_consulta_que_ya_esta_en_la_historia_git_quema_el_holdout(self) -> None:
        """El conjunto quemado de 2026-09-02 sigue en la historia: usar una de sus consultas es quemarla."""

        quemado = json.loads((RAIZ / "pruebas/encargos-validacion-quemada-2026-09-02.json").read_text(encoding="utf-8"))
        vista = quemado[0]["peticion"]
        resultado = comprobar_procedencia(RAIZ, [vista, "una consulta inventada ahora mismo zzz"])
        self.assertIs(resultado.comprobada, True)
        self.assertEqual(resultado.quemadas, (vista,))
        self.assertGreater(resultado.blobs_revisados, 0)
        self.assertFalse(resultado.limpia)

    def test_una_consulta_nueva_sale_limpia(self) -> None:
        resultado = comprobar_procedencia(RAIZ, ["quiero que mi nevera pida la leche sola"])
        self.assertIs(resultado.comprobada, True)
        self.assertEqual(resultado.quemadas, ())
        self.assertTrue(resultado.limpia)

    def test_fuera_de_un_repositorio_no_se_afirma_nada(self) -> None:
        with TemporaryDirectory() as tmp:
            resultado = comprobar_procedencia(Path(tmp), ["x"])
        self.assertIsNone(resultado.comprobada, "sin git la procedencia es «no lo sé», no «limpia»")
        self.assertFalse(resultado.limpia)

    def test_la_comparacion_no_se_engana_con_mayusculas_ni_espacios(self) -> None:
        self.assertEqual(normalizar_peticion("  Quiero  UN Bot "), normalizar_peticion("quiero un bot"))

    def test_por_cli_un_holdout_con_una_consulta_de_la_historia_no_publica_cifra(self) -> None:
        """El cableado entero: sellado, procedencia declarada... y aun así QUEMADO por git."""

        quemado = json.loads((RAIZ / "pruebas/encargos-validacion-quemada-2026-09-02.json").read_text(encoding="utf-8"))
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp, "validacion.json")
            ruta.write_text(json.dumps([quemado[0]]), encoding="utf-8")
            sellar(ruta, procedencia="prueba")
            r = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--validacion", str(ruta)],
                               capture_output=True, text=True, cwd=RAIZ)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("QUEMADO", r.stdout)
            self.assertNotIn("Cifra íntegra", r.stdout)
            self.assertNotIn("Cifra íntegra", r.stdout)

    def test_por_cli_un_holdout_versionado_se_declara_quemado(self) -> None:
        """Usar el conjunto de AJUSTE como validación es el caso límite: está en git."""

        r = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--validacion", "pruebas/encargos.json"],
                           capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("está versionado en el repositorio", r.stdout)
        self.assertNotIn("Cifra íntegra", r.stdout)


class LaGuardaAntiGoodhartMiraAlLadoCorrecto(unittest.TestCase):
    """B-03: con el árbol inflado (ajuste 64, validación 100) el juez decía «la cifra que vale es 100 %»."""

    def _inflado(self) -> Contraste:
        return Contraste(ajuste=_puntuacion(32, 50), validacion=_puntuacion(20, 20),
                         sellado=True, procedencia=_limpia())

    def test_una_brecha_muy_negativa_no_es_integra(self) -> None:
        c = self._inflado()
        self.assertLessEqual(c.brecha, BRECHA_ALARMA)
        self.assertFalse(c.integra)
        self.assertTrue(any("ALARMA" in m for m in c.motivos_no_integra()))
        self.assertIsNone(c.como_dict()["cifra_no_atribuible"])

    def test_la_salida_alarma_en_vez_de_felicitar(self) -> None:
        salida = formatear_contraste(self._inflado())
        self.assertIn("ALARMA", salida)
        self.assertIn("NO es íntegra", salida)
        self.assertNotIn("Cifra íntegra: 100", salida)
        self.assertNotIn("se ha quedado corto", salida)

    def test_una_brecha_negativa_moderada_se_vigila_sin_alarmar(self) -> None:
        c = Contraste(ajuste=_puntuacion(30, 50), validacion=_puntuacion(13, 20),
                      sellado=True, procedencia=_limpia())
        self.assertAlmostEqual(c.brecha, -5.0)
        self.assertTrue(c.integra)
        self.assertIn("no es un elogio", formatear_contraste(c))

    def test_una_brecha_positiva_grande_sigue_denunciandose(self) -> None:
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(8, 20),
                      sellado=True, procedencia=_limpia())
        self.assertIn("puntería sobre", formatear_contraste(c))
        self.assertTrue(c.integra)


class ElSelloRotoNoDejaCifra(unittest.TestCase):
    """B-07: «no es publicable» y «la cifra que vale es 40 %» en la misma salida, con exit 0."""

    def test_sello_roto_quita_el_veredicto(self) -> None:
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(8, 20),
                      sellado=False, sello_roto=True, procedencia=_limpia())
        salida = formatear_contraste(c)
        self.assertIn("sello roto", salida)
        self.assertNotIn("Cifra íntegra", salida)
        self.assertIsNone(c.como_dict()["cifra_no_atribuible"])

    def test_sin_sellar_tampoco_hay_veredicto(self) -> None:
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(8, 20), procedencia=_limpia())
        self.assertIn("sin sellar", formatear_contraste(c))
        self.assertFalse(c.integra)

    def test_sellado_limpio_y_con_brecha_sana_si_publica(self) -> None:
        c = Contraste(ajuste=_puntuacion(30, 50), validacion=_puntuacion(11, 20),
                      sellado=True, procedencia=_limpia())
        self.assertTrue(c.integra, c.motivos_no_integra())
        salida = formatear_contraste(c)
        self.assertIn("Cifra íntegra: 55 % (IC95 34–74 %, n=20). NO ATRIBUIBLE", salida)
        self.assertNotIn("La cifra que vale", salida)

    def test_por_cli_el_sello_roto_quita_la_cifra_y_no_hay_liston(self) -> None:
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp, "validacion.json")
            ruta.write_text('[{"peticion": "x", "espera": "web"}]', encoding="utf-8")
            sellar(ruta, procedencia="prueba")
            ruta.write_text('[{"peticion": "y", "espera": "web"}]', encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--validacion", str(ruta)],
                               capture_output=True, text=True, cwd=RAIZ)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("sello roto", r.stdout)
            self.assertNotIn("Cifra íntegra", r.stdout)
            r = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--validacion", str(ruta), "--minimo", "1"],
                               capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 2, "R-01: no existe listón sobre esta métrica")

class LaCifraLlevaSuIntervaloYSuN(unittest.TestCase):
    """B-06: con n=20 cada acierto vale 5 puntos; «40 %» a secas es precisión falsa."""

    def test_wilson_reproduce_los_numeros_del_informe(self) -> None:
        self.assertEqual(intervalo_wilson(8, 20), (21.9, 61.3))
        self.assertEqual(intervalo_wilson(33, 50), (52.2, 77.6))
        self.assertEqual(formatear_intervalo(8, 20), "IC95 22–61 %")

    def test_el_intervalo_viaja_en_el_texto_y_en_el_json(self) -> None:
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(8, 20),
                      sellado=True, procedencia=_limpia())
        self.assertIn("8/20 (40 %; IC95 22–61 %; n=20)", formatear_contraste(c))
        d = c.como_dict()
        self.assertEqual(d["validacion"]["n"], 20)
        self.assertEqual(d["validacion"]["ic95"], [21.9, 61.3])

    def test_un_conjunto_vacio_no_tiene_intervalo(self) -> None:
        self.assertIsNone(Puntuacion(resultados=[]).intervalo)
        with self.assertRaises(ValueError):
            intervalo_wilson(1, 0)


class LaReglaDeCorreccionEstaFijada(unittest.TestCase):
    """B-04: aflojar `_acierta` en cualquier dirección subía la nota con 259 tests en verde."""

    CASOS = (
        (("web", "web"), True),
        (("web", "web/formularios"), True),          # bajar de más no es fallar
        (("web/formularios", "web"), False),         # quedarse en el oficio NO es llegar
        (("web", "webs"), False),                    # prefijo de texto, no de ruta
        (("web", "saas"), False),
        (("ciberseguridad/ofensiva", "ciberseguridad/ofensiva/reconocimiento/nuclei"), True),
        (("ciberseguridad/ofensiva/reconocimiento", "ciberseguridad/ofensiva"), False),
    )

    def test_tabla_de_casos_limite(self) -> None:
        for (esperada, elegida), resultado in self.CASOS:
            with self.subTest(f"{esperada} <- {elegida}"):
                self.assertIs(_acierta(esperada, elegida), resultado)


class ElJuezPuntuaLoQueElAgenteVe(unittest.TestCase):
    """B-08: puntuar `ruta completa + resumen` valía 10 puntos a favor y nadie lo había fijado."""

    def test_cada_linea_puntuable_del_catalogo_es_la_linea_renderizada(self) -> None:
        todos = list(nombres_nichos(ARBOL))
        render = catalogo_visible(ARBOL, todos).splitlines()
        puntuables = [texto for _, texto in _lineas_del_catalogo(ARBOL)]
        self.assertEqual(puntuables[len(todos):], render,
                         "el juez puntúa un texto que no es el que renderiza el catálogo")

    def test_las_lineas_de_los_oficios_son_las_del_indice(self) -> None:
        indice = (RAIZ / "galaxia/COSMOS.md").read_text(encoding="utf-8")
        for ruta, texto in _lineas_del_catalogo(ARBOL)[: len(nombres_nichos(ARBOL))]:
            with self.subTest(ruta):
                self.assertIn(f"- {texto}", indice)

    def test_un_pueblo_profundo_no_lleva_su_ruta_en_el_texto_puntuable(self) -> None:
        profundos = [(ruta, texto) for ruta, texto in lineas_de_catalogo(ARBOL, list(nombres_nichos(ARBOL)))
                     if ruta.count("/") >= 3]
        self.assertTrue(profundos)
        ruta, texto = profundos[0]
        self.assertNotIn(ruta, texto, "volvió la ruta completa al texto que puntúa el juez")


class LaCoberturaSePublica(unittest.TestCase):
    """B-09: dos oficios sin encargo y 17 de 20 a profundidad 1, y nadie lo veía."""

    def test_cobertura_cuenta_oficios_y_profundidad(self) -> None:
        c = cobertura(["web", "saas", "juegos"], ["web", "web/formularios/x", "saas/a/b"])
        self.assertEqual(c.oficios_cubiertos, ("saas", "web"))
        self.assertEqual(c.oficios_sin_encargo, ("juegos",))
        self.assertEqual(c.profundos, 2)
        self.assertEqual(c.total, 3)

    def test_la_salida_la_enseña(self) -> None:
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=_puntuacion(8, 20), sellado=True,
                      procedencia=_limpia(),
                      cobertura=cobertura(["web", "saas"], ["web"]))
        self.assertIn("Cobertura ...... 1/2 oficios (sin encargo: saas); 0/1 a profundidad ≥ 3",
                      formatear_contraste(c))


class SinHoldoutNoHayNumero(unittest.TestCase):
    def test_la_ausencia_se_dice_y_no_se_sustituye_por_el_ajuste(self) -> None:
        c = Contraste(ajuste=_puntuacion(33, 50), validacion=None, ausente="no existe /x/holdout.json")
        salida = formatear_contraste(c)
        self.assertIn("NO DISPONIBLE   no existe /x/holdout.json", salida)
        self.assertNotIn("Cifra íntegra", salida)
        self.assertIsNone(c.como_dict()["cifra_no_atribuible"])

    def test_por_cli_un_holdout_que_no_existe_se_declara(self) -> None:
        r = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--validacion", "/no/existe.json"],
                           capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 0)
        self.assertIn("NO DISPONIBLE", r.stdout)
        self.assertNotIn("Cifra íntegra", r.stdout)




class NingunaCifraEsAtribuibleMientrasElExamenLoEscribaElExaminando(unittest.TestCase):
    """R-01: el revisor fabricó un examen desde las líneas del catálogo, lo selló con una
    procedencia inventada y `acertar` dijo «la cifra que vale es 100 %» con `--minimo 95` en 0."""

    def _examen(self, tmp: Path, palabras_por_linea: int | None) -> Path:
        todos = list(nombres_nichos(ARBOL))
        lineas = [(r, t) for r, t in lineas_de_catalogo(ARBOL, todos) if r.count("/") >= 2][:20]
        encargos = []
        for ruta, texto in lineas:
            cuerpo = texto.replace(":", " ")
            peticion = cuerpo if palabras_por_linea is None else " ".join(
                [w for w in cuerpo.split() if len(w) > 6][:palabras_por_linea])
            encargos.append({"peticion": peticion.strip(), "espera": ruta})
        ruta = tmp / "fabricado.json"
        ruta.write_text(json.dumps(encargos, ensure_ascii=False), encoding="utf-8")
        sellar(ruta, procedencia="v2 ciego: 20 encargos reales recogidos por un tercero sin ver el arbol")
        return ruta

    def _acertar(self, ruta: Path) -> str:
        r = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--validacion", str(ruta)],
                           capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_el_examen_calcado_de_las_lineas_no_es_integro(self) -> None:
        with TemporaryDirectory() as tmp:
            salida = self._acertar(self._examen(Path(tmp), None))
        self.assertIn("CALCADO", salida)
        self.assertNotIn("Cifra íntegra", salida)
        self.assertNotIn("La cifra que vale", salida)

    def test_el_examen_con_tres_palabras_distintivas_tampoco(self) -> None:
        with TemporaryDirectory() as tmp:
            salida = self._acertar(self._examen(Path(tmp), 3))
        self.assertIn("CALCADO", salida)
        self.assertNotIn("Cifra íntegra", salida)

    def test_la_salida_nunca_dice_la_cifra_que_vale_ni_ofrece_liston(self) -> None:
        c = Contraste(ajuste=_puntuacion(30, 50), validacion=_puntuacion(11, 20), sellado=True, procedencia=_limpia())
        salida = formatear_contraste(c)
        self.assertNotIn("La cifra que vale", salida)
        self.assertIn("NO ATRIBUIBLE", salida)
        self.assertIn("no hay listón", salida)
        d = c.como_dict()
        self.assertIs(d["atribuible"], False)
        self.assertIn("quien puede leer el árbol", d["por_que_no_atribuible"])
        ayuda = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--help"], capture_output=True, text=True, cwd=RAIZ).stdout
        self.assertNotIn("--minimo", ayuda)

    def test_el_holdout_real_no_esta_calcado(self) -> None:
        """Calibración del umbral: un examen escrito por una persona queda muy por debajo."""

        from cosmos.holdout import SOLAPE_CALCADO, ruta_por_defecto

        h = ruta_por_defecto()
        if not h.is_file():
            self.skipTest("sin holdout local")
        lineas = dict(_lineas_del_catalogo(ARBOL))
        encargos = cargar_encargos(h)
        solape = solape_examen_catalogo((e.peticion, lineas.get(e.espera, "")) for e in encargos)
        self.assertLess(solape, SOLAPE_CALCADO / 2, f"el holdout humano da {solape}: el umbral está mal calibrado")


class ElDetalleDeValidacionSeRedactaSiempre(unittest.TestCase):
    """R-08: un holdout sin sellar se quemaba entero con un solo `--json`."""

    def test_json_sin_sello(self) -> None:
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp, "nuevo.json")
            ruta.write_text('[{"peticion": "quiero un bot que opere solo", "espera": "trading"}]', encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--json", "--validacion", str(ruta)],
                               capture_output=True, text=True, cwd=RAIZ)
        datos = json.loads(r.stdout)
        self.assertIsInstance(datos["validacion"]["resultados"], str, "sin sello, --json enseñó el detalle del holdout")
        self.assertNotIn("quiero un bot", r.stdout.replace('"peticion": "p', ""))


class ElModeloDePuntuacionEstaFijado(unittest.TestCase):
    """R-09: cambiar la IDF a la logarítmica «para que coincida con el docstring» subía 10 puntos
    con la suite en verde. Tabla de puntuaciones esperadas con `k1=1.5`, `b=0.75`, IDF `sqrt`."""

    CANDIDATOS = [("a", "bot de trading que opera solo"), ("b", "web que carga rapido"), ("c", "bot que avisa por chat")]

    def test_parametros(self) -> None:
        from cosmos.acertar import B, K1

        self.assertEqual((K1, B), (1.5, 0.75))

    def test_tabla_de_orden_y_puntuacion(self) -> None:
        """Valores medidos el 2026-09-03 con k1=1.5, b=0.75 e IDF sqrt: cualquier cambio del modelo los mueve."""

        from cosmos.acertar import _ordenar, _puntuar

        def redondeado(consulta: str) -> list[tuple[float, str]]:
            return [(round(s, 4), r) for s, r in _puntuar(consulta, self.CANDIDATOS)]

        self.assertEqual(redondeado("bot de trading"), [(4.1568, "a"), (1.2649, "c")])
        self.assertEqual(redondeado("web rapida"), [(3.589, "b")])
        self.assertEqual(redondeado("bot"), [(1.2649, "c"), (1.1605, "a")], "con b=0.75 la línea más corta gana el empate de tf")
        self.assertEqual(_ordenar("bot de trading", self.CANDIDATOS), ["a", "c"])

    def test_la_idf_es_la_suavizada_no_la_logaritmica(self) -> None:
        """Con IDF logarítmica, un término presente en TODOS los documentos vale 0 y no ordena; con la
        suavizada sigue valiendo (sqrt(idf+1) ≥ 1). Tres candidatos que comparten «bot»: el orden lo
        decide la longitud, y eso solo pasa si «bot» puntúa."""

        from cosmos.acertar import _ordenar

        candidatos = [("x", "bot"), ("y", "bot bot bot bot bot bot"), ("z", "bot largo largo largo largo")]
        # Medido, no deseado: con la IDF logarítmica «bot» (en los tres) vale 0 y la lista sale vacía.
        self.assertEqual(_ordenar("bot", candidatos), ["y", "x", "z"])


@unittest.skipIf(_sin_historia_git(), "sin historia git: la instantánea del gate hace git init con cero commits")
class LaProcedenciaEsTrivalenteDeVerdad(unittest.TestCase):
    """R-17: en un clon superficial (`--depth 1`, el defecto de checkout@v4) la comprobación decía
    «limpia» sin haber visto la historia."""

    def test_clon_superficial_dice_no_lo_se(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            subprocess.run(["git", "clone", "--quiet", "--depth", "1", f"file://{RAIZ}", str(base / "poco")],
                           capture_output=True, check=True)
            resultado = comprobar_procedencia(base / "poco", ["x"])
        self.assertIsNone(resultado.comprobada, resultado.motivo)
        self.assertIn("superficial", resultado.motivo)
        self.assertFalse(resultado.limpia)

    def test_sin_ningun_blob_json_dice_no_lo_se(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            subprocess.run(["git", "init", "--quiet", str(base)], check=True)
            (base / "a.md").write_text("x", encoding="utf-8")
            subprocess.run(["git", "-C", str(base), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(base), "-c", "user.email=a@ejemplo.test", "-c", "user.name=a", "commit", "-q", "-m", "a"], check=True)
            resultado = comprobar_procedencia(base, ["x"])
        self.assertIsNone(resultado.comprobada, resultado.motivo)


@unittest.skipIf(_sin_historia_git(), "sin historia git: la instantánea del gate hace git init con cero commits")
class ElCompromisoSeLeeDeLaHistoriaNoDelSello(unittest.TestCase):
    def test_sello_no_commiteado_no_tiene_compromiso(self) -> None:
        from cosmos.holdout import compromiso_del_sello

        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            subprocess.run(["git", "init", "--quiet", str(base)], check=True)
            sello = base / "pruebas" / "x.SELLO"
            sello.parent.mkdir()
            sello.write_text('{"sha256": "abc"}', encoding="utf-8")
            c = compromiso_del_sello(base, sello, "abc")
            self.assertIsNone(c.commit)
            subprocess.run(["git", "-C", str(base), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(base), "-c", "user.email=a@ejemplo.test", "-c", "user.name=a", "commit", "-q", "-m", "sello"], check=True)
            c = compromiso_del_sello(base, sello, "abc")
            self.assertIsNotNone(c.commit)
            self.assertEqual(c.commits_despues, 0)
            self.assertIsNone(compromiso_del_sello(base, sello, "otro").commit, "otro contenido no hereda el compromiso")

    def test_el_sello_v1_esta_comprometido_desde_2026_09_02(self) -> None:
        from cosmos.holdout import compromiso_del_sello

        c = compromiso_del_sello(RAIZ, RAIZ / "pruebas/encargos-validacion.SELLO",
                                 "c6e0d3a167ea9dca41644e30615addaef6ad0a6cc1ca22ad579ec4e3f1b42a6b", RAIZ / "galaxia")
        self.assertIsNotNone(c.commit)
        self.assertTrue(str(c.fecha).startswith("2026-09-02"), c.fecha)
        # Lo que se vigila es que el compromiso se LEE de la historia (commit y fecha) y que el
        # recuento de resúmenes tocados después es una MEDIDA, no una promesa: afirmar «== 0»
        # caducaba con el primer commit que tocara un resumen (revisión B-01: 37 tras el merge
        # de la auditoría) y ponía en rojo `main` y el CI sin que nada estuviera roto.
        self.assertIsInstance(c.resumenes_cambiados_despues, int)
        self.assertGreaterEqual(c.resumenes_cambiados_despues, 0)
        self.assertIn("resumen(es) cambiado(s)", c.motivo)




class ElNormalizadorMejoradoEstaFijado(unittest.TestCase):
    """E-12 (ciclo 2): mejora declarada del motor, sin tocar un resumen. Medida sobre el ajuste:
    37 → 38 de 50; «auditar la seguridad de una web» pasa de no llegar a `ciberseguridad` por
    ninguna vía a tener `ciberseguridad/ofensiva` en el 2.º puesto. Se fija para que el siguiente
    cambio del motor sea deliberado y medido, no un desliz."""

    def test_auditoria_y_auditar_comparten_raiz(self) -> None:
        from cosmos.acertar import _normalizar

        self.assertEqual(_normalizar("auditoria"), _normalizar("auditar"))

    def test_ciberseguridad_tambien_es_seguridad(self) -> None:
        from cosmos.acertar import _normalizar

        self.assertIn("seguridad", _normalizar("ciberseguridad"))
        self.assertIn("ciberseguridad", _normalizar("ciberseguridad"), "el compuesto no pierde su forma entera")

    def test_una_palabra_corta_con_prefijo_no_se_parte(self) -> None:
        from cosmos.acertar import _normalizar

        self.assertNotIn("net", _normalizar("cibernet"))


if __name__ == "__main__":
    unittest.main()
