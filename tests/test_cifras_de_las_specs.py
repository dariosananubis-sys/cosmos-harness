"""Toda cifra que una spec afirma en prosa la calcula el repositorio.

Una revisión de coherencia encontró 15 incoherencias y **once eran cifras escritas a mano
que este repositorio ya sabe generar**: «uno de los 20 sistemas solares» cuando son 21,
«465 pares de nodos co-cargables» cuando son 496, «los 312 nodos de la galaxia real»
cuando son 408, «E00–E03 y E05–E19» cuando el validador comprueba hasta E20. Ninguna
mentía cuando se escribió; el árbol creció y la prosa no.

Lo irónico es que `spec/UNIVERSO.md` ya dice *«las cifras de este documento no se escriben
a mano»*… dos párrafos antes de una escrita a mano. La costumbre no basta, como no bastó
para el índice ni para el inventario: **lo que se escribe a mano se desincroniza**.

Aquí no se puede generar el texto —lo redacta una persona y eso es bueno—, así que se
compara. Cada entrada del registro dice dónde vive la cifra, cómo se extrae y **quién
calcula la verdad**. Añadir una cifra nueva a una spec obliga a registrarla aquí, que es
justo la fricción que se busca.
"""

from __future__ import annotations

import re
import unittest
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from cosmos.modelo import cargar_arbol, cargar_configuracion
from cosmos.validar import _co_cargables, codigos_comprobados

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = cargar_configuracion(RAIZ / "cosmos.toml")
ARBOL = cargar_arbol(CONFIG.arbol, tambien=(CONFIG.registro,) if CONFIG.registro else ())


def _sistemas() -> int:
    return sum(1 for n in ARBOL.nodos if n.cosmos == "sistema-solar")


def _nodos() -> int:
    return len(ARBOL.nodos)


def _pares_co_cargables() -> int:
    n = len(_co_cargables(ARBOL))
    return n * (n - 1) // 2


def _mayor_nicho() -> int:
    cuenta: Counter[str] = Counter()
    for nodo in ARBOL.nodos:
        padre = nodo.datos.get("padre")
        if nodo.cosmos == "pueblo" and isinstance(padre, str) and padre:
            cuenta[padre.split("/", 1)[0]] += 1
    return max(cuenta.values())


def _ultimo_codigo() -> int:
    return int(max(codigos_comprobados())[1:])


@dataclass(frozen=True)
class Cifra:
    fichero: str
    patron: str          # un grupo, el número
    calcular: Callable[[], int]
    por_que: str

    def declarada(self) -> int | None:
        texto = (RAIZ / self.fichero).read_text(encoding="utf-8")
        hallado = re.search(self.patron, texto)
        return int(hallado.group(1)) if hallado else None


REGISTRO = (
    Cifra("spec/REGISTRO.md", r"uno de los (\d+) sistemas solares", _sistemas,
          "el nicho de un parte tiene que existir"),
    Cifra("spec/NUCLEO.md", r"(\d+) pares de nodos co-cargables", _pares_co_cargables,
          "E17 compara ese número de pares; con otro, su conclusión está medida sobre otro árbol"),
    Cifra("spec/VALIDADOR.md", r"los (\d+) nodos de la galaxia real", _nodos,
          "el umbral de E08 se calibró sobre ese corpus"),
    Cifra("spec/NUCLEO.md", r"siguen siendo E00–E03 y E05–E(\d+)", _ultimo_codigo,
          "es la frase que existe para que la numeración no se toque: la peor donde envejecer"),
)


class LasSpecsDicenLoQueElArbolCuenta(unittest.TestCase):
    def test_cada_cifra_declarada_coincide_con_la_calculada(self) -> None:
        for cifra in REGISTRO:
            with self.subTest(f"{cifra.fichero}: {cifra.patron}"):
                declarada = cifra.declarada()
                self.assertIsNotNone(
                    declarada,
                    f"la frase desapareció de {cifra.fichero}; si se retiró a propósito, "
                    f"quítala también del registro de esta prueba",
                )
                self.assertEqual(
                    declarada, cifra.calcular(),
                    f"{cifra.fichero} afirma {declarada} y el árbol cuenta "
                    f"{cifra.calcular()} — importa porque {cifra.por_que}",
                )

    def test_el_registro_no_se_ha_quedado_vacio(self) -> None:
        """Un canario que no vigila nada pasa siempre y da falsa tranquilidad."""

        self.assertGreaterEqual(len(REGISTRO), 4)


