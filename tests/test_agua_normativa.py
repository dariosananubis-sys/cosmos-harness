"""Cada afirmacion normativa de los mares, enumerada A MANO y exigida presente.

El agua se condenso el 2026-09-02 para que el arbol cupiera con el tokenizador real
(1.546 -> 1.248 tokens; el exacto pasaba de rojo -279 a verde). La condicion del
encargo: reescritura, no recorte — lo que se va es la prosa que envuelve la norma,
nunca la norma. Este fichero es la prueba de esa condicion: la lista de afirmaciones
se escribio LEYENDO el texto anterior a la condensacion (el contrato), y cada una
lleva sondas literales del texto nuevo. Deducir la lista del propio texto seria la
tautologia de siempre: aqui, si alguien borra una afirmacion, su sonda desaparece y
esto se pone rojo con el nombre de la norma perdida.

Lo que se retiro A PROPOSITO al condensar esta declarado en el parte
`registro/commits/universo/2026/09/agua-condensada.md` (evidencia anecdotica, nunca
norma): la anecdota del fichero de semilla (criterio), las cifras «once de once y
nueve avisos» y «siete campos» de los casos de revision, y la fusion de «midiendo el
arbol» + «comparando arboles» de criterio, que eran el mismo mecanismo dicho dos veces.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from cosmos.modelo import cargar_arbol, cuerpo

RAIZ = Path(__file__).resolve().parent.parent

# (nombre de la norma, sondas literales que la anclan en el texto vigente)
AFIRMACIONES: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "criterio": (
        ("tocar lo minimo", ("Se toca lo minimo",)),
        ("cambio grande en pasos verificables", ("pasos verificables por separado",)),
        ("buscar antes de crear; duplicar es deuda", ("se busca si ya existe", "duplicar es deuda")),
        ("reutilizar por simbolo y referencia, no a ciegas",
         ("por simbolo y por quien lo", "barriendo a ciegas")),
        ("lo mecanico lo mide un analizador sintactico", ("analizador con arbol sintactico, no la vista",)),
        ("regla escribible -> la comprueba una maquina", ("la comprueba una maquina y deja de discutirse",)),
        ("modelo no garantiza consistencia; regla determinista si",
         ("no garantiza consistencia", "regla determinista si")),
        ("cambio repetido como patron aplicado por herramienta",
         ("se declara como patron", "nunca la mano")),
        ("el error humano escala", ("el error humano escala",)),
        ("tocar lo justo se demuestra comparando arboles", ("comparando arboles, no leyendo el diff",)),
        ("reformatear no es cambiar ni puede tapar el error", ("lo reformateado no cuenta",)),
        ("lista previa de ficheros tocables; fuera se pide permiso",
         ("que ficheros puede tocar el encargo", "pide")),
        ("mover no es reescribir de memoria; el conteo cuadra",
         ("no es reescribirlo de memoria", "se cuadra el conteo")),
        ("el mar fija politica; el catalogo, la herramienta",
         ("se decide en `refactorizacion`", "fija la politica, no el catalogo")),
    ),
    "pruebas": (
        ("medir primero, asercion despues", ("el test afirma lo medido, no lo deseado",)),
        ("solo la mutacion separa real de decorativo",
         ("Solo la mutacion separa", "se rompe el codigo a proposito")),
        ("mutante vivo = rama sin comprobar", ("mutante vivo es una rama que nadie comprobaba",)),
        ("mutacion cara: por modulo y de madrugada",
         ("ordenes de magnitud mas que la suite", "de madrugada")),
        ("el caso que rompe se busca mutando la entrada",
         ("se muta la entrada", "datos que nadie escribiria")),
        ("el fallo intermitente se graba", ("se graba, no se razona", "repetible bit a bit")),
        ("en distribuido se inyecta el fallo real",
         ("reloj desviado", "historia observada")),
        ("el disparador es el de produccion", ("disparador que no es el de produccion",)),
        ("e2e en navegador real con traza", ("navegador real con traza, nunca simulado",)),
        ("doblar el borde mas externo; tres claves = demasiado adentro",
         ("el borde mas externo", "mas de tres claves")),
        ("puntero a los motores de mutacion", ("`refactorizacion/mutacion`",)),
    ),
    "revision": (
        ("quien escribe no aprueba", ("Quien la escribe no la aprueba",)),
        ("premisa invertida y recuento de intentos",
         ("dando por hecho que esta mal", "que intento para tumbarla")),
        ("lo arreglado tras revisar no esta revisado; revisores encadenados",
         ("no esta revisado", "se encadenan")),
        ("sin la invocacion exacta no es reproducible",
         ("sin su llamada exacta no se reejecuta", "tercer parametro de cinco")),
        ("fallo generico con auditoria = contrato de campos", ("contrato de campos, no los datos",)),
        ("grep no distingue nombres; se arranca y se restan claves",
         ("se llama de otra forma", "restan las claves reales")),
    ),
    "resistencia": (
        ("valor mostrado != valor conocido", ("Un valor mostrado no es un valor conocido",)),
        ("fuente muda -> ausente, no cero", ("el resultado es ausente", "se confunde con un dato bueno")),
        ("la telemetria no repara el numero mostrado", ("telemetria de degradacion no repara",)),
        ("bandera de seguridad trivalente", ("trivalente",)),
        ("la insignia sale del estado autoritativo",
         ("autoritativo", "valor por defecto de la plantilla")),
        ("exit 0 no prueba ejecucion; el binario se comprueba",
         ("binario que no existe sale igual", "se comprueba que el programa existe")),
    ),
    "custodia": (
        ("secretos son credenciales; aqui personas", ("alli credenciales, aqui personas",)),
        ("minimo, en su sitio, sin copiar a terceros",
         ("Se recoge lo minimo", "no se copia a un tercero")),
        ("detector de datos personales antes de exportar", ("detector de datos personales",)),
        ("flujo en codigo; reconocedores y sumas en datos",
         ("analisis de flujo", "sumas de control")),
    ),
    "accesibilidad": (
        ("EN 301 549 -> WCAG 2.2 AA, exigible desde 2025", ("EN 301 549", "WCAG 2.2 AA", "2025")),
        ("el motor encuentra la mitad; el resto a mano",
         ("la mitad de los fallos", "se comprueban a mano")),
        ("estar en el arbol no es estar disponible", ("tamano y visibilidad reales",)),
    ),
}


from tests._integrado import solo_en_el_origen

solo_en_el_origen()  # cifras y listas del catálogo del origen, no del motor


class NingunaNormaSePierdeAlCondensar(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        arbol = cargar_arbol(RAIZ / "galaxia")
        cls.mares = {n.nombre: cuerpo(n) for n in arbol.nodos if n.cosmos == "mar"}

    def test_la_lista_cubre_todos_los_mares_del_disco(self) -> None:
        """Un mar nuevo sin su lista de normas pasaria sin vigilancia."""

        self.assertEqual(sorted(self.mares), sorted(AFIRMACIONES),
                         "hay mares sin lista de afirmaciones (o listas de mares que ya no existen)")

    def test_cada_afirmacion_sigue_presente(self) -> None:
        for mar, normas in AFIRMACIONES.items():
            texto = self.mares[mar]
            for nombre, sondas in normas:
                for sonda in sondas:
                    with self.subTest(f"{mar}: {nombre}"):
                        self.assertIn(sonda, texto,
                                      f"mar/{mar} perdio la norma «{nombre}» (sonda: {sonda!r})")

    def test_la_lista_no_se_ha_quedado_vacia(self) -> None:
        total = sum(len(normas) for normas in AFIRMACIONES.values())
        self.assertGreaterEqual(total, 44, "el registro de normas menguo: un canario vacio no vigila")


if __name__ == "__main__":
    unittest.main()
