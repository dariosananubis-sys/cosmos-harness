"""Un verbo que cuida el repositorio no se paga en cada encargo.

Los ríos son los verbos de COSMOS y su resumen viaja en el contexto inicial. Cinco de
ellos —`arrancar`, `enganchar`, `desenganchar`, `proyectar`, `mapa`— se ejecutan una vez,
al montar el repositorio, y cobraban su línea en cada sesión de toda su vida. Es la forma
exacta del problema que el proyecto persigue: coste que crece con lo que existe en vez de
con lo que se usa, aplicado esta vez a las herramientas del propio sistema.

`momento: mantenimiento` los deja **nombrados y no descritos**. Siguen estando —el catálogo
los lista y `cosmos abrir rio/<nombre>` da el cuerpo entero—, solo dejan de estar
precargados. Estas pruebas exigen las dos mitades: que dejen de costar y que sigan
encontrándose.
"""

from __future__ import annotations

import argparse
import re
import unittest
from pathlib import Path

from cosmos.medir import catalogo_visible, contar_generado
from cosmos.modelo import cargar_arbol

RAIZ = Path(__file__).resolve().parent.parent
ARBOL = cargar_arbol(RAIZ / "galaxia")


def _rios(momento: str | None) -> list[str]:
    return sorted(
        n.nombre
        for n in ARBOL.nodos
        if n.cosmos == "rio" and n.datos.get("momento") == momento
    )


class LosVerbosDeMontarNoSePaganCadaSesion(unittest.TestCase):
    def test_su_resumen_no_esta_en_el_catalogo(self) -> None:
        catalogo = catalogo_visible(ARBOL, ["ciberseguridad"])
        for nombre in _rios("mantenimiento"):
            with self.subTest(nombre):
                nodo = next(n for n in ARBOL.nodos if n.cosmos == "rio" and n.nombre == nombre)
                self.assertNotIn(nodo.resumen, catalogo)

    def test_pero_siguen_nombrados_para_poder_encontrarlos(self) -> None:
        """Ahorrar tokens escondiendo una herramienta no es ahorrar: es perderla."""

        catalogo = catalogo_visible(ARBOL, ["ciberseguridad"])
        linea = next((l for l in catalogo.splitlines() if l.startswith("rio (mantenimiento")), None)
        self.assertIsNotNone(linea, "los ríos de mantenimiento desaparecieron del catálogo")
        for nombre in _rios("mantenimiento"):
            self.assertIn(nombre, linea)

    def test_el_verbo_de_trabajo_si_lleva_su_resumen(self) -> None:
        catalogo = catalogo_visible(ARBOL, ["ciberseguridad"])
        medir = next(n for n in ARBOL.nodos if n.cosmos == "rio" and n.nombre == "medir")
        self.assertIn(medir.resumen, catalogo)

    def test_agrupar_sale_mas_barato_que_describir(self) -> None:
        """El ahorro, medido: no se afirma que ahorra, se cuenta cuánto."""

        de_montaje = [
            n for n in ARBOL.nodos
            if n.cosmos == "rio" and n.datos.get("momento") == "mantenimiento"
        ]
        descritos = sum(contar_generado(f"rio/{n.nombre}: {n.resumen}\n") for n in de_montaje)
        agrupados = contar_generado(
            "rio (montaje, 'cosmos abrir rio/x'): " + ", ".join(sorted(n.nombre for n in de_montaje)) + "\n"
        )
        self.assertGreater(descritos - agrupados, 50, "el agrupado dejó de ahorrar: revísalo")


# Contrato explícito. No se deduce del árbol: si se deduce, quitarle el campo a un río
# no rompe nada y el coste vuelve a subir en silencio — que es justo lo que pasó al
# probar este fichero con un sabotaje. Añadir un río obliga a decidir en qué lado cae.
DE_MANTENIMIENTO = {
    "acertar", "arrancar", "compilar", "configurar", "desenganchar",
    "enganchar", "generar", "instalar", "mapa", "proyectar",
}


class ElCampoTieneUnValorOOtro(unittest.TestCase):
    def test_los_rios_de_mantenimiento_son_estos_y_no_otros(self) -> None:
        self.assertEqual(set(_rios("mantenimiento")), DE_MANTENIMIENTO)

    def test_todo_rio_declara_un_momento_conocido(self) -> None:
        from cosmos.validar import MOMENTOS_DE_RIO

        for nodo in ARBOL.nodos:
            if nodo.cosmos != "rio":
                continue
            momento = nodo.datos.get("momento", "trabajo")
            with self.subTest(nodo.nombre):
                self.assertIn(momento, MOMENTOS_DE_RIO)

    def test_un_momento_inventado_sale_en_rojo(self) -> None:
        """El validador tiene que rechazarlo, no el árbol tiene que no tenerlo."""

        from tempfile import TemporaryDirectory

        from cosmos.validar import _comprobar_e00, validar_arbol

        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "galaxia.md").write_text(
                "---\ncosmos: galaxia\nnombre: t\nresumen: Arbol de prueba.\n---\n", encoding="utf-8")
            (base / "agua").mkdir()
            (base / "agua/rio-x.md").write_text(
                "---\ncosmos: rio\nnombre: equis\nmoja: []\ninvoca: echo\n"
                "momento: cuando-me-apetezca\nresumen: Un rio con un momento que no existe.\n---\n",
                encoding="utf-8")
            errores = validar_arbol(cargar_arbol(base), comprobaciones=[_comprobar_e00]).errores
            codigos = {e.codigo for e in errores}
            self.assertIn("E00", codigos)
            self.assertTrue(
                any("momento" in str(e.mensaje) for e in errores),
                "E00 salta, pero no por el campo que se saboteó",
            )

    def test_cada_verbo_del_cli_tiene_su_rio(self) -> None:
        """El hueco que motivó `rio/abrir`: se añadió el comando y no su verbo."""

        # Se leen los subcomandos del PARSER, no un patrón del fuente: `configurar` se añadió
        # con `subparsers.add_parser(...)` en vez de `base(...)`, y este test lo dejó pasar sin
        # río durante un día (revisión B-05).
        from cosmos.cli import _parser

        acciones = [a for a in _parser()._actions if isinstance(a, argparse._SubParsersAction)]
        comandos = set(acciones[0].choices)
        rios = {n.nombre for n in ARBOL.nodos if n.cosmos == "rio"}
        self.assertEqual(comandos - rios, set(), "hay comandos sin su río en el árbol")


if __name__ == "__main__":
    unittest.main()
