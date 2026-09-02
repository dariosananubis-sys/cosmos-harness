"""Escribir el índice entero, y un cerrojo del que se pueda salir.

Dos fallos hermanos en el mismo sitio:

- **F16**: `escribir_indice` era un `write_text` pelado mientras el manifiesto —menos
  crítico— ya tenía temporal, `fsync` y `os.replace`. El índice **es** el contexto de
  entrada: cortado a medias deja el árbol rojo por E15, y G03 impide arreglarlo a mano.
  Y dos `generar` simultáneos se entrelazaban, porque ninguno tomaba cerrojo.
- **F09**: el cerrojo de `compilar` era un `O_EXCL` a secas. Si el proceso moría sin
  llegar a su `finally` —`kill -9`, batería, terminal cerrada—, el fichero quedaba y
  **toda compilación futura fallaba para siempre**. Un cerrojo que no se puede abrir no
  protege nada: rompe el repositorio.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.modelo import ErrorCerrojo, cerrojo, escribir_atomico


class EscribirEnteroONada(unittest.TestCase):
    def test_deja_el_fichero_completo(self) -> None:
        with TemporaryDirectory() as tmp:
            destino = Path(tmp, "sub", "COSMOS.md")
            escribir_atomico(destino, "contenido\nentero\n")
            self.assertEqual(destino.read_text(encoding="utf-8"), "contenido\nentero\n")

    def test_reemplaza_la_entrada_del_directorio_y_no_el_fichero(self) -> None:
        """La propiedad que separa atómico de `write_text`, y que se puede medir.

        Un primer intento de prueba de rojo no distinguía las dos implementaciones: en el
        caso feliz dan el mismo resultado. Lo que sí las separa es que `os.replace` opera
        sobre la **entrada del directorio**, no sobre el fichero — así que un destino de
        solo lectura, en un directorio escribible, deja pasar la escritura atómica y hace
        fallar a `write_text` con `PermissionError`.

        Y esa es exactamente la propiedad que hace que un corte a mitad no deje el índice
        truncado: nadie escribe nunca sobre el fichero bueno.
        """

        with TemporaryDirectory() as tmp:
            destino = Path(tmp, "COSMOS.md")
            destino.write_text("version buena\n", encoding="utf-8")
            destino.chmod(0o444)
            with self.assertRaises(PermissionError):
                destino.write_text("no deberia entrar\n", encoding="utf-8")
            escribir_atomico(destino, "version nueva\n")
            self.assertEqual(destino.read_text(encoding="utf-8"), "version nueva\n")

    def test_no_deja_temporales_tirados(self) -> None:
        with TemporaryDirectory() as tmp:
            destino = Path(tmp, "COSMOS.md")
            escribir_atomico(destino, "x\n")
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["COSMOS.md"])


class UnCerrojoDelQueSePuedeSalir(unittest.TestCase):
    def test_protege_mientras_alguien_esta_dentro(self) -> None:
        with TemporaryDirectory() as tmp:
            lock = Path(tmp, "x.lock")
            # Un PID que existe y no es el nuestro: el propio proceso padre.
            lock.write_text(f"{os.getppid()}\n", encoding="utf-8")
            with self.assertRaises(ErrorCerrojo) as caso:
                with cerrojo(lock):
                    pass
            self.assertIn("en curso", str(caso.exception))

    def test_un_cerrojo_rancio_se_retoma(self) -> None:
        """F09: el proceso que lo dejó ya no existe. Bloquear para siempre no protege nada."""

        with TemporaryDirectory() as tmp:
            lock = Path(tmp, "x.lock")
            lock.write_text("999999\n", encoding="utf-8")  # PID que no existe
            with cerrojo(lock):
                self.assertTrue(lock.is_file())
            self.assertFalse(lock.is_file())

    def test_un_cerrojo_ilegible_tambien_se_retoma(self) -> None:
        with TemporaryDirectory() as tmp:
            lock = Path(tmp, "x.lock")
            lock.write_text("basura sin pid\n", encoding="utf-8")
            with cerrojo(lock):
                pass
            self.assertFalse(lock.is_file())

    def test_se_suelta_aunque_el_cuerpo_reviente(self) -> None:
        with TemporaryDirectory() as tmp:
            lock = Path(tmp, "x.lock")
            with self.assertRaises(ValueError):
                with cerrojo(lock):
                    raise ValueError("algo falló dentro")
            self.assertFalse(lock.is_file(), "un cerrojo que no se suelta al fallar es el fallo")


if __name__ == "__main__":
    unittest.main()
