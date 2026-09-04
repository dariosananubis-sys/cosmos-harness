"""El holdout se quema con un gesto, y el sello existe para impedir ese gesto.

El conjunto anterior no lo quemó la mala fe: alguien abrió su detalle para ver qué
fallaba y lo contaminó sin querer. Un sello que no impida ESE gesto no sella nada.
El .SELLO ata el sha256 del contenido exacto (editar invalida, como una marca de
lectura), se versiona, y mientras está vigente el detalle por encargo de la
validación no se enseña por ninguna salida — romperlo es borrar el fichero, y ese
gesto queda en git. Aserciones escritas tras medir cada salida.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.acertar import (Contraste, Encargo, Puntuacion, Resultado, formatear_contraste,
                            leer_sello, ruta_sello, sellar, sello_vigente)

RAIZ = Path(__file__).resolve().parent.parent


def _puntuacion(aciertos: int, total: int) -> Puntuacion:
    resultados = [
        Resultado(encargo=Encargo(peticion=f"p{i}", espera="web"), elegida="web",
                  posicion=1 if i < aciertos else None, acierta=i < aciertos)
        for i in range(total)
    ]
    return Puntuacion(resultados=resultados)


class ElSelloAtaElContenidoExacto(unittest.TestCase):
    def test_sellar_y_editar_invalida(self) -> None:
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp, "validacion.json")
            ruta.write_text('[{"peticion": "x", "espera": "web"}]', encoding="utf-8")
            datos = sellar(ruta)
            self.assertEqual(datos["encargos"], 1)
            self.assertTrue(sello_vigente(ruta))
            ruta.write_text('[{"peticion": "x editada", "espera": "web"}]', encoding="utf-8")
            self.assertFalse(sello_vigente(ruta), "el sello sobrevivió a una edición del contenido")
            self.assertIsNotNone(leer_sello(ruta), "el fichero de sello tiene que seguir ahí para avisar")

    def test_un_sello_ilegible_no_es_un_sello(self) -> None:
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp, "validacion.json")
            ruta.write_text("[]", encoding="utf-8")
            ruta_sello(ruta).write_text("no json", encoding="utf-8")
            self.assertFalse(sello_vigente(ruta))


class ElDetallePorEncargoNoSeEnsenaSellado(unittest.TestCase):
    def test_como_dict_redacta_solo_la_validacion(self) -> None:
        contraste = Contraste(ajuste=_puntuacion(3, 5), validacion=_puntuacion(2, 4), sellado=True)
        datos = contraste.como_dict()
        self.assertIsInstance(datos["ajuste"]["resultados"], list,
                              "el ajuste no está sellado: su detalle es legítimo")
        self.assertIsInstance(datos["validacion"]["resultados"], str)
        self.assertIn("REDACTADO", datos["validacion"]["resultados"])
        self.assertEqual(datos["validacion"]["aciertos"], 2, "el agregado sí se publica")

    def test_sin_sello_el_detalle_TAMBIEN_se_redacta(self) -> None:
        """R-08: un holdout recién escrito se quemaba con un solo `--json` porque la redacción
        era opt-in con el sello. El detalle de validación no se enseña nunca; el de ajuste sí."""

        datos = Contraste(ajuste=_puntuacion(3, 5), validacion=_puntuacion(2, 4)).como_dict()
        self.assertIsInstance(datos["validacion"]["resultados"], str)
        self.assertIsInstance(datos["ajuste"]["resultados"], list)

    def test_el_texto_humano_dice_si_esta_sellado(self) -> None:
        sellado = formatear_contraste(Contraste(_puntuacion(3, 5), _puntuacion(2, 4), sellado=True))
        self.assertIn("Cifra íntegra", sellado)
        sin_sellar = formatear_contraste(Contraste(_puntuacion(3, 5), _puntuacion(2, 4)))
        self.assertIn("sin sellar", sin_sellar)
        self.assertNotIn("Cifra íntegra", sin_sellar, "sin sello no hay cifra íntegra")


class ElCliRespetaElSello(unittest.TestCase):
    """Con un holdout de prueba en un temporal: el real vive fuera del repositorio y en
    un clon recién bajado —o en CI— no existe, así que no se puede suponer."""

    def test_json_con_un_holdout_sellado_no_filtra_su_detalle(self) -> None:
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp, "validacion.json")
            ruta.write_text('[{"peticion": "quiero un bot que opere solo", "espera": "trading"}]',
                            encoding="utf-8")
            sellar(ruta, procedencia="prueba")
            r = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--json", "--validacion", str(ruta)],
                               capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 0, r.stderr)
        datos = json.loads(r.stdout)
        self.assertIsInstance(datos["validacion"]["resultados"], str,
                              "--json enseñó el detalle del holdout")
        self.assertIsInstance(datos["ajuste"]["resultados"], list)
        self.assertEqual(datos["procedencia_declarada"], "prueba")

    def test_un_sello_desfasado_avisa_y_quita_la_cifra(self) -> None:
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp, "validacion.json")
            ruta.write_text('[{"peticion": "x", "espera": "web"}]', encoding="utf-8")
            sellar(ruta, procedencia="prueba")
            ruta.write_text('[{"peticion": "y", "espera": "web"}]', encoding="utf-8")
            r = subprocess.run(
                [sys.executable, "-m", "cosmos", "acertar", "--validacion", str(ruta)],
                capture_output=True, text=True, cwd=RAIZ,
            )
        self.assertIn("sello roto", r.stdout)
        self.assertNotIn("Cifra íntegra", r.stdout)

    def test_sellar_exige_procedencia(self) -> None:
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp, "validacion.json")
            ruta.write_text('[{"peticion": "x", "espera": "web"}]', encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--sellar", "--validacion", str(ruta)],
                               capture_output=True, text=True, cwd=RAIZ)
            self.assertEqual(r.returncode, 2)
            self.assertIn("--procedencia", r.stderr)
            self.assertFalse(ruta_sello(ruta).exists())
            r = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--sellar", "--validacion", str(ruta),
                                "--procedencia", "dictado sin ver el árbol"],
                               capture_output=True, text=True, cwd=RAIZ)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(leer_sello(ruta)["procedencia"], "dictado sin ver el árbol")


if __name__ == "__main__":
    unittest.main()
