"""Medición honesta del contexto controlado por COSMOS."""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass, field
from typing import Callable

from .generar import generar_indice
from .modelo import NIVELES_AGUA, RANGOS, Arbol, Nodo, cuerpo, nicho_de_nodo, nombres_nichos, normalizar_nichos


HEURISTICA = "heurística v3"
# Dos factores, porque el error NO es uniforme y calibrarlo con un solo corpus fue
# el fallo F01: la v2 se midió sobre 78 ficheros de PROSA y no incluyó ni una muestra
# del índice ni del catálogo generados — que son justo los dos bloques que forman la
# entrada, y los que peor tokeniza contar palabras (listas de `ruta: resumen`, llenas
# de barras, guiones y acentos, sin prosa que amortigüe).
#
# Resultado de aquel descuido: con un tokenizador real el árbol estaba en 4.544/4.000
# mientras el medidor decía verde. El número que decide el proyecto iba un 15 % bajo.
#
# Medido el 2026-09-02 contra tiktoken/cl100k_base. Ver docs/CALIBRACION.md.
FACTOR_CALIBRACION = 1.204          # prosa: specs, fichas, código, agua
FACTOR_GENERADO = 1.381             # índice y catálogo: densos en símbolos
FACTOR_ESTRUCTURA = 1.314           # agua, estrellas y ríos: prosa española densa
MARGEN_ERROR: float | None = 0.052
# El peor fichero del corpus de calibración se fue a un tercio (código con muchos
# identificadores largos). No aplica al agregado que decide el presupuesto —el sesgo
# medio de muchos ficheros es, por desigualdad triangular, menor o igual que el error
# medio absoluto—, pero se publica, porque un margen que esconde su peor caso da una
# precisión falsa (auditoría A-10; docs/CALIBRACION.md).
PEOR_CASO_FICHERO: float | None = 0.336
# Lo que cuesta una línea más de catálogo (nombre + resumen), medido el 2026-09-03 sobre la galaxia
# añadiendo pueblos mínimos al peor nicho: ≈27,6 tokens cada uno (revisión §4.1).
COSTE_POR_HERRAMIENTA = 27.6
PATRON_TOKEN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def descripcion_margen(margen_error: float | None) -> str:
    """El margen tal cual está calibrado: `±5,2 %` no es `±5%`, y el peor caso se dice."""

    if margen_error is None:
        return "±desconocido"
    texto = f"±{margen_error * 100:.1f} %".replace(".", ",")
    if PEOR_CASO_FICHERO is not None:
        texto += f" medio (peor fichero {PEOR_CASO_FICHERO * 100:.1f} %)".replace(".", ",")
    return texto


class MetodoNoDisponible(RuntimeError):
    pass


@dataclass(frozen=True)
class ParteMedida:
    nombre: str
    tokens: int


@dataclass(frozen=True)
class ResultadoMedicion:
    entrada: int
    universo: int
    resto: int
    descarga: float | str
    metodo: str
    tokenizador: str | None
    estimado: bool
    margen_error: float | None
    presupuesto: int
    detalle_entrada: list[ParteMedida]
    detalle_arbol: list[ParteMedida]
    nichos: tuple[str, ...] = field(default_factory=tuple)
    pueblos_visibles: int = 0
    agua: int = 0
    detalle_agua: list[ParteMedida] = field(default_factory=list)
    fuera_cosmos: str = field(init=False, default="no_medido")

    @property
    def arbol(self) -> int:
        """Alias de compatibilidad; NUCLEO denomina universo al total."""

        return self.universo

    @property
    def entrada_con_agua(self) -> int:
        """Lo que se paga sin invocar nada: entrada + agua que se carga por 'paths:'.

        NUCLEO §3. El agua condicional ya está dentro de 'resto', así que no se
        vuelve a sumar a 'universo': solo se publica y se compara con el presupuesto.
        """

        return self.entrada + self.agua

    def como_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ResumenMedicion:
    base: ResultadoMedicion
    peor_nicho: str | None
    peor: ResultadoMedicion
    seleccion_nichos: tuple[str, ...] = field(default_factory=tuple)
    seleccion: ResultadoMedicion | None = None

    @property
    def evaluada(self) -> ResultadoMedicion:
        return self.seleccion or self.peor

    def como_dict(self) -> dict[str, object]:
        return {
            "base": self.base.como_dict(),
            "peor_nicho": self.peor_nicho,
            "peor": self.peor.como_dict(),
            "seleccion_nichos": list(self.seleccion_nichos),
            "seleccion": self.seleccion.como_dict() if self.seleccion is not None else None,
            "evaluada": "seleccion" if self.seleccion is not None else "peor_nicho",
        }


