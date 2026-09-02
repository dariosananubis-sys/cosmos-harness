"""Medición honesta del contexto controlado por COSMOS."""

from __future__ import annotations

import json
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
MARGEN_ERROR: float | None = 0.052
PATRON_TOKEN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


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


def _contador_exacto() -> tuple[Callable[[str], int], str] | None:
    try:
        import tiktoken  # type: ignore[import-not-found]
    except ImportError:
        return None
    codificacion = tiktoken.get_encoding("cl100k_base")
    return lambda texto: len(codificacion.encode(texto)), "tiktoken/cl100k_base"


def tokenizador_exacto_disponible() -> bool:
    return _contador_exacto() is not None


def _seleccionar_contador(metodo: str) -> tuple[Callable[[str], int], str, str | None, bool]:
    if metodo not in {"aprox", "exacto"}:
        raise ValueError("metodo debe ser aprox o exacto")
    if metodo == "exacto":
        exacto = _contador_exacto()
        if exacto is None:
            raise MetodoNoDisponible("se pidió método exacto, pero no hay tokenizador local")
        return exacto[0], "exacto", exacto[1], False
    return contar_aprox, "aprox", None, True


def agua_condicional(arbol: Arbol) -> list[Nodo]:
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
        and isinstance(nodo.datos.get("moja"), list)
        and nodo.datos["moja"]
        and cuerpo(nodo)
    ]


def catalogo_visible(arbol: Arbol, nichos: list[str] | tuple[str, ...] | None = None) -> str:
    """Materializa exactamente los nombres/resúmenes visibles antes de bajar."""

    seleccion = normalizar_nichos(arbol, nichos)
    con_resumen = {"pueblo", "rio"}
    intermedios = {"planeta", "continente", "pais", "provincia"}
    orden_agua = {"rio": len(RANGOS) + 1}

    def clave(nodo: Nodo) -> tuple[int, str]:
        return RANGOS.get(nodo.cosmos, orden_agua.get(nodo.cosmos, len(RANGOS) + 2)), nodo.referencia

    lineas: list[str] = []
    for nodo in sorted(arbol.nodos, key=clave):
        del_nicho = seleccion is not None and nicho_de_nodo(arbol, nodo) in seleccion
        if nodo.cosmos in intermedios:
            # Los intermedios son el mapa de descenso, y un mapa sin leyenda no
            # sirve: sin su resumen, «ciberseguridad/analisis» obliga a adivinar.
            # Medido el 2026-09-02 con la contra-métrica: con solo la ruta, el
            # catálogo acertaba el 10 % de 50 encargos reales.
            #
            # Pero solo los del oficio activo. Antes se listaban los 48 de los 21
            # oficios siempre, que es incoherente con el catálogo por nicho: quien
            # trabaja en `web` no necesita el mapa interno de `embebidos`, y el
            # índice ya nombra los 21 para saber que existen.
            if del_nicho:
                lineas.append(f"{nodo.ruta_cosmos}: {nodo.resumen}")
        elif nodo.cosmos == "pueblo":
            if del_nicho:
                lineas.append(f"{nodo.referencia}: {nodo.resumen}")
        elif nodo.cosmos in con_resumen:
            lineas.append(f"{nodo.referencia}: {nodo.resumen}")
    return "\n".join(lineas)


def _bloques_contexto_inicial(
    arbol: Arbol,
    indice: str | None = None,
    nichos: list[str] | tuple[str, ...] | None = None,
) -> list[tuple[str, str]]:
    indice_real = generar_indice(arbol) if indice is None else indice
    bloques: list[tuple[str, str]] = []
    if indice_real:
        bloques.append(("índice de galaxia", indice_real.rstrip("\n")))
    for nodo in sorted((n for n in arbol.nodos if n.cosmos == "oceano"), key=lambda n: n.nombre):
        contenido = cuerpo(nodo)
        if contenido:
            bloques.append((f"oceano/{nodo.nombre}", contenido))
    catalogo = catalogo_visible(arbol, nichos)
    if catalogo:
        bloques.append(("catálogo visible", catalogo))
    return bloques


def contexto_inicial(
    arbol: Arbol,
    nichos: list[str] | tuple[str, ...] | None = None,
    *,
    indice: str | None = None,
) -> str:
    """Materializa la secuencia normativa única que se paga al entrar."""

    return "\n".join(texto for _, texto in _bloques_contexto_inicial(arbol, indice, nichos))


