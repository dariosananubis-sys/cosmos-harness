"""El verbo que faltaba: encontrar sin conocer el árbol.

COSMOS sabía decidir (`validar`), medir, cargar (`abrir`) y aplanar (`compilar`);
no sabía ENCONTRAR. Un agente que no conoce el árbol solo podía leer el índice y
adivinar por qué oficio bajar — y si fallaba, volvía al `grep` que este proyecto
existe para eliminar. El motor ya estaba escrito y escondido dentro de la
contra-métrica: el mismo BM25 con recorte de sufijos sobre índice + catálogo con
el que `acertar` puntúa.

Exponerlo tiene valor doble: da el verbo, y convierte la contra-métrica en la
evaluación del camino real — lo que `acertar` puntúa es, por construcción, lo que
este comando devuelve (comparten `_lineas_del_catalogo` y `_ordenar`). Antes, el
66 % de acierto medía una función interna que ningún agente podía invocar.

Determinista, sin red, sin modelo y sin coste: léxico. Encontrar aquí es condición
necesaria, no suficiente — la misma honestidad que declara `acertar`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .acertar import _lineas_del_catalogo, _ordenar
from .modelo import Arbol


@dataclass(frozen=True)
class Hallazgo:
    ruta: str
    resumen: str


def buscar_nodos(arbol: Arbol, consulta: str, limite: int = 5) -> list[Hallazgo]:
    """Los candidatos que mejor casan con la consulta, en el orden del motor."""

    candidatos = _lineas_del_catalogo(arbol)
    textos = dict(candidatos)
    hallazgos = []
    for ruta in _ordenar(consulta, candidatos)[: max(limite, 0)]:
        texto = textos.get(ruta, "")
        resumen = texto[len(ruta):].strip() if texto.startswith(ruta) else texto
        hallazgos.append(Hallazgo(ruta=ruta, resumen=resumen))
    return hallazgos


def formatear_busqueda(hallazgos: list[Hallazgo], consulta: str) -> str:
    if not hallazgos:
        return (
            "COSMOS  buscar  sin resultados\n\n"
            f"  Ninguna línea del índice ni del catálogo casa con «{consulta}».\n"
            "  Prueba con otras palabras, o mira el índice: los oficios están todos ahí.\n"
        )
    lineas = ["COSMOS  buscar", ""]
    for numero, hallazgo in enumerate(hallazgos, start=1):
        lineas.append(f"  {numero}.  {hallazgo.ruta}")
        if hallazgo.resumen:
            lineas.append(f"      {hallazgo.resumen}")
    lineas += ["", "  'cosmos abrir <ruta>' carga el nodo; esto solo encuentra."]
    return "\n".join(lineas) + "\n"


def busqueda_json(hallazgos: list[Hallazgo], consulta: str) -> str:
    return json.dumps(
        {
            "consulta": consulta,
            "metodo": "BM25 léxico sobre índice + catálogo; el mismo motor que puntúa 'acertar'",
            "resultados": [{"ruta": h.ruta, "resumen": h.resumen} for h in hallazgos],
        },
        ensure_ascii=False, indent=2, sort_keys=True,
    ) + "\n"