def contar_aprox(texto: str) -> int:
    """Cuenta palabras y signos, corregido por el factor medido contra un tokenizador real.

    Contar palabras es reproducible en cualquier máquina, pero **subestima**: un
    tokenizador BPE parte las palabras largas y los acentos. Medido sobre 78 ficheros
    de este repo, el sesgo era del 20,4 % y siempre en la misma dirección — es decir,
    predecible, y por tanto corregible.

    Con el factor, el error medio baja a 5,2 %. Ese número no es cosmético: sin él,
    el presupuesto era un 20 % más laxo de lo que decía ser, y un presupuesto que
    miente a su favor es peor que no tenerlo.
    """

    return round(len(PATRON_TOKEN.findall(texto)) * FACTOR_CALIBRACION)


def contar_generado(texto: str) -> int:
    """Cuenta índice y catálogo, que tokenizan un 15 % peor que la prosa.

    Una lista de `ruta: resumen` no se parece a un párrafo: cada barra, cada guion y
    cada acento es una pieza aparte para un tokenizador BPE. Usar aquí el factor de
    la prosa fue el fallo F01, y no era un matiz — ponía verde un árbol que estaba
    en rojo.
    """

    return round(len(PATRON_TOKEN.findall(texto)) * FACTOR_GENERADO)


def contar_estructura(texto: str) -> int:
    """Cuenta el agua, las estrellas y los ríos, que van un 9 % por encima de una ficha.

    Tercera clase de contenido y tercer factor, por la misma razón que hubo un segundo:
    **una calibración solo vale para el corpus con el que se hizo**. `FACTOR_CALIBRACION`
    salió de un corpus donde 264 de 312 muestras son fichas de herramienta, y las fichas
    tokenizan bien —llevan URLs, nombres propios e inglés, que es lo que `cl100k_base`
    conoce—. Los mares son prosa española densa y sin nada de eso:

        ficha            n=264   media 1.015x    <- manda en la media global
        agua/estructura  n= 48   media 1.091x    <- y es lo que se paga SIEMPRE

    El global decía 1.026x mientras el bloque caro iba a 1.091x, y por eso el árbol daba
    verde con el contador aproximado y rojo con el tokenizador real. La media de un corpus
    desequilibrado es la media de su clase mayoritaria con otro nombre.
    """

    return round(len(PATRON_TOKEN.findall(texto)) * FACTOR_ESTRUCTURA)


def _contador_exacto() -> tuple[Callable[[str], int], str] | None:
    try:
        import tiktoken  # type: ignore[import-not-found]
    except ImportError:
        return None
    codificacion = tiktoken.get_encoding("cl100k_base")
    return lambda texto: len(codificacion.encode(texto)), "tiktoken/cl100k_base"


def _seleccionar_contador(metodo: str) -> tuple[Callable[[str], int], str, str | None, bool]:
    if metodo not in {"aprox", "exacto"}:
        raise ValueError("metodo debe ser aprox o exacto")
    if metodo == "exacto":
        exacto = _contador_exacto()
        if exacto is None:
            raise MetodoNoDisponible("se pidió método exacto, pero no hay tokenizador local")
        return exacto[0], "exacto", exacto[1], False
    return contar_aprox, "aprox", None, True


def es_de_runtime(nodo: Nodo, solo_anfitrion: bool) -> bool:
    """En vista anfitrión, solo lo que `compilar` lleva al runtime se paga: los nodos con
    `anfitrion`. El resto del árbol (el catálogo genérico de COSMOS) se busca, no se carga."""

    return not solo_anfitrion or "anfitrion" in nodo.datos


