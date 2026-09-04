"""La contra-métrica: ¿el árbol lleva a la herramienta correcta?

Todo lo que COSMOS medía era **coste** — tokens, presupuesto, descarga, solapamiento.
Ni una sola cifra de si el sistema **acierta**. Y eso deja abierta la puerta a
Goodhart en su forma más pura, con el camino ya pavimentado:

> **La manera más barata de pasar el presupuesto es escribir resúmenes peores.**

Recortar un resumen baja la entrada, pone verde E16 y no dispara ninguna invariante
— degradando justo aquello por lo que se paga el resumen. Con una veintena de oficios se nota
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

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from puente.lluvia import normalizar
from .holdout import (SOLAPE_CALCADO, Cobertura, Compromiso, Procedencia, formatear_intervalo,
                      intervalo_wilson, solape_examen_catalogo)
from .medir import lineas_de_catalogo
from .modelo import Arbol

# Una validación que va MUY por encima del ajuste no es una buena noticia: es la firma
# de un examen filtrado a los resúmenes (auditoría B-01/B-03: copiar las veinte
# consultas del holdout a los resúmenes dejó ajuste 64 %, validación 100 %, brecha −36,
# y el árbol estrictamente peor). Por debajo de este umbral la cifra no se publica.
BRECHA_ALARMA = -15.0


class ErrorEncargos(ValueError):
    """El fichero de encargos no existe o no cumple su esquema. Mensaje entero, sin traceback."""


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

    @property
    def intervalo(self) -> tuple[float, float] | None:
        """IC95 de Wilson en puntos porcentuales. Con n=20 cada acierto vale 5 puntos:
        publicar «40 %» a secas es precisión falsa (auditoría B-06)."""

        return intervalo_wilson(self.aciertos, self.total) if self.total else None

    def como_dict(self) -> dict[str, object]:
        return {
            "total": self.total,
            "aciertos": self.aciertos,
            "en_los_tres": self.en_los_tres,
            "n": self.total,
            "ic95": list(self.intervalo) if self.intervalo else None,
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
# Parámetros del modelo de puntuación, fijados por prueba (R-09).
K1, B = 1.5, 0.75

SUFIJOS = (
    "aciones", "amientos", "imientos", "acion", "amiento", "imiento", "oria",
    "andose", "endose", "arse", "erse", "irse",
    "ando", "endo", "ados", "idos", "adas", "idas",
    "aban", "ian", "aba", "ado", "ido", "ada", "ida",
    "ares", "eres", "ires", "amos", "emos", "imos",
    "aran", "eran", "iran", "aria", "eria", "iria",
    "an", "en", "es", "ar", "er", "ir", "as", "os", "a", "e", "o", "s",
)
RAIZ_MINIMA = 4
PREFIJOS_COMPUESTOS = ("ciber",)


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
    """La tokenización de `puente/lluvia` más el recorte de sufijos.

    El docstring de `_ordenar` promete «la misma normalización que usa la búsqueda de
    memoria», y hasta hoy era una copia casi igual: verdadera a medias, y con la
    divergencia garantizada en la primera corrección que tocara una de las dos. Ahora
    es la misma función por construcción — lo único propio de aquí es `_raiz`.
    """

    raices: list[str] = []
    for palabra in normalizar(texto):
        raices.append(_raiz(palabra))
        # Compuestos con prefijo: «ciberseguridad» también es «seguridad». Sin esto, «auditar la
        # seguridad de una web» no llegaba a `ciberseguridad` por ninguna vía (auditoría E-12).
        # Mejora del motor declarada y medida el 2026-09-03: ajuste 37 → 38 de 50; ningún
        # resumen se tocó, y el holdout —quemado— no publica cifra que pudiera moverse.
        for prefijo in PREFIJOS_COMPUESTOS:
            if palabra.startswith(prefijo) and len(palabra) - len(prefijo) >= RAIZ_MINIMA + 2:
                raices.append(_raiz(palabra[len(prefijo):]))
    return raices


def _lineas_del_catalogo(arbol: Arbol) -> list[tuple[str, str]]:
    """(ruta, texto puntuable) por cada línea que el agente tiene delante al elegir.

    Se puntúa con **todos** los nichos, no con el caso base. La pregunta que responde
    esta métrica es «¿el árbol lleva a la herramienta correcta?», y quien pregunta
    todavía no sabe en qué oficio está — si lo supiera, ya habría encontrado la mitad
    del camino. Medir solo el caso base daría 0 % siempre y no diría nada.

    Y se puntúa sobre el **índice más el catálogo**, no sobre el catálogo solo. La
    primera versión de esta función se dejaba fuera los oficios, que viven en el
    índice y no en el catálogo: 309 líneas de candidatos y ni una de profundidad cero.
    Con eso, los quince encargos cuya respuesta es un oficio —«que google encuentre mi
    web»— solo podían acertar de rebote, por un nieto, compitiendo contra el catálogo
    entero. No medía el árbol: medía un recorte del árbol que ningún agente ve.

    Y se puntúa **la línea tal cual se renderiza**, ni una palabra más. Hasta el
    2026-09-03 el juez añadía la ruta completa a cada línea («la información que la
    indentación le da al agente, dicha en palabras»); defendible, pero era una decisión
    de modelado sin fijar que valía 10 puntos de la cifra publicada, y a favor de la
    cifra (auditoría B-08: 40 % con ruta, 30 % con la línea literal). Ahora el texto
    sale de `medir.lineas_de_catalogo`, la misma función que renderiza: el juez no
    puede puntuar nada que el agente no tenga delante. Las líneas del índice (los
    oficios) se puntúan igual: `nombre: resumen`, que es lo que el índice imprime.
    """

    lineas = [
        (nodo.nombre, f"{nodo.nombre}: {nodo.resumen}")
        for nodo in arbol.nodos
        if nodo.cosmos == "sistema-solar"
    ]
    todos = [nombre for nombre, _ in lineas]
    lineas.extend(lineas_de_catalogo(arbol, todos))
    return lineas


def _puntuar(consulta: str, candidatos: list[tuple[str, str]]) -> list[tuple[float, str]]:
    """Las puntuaciones BM25 de cada candidato con puntuación > 0, ordenadas. `_ordenar` las usa;
    `tests/test_juez_honesto.py` fija sus VALORES sobre un corpus mínimo (R-09)."""

    terminos = list(dict.fromkeys(_normalizar(consulta)))
    if not terminos or not candidatos:
        return []

    documentos = [(_normalizar(texto), ruta) for ruta, texto in candidatos]
    frec_doc: Counter[str] = Counter()
    for tokens, _ in documentos:
        frec_doc.update(set(tokens))
    media = sum(len(t) for t, _ in documentos) / len(documentos) or 1.0

    n = len(documentos)
    k1, b = K1, B
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
    return puntuados


def _ordenar(consulta: str, candidatos: list[tuple[str, str]]) -> list[str]:
    """BM25 con la misma normalización que usa la búsqueda de memoria.

    No es el BM25 «clásico»: la IDF va suavizada por raíz cuadrada (`sqrt(idf + 1)`), no
    logarítmica, con `k1 = 1.5` y `b = 0.75`. Es una decisión de modelado y está
    **fijada** por `tests/test_juez_honesto.py::ElModeloDePuntuacionEstaFijado` con una
    tabla de puntuaciones esperadas (auditoría R-09): cambiar la IDF a la logarítmica
    «para que coincida con el docstring» sube la cifra publicada 10 puntos con la suite en
    verde. Cualquier cambio aquí se declara y se mide, no se disimula como corrección.
    """

    return [ruta for _, ruta in _puntuar(consulta, candidatos)]


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
    """Carga y valida el fichero de encargos, o explica qué le pasa.

    `rio/acertar` se anuncia en cualquier proyecto sobre el que se clone COSMOS, y en
    todos menos éste `pruebas/encargos.json` no existe: el caso de estreno terminaba en
    un `FileNotFoundError` crudo. El mismo trato que ya recibía `--validacion` —mensaje
    entero y salida limpia— se aplica aquí a lo que se lee, no solo a un fichero de los
    dos. Validar en el borde es lo que evita que el `KeyError` salga desde el fondo.
    """

    ruta = Path(ruta)
    try:
        crudo = ruta.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ErrorEncargos(
            f"no existe {ruta}: sin encargos no hay nada que puntuar. En un proyecto "
            "recién clonado es lo esperable — créalo como lista JSON de objetos "
            '{"peticion": "...", "espera": "ruta/del/nodo"} antes de medir el acierto.'
        ) from None
    except OSError as exc:
        raise ErrorEncargos(f"no se puede leer {ruta}: {exc}") from exc
    try:
        datos = json.loads(crudo)
    except json.JSONDecodeError as exc:
        raise ErrorEncargos(f"{ruta} no es JSON válido ({exc}); se esperaba una lista de encargos") from exc
    if not isinstance(datos, list):
        raise ErrorEncargos(f"{ruta} debe ser una lista de encargos y es {type(datos).__name__}")
    encargos: list[Encargo] = []
    for indice, dato in enumerate(datos):
        if (
            not isinstance(dato, dict)
            or not isinstance(dato.get("peticion"), str)
            or not isinstance(dato.get("espera"), str)
        ):
            raise ErrorEncargos(
                f"{ruta}: el encargo {indice} necesita 'peticion' y 'espera' de texto"
            )
        encargos.append(Encargo(peticion=dato["peticion"], espera=dato["espera"], nota=str(dato.get("nota", ""))))
    return encargos


def ruta_sello(ruta: str | Path, sello: str | Path | None = None) -> Path:
    """El sello vive en el repositorio; el holdout, fuera de él.

    Por defecto va al lado del fichero (`.SELLO`), que es lo que hace cómodo sellar un
    conjunto de prueba en un temporal. En el repositorio real se pasa explícito:
    `pruebas/encargos-validacion.SELLO` se versiona y el holdout al que ata no.
    """

    return Path(sello) if sello is not None else Path(ruta).with_suffix(".SELLO")


def sellar(ruta: str | Path, sello: str | Path | None = None, *, procedencia: str = "") -> dict:
    """Sella el holdout: a partir de aquí, su detalle por encargo no se enseña.

    El holdout anterior no lo quemó la mala fe: lo quemó un `--detalle`/`--json`
    abierto para ver qué fallaba. Un sello que no impida ESE gesto no sella nada.
    El fichero .SELLO se versiona: romperlo es borrarlo, y ese gesto queda en git.

    `procedencia` dice quién escribió el examen y en qué condiciones (auditoría B-05:
    el primero lo escribió quien ajusta el árbol, con el árbol delante, y eso solo se
    supo leyendo el registro). Un sello sin procedencia no dice de qué se fía uno.
    """

    encargos = cargar_encargos(ruta)  # valida el esquema antes de sellar
    datos = {
        "sha256": hashlib.sha256(Path(ruta).read_bytes()).hexdigest(),
        "sellado": date.today().isoformat(),
        "encargos": len(encargos),
        "procedencia": procedencia.strip(),
    }
    destino = ruta_sello(ruta, sello)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return datos


def leer_sello(ruta: str | Path, sello: str | Path | None = None) -> dict | None:
    fichero = ruta_sello(ruta, sello)
    if not fichero.is_file():
        return None
    try:
        datos = json.loads(fichero.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return datos if isinstance(datos, dict) else None


def sello_vigente(ruta: str | Path, sello: str | Path | None = None) -> bool:
    """El sello ata el CONTENIDO exacto: editar el fichero lo invalida, como una marca de lectura."""

    datos = leer_sello(ruta, sello)
    return bool(
        datos and Path(ruta).is_file()
        and datos.get("sha256") == hashlib.sha256(Path(ruta).read_bytes()).hexdigest()
    )


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

    Dos propiedades distintas, y se publican por separado (auditoría R-01):
    **integridad** (sellado, no quemado, no calcado del catálogo, brecha sana) es lo que el
    sistema puede comprobar; **atribución** —que la cifra describa el árbol y no a quien
    escribió el examen— NO la puede comprobar nadie mientras el examen lo escriba quien
    puede leer el árbol. Por eso este comando no dice nunca «la cifra que vale»: dice
    «cifra íntegra, no atribuible» o «DESCONOCIDA», y no ofrece listón.
    """

    ajuste: Puntuacion
    validacion: Puntuacion | None
    quemado: str | None = None
    sellado: bool = False
    # `sello_roto`: hubo sello y el contenido ya no coincide. Distinto de «nunca se
    # selló»: el primero es una edición después de fijar el examen (auditoría B-07).
    sello_roto: bool = False
    # Por qué no hay validación, cuando no la hay: se publica la razón, nunca un número.
    ausente: str | None = None
    procedencia: Procedencia | None = None
    cobertura: Cobertura | None = None
    declarada: str = ""   # la procedencia que declara el sello (texto libre: NO es una verificación)
    compromiso: Compromiso | None = None
    # Solape medio petición↔línea esperada: un examen calcado del catálogo lo delata (R-01).
    calcado: float | None = None
    calcado_ajuste: float | None = None   # el ajuste también se puede fabricar: entonces la brecha no dice nada
    # `None` = no se pudo comprobar (git no contestó); `True` = está versionado (quemado);
    # `False` = no lo está (fuera del repositorio o sin trackear), que es el caso normal.
    versionado: bool | None = False
    candidatos: int = 0   # líneas del catálogo sobre las que se puntúa (R-02: n del examen, no solo del árbol)

    @property
    def brecha(self) -> float | None:
        """Puntos porcentuales de más que saca el conjunto que sí se miró."""

        if not self.validacion or not self.validacion.total:
            return None
        return (100 * self.ajuste.aciertos / self.ajuste.total
                - 100 * self.validacion.aciertos / self.validacion.total)

    def motivos_no_integra(self) -> list[str]:
        """Todo lo que impide que la cifra de validación sea siquiera ÍNTEGRA. Vacío = íntegra.

        Cada motivo es una puerta que antes no existía o felicitaba al tramposo: sin
        holdout se publicaba la cifra del ajuste (nunca: es el examen que se mira); con
        el sello roto se decía «no publicable» y cuatro líneas después «la cifra que
        vale» (B-07); con el examen en el repositorio —o en su historia— se daba por
        ciego un conjunto que cualquiera podía leer con un `cat` (B-02); una brecha muy
        negativa se leía como elogio en vez de como alarma (B-03); y un examen fabricado
        copiando las líneas del catálogo pasaba por examen (R-01). Íntegra no es
        atribuible: eso lo dice `atribucion()`.
        """

        motivos: list[str] = []
        if self.validacion is None:
            return [self.ausente or "no hay conjunto de validación"]
        if not self.validacion.total:
            return ["el conjunto de validación está VACÍO: no vale de listón"]
        if self.quemado:
            motivos.append("QUEMADO: " + self.quemado.strip().splitlines()[0])
        if self.versionado is True:
            motivos.append("QUEMADO: el holdout está versionado en el repositorio; quien tiene el repo tiene el examen")
        elif self.versionado is None:
            motivos.append("no se pudo comprobar si el holdout está versionado (sin git)")
        if self.procedencia is not None:
            if self.procedencia.comprobada is None:
                motivos.append("procedencia NO comprobada: " + self.procedencia.motivo)
            elif self.procedencia.quemadas:
                motivos.append("QUEMADO: " + self.procedencia.motivo)
        if self.calcado is not None and self.calcado >= SOLAPE_CALCADO:
            motivos.append(
                f"CALCADO: las peticiones comparten el {self.calcado:.0%} de su vocabulario con la línea que esperan; "
                "eso no es un examen, es una copia del catálogo"
            )
        if self.calcado_ajuste is not None and self.calcado_ajuste >= SOLAPE_CALCADO:
            motivos.append(
                f"AJUSTE CALCADO: el conjunto de ajuste comparte el {self.calcado_ajuste:.0%} con sus líneas; "
                "una brecha medida contra un ajuste fabricado no significa nada"
            )
        if self.sello_roto:
            motivos.append("sello roto: el conjunto cambió después de sellarse ('cosmos acertar --sellar' lo fija de nuevo)")
        elif not self.sellado:
            motivos.append("sin sellar: 'cosmos acertar --sellar --procedencia \"...\"' fija el examen antes de medir")
        brecha = self.brecha
        if brecha is not None and brecha <= BRECHA_ALARMA:
            motivos.append(
                f"ALARMA: la validación va {-brecha:.0f} puntos por encima del ajuste; "
                "o el holdout se filtró a los resúmenes, o el ajuste está roto"
            )
        return motivos

    @property
    def integra(self) -> bool:
        return not self.motivos_no_integra()

    def atribucion(self) -> str:
        """Por qué la cifra NO se puede atribuir al árbol. Hoy, siempre hay un porqué.

        Ningún mecanismo de este repositorio puede probar que quien escribió el examen no
        había leído el árbol: la `procedencia` del sello es texto libre y el holdout vive
        en una ruta que el mismo agente puede leer. Lo único verificable es el compromiso
        (desde cuándo está fijado) y cuántos resúmenes cambiaron desde entonces.
        """

        partes = ["el examen lo escribe quien puede leer el árbol y la procedencia es una declaración, no una prueba"]
        if self.compromiso is not None and self.compromiso.commit:
            partes.append(f"compromiso: {self.compromiso.motivo}")
        elif self.compromiso is not None:
            partes.append(self.compromiso.motivo)
        return "; ".join(partes)

    def como_dict(self) -> dict[str, object]:
        validacion = self.validacion.como_dict() if self.validacion else None
        if validacion is not None:
            # El detalle por encargo es EXACTAMENTE lo que quema un holdout: verlo una vez
            # basta para escribir hacia el examen. Se redacta SIEMPRE, sellado o no
            # (auditoría R-08: un holdout recién escrito se quemaba con un solo `--json`).
            validacion["resultados"] = (
                "REDACTADO: el detalle por encargo quemaría el holdout; el de ajuste sí se enseña"
            )
        motivos = self.motivos_no_integra()
        return {
            "ajuste": self.ajuste.como_dict(),
            "validacion": validacion,
            "candidatos": self.candidatos,
            "brecha_puntos": self.brecha,
            "quemado": self.quemado,
            "integra": not motivos,
            "motivos_no_integra": motivos,
            "atribuible": False,
            "por_que_no_atribuible": self.atribucion(),
            "procedencia_declarada": self.declarada,
            "compromiso": (
                {"commit": self.compromiso.commit, "fecha": self.compromiso.fecha,
                 "commits_despues": self.compromiso.commits_despues,
                 "resumenes_cambiados_despues": self.compromiso.resumenes_cambiados_despues}
                if self.compromiso is not None else None
            ),
            "calcado": self.calcado,
            "calcado_ajuste": self.calcado_ajuste,
            "versionado": self.versionado,
            "procedencia_git": (
                {
                    "comprobada": self.procedencia.comprobada,
                    "quemadas": len(self.procedencia.quemadas),
                    "blobs_revisados": self.procedencia.blobs_revisados,
                }
                if self.procedencia is not None
                else None
            ),
            "cobertura": (
                {
                    "oficios_cubiertos": list(self.cobertura.oficios_cubiertos),
                    "oficios_sin_encargo": list(self.cobertura.oficios_sin_encargo),
                    "profundos": self.cobertura.profundos,
                    "total": self.cobertura.total,
                }
                if self.cobertura is not None
                else None
            ),
            "cifra_no_atribuible": (
                round(100 * self.validacion.aciertos / self.validacion.total, 1)
                if self.validacion and self.validacion.total and not motivos
                else None
            ),
        }


