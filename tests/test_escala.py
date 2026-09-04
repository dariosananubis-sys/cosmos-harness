"""¿En qué número se rompe? Nadie lo sabía, y por eso esta prueba existe.

`GOAL.md` §2 dice que el coste tiene que crecer con **lo que se usa**, no con lo que
existe. El contenido cumple: un pueblo no se carga hasta que se entra en él. El **mapa**
no: `NUCLEO.md` §2 fija que continentes, países y provincias aparecen siempre, porque
«forman el mapa de descenso». Con 21 oficios sale barato. La pregunta que nadie había
medido es cuándo deja de salir barato.

Esta prueba no propone cambiar esa decisión: la **instrumenta**. Genera árboles
sintéticos cada vez más grandes y afirma lo medido, no lo deseado — el número real en el
que la entrada rebasa el presupuesto, para que la conversación se tenga con datos.

Corolario que sí se afirma: el coste del mapa crece con el universo entero y el del
contenido no. Si algún día el mapa dejara de crecer así, esta prueba se pondría roja y
querría decir que alguien adoptó la propuesta 4 — momento de actualizarla, no de
silenciarla.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cosmos.medir import medir_arbol
from cosmos.modelo import cargar_arbol

RAIZ = Path(__file__).resolve().parent.parent

PRESUPUESTO = 4000


def _escribir(base: Path, ruta: str, campos: dict[str, str], cuerpo: str = "") -> None:
    destino = base / ruta
    destino.parent.mkdir(parents=True, exist_ok=True)
    cabecera = ["---"] + [f"{k}: {v}" for k, v in campos.items()] + ["---", ""]
    destino.write_text("\n".join(cabecera) + cuerpo + "\n", encoding="utf-8")


def _arbol_sintetico(base: Path, oficios: int, paises_por_oficio: int, pueblos_por_pais: int) -> None:
    """Un universo de juguete con la misma forma que el real: oficio > país > pueblo."""

    _escribir(base, "galaxia.md", {"cosmos": "galaxia", "nombre": "escala",
                                   "resumen": "Arbol sintetico para medir el coste del mapa."})
    for o in range(oficios):
        oficio = f"oficio{o:02d}"
        _escribir(base, f"sistemas/{oficio}.md",
                  {"cosmos": "sistema-solar", "nombre": oficio, "padre": '""',
                   "resumen": f"Resumen del oficio numero {o}, con la longitud tipica de uno real."})
        for p in range(paises_por_oficio):
            pais = f"pais{p:02d}"
            _escribir(base, f"paises/{oficio}--{pais}.md",
                      {"cosmos": "pais", "nombre": pais, "padre": oficio,
                       "resumen": f"Resumen del pais {p} del oficio {o}, tambien de longitud tipica."})
            for h in range(pueblos_por_pais):
                _escribir(base, f"pueblos/{oficio}-{pais}-h{h:02d}/SKILL.md",
                          {"cosmos": "pueblo", "nombre": f"{oficio}-{pais}-h{h:02d}",
                           "padre": f"{oficio}/{pais}",
                           "resumen": f"Herramienta {h} que hace algo concreto y util en su hueco."},
                          "Cuerpo de la ficha, que no se carga hasta invocarla.")


def _entrada_con_un_nicho(oficios: int, paises: int = 2, pueblos: int = 10) -> int:
    with TemporaryDirectory() as tmp:
        base = Path(tmp)
        _arbol_sintetico(base, oficios, paises, pueblos)
        arbol = cargar_arbol(base)
        return medir_arbol(arbol, nichos=["oficio00"]).entrada


# Densidad del árbol real (medida con `cosmos estado`): 21 oficios, 42 países, 6
# continentes. Dos países por oficio, que es lo que usan los árboles sintéticos de
# aquí para que la extrapolación no sea una suposición cómoda.
PAISES_POR_OFICIO = 2


class ElCosteDelMapaCreceConElUniverso(unittest.TestCase):
    def test_el_mapa_cuesta_lo_mismo_se_trabaje_o_no_en_el(self) -> None:
        """El contenido es perezoso; el mapa no. Aquí está la pendiente, medida.

        Mismo nicho activo y mismos pueblos cargados en los dos árboles: todo lo que
        sube al añadir oficios en los que nadie trabaja es mapa. Medido: unos 23 tokens
        por oficio, constante — crece con lo que existe, no con lo que se usa, que es
        justo lo que `GOAL.md` §2 llama el problema.
        """

        medidas = {n: _entrada_con_un_nicho(n) for n in (10, 40, 80)}
        pendiente_baja = (medidas[40] - medidas[10]) / 30
        pendiente_alta = (medidas[80] - medidas[40]) / 40

        self.assertGreater(pendiente_baja, 15, "el mapa dejó de crecer: revisa si se adoptó la propuesta 4")
        # Lineal, no amortiguada: la segunda pendiente no baja respecto a la primera.
        self.assertAlmostEqual(pendiente_alta, pendiente_baja, delta=5)

    def test_el_punto_de_rotura_esta_medido_y_no_supuesto(self) -> None:
        """Afirma el número medido. Si el diseño cambia, esta prueba lo canta."""

        rotura = next(
            (n for n in range(10, 301, 10) if _entrada_con_un_nicho(n) > PRESUPUESTO),
            None,
        )
        self.assertIsNotNone(rotura, "no se rompió ni con 300 oficios: el mapa dejó de crecer")
        # Medido: 150 oficios con 2 países y 10 herramientas cada uno. El rango es ancho
        # a propósito — fija el orden de magnitud, no un número que se mueva al tocar un
        # resumen. Lo que importa del dato: el techo existe y está lejos de los 21 de hoy,
        # pero no tan lejos como para no planearlo.
        self.assertIn(rotura, range(100, 221), f"punto de rotura medido: {rotura} oficios")

    def test_una_herramienta_de_otro_oficio_no_cuesta_nada(self) -> None:
        """El contrapunto: lo que SÍ es perezoso tiene que seguir siéndolo.

        Se comparan dos árboles con los mismos pueblos en el nicho activo y muy
        distinto número fuera. Si lo de fuera costara, la entrada subiría.
        """

        def entrada(pueblos_fuera: int) -> int:
            with TemporaryDirectory() as tmp:
                base = Path(tmp)
                _escribir(base, "galaxia.md", {"cosmos": "galaxia", "nombre": "escala",
                                               "resumen": "Arbol sintetico para medir el coste del mapa."})
                for o in range(6):
                    oficio = f"oficio{o:02d}"
                    _escribir(base, f"sistemas/{oficio}.md",
                              {"cosmos": "sistema-solar", "nombre": oficio, "padre": '""',
                               "resumen": f"Resumen del oficio numero {o}, con longitud tipica."})
                    _escribir(base, f"paises/{oficio}--unico.md",
                              {"cosmos": "pais", "nombre": "unico", "padre": oficio,
                               "resumen": f"Unico pais del oficio {o}, de longitud tipica."})
                    cuantos = 5 if o == 0 else pueblos_fuera
                    for h in range(cuantos):
                        _escribir(base, f"pueblos/{oficio}-h{h:02d}/SKILL.md",
                                  {"cosmos": "pueblo", "nombre": f"{oficio}-h{h:02d}",
                                   "padre": f"{oficio}/unico",
                                   "resumen": f"Herramienta {h} que hace algo concreto en su hueco."},
                                  "Cuerpo que no se carga hasta invocar.")
                return medir_arbol(cargar_arbol(base), nichos=["oficio00"]).entrada

        self.assertEqual(entrada(2), entrada(30), "un pueblo de otro oficio está costando")




class LosArreglosDeRendimientoSeCuentanNoSeCreen(unittest.TestCase):
    """Revisión R-47: cuatro arreglos de rendimiento sin ninguna prueba, y por ahí se coló D-06
    entregado sin hacer (un `setdefault` que no cacheaba: 1.056 → 1.089 parseos, firmado por
    las 320 pruebas). Se cuentan llamadas, que es inmune a la contención de CPU."""

    def _arbol(self):
        from cosmos.modelo import cargar_arbol, cargar_configuracion

        cfg = cargar_configuracion(RAIZ / "cosmos.toml")
        return cfg, cargar_arbol(cfg.arbol, tambien=(cfg.registro,) if cfg.registro else ())

    def test_d06_e17_parsea_cada_co_cargable_una_sola_vez(self) -> None:
        from unittest import mock

        import cosmos.validar as v

        cfg, arbol = self._arbol()
        # En vista anfitrión E17 compara solo los nodos del anfitrión: los que parsea son esos.
        n = len(v._co_cargables(arbol, solo_anfitrion=cfg.vista_compilacion == "anfitrion"))
        real, cuenta = v._afirmaciones, {"n": 0}

        def espia(nodo):
            cuenta["n"] += 1
            return real(nodo)

        with mock.patch.object(v, "_afirmaciones", espia):
            v._comprobar_e17(arbol, cfg, cfg.arbol)
        self.assertEqual(cuenta["n"], n, f"E17 parseó {cuenta['n']} veces {n} nodos: la caché no cachea")

    def test_d01_el_conjunto_de_nichos_se_construye_una_vez_por_arbol(self) -> None:
        from unittest import mock

        import cosmos.modelo as m
        from cosmos.medir import medir_casos

        cfg, arbol = self._arbol()
        real, cuenta = m.nombres_nichos, {"n": 0}

        def espia(a):
            cuenta["n"] += 1
            return real(a)

        with mock.patch.object(m, "nombres_nichos", espia):
            medir_casos(arbol, metodo="aprox", presupuesto=cfg.entrada)
        # una por la caché del árbol + las que `medir_casos` hace a propósito (una vez por llamada)
        self.assertLessEqual(cuenta["n"], 3, f"nombres_nichos se reconstruyó {cuenta['n']} veces: volvió el cúbico")

    def test_d07_generar_mapa_no_recorre_el_arbol_por_cada_nodo(self) -> None:
        from cosmos.generar import generar_mapa

        cfg, arbol = self._arbol()
        clase = type(arbol.nodos)
        iteraciones = {"n": 0}
        original = clase.__iter__

        class Vigilada(list):
            def __iter__(self):
                iteraciones["n"] += 1
                return original(self)

        arbol.nodos = Vigilada(arbol.nodos)
        generar_mapa(arbol)
        self.assertLessEqual(iteraciones["n"], 4, f"generar_mapa iteró la lista de nodos {iteraciones['n']} veces")

    def test_d10_el_error_de_lectura_lleva_ruta_relativa(self) -> None:
        import os
        import tempfile

        from cosmos.modelo import cargar_arbol

        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            (raiz / "galaxia.md").write_text("---\ncosmos: galaxia\nnombre: g\nresumen: Nada se carga.\n---\n", encoding="utf-8")
            ilegible = raiz / "prohibido.md"
            ilegible.write_text("---\ncosmos: oceano\n---\n", encoding="utf-8")
            os.chmod(ilegible, 0)
            try:
                arbol = cargar_arbol(raiz)
            finally:
                os.chmod(ilegible, 0o644)
        lectura = [e for e in arbol.errores if "no se puede leer" in e.mensaje]
        if not lectura:
            self.skipTest("este usuario puede leer ficheros con modo 000 (root)")
        self.assertEqual(lectura[0].ruta, "prohibido.md", "el error de lectura volvió a llevar la ruta absoluta")


if __name__ == "__main__":
    unittest.main()