def agua_condicional(arbol: Arbol, *, solo_anfitrion: bool = False) -> list[Nodo]:
    """Agua que no está en la entrada y se carga sola al tocar un fichero que moja.

    NUCLEO §3. Son los mares y lagos: entran por `paths:`, sin que nadie los
    invoque, y por eso su coste es real aunque no aparezca en `contexto_inicial`.
    Quedan fuera los océanos (ya están en la entrada) y el agua con `moja: []`
    —río y lluvia—, que se invoca a mano y cuyo resumen ya se paga en el catálogo.
    """

    return [
        nodo
        for nodo in arbol.nodos
        if nodo.cosmos in NIVELES_AGUA
        and nodo.cosmos != "oceano"
        and es_de_runtime(nodo, solo_anfitrion)
        and isinstance(nodo.datos.get("moja"), list)
        and nodo.datos["moja"]
        and cuerpo(nodo)
    ]


def nodos_de_catalogo(
    arbol: Arbol, nichos: list[str] | tuple[str, ...] | None = None, *, con_rios: bool = True,
    herramientas: tuple[str, ...] | None = None,
) -> list[Nodo]:
    """Los nodos con línea propia en el catálogo, en su orden. UNA selección para todos.

    La comparten el renderizado (`catalogo_visible`) y la contra-métrica
    (`acertar._lineas_del_catalogo`): si divergieran, la métrica volvería a puntuar
    sobre un recorte del árbol que ningún agente ve — el fallo que ya ocurrió una vez.
    Orden: el mapa del nicho en profundidad (alfabético por ruta = cada familia junta),
    después los ríos. Los de mantenimiento no llevan línea propia: los agrupa el render.
    """

    seleccion = normalizar_nichos(arbol, nichos)
    solidos = sorted(
        (
            nodo
            for nodo in arbol.nodos
            if nodo.cosmos in {"planeta", "continente", "pais", "provincia", "pueblo"}
            and seleccion is not None
            and nicho_de_nodo(arbol, nodo) in seleccion
            # El perfil del usuario (`cosmos configurar`) deja fuera los pueblos que no eligió.
            and (herramientas is None or nodo.cosmos != "pueblo" or nodo.nombre in herramientas)
        ),
        key=lambda nodo: nodo.ruta_cosmos,
    )
    if not con_rios:
        # El bloque que se proyecta sobre un repo ajeno no puede anunciar verbos que ese
        # repo no tiene (auditoría E-01): los ríos viven en el repositorio COSMOS de origen.
        return solidos
    rios = sorted(
        (nodo for nodo in arbol.nodos if nodo.cosmos == "rio"),
        key=lambda nodo: nodo.referencia,
    )
    return solidos + rios


def catalogo_visible(
    arbol: Arbol, nichos: list[str] | tuple[str, ...] | None = None, *, con_rios: bool = True,
    herramientas: tuple[str, ...] | None = None,
) -> str:
    """Materializa exactamente los nombres/resúmenes visibles antes de bajar.

    **Árbol indentado, no lista de rutas** (2026-09-02). El formato anterior pagaba la
    ruta completa en cada línea: en el peor nicho, el 40 % del coste eran prefijos
    repetidos («ciberseguridad/analisis/cadena-de-suministro/» delante de cinco pueblos),
    medido con tiktoken. Un pueblo paga ahora su nombre y su sitio lo dice la
    indentación — E18 garantiza que el nombre es único en toda la galaxia y
    `cosmos abrir <nombre>` resuelve. Los hijos directos del sistema conservan el
    prefijo `<nicho>/` porque son el ancla del árbol (y con varios nichos activos,
    la única forma de saber de cuál cuelga cada mapa).

    La idea viene del repo-map de aider (jerarquía comprimida bajo presupuesto de
    tokens); aquí sin grafo de referencias porque el árbol ya declara la jerarquía.
    """

    return "\n".join(texto for _, texto in lineas_de_catalogo(arbol, nichos, con_rios=con_rios, herramientas=herramientas))


