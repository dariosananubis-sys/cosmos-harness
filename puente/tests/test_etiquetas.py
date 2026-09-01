"""La etiqueta existe para una sola cosa: no dejar ver la ruta que etiqueta."""

from __future__ import annotations

import re
import unittest

from puente.etiquetas import LONGITUD, PREFIJO, etiqueta_de_ruta

TRAMO = re.compile(r"[0-9a-z]{3,}")


class EtiquetaOpaca(unittest.TestCase):
    # Las tres primeras son colisiones reales: su resumen hexadecimal ingenuo
    # contiene un tramo de la propia ruta ('deb', 'dad'), que es exactamente lo
    # que esta función existe para que no ocurra.
    RUTAS = (
        "clientes/deb-cafe/informe.md",
        "src/ade/deb.py",
        "bad/dad",
        "clientes/panaderia-la-esquina/facturas-2026.csv",
        "notas/decafe/beef/dead.md",
        "a/bad/cafe/face/dead/beef/abc.txt",
        ".env.produccion",
        "spec/NUCLEO.md",
    )

    def test_la_etiqueta_no_contiene_ningun_tramo_de_la_ruta(self) -> None:
        for ruta in self.RUTAS:
            with self.subTest(ruta=ruta):
                etiqueta = etiqueta_de_ruta(ruta)
                cuerpo = etiqueta[len(PREFIJO) :]
                tramos = {t.group(0) for t in TRAMO.finditer(ruta.lower())}
                for tramo in tramos:
                    self.assertNotIn(tramo, cuerpo, f"{tramo!r} visible en {etiqueta}")

    def test_es_estable_y_no_distingue_texto_de_bytes(self) -> None:
        ruta = "clientes/panaderia-la-esquina/facturas-2026.csv"
        self.assertEqual(etiqueta_de_ruta(ruta), etiqueta_de_ruta(ruta))
        self.assertEqual(etiqueta_de_ruta(ruta), etiqueta_de_ruta(ruta.encode("utf-8")))

    def test_rutas_distintas_dan_etiquetas_distintas(self) -> None:
        etiquetas = {etiqueta_de_ruta(ruta) for ruta in self.RUTAS}
        self.assertEqual(len(etiquetas), len(self.RUTAS))

    def test_forma_de_la_etiqueta(self) -> None:
        etiqueta = etiqueta_de_ruta("spec/NUCLEO.md")
        self.assertTrue(etiqueta.startswith(PREFIJO))
        self.assertLessEqual(len(etiqueta) - len(PREFIJO), LONGITUD + LONGITUD // 2)


if __name__ == "__main__":
    unittest.main()
