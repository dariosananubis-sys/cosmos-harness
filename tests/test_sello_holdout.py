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
        self.assertIn("SELLADO", datos["validacion"]["resultados"])
        self.assertEqual(datos["validacion"]["aciertos"], 2, "el agregado sí se publica")

    def test_sin_sello_el_detalle_sigue_saliendo(self) -> None:
        """Pin de la diferencia: la redacción la causa el sello, no el código nuevo."""

        datos = Contraste(ajuste=_puntuacion(3, 5), validacion=_puntuacion(2, 4)).como_dict()
        self.assertIsInstance(datos["validacion"]["resultados"], list)

    def test_el_texto_humano_dice_si_esta_sellado(self) -> None:
        sellado = formatear_contraste(Contraste(_puntuacion(3, 5), _puntuacion(2, 4), sellado=True))
        self.assertIn("SELLADO", sellado)
        sin_sellar = formatear_contraste(Contraste(_puntuacion(3, 5), _puntuacion(2, 4)))
        self.assertIn("SIN SELLAR", sin_sellar)


class ElCliRespetaElSello(unittest.TestCase):
    def test_json_sobre_el_repo_real_no_filtra_el_detalle_de_validacion(self) -> None:
        r = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--json"],
                           capture_output=True, text=True, cwd=RAIZ)
        self.assertEqual(r.returncode, 0)
        datos = json.loads(r.stdout)
        self.assertIsInstance(datos["validacion"]["resultados"], str,
                              "el holdout del repo está sellado y --json enseñó su detalle")
        self.assertIsInstance(datos["ajuste"]["resultados"], list)

    def test_un_sello_desfasado_avisa(self) -> None:
        with TemporaryDirectory() as tmp:
            ruta = Path(tmp, "validacion.json")
            ruta.write_text('[{"peticion": "x", "espera": "web"}]', encoding="utf-8")
            sellar(ruta)
            ruta.write_text('[{"peticion": "y", "espera": "web"}]', encoding="utf-8")
            r = subprocess.run(
                [sys.executable, "-m", "cosmos", "acertar", "--validacion", str(ruta)],
                capture_output=True, text=True, cwd=RAIZ,
            )
        self.assertIn("cambió después de sellarse", r.stderr)


if __name__ == "__main__":
    unittest.main()