LINEA_MANTENIMIENTO = "rio (mantenimiento, 'cosmos abrir rio/x')"


def lineas_de_catalogo(
    arbol: Arbol, nichos: list[str] | tuple[str, ...] | None = None, *, con_rios: bool = True,
    herramientas: tuple[str, ...] | None = None,
) -> list[tuple[str, str]]:
    """Cada línea del catálogo tal cual se renderiza, con la ruta del nodo que la paga.

    Es la única fuente del texto del catálogo: `catalogo_visible` la une con saltos de
    línea y `acertar._lineas_del_catalogo` la puntúa **literalmente**. Antes el juez
    componía su propio texto (`ruta completa + resumen`) y el render otro (nombre +
    resumen, indentado): la diferencia valía 10 puntos de la cifra publicada y nadie la
    había fijado (auditoría B-08). Ahora no puede divergir: se puntúa lo que se ve.
    """

    lineas: list[tuple[str, str]] = []
    de_mantenimiento: list[str] = []
    for nodo in nodos_de_catalogo(arbol, nichos, con_rios=con_rios, herramientas=herramientas):
        if nodo.cosmos == "rio":
            if nodo.datos.get("momento") == "mantenimiento":
                de_mantenimiento.append(nodo.nombre)
            else:
                lineas.append((nodo.referencia, f"{nodo.referencia}: {nodo.resumen}"))
            continue
        profundidad = nodo.ruta_cosmos.count("/")
        if profundidad <= 1:
            lineas.append((nodo.referencia, f"{nodo.ruta_cosmos}: {nodo.resumen}"))
        else:
            lineas.append((nodo.referencia, "  " * (profundidad - 1) + f"{nodo.nombre}: {nodo.resumen}"))

    # Los verbos de cuidar el repositorio se nombran, no se describen. `enganchar`,
    # `proyectar` o `generar` no resuelven el encargo de nadie y su resumen se pagaba en
    # cada sesión: coste que crece con lo que existe y no con lo que se usa, que es el
    # problema que este proyecto persigue. Siguen siendo descubribles —están aquí, y
    # `cosmos abrir rio/<nombre>` da el detalle entero—, solo dejan de estar precargados.
    if de_mantenimiento:
        lineas.append((LINEA_MANTENIMIENTO, f"{LINEA_MANTENIMIENTO}: " + ", ".join(sorted(de_mantenimiento))))
    return lineas


def _bloques_contexto_inicial(
    arbol: Arbol,
    indice: str | None = None,
    nichos: list[str] | tuple[str, ...] | None = None,
    *,
    con_rios: bool = True,
    herramientas: tuple[str, ...] | None = None,
    solo_anfitrion: bool = False,
) -> list[tuple[str, str]]:
    indice_real = generar_indice(arbol) if indice is None else indice
    bloques: list[tuple[str, str]] = []
    if indice_real:
        bloques.append(("índice de galaxia", indice_real.rstrip("\n")))
    for nodo in sorted((n for n in arbol.nodos if n.cosmos == "oceano"), key=lambda n: n.nombre):
        contenido = cuerpo(nodo)
        if contenido and es_de_runtime(nodo, solo_anfitrion):
            bloques.append((f"oceano/{nodo.nombre}", contenido))
    catalogo = catalogo_visible(arbol, nichos, con_rios=con_rios, herramientas=herramientas)
    if catalogo:
        bloques.append(("catálogo visible", catalogo))
    return bloques


def contexto_inicial(
    arbol: Arbol,
    nichos: list[str] | tuple[str, ...] | None = None,
    *,
    indice: str | None = None,
    con_rios: bool = True,
    herramientas: tuple[str, ...] | None = None,
) -> str:
    """Materializa la secuencia normativa única que se paga al entrar.

    `con_rios=False` es solo para el bloque proyectado sobre un repo ajeno (E-01): la
    secuencia normativa de NUCLEO §2 es la de `con_rios=True`.
    """

    return "\n".join(texto for _, texto in _bloques_contexto_inicial(arbol, indice, nichos, con_rios=con_rios, herramientas=herramientas))


