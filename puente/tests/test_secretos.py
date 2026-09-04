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

# Los cebos se arman en tiempo de ejecución, nunca literales: un fichero de pruebas
# con secretos enteros dentro hace que el escáner se denuncie a sí mismo, y entonces
# el gate se queda en rojo para siempre o alguien lo silencia con una excepción.
SECRETOS = {
    "clave privada": b"-----BEGIN RSA " + b"PRIVATE KEY-----\nMIIE\n",
    "token GitHub": b'token = "ghp_' + b"A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7" + b'"\n',
    "clave AWS": b"AKIA" + b"IOSFODNN7EXAMPLE\n",
    "secreto asignado": b'api_key = "' + b"aB3xK9mQ2pL7vN4tR8wY" + b'"\n',
    "URI con credencial": b"postgres:" + b"//usuario:Zx91kdLL2mQ@" + b"servidor.interno/base\n",
    "correo electrónico": b"contacto = persona.apellido@" + b"servidor-interno.local\n",
    "IBAN asignado": b'iban = "' + b"ES9121000418450200051332" + b'"\n',
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
            self.assertNotIn("aB3x" "K9mQ2pL7vN4tR8wY", hallazgo)
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




class LaExcepcionIndultaUnValorNoUnFichero(unittest.TestCase):
    """Auditoría F-01: la lista de excepciones comparaba (fichero × clase) y blanqueaba el
    fichero entero para esa clase. Dos credenciales nuevas y distintas atravesaron el gate
    con exit 0 y «limpio de nuevos». Desde hoy la clave es el valor."""

    def test_dos_valores_distintos_de_la_misma_clase_son_dos_hallazgos(self) -> None:
        datos = SECRETOS["clave AWS"] + b"otra = AKIA" + b"ZZZZZZZZZZZZZZZZ\n"
        hallazgos = [h for h in _hallazgos(datos) if "clave AWS" in h]
        self.assertEqual(len(hallazgos), 2, hallazgos)
        self.assertNotEqual(hallazgos[0].split("[valor ")[1], hallazgos[1].split("[valor ")[1])

    def test_el_mismo_valor_repetido_es_un_solo_hallazgo(self) -> None:
        hallazgos = [h for h in _hallazgos(SECRETOS["clave AWS"] * 2) if "clave AWS" in h]
        self.assertEqual(len(hallazgos), 1)

    def test_una_excepcion_por_valor_no_cubre_otro_valor_en_el_mismo_fichero(self) -> None:
        from puente.secretos import separar_conocidos
        from cosmos.guardarrailes import clave_hallazgo

        inventariado = [h for h in _hallazgos(SECRETOS["clave AWS"]) if "clave AWS" in h]
        conocidos = {clave_hallazgo(h) for h in inventariado}
        nuevo = _hallazgos(b"otra = AKIA" + b"ZZZZZZZZZZZZZZZZ\n")
        nuevos, viejos = separar_conocidos(inventariado + nuevo, conocidos)
        self.assertEqual(len(viejos), 1, "el valor inventariado sigue indultado")
        self.assertEqual(len(nuevos), 1, "un valor distinto en el mismo fichero pasó como conocido")

    def test_mover_el_valor_de_linea_no_lo_convierte_en_nuevo(self) -> None:
        from puente.secretos import separar_conocidos
        from cosmos.guardarrailes import clave_hallazgo

        arriba = _hallazgos(SECRETOS["clave AWS"])
        abajo = _hallazgos(b"\n\n\n" + SECRETOS["clave AWS"])
        self.assertNotEqual(arriba, abajo, "el número de línea tiene que cambiar")
        nuevos, _ = separar_conocidos(abajo, {clave_hallazgo(h) for h in arriba})
        self.assertEqual(nuevos, [])

    def test_la_huella_no_ensena_el_valor(self) -> None:
        for hallazgo in _hallazgos(SECRETOS["clave AWS"]):
            self.assertNotIn("IOSFODNN", hallazgo)
            self.assertRegex(hallazgo, r"\[valor [0-9a-f]{12}\]")


class LasRutasDeUnaMaquinaPersonalSaltan(unittest.TestCase):
    """Auditoría F-11: 64 rutas absolutas del Mac del autor y ningún patrón para ellas."""

    def test_una_ruta_de_usuario_salta(self) -> None:
        self.assertTrue(any("ruta de máquina personal" in h
                            for h in _hallazgos(b"cd /Users/" + b"alguien/proyecto\n")))
        self.assertTrue(any("ruta de máquina personal" in h
                            for h in _hallazgos(b"cd /home/" + b"alguien/proyecto\n")))

    def test_las_cuentas_de_servicio_y_los_marcadores_no(self) -> None:
        for texto in (b"-v n8n_data:/home/node/.n8n\n", b"/home/runner/work/\n",
                      b"/Users/<usuario>/repo\n", b"~/cosmos\n"):
            with self.subTest(texto):
                self.assertFalse(any("ruta de máquina personal" in h for h in _hallazgos(texto)))


if __name__ == "__main__":
    unittest.main()
