"""Inventario del árbol, generado en vez de escrito a mano.

Existe por un fallo concreto y documentado. `QUEDA.md` se escribió a mano
presentándose como «estado medido», y la revisión adversarial (hallazgo H11)
comprobó que era falso en 6 de sus 8 puntos: el repo avanzó y el documento no.

Es el mismo problema que COSMOS ya resuelve para el índice de la galaxia —
**lo que se escribe a mano se desincroniza**— y la misma solución: se genera.
Un inventario generado no puede mentir sobre el árbol que acaba de contar.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from .modelo import Arbol, NIVELES_AGUA, NIVELES_SOLIDOS, RANGOS


@dataclass
class Inventario:
    por_nivel: dict[str, int]
    por_nicho: dict[str, int]
    nichos_sin_estrella: list[str]
    niveles_vacios: list[str]
    huerfanos: list[str]
    niveles_de_relleno: list[tuple[str, str]] = field(default_factory=list)

    def como_dict(self) -> dict[str, object]:
        return {
            "por_nivel": self.por_nivel,
            "por_nicho": self.por_nicho,
            "nichos_sin_estrella": self.nichos_sin_estrella,
            "niveles_vacios": self.niveles_vacios,
            "huerfanos": self.huerfanos,
            "niveles_de_relleno": [list(par) for par in self.niveles_de_relleno],
        }


def _nicho(ruta: str) -> str:
    return ruta.split("/", 1)[0] if ruta else ""


def inventariar(arbol: Arbol) -> Inventario:
    por_nivel = Counter(nodo.cosmos for nodo in arbol.nodos)

    por_nicho: Counter[str] = Counter()
    hijos: dict[str, list[str]] = defaultdict(list)
    for nodo in arbol.nodos:
        padre = nodo.datos.get("padre")
        if isinstance(padre, str) and padre:
            hijos[padre].append(nodo.nombre)
        if nodo.cosmos == "pueblo" and isinstance(padre, str):
            por_nicho[_nicho(padre)] += 1

    sistemas = [n.nombre for n in arbol.nodos if n.cosmos == "sistema-solar"]
    iluminados = {
        n.datos.get("ilumina") for n in arbol.nodos if n.cosmos == "estrella"
    }
    sin_estrella = sorted(s for s in sistemas if s not in iluminados)

    vacios = sorted(
        nivel
        for nivel in (*NIVELES_SOLIDOS, *NIVELES_AGUA, "estrella", "luna")
        if not por_nivel.get(nivel)
    )

    # Un nivel intermedio con un solo hijo no agrupa: estorba y cobra su resumen
    # (spec/TAXONOMIA.md). No es un error del validador, es una señal para quien mira.
    relleno = sorted(
        (ruta, unico[0])
        for ruta, unico in hijos.items()
        if len(unico) == 1 and ruta
    )

    return Inventario(
        por_nivel=dict(sorted(por_nivel.items(), key=lambda kv: RANGOS.get(kv[0], 99))),
        por_nicho=dict(por_nicho.most_common()),
        nichos_sin_estrella=sin_estrella,
        niveles_vacios=vacios,
        huerfanos=[],
        niveles_de_relleno=relleno,
    )


def formatear(inv: Inventario) -> str:
    lineas = ["COSMOS  estado", ""]

    lineas.append("  Nodos por nivel")
    for nivel, n in inv.por_nivel.items():
        lineas.append(f"    {nivel:<16} {n:>4}")

    lineas.extend(["", "  Herramientas por oficio"])
    for nicho, n in inv.por_nicho.items():
        lineas.append(f"    {nicho:<20} {n:>4}")

    if inv.por_nicho:
        valores = list(inv.por_nicho.values())
        lineas.append(f"    {'':<20} {'':>4}   (mayor {max(valores)}, menor {min(valores)})")

    if inv.nichos_sin_estrella:
        lineas.extend(["", "  Oficios SIN estrella — una puerta que no dice nada al entrar"])
        for nombre in inv.nichos_sin_estrella:
            lineas.append(f"    {nombre}")

    if inv.niveles_vacios:
        lineas.extend(["", "  Niveles sin un solo nodo"])
        lineas.append("    " + ", ".join(inv.niveles_vacios))
        # H20 salió de leer esta lista como «media taxonomía está muerta». No lo
        # estaba: seis de los ocho niveles vivían en el otro árbol del repositorio.
        # El inventario carga la raíz que le pasan y no puede saberlo; quien sí puede
        # es el canario, que cuenta sobre todos los árboles a la vez.
        lineas.append("    (no es un fallo: son niveles que este árbol no necesita)")
        lineas.append("    (que ninguno esté muerto lo vigila tests/test_niveles_vivos.py)")

    if inv.niveles_de_relleno:
        lineas.extend(["", "  Niveles con un solo hijo — no agrupan, y su resumen se paga"])
        for ruta, unico in inv.niveles_de_relleno[:12]:
            lineas.append(f"    {ruta}  ->  {unico}")
        if len(inv.niveles_de_relleno) > 12:
            lineas.append(f"    … y {len(inv.niveles_de_relleno) - 12} más")

    return "\n".join(lineas) + "\n"


def estado_json(inv: Inventario) -> str:
    return json.dumps(inv.como_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
