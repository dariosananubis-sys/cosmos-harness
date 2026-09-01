"""Un secreto plantado tiene que saltar; el ruido típico, no.

El ruido no es un defecto estético: una herramienta que grita por cada
'obtener_clave_del_entorno' se desactiva, y desactivada no encuentra nada.
"""

from __future__ import annotations

import io
import unittest

from puente.etiquetas import etiqueta_de_ruta
from puente.secretos import _hallazgos_de_ruta, escanear_flujo

RUTA = b"src/configuracion.py"

SECRETOS = {
    "clave privada": b"-----BEGIN RSA PRIVATE KEY-----\nMIIE\n",
    "token GitHub": b'token = "ghp_' + b"A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7" + b'"\n',
    "clave AWS": b"AKIAIOSFODNN7EXAMPLE\n",
    "secreto asignado": b'api_key = "aB3xK9mQ2pL7vN4tR8wY"\n',
    "URI con credencial": b"postgres://usuario:Zx91kdLL2mQ@servidor.interno/base\n",
    "IBAN asignado": b'iban = "ES9121000418450200051332"\n',
}

RUIDO = (
    b'token = os.environ["SERVICIO_TOKEN"]\n',
    b"api_key = configuracion.obtener_clave_del_entorno\n",
    b"password = get_password_from_vault()\n",
    b'GITHUB_TOKEN = os.getenv("GITHUB_TOKEN_DE_INTEGRACION")\n',
    b"secret_key = settings.SECRETO_DE_LA_APLICACION_WEB\n",
    b'api_key = "example"\n',
    b'correo = "alguien@example.com"\n',
    b'contacto = "nadie@dominio.invalid"\n',
)


def _hallazgos(datos: bytes) -> list[str]:
    return escanear_flujo(io.BytesIO(datos), RUTA)


class SecretosPlantados(unittest.TestCase):
    def test_cada_secreto_plantado_se_detecta(self) -> None:
        for etiqueta, datos in SECRETOS.items():
            with self.subTest(secreto=etiqueta):
                hallazgos = _hallazgos(datos)
                self.assertTrue(
                    any(etiqueta in hallazgo for hallazgo in hallazgos),
                    f"{etiqueta} no detectado: {hallazgos}",
                )

    def test_el_hallazgo_no_filtra_el_valor_ni_la_ruta(self) -> None:
        hallazgos = _hallazgos(SECRETOS["secreto asignado"])
        self.assertTrue(hallazgos)
        for hallazgo in hallazgos:
            self.assertIn(etiqueta_de_ruta(RUTA), hallazgo)
            self.assertNotIn("aB3xK9mQ2pL7vN4tR8wY", hallazgo)
            self.assertNotIn("configuracion", hallazgo)


class SinRuido(unittest.TestCase):
    def test_las_expresiones_que_se_llaman_como_un_secreto_no_saltan(self) -> None:
        for linea in RUIDO:
            with self.subTest(linea=linea.decode().strip()):
                self.assertEqual(_hallazgos(linea), [], linea.decode())

    def test_un_fichero_de_codigo_normal_esta_limpio(self) -> None:
        fuente = b"".join(RUIDO) + b"\ndef principal():\n    return 0\n"
        self.assertEqual(_hallazgos(fuente), [])


class RutasProhibidas(unittest.TestCase):
    def test_la_vista_plana_generada_no_es_versionable(self) -> None:
        hallazgos = _hallazgos_de_ruta(b".claude/skills/medir-anchos")
        self.assertTrue(any("vista plana" in hallazgo for hallazgo in hallazgos))

    def test_un_env_versionado_salta_y_su_ejemplo_no(self) -> None:
        self.assertTrue(_hallazgos_de_ruta(b".env"))
        self.assertEqual(_hallazgos_de_ruta(b".env.example"), [])


if __name__ == "__main__":
    unittest.main()