def _extensiones_de(patrones: list[str]) -> set[str]:
    """Extensiones que un conjunto de globs puede tocar. `**` significa todas."""

    exts: set[str] = set()
    for patron in patrones:
        p = str(patron)
        if p.strip() in {"**", "**/*", "*"}:
            return {"*"}
        punto = p.rfind(".")
        exts.add(p[punto:] if punto != -1 and "/" not in p[punto:] else "*")
    return exts


def _peor_agua_coincidente(arbol: Arbol, contador) -> list[ParteMedida]:
    """El agua que de verdad puede coincidir, no la suma de toda el agua que existe.

    Sumar todos los mares supone que alguien toca un `.py`, un `.css` y un `.html`
    **en el mismo instante**, y por tanto que se cargan a la vez. No pasa: cada mar
    declara sus extensiones y `criterio` (código) y `accesibilidad` (marcado y hojas
    de estilo) casi no se solapan.

    Medido el 2026-09-02, el peor caso absoluto daba 1.499 tokens y dejaba 63 de
    margen; el peor caso **real** —la extensión que más agua atrae— es bastante
    menor. La diferencia no es un matiz: con la medida irreal, añadir una lección
    buena a un mar obligaba a recortar otra que no tenía nada que ver con ella.

    Se calcula por extensión: para cada una que alguna agua nombre, se suma lo que
    se cargaría al tocar un fichero así, y gana la más cara. Un agua que moja `**`
    entra siempre, porque de verdad entra siempre.
    """

    aguas = [
        (nodo, _extensiones_de(nodo.datos["moja"]), contador(cuerpo(nodo)))
        for nodo in agua_condicional(arbol)
    ]
    if not aguas:
        return []

    universales = [(n, c) for n, e, c in aguas if "*" in e]
    todas_ext = {e for _, exts, _ in aguas for e in exts if e != "*"}

    mejor: list[ParteMedida] = [
        ParteMedida(f"{n.cosmos}/{n.nombre}", c) for n, c in universales
    ]
    mejor_coste = sum(p.tokens for p in mejor)

    for ext in todas_ext:
        grupo = [(n, c) for n, exts, c in aguas if ext in exts or "*" in exts]
        coste = sum(c for _, c in grupo)
        if coste > mejor_coste:
            mejor_coste = coste
            mejor = [ParteMedida(f"{n.cosmos}/{n.nombre}", c) for n, c in grupo]
    return mejor


def medir_arbol(
    arbol: Arbol,
    *,
    metodo: str = "aprox",
    presupuesto: int = 4000,
    indice: str | None = None,
    nichos: list[str] | tuple[str, ...] | None = None,
) -> ResultadoMedicion:
    contador, metodo_real, tokenizador, estimado = _seleccionar_contador(metodo)
    seleccion = normalizar_nichos(arbol, nichos)
    partes_entrada = _bloques_contexto_inicial(arbol, indice, seleccion)

    # El índice y el catálogo se cuentan con su propio factor: son listas densas en
    # símbolos, no prosa, y tokenizan un 15 % peor (fallo F01). Con `exacto` no hay
    # dos factores que valgan — el tokenizador ya cuenta lo que hay.
    def _cuenta(nombre: str, texto: str) -> int:
        if metodo_real == "aprox" and ("índice" in nombre or "catálogo" in nombre):
            return contar_generado(texto)
        return contador(texto)

    detalle_entrada = [ParteMedida(nombre, _cuenta(nombre, texto)) for nombre, texto in partes_entrada]
    entrada = sum(parte.tokens for parte in detalle_entrada)
    nodos_resto = [nodo for nodo in arbol.nodos if nodo.cosmos != "oceano"]
    detalle_arbol = [
        ParteMedida(nodo.referencia, contador(cuerpo(nodo)))
        for nodo in sorted(nodos_resto, key=lambda n: (RANGOS.get(n.cosmos, 99), n.referencia, n.ruta_relativa))
    ]
    resto = sum(parte.tokens for parte in detalle_arbol)
    universo = entrada + resto
    descarga: float | str = "no_definida" if universo == 0 else 1 - entrada / universo
    detalle_agua = _peor_agua_coincidente(arbol, contador)
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
) -> ResumenMedicion:
    """Mide el caso base, cada nicho y, si se pidió, una selección concreta."""

    base = medir_arbol(arbol, metodo=metodo, presupuesto=presupuesto, indice=indice, nichos=None)
    por_nicho = [
        (
            nombre,
            medir_arbol(arbol, metodo=metodo, presupuesto=presupuesto, indice=indice, nichos=[nombre]),
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
        )
        if seleccion_nichos is not None
        else None
    )
    return ResumenMedicion(base, peor_nicho, peor, seleccion_nichos or (), seleccion)