def _detalle_agua(arbol: Arbol, contador, *, solo_anfitrion: bool = False) -> list[ParteMedida]:
    """Toda el agua condicional del árbol, que es la definición de NUCLEO §3.

    Aquí vivía un cálculo que agrupaba los mares «por extensión» y publicaba solo
    el grupo más caro. Su premisa era que nadie toca un `.py`, un `.css` y un
    `.html` **en el mismo instante**, y por tanto que no se cargan a la vez. Es
    falsa por dos motivos, y los dos se midieron (F06):

    1. El agua entra por `paths:` y **se queda en el contexto el resto de la
       sesión**. Un proyecto React + Python toca las dos cosas en la misma sesión
       y paga las dos. Lo que decide el presupuesto no es un instante, es la
       sesión — que es literalmente lo que `spec/MEDIDOR.md` llama «el techo real
       de una sesión de trabajo».
    2. La «extensión» se sacaba con `rfind(".")`, así que `**/tests/**` y
       `**/Makefile` se volvían universales, y dos globs que casan el MISMO
       fichero caían en grupos distintos y no se sumaban nunca. Medido: un árbol
       con `**/*.spec.*` y `**/*.ts` publicaba 240 tokens donde `src/app.spec.ts`
       carga 480. El medidor publicaba la mitad.

    Y era, además, una divergencia silenciosa de la norma: `NUCLEO.md` §3 define
    `agua = Σ tokens(cuerpo(n)) para n en agua_condicional(árbol)` y nadie tocó la
    spec al cambiar el código. Un medidor que se afloja para que quepa el
    contenido es el fallo F01 por la otra puerta.

    No se publica un segundo número «por fichero». Calcularlo de verdad es
    intersecar globs, y toda aproximación barata se equivoca **hacia abajo**, que
    es justo el error que este arreglo viene a cerrar. El detalle nodo a nodo
    (`medir --detalle`) dice quién cobra qué sin fabricar un segundo veredicto.
    """

    return [
        ParteMedida(f"{nodo.cosmos}/{nodo.nombre}", contador(cuerpo(nodo)))
        for nodo in agua_condicional(arbol, solo_anfitrion=solo_anfitrion)
    ]


