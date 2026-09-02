"""La contra-métrica: ¿el árbol lleva a la herramienta correcta?

Todo lo que COSMOS medía era **coste** — tokens, presupuesto, descarga, solapamiento.
Ni una sola cifra de si el sistema **acierta**. Y eso deja abierta la puerta a
Goodhart en su forma más pura, con el camino ya pavimentado:

> **La manera más barata de pasar el presupuesto es escribir resúmenes peores.**

Recortar un resumen baja la entrada, pone verde E16 y no dispara ninguna invariante
— degradando justo aquello por lo que se paga el resumen. Con 21 oficios se nota
poco; con cincuenta sería el modo de fallo dominante.

Darío lo dijo antes de que existiera este fichero, corrigiendo el principio rector:
*«yo no te dije que se centre en mínimo coste, sino que no hubiese costes
innecesarios, que es distinto»*. El coste mínimo lo gana un árbol vacío. Esto mide
la otra mitad.

**El control contra uno mismo.** Una métrica que se mira mientras se retoca el contenido
deja de medir el contenido y empieza a medir el retoque. Por eso hay dos conjuntos de
encargos: uno de **ajuste**, que se mira al trabajar, y uno de **validación**, escrito
aparte y que no guía ninguna decisión. Cuando la brecha entre ambos crece, lo que ha
mejorado no es el árbol: es la puntería sobre las preguntas conocidas. La salida publica
las dos cifras y dice cuál vale.

**Qué es y qué no es.** Se puntúa con BM25 sobre **las líneas del catálogo**, que es
exactamente lo que un agente ve antes de decidir. Es léxico y determinista: cero red,
cero modelo, cero dinero. Y por eso mismo **no es un agente**: mide si el resumen
contiene las palabras del encargo, no si un modelo elegiría bien. Un acierto aquí es
condición necesaria, no suficiente — y se dice en la salida, como se declara el
límite de E17.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from .medir import catalogo_visible
from .modelo import Arbol


@dataclass(frozen=True)
class Encargo:
    peticion: str
    espera: str          # ruta que debería alcanzarse
    nota: str = ""


@dataclass
class Resultado:
    encargo: Encargo
    elegida: str | None
    posicion: int | None   # 1 = primera; None = no aparece
    acierta: bool


@dataclass
class Puntuacion:
    resultados: list[Resultado]

    @property
    def total(self) -> int:
        return len(self.resultados)

    @property
    def aciertos(self) -> int:
        return sum(1 for r in self.resultados if r.acierta)

    @property
    def en_los_tres(self) -> int:
        return sum(1 for r in self.resultados if r.posicion and r.posicion <= 3)

    @property
    def perdidos(self) -> list[Resultado]:
        return [r for r in self.resultados if not r.posicion]

    def como_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "aciertos": self.aciertos,
            "en_los_tres": self.en_los_tres,
            "metodo": "BM25 léxico sobre el catálogo; no es un agente",
            "resultados": [
                {
                    "peticion": r.encargo.peticion,
                    "espera": r.encargo.espera,
                    "elegida": r.elegida,
                    "posicion": r.posicion,
                    "acierta": r.acierta,
                }
                for r in self.resultados
            ],
        }


# Sufijos del castellano, del más largo al más corto: el orden importa, porque
# «encuentren» tiene que perder «-en» y no quedarse a medias en «-n».
SUFIJOS = (
    "aciones", "amientos", "imientos", "acion", "amiento", "imiento",
    "andose", "endose", "arse", "erse", "irse",
    "ando", "endo", "ados", "idos", "adas", "idas",
    "aban", "ian", "aba", "ado", "ido", "ada", "ida",
    "ares", "eres", "ires", "amos", "emos", "imos",
    "aran", "eran", "iran", "aria", "eria", "iria",
    "an", "en", "es", "ar", "er", "ir", "as", "os", "a", "e", "o", "s",
)
RAIZ_MINIMA = 4


def _raiz(palabra: str) -> str:
    """Recorte de sufijos, no lematización: barato, sin diccionario y sin red.

    El catálogo y el encargo casi nunca coinciden en la forma exacta —«que google
    **encuentre** mi web» contra «que te **encuentren**»— y una comparación de palabras
    enteras cuenta eso como cero parecido. No es un defecto del árbol sino del medidor:
    lo que separa a esas dos palabras es una `n`.

    Conservador a propósito: nunca deja una raíz de menos de cuatro letras, así que
    «casa» o «sitio» quedan intactos y no se funden con vecinos que no son.
    """

    for sufijo in SUFIJOS:
        if palabra.endswith(sufijo) and len(palabra) - len(sufijo) >= RAIZ_MINIMA:
            return palabra[: -len(sufijo)]
    return palabra


def _normalizar(texto: str) -> list[str]:
    plano = unicodedata.normalize("NFKD", texto.lower())
    plano = "".join(c for c in plano if not unicodedata.combining(c))
    return [_raiz(p) for p in re.findall(r"[a-z0-9]{2,}", plano)]


def _lineas_del_catalogo(arbol: Arbol) -> list[tuple[str, str]]:
    """(ruta, texto puntuable) por cada línea que el agente tiene delante al elegir.

    Se puntúa con **todos** los nichos, no con el caso base. La pregunta que responde
    esta métrica es «¿el árbol lleva a la herramienta correcta?», y quien pregunta
    todavía no sabe en qué oficio está — si lo supiera, ya habría encontrado la mitad
    del camino. Medir solo el caso base daría 0 % siempre y no diría nada.

    Y se puntúa sobre el **índice más el catálogo**, no sobre el catálogo solo. La
    primera versión de esta función se dejaba fuera los 21 oficios, que viven en el
    índice y no en el catálogo: 309 líneas de candidatos y ni una de profundidad cero.
    Con eso, los quince encargos cuya respuesta es un oficio —«que google encuentre mi
    web»— solo podían acertar de rebote, por un nieto, compitiendo contra el catálogo
    entero. No medía el árbol: medía un recorte del árbol que ningún agente ve.
    """

    lineas = [
        (nodo.nombre, f"{nodo.nombre} {nodo.resumen}")
        for nodo in arbol.nodos
        if nodo.cosmos == "sistema-solar"
    ]
    todos = [nombre for nombre, _ in lineas]
    for linea in catalogo_visible(arbol, todos).splitlines():
        if not linea.strip():
            continue
        ruta, _, resumen = linea.partition(":")
        lineas.append((ruta.strip(), f"{ruta} {resumen}".strip()))
    return lineas


def _ordenar(consulta: str, candidatos: list[tuple[str, str]]) -> list[str]:
    """BM25 clásico, con la misma normalización que usa la búsqueda de memoria."""

    terminos = list(dict.fromkeys(_normalizar(consulta)))
    if not terminos or not candidatos:
        return []

    documentos = [(_normalizar(texto), ruta) for ruta, texto in candidatos]
    frec_doc: Counter[str] = Counter()
    for tokens, _ in documentos:
        frec_doc.update(set(tokens))
    media = sum(len(t) for t, _ in documentos) / len(documentos) or 1.0

    n = len(documentos)
    k1, b = 1.5, 0.75
    puntuados: list[tuple[float, str]] = []
    for tokens, ruta in documentos:
        cuenta = Counter(tokens)
        largo = len(tokens) or 1
        total = 0.0
        for termino in terminos:
            if termino not in cuenta:
                continue
            df = frec_doc[termino]
            idf = max(0.0, ((n - df + 0.5) / (df + 0.5)))
            idf = (idf + 1) ** 0.5
            tf = cuenta[termino]
            total += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * largo / media))
        if total > 0:
            puntuados.append((total, ruta))
    puntuados.sort(key=lambda par: (-par[0], par[1]))
    return [ruta for _, ruta in puntuados]


def _acierta(esperada: str, elegida: str) -> bool:
    """Vale el nodo exacto o cualquiera bajo él: bajar de más no es fallar."""

    return elegida == esperada or elegida.startswith(esperada + "/")


def puntuar(arbol: Arbol, encargos: list[Encargo]) -> Puntuacion:
    candidatos = _lineas_del_catalogo(arbol)
    resultados = []
    for encargo in encargos:
        orden = _ordenar(encargo.peticion, candidatos)
        posicion = next(
            (i for i, ruta in enumerate(orden, start=1) if _acierta(encargo.espera, ruta)), None
        )
        resultados.append(
            Resultado(
                encargo=encargo,
                elegida=orden[0] if orden else None,
                posicion=posicion,
                acierta=posicion == 1,
            )
        )
    return Puntuacion(resultados=resultados)


def cargar_encargos(ruta: str | Path) -> list[Encargo]:
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    return [
        Encargo(peticion=d["peticion"], espera=d["espera"], nota=d.get("nota", ""))
        for d in datos
    ]


def formatear(p: Puntuacion, *, detalle: bool = False) -> str:
    if not p.total:
        return "COSMOS  acertar\n\n  sin encargos que puntuar\n"

    pct = 100 * p.aciertos / p.total
    pct3 = 100 * p.en_los_tres / p.total
    lineas = [
        "COSMOS  acertar",
        "",
        f"  Encargos ........ {p.total}",
        f"  Acierta a la 1 .. {p.aciertos} ({pct:.0f} %)",
        f"  En los tres ..... {p.en_los_tres} ({pct3:.0f} %)",
        "",
        "  Método .......... BM25 léxico sobre el catálogo. NO es un agente:",
        "                    mide si el resumen contiene las palabras del encargo,",
        "                    no si un modelo elegiría bien. Necesario, no suficiente.",
    ]

    if p.perdidos:
        lineas.extend(["", "  No alcanzados — el catálogo no lleva hasta ellos:"])
        for r in p.perdidos[:10]:
            lineas.append(f"    «{r.encargo.peticion}»")
            lineas.append(f"      esperaba {r.encargo.espera}, el catálogo llevó a {r.elegida or '—'}")

    fallados = [r for r in p.resultados if r.posicion and r.posicion > 1]
    if detalle and fallados:
        lineas.extend(["", "  Alcanzados, pero no los primeros:"])
        for r in fallados:
            lineas.append(f"    {r.posicion}º  {r.encargo.espera}  ←  «{r.encargo.peticion}»")

    return "\n".join(lineas) + "\n"


def puntuacion_json(p: Puntuacion) -> str:
    return json.dumps(p.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


@dataclass
class Contraste:
    """Las dos puntuaciones, y la distancia entre ellas.

    `quemado` lleva el motivo cuando el conjunto de validación **ya se ha mirado**. Un
    holdout es de un solo uso: en cuanto alguien lee su lista de fallos y escribe hacia
    ella, mide un examen visto y su cifra deja de significar lo que dice. Pasó aquí el
    mismo día que se creó, y no por mala fe — basta con abrir el `--detalle` una vez.
    """

    ajuste: Puntuacion
    validacion: Puntuacion | None
    quemado: str | None = None

    @property
    def brecha(self) -> float | None:
        """Puntos porcentuales de más que saca el conjunto que sí se miró."""

        if not self.validacion or not self.validacion.total:
            return None
        return (100 * self.ajuste.aciertos / self.ajuste.total
                - 100 * self.validacion.aciertos / self.validacion.total)

    def como_dict(self) -> dict[str, object]:
        return {
            "ajuste": self.ajuste.como_dict(),
            "validacion": self.validacion.como_dict() if self.validacion else None,
            "brecha_puntos": self.brecha,
            "quemado": self.quemado,
            "cifra_honesta": (
                round(100 * self.validacion.aciertos / self.validacion.total, 1)
                if self.validacion and self.validacion.total and not self.quemado
                else None
            ),
        }


def formatear_contraste(c: Contraste) -> str:
    if not c.validacion:
        return formatear(c.ajuste)

    aj = 100 * c.ajuste.aciertos / c.ajuste.total
    va = 100 * c.validacion.aciertos / c.validacion.total
    lineas = [
        "COSMOS  acertar",
        "",
        f"  Ajuste ......... {c.ajuste.aciertos}/{c.ajuste.total} ({aj:.0f} %)   "
        "los encargos que SÍ se miran al trabajar",
        f"  Validación ..... {c.validacion.aciertos}/{c.validacion.total} ({va:.0f} %)   "
        "escritos aparte; no guían ninguna decisión",
        "",
        f"  La cifra que vale es {va:.0f} %."
        if not c.quemado
        else f"  {va:.0f} %, pero ESTE CONJUNTO YA SE MIRÓ y un holdout es de un solo uso:",
    ]

    if c.quemado:
        lineas.extend(
            [f"    {linea}" for linea in c.quemado.strip().splitlines()[:3]]
            + ["  Mientras no haya un conjunto nuevo sin estrenar, la cifra honesta es DESCONOCIDA."]
        )
        return "\n".join(lineas) + "\n"

    brecha = c.brecha or 0.0
    if brecha >= 10:
        lineas += [
            f"  Y la brecha es de {brecha:.0f} puntos: parte de lo ganado es puntería sobre",
            "  las preguntas conocidas, no un árbol que lleve mejor. Se corrige mejorando",
            "  resúmenes en general, no los que salen en esta lista.",
        ]
    elif brecha <= -5:
        lineas.append("  La validación va por delante: el conjunto de ajuste se ha quedado corto.")
    else:
        lineas.append(f"  Brecha de {brecha:.0f} puntos: lo ganado generaliza.")

    lineas += [
        "",
        "  Método ......... BM25 léxico con recorte de sufijos, sobre índice + catálogo.",
        "                   NO es un agente: mide si el resumen contiene las palabras del",
        "                   encargo, no si un modelo elegiría bien. Necesario, no suficiente.",
    ]
    return "\n".join(lineas) + "\n"