def _numero(numero: int) -> str:
    return f"{numero:,}".replace(",", ".")


def formatear_medicion(resultado: ResultadoMedicion, *, detalle: bool = False) -> str:
    if resultado.metodo == "exacto":
        metodo = f"exacto, {resultado.tokenizador}"
    else:
        margen = "±desconocido" if resultado.margen_error is None else f"±{resultado.margen_error:.0%}"
        metodo = f"estimado, {margen}, {HEURISTICA}"
    descarga = (
        "no_definida"
        if resultado.descarga == "no_definida"
        else f"{float(resultado.descarga) * 100:.1f} %".replace(".", ",")
    )
    evaluado = resultado.entrada_con_agua
    if evaluado <= resultado.presupuesto:
        estado = f"OK, quedan {_numero(resultado.presupuesto - evaluado)} tokens"
    else:
        estado = f"ROJO, excede en {_numero(evaluado - resultado.presupuesto)} tokens"
    lineas = [
        "COSMOS  medir",
        "",
        f"  Entrada ......... {_numero(resultado.entrada)} tokens   ({metodo})",
        f"  Agua condicional  {_numero(resultado.agua)} tokens   ({len(resultado.detalle_agua)} aguas por paths:, fuera de la entrada)",
        f"  Entrada con agua  {_numero(evaluado)} tokens   (lo que se paga sin invocar nada)",
        f"  Universo ........ {_numero(resultado.universo)} tokens   ({metodo})",
        f"  Descarga ........ {descarga}",
        f"  Presupuesto ..... {_numero(resultado.presupuesto)}     {estado}",
        "",
        "  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)",
        "",
        "  Lo más caro de la entrada:",
    ]
    if resultado.detalle_entrada:
        for numero, parte in enumerate(resultado.detalle_entrada if detalle else resultado.detalle_entrada[:3], start=1):
            lineas.append(f"    {numero}.  {_numero(parte.tokens)} tok  {parte.nombre}")
    else:
        lineas.append("    (entrada vacía)")
    if detalle:
        lineas.extend(["", "  Resto, nodo a nodo:"])
        lineas.extend(f"    {_numero(parte.tokens)} tok  {parte.nombre}" for parte in resultado.detalle_arbol)
    return "\n".join(lineas) + "\n"


def formatear_casos(resultado: ResumenMedicion, *, detalle: bool = False) -> str:
    evaluada = resultado.evaluada
    if evaluada.metodo == "exacto":
        metodo = f"exacto, {evaluada.tokenizador}"
    else:
        margen = "±desconocido" if evaluada.margen_error is None else f"±{evaluada.margen_error:.0%}"
        metodo = f"estimado, {margen}, {HEURISTICA}"
    descarga = (
        "no_definida"
        if evaluada.descarga == "no_definida"
        else f"{float(evaluada.descarga) * 100:.1f} %".replace(".", ",")
    )
    evaluado = evaluada.entrada_con_agua
    if evaluado <= evaluada.presupuesto:
        estado = f"OK, quedan {_numero(evaluada.presupuesto - evaluado)} tokens"
    else:
        estado = f"ROJO, excede en {_numero(evaluado - evaluada.presupuesto)} tokens"
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
    if resultado.seleccion is None:
        ambito = "el peor caso"
    elif len(resultado.seleccion_nichos) == 1:
        ambito = "el nicho activo"
    else:
        ambito = "la combinación"
    lineas.extend(
        [
            f"  Peor con agua ... {_numero(evaluado)} tokens   ({ambito} + agua condicional)",
            f"  Universo ........ {_numero(evaluada.universo)} tokens   ({metodo})",
            f"  Descarga ........ {descarga}",
            f"  Presupuesto ..... {_numero(evaluada.presupuesto)}     {estado} en {ambito} con agua",
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


def medicion_json(resultado: ResultadoMedicion) -> str:
    return json.dumps(resultado.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def casos_json(resultado: ResumenMedicion) -> str:
    return json.dumps(resultado.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
