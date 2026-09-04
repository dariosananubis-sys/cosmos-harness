"""Abrir un nodo: el verbo que le faltaba a COSMOS.

El hallazgo que lo motiva (`reviews/mejoras-especialista.md`, propuesta 1) es de
los que no se ven porque todo lo demás está bien: el sistema sabe **decidir** dónde
vive algo, **garantizar** que el árbol está bien formado y **medir** lo que cuesta —
pero no sabía **cargar un nodo cuando toca**.

Y el síntoma era peor de lo que parece. El catálogo entrega rutas cosmográficas
(`ciberseguridad/analisis`) y el disco tiene ficheros planos con otro nombre
(`galaxia/paises/ciberseguridad-analisis.md`), con `-` y `--` conviviendo como
separador. La ruta **no era derivable** del nombre de fichero, así que un agente que
leía una ruta en su contexto solo podía abrirla barriendo con `grep` — exactamente el
gasto que COSMOS existe para eliminar.

Un mapa que da direcciones que no se pueden seguir no es un mapa.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from .modelo import Arbol, NIVELES_AGUA, NIVELES_SOLIDOS, Nodo, cuerpo
from .validar import _glob_a_regex


@dataclass
class Apertura:
    nodo: Nodo
    estrella: Nodo | None
    hijos: list[Nodo] = field(default_factory=list)
    agua: list[Nodo] = field(default_factory=list)

    def como_dict(self) -> dict[str, object]:
        return {
            "ruta": self.nodo.referencia,
            "nivel": self.nodo.cosmos,
            "resumen": self.nodo.resumen,
            "cuerpo": cuerpo(self.nodo),
            "estrella": cuerpo(self.estrella) if self.estrella else None,
            "hijos": [
                {"ruta": h.referencia, "nivel": h.cosmos, "resumen": h.resumen}
                for h in self.hijos
            ],
            # Nombre y resumen, nunca el cuerpo: describir es una cosa y cargar es otra.
            # Volcar los seis mares eran 1.499 tokens por cada `abrir`, que es justo el
            # «cargarlo todo por si acaso» contra el que existe el proyecto (GOAL §2).
            "agua": [
                {"nombre": f"{a.cosmos}/{a.nombre}", "resumen": a.resumen} for a in self.agua
            ],
        }


class NodoNoEncontrado(LookupError):
    pass


def _indice(arbol: Arbol) -> dict[str, Nodo]:
    """Ruta cosmográfica -> nodo. Es lo que faltaba: la traducción."""

    indice: dict[str, Nodo] = {}
    for nodo in arbol.nodos:
        indice[nodo.referencia] = nodo
        ruta = getattr(nodo, "ruta_cosmos", None)
        if ruta:
            indice.setdefault(ruta, nodo)
        if nodo.cosmos in NIVELES_AGUA:
            indice.setdefault(f"{nodo.cosmos}/{nodo.nombre}", nodo)
    return indice


def resolver(arbol: Arbol, ruta: str) -> Nodo:
    """Encuentra un nodo por su ruta, o por su nombre si no es ambiguo.

    Acepta el nombre suelto por comodidad, pero **solo si identifica a uno**: si dos
    nodos lo comparten, es mejor un error que abrir el que no era. Un sistema que
    elige por ti cuando hay duda te hace perder más tiempo del que ahorra.
    """

    indice = _indice(arbol)
    if ruta in indice:
        return indice[ruta]

    candidatos = [n for n in arbol.nodos if n.nombre == ruta]
    if len(candidatos) == 1:
        return candidatos[0]
    if len(candidatos) > 1:
        rutas = ", ".join(sorted(n.referencia for n in candidatos))
        raise NodoNoEncontrado(f"'{ruta}' es ambiguo: {rutas}")

    cercanos = sorted(r for r in indice if ruta in r)[:5]
    pista = f" ¿Querías {', '.join(cercanos)}?" if cercanos else ""
    raise NodoNoEncontrado(f"no existe '{ruta}'.{pista}")


def agua_que_moja(arbol: Arbol, ruta_fichero: str | None) -> list[Nodo]:
    """El agua que alcanza a UN fichero concreto, por su glob real.

    `moja` es un glob de **ficheros** —`**/tests/**`, `**/*.tf`—, no una etiqueta de
    oficio. El primer intento filtraba por nicho (`nicho in str(moja)`) y devolvia los
    seis mares para cualquier nodo, porque todos los `moja` empiezan por `**/` y la
    comprobacion de subcadena siempre acertaba. Dos oficios sin nada en comun recibian
    identica lista.

    Sin fichero no hay respuesta: que se toca es lo unico que decide que agua moja, y
    adivinarlo es como devolverlo todo. Los oceanos no se listan porque mojan siempre —
    ya estan cargados antes de abrir nada.
    """

    if not ruta_fichero:
        return []

    # Una ruta absoluta devolvía agua vacía en silencio, porque los `moja` casan contra
    # rutas relativas al proyecto. Devolver «ninguna» ante algo que no se supo interpretar
    # es el mismo defecto que tenía el filtro por nicho al revés: aquí no se distingue
    # «este fichero no lo moja nada» de «no entendí lo que me diste».
    # Canonizar ANTES de casar. `tests//test_x.py` perdía tres de sus cuatro mares y
    # devolvía una respuesta creíble en vez de vacía —el componente vacío impide que
    # `[^/]*` llegue al final del patrón, así que se caían justo los criterios de código—
    # y `~/x.py`, al no empezar por `/`, recibía el agua del proyecto siendo del HOME.
    # Una respuesta plausible y equivocada es peor que ninguna: no se nota.
    relativa = str(PurePosixPath(os.path.expanduser(ruta_fichero)))
    if relativa.startswith("/"):
        candidata = Path(relativa)
        raices = [arbol.raiz, arbol.raiz.parent]
        for raiz in raices:
            try:
                relativa = str(candidata.relative_to(raiz))
                break
            except ValueError:
                continue
        else:
            raise NodoNoEncontrado(
                f"'{ruta_fichero}' está fuera del proyecto ({arbol.raiz.parent}): el agua se "
                f"decide por la ruta relativa a la raíz, así que una de fuera no moja nada. "
                f"Pásala relativa."
            )
    alcanzadas = []
    for nodo in arbol.nodos:
        if nodo.cosmos not in NIVELES_AGUA or nodo.cosmos == "oceano":
            continue
        patrones = [p for p in nodo.datos.get("moja", []) if isinstance(p, str)]
        if any(_glob_a_regex(patron).match(relativa) for patron in patrones):
            alcanzadas.append(nodo)
    return sorted(alcanzadas, key=lambda n: (n.cosmos, n.nombre))


def abrir(arbol: Arbol, ruta: str, *, tocando: str | None = None) -> Apertura:
    """Devuelve lo que hay que leer para trabajar en ese nodo, y nada más.

    El cuerpo del nodo, el de su estrella si la tiene (ahí está lo que es cierto en
    ese oficio y falso fuera), y **los nombres** de sus hijos — nombres, no cuerpos:
    describir a los hijos es cargarlos, que es lo que el `GOAL.md` prohíbe.

    Con `tocando`, ademas, **los nombres** del agua que alcanza a ese fichero concreto.
    """

    nodo = resolver(arbol, ruta)

    # `ilumina` lleva la ruta completa y solo se compara con la ruta completa. Aceptar
    # tambien el nombre suelto reabria la colision que NUCLEO §1 cerro: una estrella que
    # ilumina `calidad` se habria enganchado a cualquier `.../calidad` del arbol. La
    # comodidad de escribir el nombre ya la da `resolver`, que trata la duda como error.
    estrella = next(
        (
            n
            for n in arbol.nodos
            if n.cosmos == "estrella" and n.datos.get("ilumina") == nodo.referencia
        ),
        None,
    )

    hijos = sorted(
        (
            n
            for n in arbol.nodos
            if n.cosmos in NIVELES_SOLIDOS and n.datos.get("padre") == nodo.referencia
        ),
        key=lambda n: n.nombre,
    )

    return Apertura(
        nodo=nodo, estrella=estrella, hijos=hijos, agua=agua_que_moja(arbol, tocando)
    )


def formatear(ap: Apertura) -> str:
    lineas = [f"COSMOS  abrir  {ap.nodo.referencia}  ({ap.nodo.cosmos})", ""]

    texto = cuerpo(ap.nodo)
    if texto:
        lineas.extend([texto, ""])

    if ap.estrella:
        lineas.extend(["  ── lo que es cierto en este oficio ──", "", cuerpo(ap.estrella), ""])

    if ap.hijos:
        lineas.append("  ── por dónde seguir bajando ──")
        for h in ap.hijos:
            lineas.append(f"    {h.referencia}  ({h.cosmos})")
            # Los hijos hoja (pueblo, rio) se describen: es el último salto y hay que elegir
            # entre herramientas parecidas. Los intermedios solo se nombran (COMPOSICION.md,
            # «Qué se ve al abrir»; auditoría E-13).
            if h.cosmos in {"pueblo", "rio"}:
                lineas[-1] += f"\n      {h.resumen}"
        lineas.append("")

    usa = ap.nodo.datos.get("usa")
    if isinstance(usa, list) and usa:
        # Solo nombres, ~10 tokens: la relación declarada en el modelo era invisible para
        # quien navega, y una relación que nadie ve no existe (auditoría E-14). No carga nada.
        lineas.extend(["  ── oficios que este usa (solo nombres; no se cargan) ──", "    " + ", ".join(str(u) for u in usa), ""])

    if ap.agua:
        lineas.append("  ── agua que moja ese fichero ──")
        for a in ap.agua:
            lineas.extend([f"    {a.cosmos}/{a.nombre}", f"      {a.resumen}"])
        lineas.append("")

    return "\n".join(lineas).rstrip() + "\n"


def apertura_json(ap: Apertura) -> str:
    return json.dumps(ap.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
