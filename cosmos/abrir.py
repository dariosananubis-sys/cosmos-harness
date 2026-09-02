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
from dataclasses import dataclass, field

from .modelo import Arbol, NIVELES_AGUA, NIVELES_SOLIDOS, Nodo, cuerpo


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
            "agua": [
                {"nombre": f"{a.cosmos}/{a.nombre}", "cuerpo": cuerpo(a)} for a in self.agua
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


def abrir(arbol: Arbol, ruta: str, *, con_agua: bool = False) -> Apertura:
    """Devuelve lo que hay que leer para trabajar en ese nodo, y nada más.

    El cuerpo del nodo, el de su estrella si la tiene (ahí está lo que es cierto en
    ese oficio y falso fuera), y **los nombres** de sus hijos — nombres, no cuerpos:
    describir a los hijos es cargarlos, que es lo que el `GOAL.md` prohíbe.
    """

    nodo = resolver(arbol, ruta)

    estrella = next(
        (
            n
            for n in arbol.nodos
            if n.cosmos == "estrella" and n.datos.get("ilumina") in {nodo.referencia, nodo.nombre}
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

    agua: list[Nodo] = []
    if con_agua:
        nicho = nodo.referencia.split("/", 1)[0]
        agua = sorted(
            (
                n
                for n in arbol.nodos
                if n.cosmos in NIVELES_AGUA
                and n.cosmos != "oceano"
                and any(nicho in str(m) or "**" in str(m) for m in n.datos.get("moja", []))
            ),
            key=lambda n: n.nombre,
        )

    return Apertura(nodo=nodo, estrella=estrella, hijos=hijos, agua=agua)


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
            if h.cosmos in {"pueblo", "ciudad", "rio"}:
                lineas[-1] += f"\n      {h.resumen}"
        lineas.append("")

    if ap.agua:
        lineas.append("  ── agua que moja este trabajo ──")
        for a in ap.agua:
            lineas.extend([f"    {a.cosmos}/{a.nombre}", f"      {cuerpo(a)}", ""])

    return "\n".join(lineas).rstrip() + "\n"


def apertura_json(ap: Apertura) -> str:
    return json.dumps(ap.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