@dataclass(frozen=True)
class Veredicto:
    """Un solo juez del presupuesto, para que no haya tres verdades.

    Había tres comparaciones distintas sobre el mismo árbol y las tres se publicaban con
    la misma etiqueta: E16 medía el peor caso con agua, `cosmos medir` el nicho activo
    con agua, y los guards de sesión el nicho activo **sin agua**. Con `[nichos] activos`
    puesto, `medir` decía «quedan 325» donde E16 vigilaba 119; el guard, más alto todavía.

    Lo que garantiza el presupuesto es que **cualquier sesión quepa**, así que el juez es
    siempre el peor nicho con toda su agua. El nicho activo se sigue enseñando, pero como
    dato, no como veredicto.
    """

    # Trivalente: `True` cabe, `False` no cabe, `None` = NO HABÍA NADA QUE MEDIR.
    # Sobre un árbol vacío —o un `--config` cuyo `arbol` resuelve a un directorio
    # que no está— el juez decía «OK, quedan 4.000 tokens»: `0 <= presupuesto` es
    # verdad, pero un cero que sale de no haber observado nada no es un verde, es
    # «no lo sé». Es el mismo patrón que `descarga` ya publica como `no_definida`.
    cabe: bool | None
    evaluado: int
    presupuesto: int
    nicho: str
    # Lo que se compara de verdad con el presupuesto: `evaluado` más el margen calibrado
    # de la heurística cuando la cifra es estimada. Con `exacto` coinciden.
    con_margen: int = 0
    margen_error: float = 0.0

    @property
    def margen(self) -> int:
        return self.presupuesto - self.con_margen

    def como_linea(self) -> str:
        if self.cabe is None:
            return "SIN MEDIR: el árbol no aporta ni un token; un veredicto sobre nada no es un OK"
        aplicado = (
            f" con el margen calibrado (+{self.margen_error * 100:.1f} %)".replace(".", ",")
            if self.margen_error
            else ""
        )
        if self.cabe:
            # El coste de entrada crece con cada alta del peor nicho (~28 tokens por herramienta,
            # revisión §4.1): decir cuántas caben es decir la verdad sobre lo que queda.
            caben = int(self.margen // (COSTE_POR_HERRAMIENTA * (1 + self.margen_error)))
            return (f"OK, quedan {self.margen} tokens{aplicado} en el peor caso con agua ({self.nicho}); "
                    f"≈ {caben} herramienta(s) más en ese nicho")
        return f"ROJO, excede en {-self.margen} tokens{aplicado} en el peor caso con agua ({self.nicho})"


def veredicto_de_presupuesto(casos: "ResumenMedicion", presupuesto: int) -> Veredicto:
    """El único sitio donde se decide si un árbol cabe. Los tres llamantes usan esto.

    Y se decide **con el margen calibrado encima** cuando la cifra es estimada: un
    guardarraíl que compara una estimación sesgada a la baja contra el techo se equivoca
    a su favor exactamente en el borde, que es donde importa. Ya pasó (F01: verde con el
    contador aproximado, 4.323/4.000 con el tokenizador real). Hoy el margen vivo era del
    12,8 % y el error medio calibrado del 5,2 % (auditoría A-10): se aplica el medio, que
    acota el sesgo del agregado; el peor caso por fichero (33,6 %) se publica y no se
    aplica, porque no describe una suma de quinientos ficheros. Con `exacto` no hay margen.
    """

    peor = casos.peor
    margen_error = float(peor.margen_error or 0.0) if peor.estimado else 0.0
    con_margen = math.ceil(peor.entrada_con_agua * (1 + margen_error))
    return Veredicto(
        cabe=None if peor.universo == 0 else con_margen <= presupuesto,
        evaluado=peor.entrada_con_agua,
        presupuesto=presupuesto,
        nicho=casos.peor_nicho or "sin nichos",
        con_margen=con_margen,
        margen_error=margen_error,
    )


def medir_arbol(
    arbol: Arbol,
    *,
    metodo: str = "aprox",
    presupuesto: int = 4000,
    indice: str | None = None,
    nichos: list[str] | tuple[str, ...] | None = None,
    herramientas: tuple[str, ...] | None = None,
    solo_anfitrion: bool = False,
) -> ResultadoMedicion:
    contador, metodo_real, tokenizador, estimado = _seleccionar_contador(metodo)
    seleccion = normalizar_nichos(arbol, nichos)
    partes_entrada = _bloques_contexto_inicial(arbol, indice, seleccion, herramientas=herramientas, solo_anfitrion=solo_anfitrion)

    # Tres clases de contenido, tres factores. El índice y el catálogo son listas densas
    # en símbolos y tokenizan un 15 % peor que una ficha (fallo F01); el agua y los
    # océanos son prosa española densa y van un 9 % por encima. Usar el de las fichas
    # para todo era lo que ponía verde un árbol que estaba en rojo — dos veces, y la
    # segunda con el arreglo de la primera ya puesto. Con `exacto` no hay factor que
    # valga: el tokenizador ya cuenta lo que hay.
    def _cuenta(nombre: str, texto: str) -> int:
        if metodo_real != "aprox":
            return contador(texto)
        if "índice" in nombre or "catálogo" in nombre:
            return contar_generado(texto)
        if nombre.startswith(("oceano/", "mar/", "lago/", "estrella/", "rio/")):
            return contar_estructura(texto)
        return contador(texto)

    detalle_entrada = [ParteMedida(nombre, _cuenta(nombre, texto)) for nombre, texto in partes_entrada]
    entrada = sum(parte.tokens for parte in detalle_entrada)
    # El universo es lo que un agente PODRÍA cargar trabajando. Los océanos quedan fuera
    # porque ya están dentro de `entrada`; la lluvia también, y por otra razón: son los
    # partes de commit del propio COSMOS, su historia interna. Nadie los carga para
    # resolver un encargo — `rio/memoria` los busca y devuelve dónde mirar, nunca el
    # cuerpo. Contarlos inflaba la descarga (98,42 % con ellos, 98,24 % sin ellos) y,
    # peor, la inflaba **sola**: cada parte nuevo mejoraba la cifra sin que el sistema
    # descargara nada. Una métrica que sube sola por escribir documentación no mide nada.
    nodos_resto = [
        nodo for nodo in arbol.nodos if nodo.cosmos not in {"oceano", "lluvia"}
    ]
    detalle_arbol = [
        ParteMedida(nodo.referencia, contador(cuerpo(nodo)))
        for nodo in sorted(nodos_resto, key=lambda n: (RANGOS.get(n.cosmos, 99), n.referencia, n.ruta_relativa))
    ]
    resto = sum(parte.tokens for parte in detalle_arbol)
    universo = entrada + resto
    descarga: float | str = "no_definida" if universo == 0 else 1 - entrada / universo
    contador_agua = contar_estructura if metodo_real == "aprox" else contador
    detalle_agua = _detalle_agua(arbol, contador_agua, solo_anfitrion=solo_anfitrion)
    return ResultadoMedicion(
        entrada=entrada,
        universo=universo,
        resto=resto,
        descarga=descarga,
        metodo=metodo_real,
        tokenizador=tokenizador,
        estimado=estimado,
        margen_error=MARGEN_ERROR if estimado else 0.0,
        presupuesto=presupuesto,
        detalle_entrada=sorted(detalle_entrada, key=lambda p: p.tokens, reverse=True),
        detalle_arbol=detalle_arbol,
        nichos=seleccion or (),
        pueblos_visibles=sum(
            1
            for nodo in arbol.nodos
            if nodo.cosmos == "pueblo" and seleccion is not None and nicho_de_nodo(arbol, nodo) in seleccion
        ),
        agua=sum(parte.tokens for parte in detalle_agua),
        detalle_agua=sorted(detalle_agua, key=lambda parte: parte.tokens, reverse=True),
    )


def medir_casos(
    arbol: Arbol,
    *,
    metodo: str = "aprox",
    presupuesto: int = 4000,
    indice: str | None = None,
    nichos: list[str] | tuple[str, ...] | None = None,
    herramientas: tuple[str, ...] | None = None,
    solo_anfitrion: bool = False,
) -> ResumenMedicion:
    """Mide el caso base, cada nicho y, si se pidió, una selección concreta.

    `herramientas` (el perfil de `cosmos configurar`) acota SOLO la selección del usuario: el
    peor nicho —el juez de E16— se mide siempre con todos los pueblos, porque el presupuesto
    tiene que valer para cualquier perfil.
    """

    base = medir_arbol(arbol, metodo=metodo, presupuesto=presupuesto, indice=indice, nichos=None, solo_anfitrion=solo_anfitrion)
    por_nicho = [
        (
            nombre,
            medir_arbol(arbol, metodo=metodo, presupuesto=presupuesto, indice=indice, nichos=[nombre], solo_anfitrion=solo_anfitrion),
        )
        for nombre in nombres_nichos(arbol)
    ]
    if por_nicho:
        peor_nicho, peor = max(por_nicho, key=lambda caso: caso[1].entrada)
    else:
        peor_nicho, peor = None, base
    seleccion_nichos = normalizar_nichos(arbol, nichos)
    seleccion = (
        medir_arbol(
            arbol,
            metodo=metodo,
            presupuesto=presupuesto,
            indice=indice,
            nichos=seleccion_nichos,
            herramientas=herramientas,
            solo_anfitrion=solo_anfitrion,
        )
        if seleccion_nichos is not None
        else None
    )
    return ResumenMedicion(base, peor_nicho, peor, seleccion_nichos or (), seleccion)


def _numero(numero: int) -> str:
    return f"{numero:,}".replace(",", ".")


def formatear_casos(resultado: ResumenMedicion, *, detalle: bool = False) -> str:
    evaluada = resultado.evaluada
    if evaluada.metodo == "exacto":
        metodo = f"exacto, {evaluada.tokenizador}"
    else:
        metodo = f"estimado, {descripcion_margen(evaluada.margen_error)}, {HEURISTICA}"
    descarga = (
        "no_definida"
        if evaluada.descarga == "no_definida"
        else f"{float(evaluada.descarga) * 100:.1f} %".replace(".", ",")
    )
    # La cuarta comparación, y la única que lee una persona. El commit «un solo juez»
    # unificó E16, el código de salida y los guards, y dejó ESTA calculándose aparte y
    # sobre `evaluada` (el nicho activo) en vez de sobre el peor caso: con nichos activos,
    # la salida decía «OK, quedan 93» y el mismo comando salía con 1.
    veredicto = veredicto_de_presupuesto(resultado, evaluada.presupuesto)
    evaluado = veredicto.evaluado
    estado = veredicto.como_linea()
    peor_nombre = resultado.peor_nicho or "sin nichos"
    lineas = [
        "COSMOS  medir",
        "",
        f"  Entrada base .... {_numero(resultado.base.entrada)} tokens   (índice + océanos + estructura, sin pueblos; {metodo})",
        f"  Peor nicho ...... {_numero(resultado.peor.entrada)} tokens   ({peor_nombre}, {resultado.peor.pueblos_visibles} pueblos)",
        f"  Agua condicional  {_numero(evaluada.agua)} tokens   ({len(evaluada.detalle_agua)} aguas por paths:, fuera de la entrada)",
    ]
    if resultado.seleccion is not None:
        nombres = ", ".join(resultado.seleccion_nichos)
        etiqueta = "Nicho activo ...." if len(resultado.seleccion_nichos) == 1 else "Combinación ....."
        lineas.append(
            f"  {etiqueta} {_numero(resultado.seleccion.entrada)} tokens   ({nombres}; {resultado.seleccion.pueblos_visibles} pueblos)"
        )
    # La cifra que se juzga es SIEMPRE el peor caso, elija quien elija los nichos activos.
    # Decir «el nicho activo» encima de un número que es el del peor caso era la última
    # etiqueta que quedaba mintiendo, y el veredicto ya trae dentro de qué nicho habla.
    if resultado.seleccion is None:
        nota_seleccion = ""
    elif len(resultado.seleccion_nichos) == 1:
        nota_seleccion = f"; nicho activo: {resultado.seleccion_nichos[0]}"
    else:
        nota_seleccion = f"; activos: {', '.join(resultado.seleccion_nichos)}"
    lineas.extend(
        [
            f"  Peor con agua ... {_numero(evaluado)} tokens   (el peor caso + agua condicional{nota_seleccion})",
            f"  Universo ........ {_numero(evaluada.universo)} tokens   ({metodo})",
            f"  Descarga ........ {descarga}",
            f"  Presupuesto ..... {_numero(evaluada.presupuesto)}     {estado}",
            "",
            "  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)",
            "",
            "  Lo más caro de la entrada evaluada:",
        ]
    )
    if evaluada.detalle_entrada:
        for numero, parte in enumerate(evaluada.detalle_entrada if detalle else evaluada.detalle_entrada[:3], start=1):
            lineas.append(f"    {numero}.  {_numero(parte.tokens)} tok  {parte.nombre}")
    else:
        lineas.append("    (entrada vacía)")
    if detalle:
        if evaluada.detalle_agua:
            lineas.extend(["", "  Agua condicional, nodo a nodo:"])
            lineas.extend(f"    {_numero(parte.tokens)} tok  {parte.nombre}" for parte in evaluada.detalle_agua)
        lineas.extend(["", "  Resto, nodo a nodo:"])
        lineas.extend(f"    {_numero(parte.tokens)} tok  {parte.nombre}" for parte in evaluada.detalle_arbol)
    return "\n".join(lineas) + "\n"


def casos_json(resultado: ResumenMedicion) -> str:
    return json.dumps(resultado.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