def formatear_contraste(c: Contraste) -> str:
    if not c.ajuste.total:
        return formatear(c.ajuste)

    aj = 100 * c.ajuste.aciertos / c.ajuste.total
    motivos = c.motivos_no_integra()
    sobre = f" sobre {c.candidatos} líneas de catálogo" if c.candidatos else ""
    lineas = [
        "COSMOS  acertar",
        "",
        f"  Ajuste ......... {c.ajuste.aciertos}/{c.ajuste.total} ({aj:.0f} %; "
        f"{formatear_intervalo(c.ajuste.aciertos, c.ajuste.total)}){sobre}   "
        "los encargos que SÍ se miran al trabajar",
    ]

    if not c.validacion or not c.validacion.total:
        # Un examen que no está no se aprueba por incomparecencia, y tampoco se
        # sustituye por el de ajuste: se dice por qué falta y se para ahí.
        lineas += [
            f"  Validación ..... NO DISPONIBLE   {motivos[0]}",
            "",
            "  Sin conjunto de validación no hay cifra: la de ajuste es la del examen que se",
            "  mira al trabajar, y mide puntería, no generalización.",
        ]
        return "\n".join(lineas + _pie_metodo()) + "\n"

    va = 100 * c.validacion.aciertos / c.validacion.total
    ic = formatear_intervalo(c.validacion.aciertos, c.validacion.total)
    n = c.validacion.total
    lineas.append(
        f"  Validación ..... {c.validacion.aciertos}/{n} ({va:.0f} %; {ic}; n={n})   "
        + ("YA MIRADO: es una segunda cifra de ajuste" if c.quemado
           else "escritos aparte; no guían ninguna decisión")
    )
    if c.cobertura is not None:
        faltan = ", ".join(c.cobertura.oficios_sin_encargo) or "ninguno"
        total_oficios = len(c.cobertura.oficios_cubiertos) + len(c.cobertura.oficios_sin_encargo)
        lineas.append(
            f"  Cobertura ...... {len(c.cobertura.oficios_cubiertos)}/{total_oficios} oficios "
            f"(sin encargo: {faltan}); {c.cobertura.profundos}/{c.cobertura.total} a profundidad ≥ 3"
        )
    if c.declarada:
        lineas.append(f"  Procedencia .... {c.declarada}   (declarada, NO verificada)")
    if c.compromiso is not None:
        lineas.append(f"  Compromiso ..... {c.compromiso.motivo}")
    if c.calcado is not None:
        lineas.append(f"  Calcado ........ solape petición↔línea esperada {c.calcado:.0%} (validación)"
                      + (f", {c.calcado_ajuste:.0%} (ajuste)" if c.calcado_ajuste is not None else "")
                      + (f"   (≥ {SOLAPE_CALCADO:.0%}: copia del catálogo)" if max(c.calcado, c.calcado_ajuste or 0) >= SOLAPE_CALCADO else ""))
    if c.procedencia is not None:
        if c.procedencia.comprobada is None:
            git = "NO COMPROBADA: " + c.procedencia.motivo
        elif c.procedencia.quemadas:
            git = "QUEMADO: " + c.procedencia.motivo
        else:
            git = "limpia; " + c.procedencia.motivo
        lineas.append(f"  Historia git ... {git}")
    if c.versionado is None:
        lineas.append("  Versionado ..... NO COMPROBADO (sin git)")
    elif c.versionado:
        lineas.append("  Versionado ..... SÍ: el holdout está en el repositorio (quemado)")
    else:
        lineas.append("  Versionado ..... no (fuera del repositorio o sin trackear)")
    lineas.append("")

    if motivos:
        lineas.append("  La cifra de validación NO es íntegra:")
        lineas.extend(f"    · {motivo}" for motivo in motivos)
        if c.quemado:
            lineas.extend(f"    {linea}" for linea in c.quemado.strip().splitlines()[1:3])
        lineas.append("  Mientras no haya un conjunto ciego, sellado y con procedencia, la cifra honesta es DESCONOCIDA.")
    else:
        lineas.append(f"  Cifra íntegra: {va:.0f} % ({ic}, n={n}). NO ATRIBUIBLE al árbol:")
        lineas.append(f"    {c.atribucion()}.")
        lineas.append("  Describe el instrumento sobre este examen, no la calidad del árbol; no hay listón que cobrar sobre ella.")

    brecha = c.brecha or 0.0
    if brecha >= 10:
        lineas += [
            f"  Y la brecha es de {brecha:.0f} puntos: parte de lo ganado es puntería sobre",
            "  las preguntas conocidas, no un árbol que lleve mejor. Se corrige mejorando",
            "  resúmenes en general, no los que salen en esta lista.",
        ]
    elif brecha <= BRECHA_ALARMA:
        lineas += [
            f"  ALARMA: la validación va {-brecha:.0f} puntos POR ENCIMA del ajuste. Eso no pasa",
            "  mejorando el árbol: pasa copiando el examen a los resúmenes o rompiendo el",
            "  ajuste. Revisión humana antes de creerse ninguna de las dos cifras.",
        ]
    elif brecha <= -5:
        lineas += [
            f"  La validación va {-brecha:.0f} puntos por delante del ajuste: no es un elogio,",
            "  es una señal a vigilar. Comprueba que el holdout sigue siendo ciego.",
        ]
    else:
        lineas.append(f"  Brecha de {brecha:.0f} puntos: sin señal de sobreajuste (lo ganado generaliza).")

    return "\n".join(lineas + _pie_metodo()) + "\n"


def _pie_metodo() -> list[str]:
    return [
        "",
        "  Método ......... BM25 léxico con recorte de sufijos, sobre la línea literal del",
        "                   índice y del catálogo. NO es un agente: mide si esa línea",
        "                   contiene las palabras del encargo, no si un modelo elegiría",
        "                   bien. Necesario, no suficiente.",
    ]