class LasCifrasQueSeRetiraronSiguenRetiradas(unittest.TestCase):
    """Algunas cifras no se corrigieron: se quitaron, porque remitir al comando es mejor.

    `spec/UNIVERSO.md` decía «el techo práctico está en unas 25 por nicho, que es donde vive
    hoy el mayor» — y el mayor tenía 27. Se sustituyó por una remisión a `cosmos estado`.
    Igual con la enumeración de ríos por `momento` en `NUCLEO.md`, que listaba cuatro de
    ocho. Esta prueba impide que vuelvan a colarse.
    """

    def test_universo_no_vuelve_a_fijar_el_techo_por_nicho(self) -> None:
        texto = (RAIZ / "spec/UNIVERSO.md").read_text(encoding="utf-8")
        self.assertIsNone(
            re.search(r"unas \d+ por nicho", texto),
            "volvió una cifra de herramientas por nicho escrita a mano",
        )

    def test_nucleo_no_vuelve_a_enumerar_los_rios_por_momento(self) -> None:
        texto = (RAIZ / "spec/NUCLEO.md").read_text(encoding="utf-8")
        bloque = texto[texto.index("- **`trabajo`**") : texto.index("- **`trabajo`**") + 400]
        rios_citados = set(re.findall(r"`(abrir|medir|memoria|saltar|enganchar|proyectar|generar|acertar)`", bloque))
        self.assertEqual(rios_citados, set(), "NUCLEO volvió a enumerar ríos que el árbol ya lista")


if __name__ == "__main__":
    unittest.main()


class LosEjemplosDeLaSpecValidan(unittest.TestCase):
    """El esquema normativo enseñaba un formato que su propio validador rechaza.

    `spec/FRONTMATTER.md` —el primer fichero que abre quien va a escribir un nodo— ponía
    `padre: provincia/navegacion-web` e `ilumina: sistema-solar/web`. `NUCLEO.md` §1 fijó
    lo contrario al resolver el hallazgo B1: esos campos llevan **la ruta completa**, y el
    nivel no aparece en ella. Copiar los ejemplos literalmente daba E02 y E13.

    Es la peor clase de incoherencia: quien la sufre está siguiendo el documento que se
    titula «normativo», así que no sospecha de él.
    """

    def test_las_referencias_de_los_ejemplos_apuntan_a_nodos_reales(self) -> None:
        texto = (RAIZ / "spec/FRONTMATTER.md").read_text(encoding="utf-8")
        ejemplos = re.findall(r"```yaml\n(---\ncosmos:.*?---)\n```", texto, re.S)
        self.assertTrue(ejemplos, "desaparecieron los ejemplos de FRONTMATTER")

        rutas = {n.referencia for n in ARBOL.nodos}
        for ejemplo in ejemplos:
            campos = dict(re.findall(r"^(\w+): (.+)$", ejemplo, re.M))
            for campo in ("padre", "ilumina", "orbita"):
                destino = campos.get(campo, "").strip().strip('"')
                if not destino:
                    continue
                with self.subTest(f"{campos.get('cosmos')}.{campo}"):
                    self.assertIn(destino, rutas,
                                  f"el ejemplo normativo apunta a '{destino}', que no existe")

    def test_ningun_ejemplo_usa_el_formato_nivel_barra_nombre(self) -> None:
        """El formato retirado por NUCLEO §1. Si vuelve, esto se pone rojo."""

        from cosmos.modelo import NIVELES_AGUA, NIVELES_SOLIDOS

        texto = (RAIZ / "spec/FRONTMATTER.md").read_text(encoding="utf-8")
        for nivel in (*NIVELES_SOLIDOS, *NIVELES_AGUA, "estrella", "luna"):
            with self.subTest(nivel):
                self.assertIsNone(
                    re.search(rf"^(padre|ilumina|orbita): {nivel}/", texto, re.M),
                    f"volvió el formato '<nivel>/<nombre>' con {nivel}",
                )


class TodaInvarianteVivaTieneValvula(unittest.TestCase):
    """E20 estuvo viva y sin salida acotada, y nada lo dijo.

    `CODIGOS_INVARIANTES` era `range(20)` escrito a mano: se añadió la invariante y esa
    línea se quedó igual. `spec/GUARDARRAILES.md` es explícito sobre por qué eso importa —
    la válvula es «obligatoria, no opcional», porque «todo guardarraíl duro sin válvula de
    escape acaba desactivado a la fuerza». Una invariante de la que no se puede salir de
    forma acotada, con motivo y caducidad, se acaba saltando de la forma que no se registra.

    Esta prueba cierra el círculo entero: el validador, la válvula y la ayuda que se enseña
    tienen que hablar de los mismos códigos.
    """

    def test_la_valvula_acepta_todas_las_que_el_validador_comprueba(self) -> None:
        from cosmos.guardarrailes import CODIGOS_INVARIANTES, normalizar_codigo

        comprobadas = set(codigos_comprobados())
        self.assertEqual(set(CODIGOS_INVARIANTES), comprobadas,
                         "hay invariantes vivas sin válvula, o válvulas de invariantes que ya no existen")
        for codigo in sorted(comprobadas):
            with self.subTest(codigo):
                self.assertEqual(normalizar_codigo(codigo), codigo)

    def test_la_ayuda_del_cli_muestra_el_rango_de_verdad(self) -> None:
        import subprocess
        import sys

        from cosmos.validar import rango_comprobado

        ayuda = subprocess.run([sys.executable, "-m", "cosmos", "saltar", "--help"],
                               capture_output=True, text=True, cwd=RAIZ).stdout
        self.assertIn(rango_comprobado(), ayuda,
                      "la ayuda de la válvula enseña un rango que no es el que se comprueba")
