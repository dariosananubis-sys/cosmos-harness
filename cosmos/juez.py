"""El juez con modelo: ¿un agente DE VERDAD baja por donde debe?

`acertar` es léxico y lo declara en cada salida: mide si el resumen contiene las
palabras del encargo, no si un modelo elegiría bien. Cerrar ese bucle es la única
forma de saber si los resúmenes sirven — y por API es dinero, que no se gasta sin
orden de Darío. Esta es la vía sin coste: un modelo local servido por ollama.

**Este módulo NUNCA arranca un modelo.** Se conecta a un servidor que ya esté
levantado (`ollama serve`, en la máquina donde sobre memoria) y si no lo hay,
falla limpio y lo dice. Levantar un modelo es decisión de quien opera la máquina,
no de una métrica. Cero dependencias: transporte por `urllib` de la stdlib.

El juez ve EXACTAMENTE lo que vería un agente recién llegado: el índice y el
catálogo (los mismos candidatos que puntúa `acertar`, por construcción), y tiene
que contestar una ruta. Se puntúa con el mismo `_acierta`: el nodo esperado o
cualquiera bajo él. Se corre sobre el conjunto de AJUSTE: el holdout sellado no
se le enseña a nada que produzca salida por encargo.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from .acertar import Encargo, Puntuacion, Resultado, _acierta, _lineas_del_catalogo
from .modelo import Arbol


class ErrorJuez(RuntimeError):
    """No hay servidor de modelos al que preguntar, o contestó basura."""


def _preguntar_ollama(servidor: str, modelo: str, prompt: str, timeout: float = 120.0) -> str:
    peticion = urllib.request.Request(
        f"{servidor.rstrip('/')}/api/generate",
        data=json.dumps({"model": modelo, "prompt": prompt, "stream": False}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(peticion, timeout=timeout) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError) as exc:
        raise ErrorJuez(
            f"no hay servidor de modelos en {servidor} ({exc}). Este comando no arranca "
            "ninguno: levántalo tú donde sobre memoria ('ollama serve') y repite."
        ) from exc
    texto = datos.get("response")
    if not isinstance(texto, str):
        raise ErrorJuez(f"el servidor contestó sin campo 'response': {sorted(datos)[:5]}")
    return texto


def _prompt(encargo: Encargo, catalogo: str) -> str:
    return (
        "Eres un agente que navega un catálogo de herramientas. Un cliente pide:\n"
        f"«{encargo.peticion}»\n\n"
        "El catálogo (una línea por destino, 'ruta: descripción'):\n"
        f"{catalogo}\n\n"
        "Contesta ÚNICAMENTE la ruta del destino más adecuado, sin explicación."
    )


def extraer_ruta(respuesta: str, rutas: list[str]) -> str | None:
    """La ruta conocida que la respuesta nombra; la más larga si nombra varias.

    Un modelo local contesta con ruido («La ruta es `web/tienda`.»): no se parsea su
    formato, se busca qué candidato real aparece en el texto. Sin candidato, None —
    y None es fallo del juez para ese encargo, nunca un acierto por defecto.
    """

    presentes = [ruta for ruta in rutas if ruta in respuesta]
    return max(presentes, key=len) if presentes else None


def juzgar(
    arbol: Arbol,
    encargos: list[Encargo],
    *,
    modelo: str,
    servidor: str = "http://localhost:11434",
    preguntar=None,
) -> Puntuacion:
    """Puntúa con el modelo. `preguntar` se inyecta en tests: se dobla el transporte
    (el borde más externo), nunca el parseo ni la puntuación, que son lo ejercitado."""

    candidatos = _lineas_del_catalogo(arbol)
    rutas = [ruta for ruta, _ in candidatos]
    catalogo = "\n".join(texto for _, texto in candidatos)
    consulta = preguntar or (lambda prompt: _preguntar_ollama(servidor, modelo, prompt))
    resultados = []
    for encargo in encargos:
        elegida = extraer_ruta(consulta(_prompt(encargo, catalogo)), rutas)
        acierta = elegida is not None and _acierta(encargo.espera, elegida)
        resultados.append(
            Resultado(encargo=encargo, elegida=elegida, posicion=1 if acierta else None, acierta=acierta)
        )
    return Puntuacion(resultados=resultados)


def formatear_juicio(p: Puntuacion, lexico: Puntuacion, modelo: str) -> str:
    pct = 100 * p.aciertos / p.total if p.total else 0.0
    pct_lexico = 100 * lexico.aciertos / lexico.total if lexico.total else 0.0
    return (
        "COSMOS  acertar --juez\n\n"
        f"  Juez ({modelo}) ... {p.aciertos}/{p.total} ({pct:.0f} %)   un modelo eligiendo de verdad\n"
        f"  BM25 léxico ..... {lexico.aciertos}/{lexico.total} ({pct_lexico:.0f} %)   la contra-métrica de siempre\n\n"
        "  Las dos cifras responden preguntas distintas: el léxico mide si las palabras\n"
        "  alcanzan; el juez, si un modelo baja por donde debe. Sirve para comparar dos\n"
        "  versiones del árbol entre sí, no como nota absoluta de un modelo pequeño.\n"
    )
