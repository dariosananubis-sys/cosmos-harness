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
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from .modelo import Arbol, NIVELES_AGUA, NIVELES_SOLIDOS, RANGOS, cuerpo

# Las reglas 4, 5 y 2 de spec/PUEBLO.md, medidas como las midió la auditoría (A-06): son prosa
# y por eso se cuentan en vez de bloquear.
# El verbo comparativo tiene que ir seguido de un identificador entre acentos graves o en mayúscula
# (revisión R-23: `opentofu` salía «sin rival» diciendo «no `terraform`», y `nmap` no salía pese a no
# nombrar ninguno, por un «en vez de» que no comparaba herramientas).
PATRON_RIVAL = re.compile(
    r"(?:[Gg]ana a|[Ff]rente a|mejor que|a diferencia de|[Ff]rontera con|[Rr]eleva a|[Ss]ustituye a|en lugar de|y no)"
    r"[^.\n]{0,60}?(?:`[^`]+`|\b[A-Z][A-Za-z0-9]+(?:\.[a-z]+)?\b)"
)
PATRON_AVISO = re.compile(r"(Ojo|Aviso|No hace|no cubre|falso verde|Limitaci|límite|Límite)")
# La fecha puede partirse por un salto de línea («(comprobado\n2026-09-03)»): `\s+`.
PATRON_FECHA = re.compile(r"comprobado\s+(?:el\s+)?20\d\d-\d\d-\d\d")


@dataclass
class Inventario:
    por_nivel: dict[str, int]
    por_nicho: dict[str, int]
    nichos_sin_estrella: list[str]
    niveles_vacios: list[str]
    huerfanos: list[str]
    niveles_de_relleno: list[tuple[str, str]] = field(default_factory=list)
    # Los ríos por `momento`. `spec/NUCLEO.md` §2 retiró la enumeración a mano («la dice
    # el árbol — cosmos estado») y este comando no la decía (auditoría A-13).
    rios_por_momento: dict[str, list[str]] = field(default_factory=dict)
    # Lo que `spec/PUEBLO.md` exige y E21 no bloquea (rival nombrado, apartado de avisos):
    # se cuenta aquí para saldarlo por tandas (auditoría A-06 / C-13).
    contrato_pueblos: dict[str, list[str]] = field(default_factory=dict)

    def como_dict(self) -> dict[str, object]:
        return {
            "por_nivel": self.por_nivel,
            "por_nicho": self.por_nicho,
            "nichos_sin_estrella": self.nichos_sin_estrella,
            "niveles_vacios": self.niveles_vacios,
            "huerfanos": self.huerfanos,
            "niveles_de_relleno": [list(par) for par in self.niveles_de_relleno],
            "rios_por_momento": self.rios_por_momento,
            "contrato_pueblos": self.contrato_pueblos,
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

    rios: dict[str, list[str]] = defaultdict(list)
    for nodo in arbol.nodos:
        if nodo.cosmos == "rio":
            rios[str(nodo.datos.get("momento") or "trabajo")].append(nodo.nombre)

    contrato: dict[str, list[str]] = {"sin rival nombrado": [], "sin apartado de avisos": [], "sin fecha de comprobacion": []}
    for nodo in arbol.nodos:
        if nodo.cosmos != "pueblo":
            continue
        texto = cuerpo(nodo)
        if not PATRON_RIVAL.search(texto):
            contrato["sin rival nombrado"].append(nodo.nombre)
        if not PATRON_AVISO.search(texto):
            contrato["sin apartado de avisos"].append(nodo.nombre)
        if nodo.datos.get("origen") != "propio" and not PATRON_FECHA.search(texto):
            contrato["sin fecha de comprobacion"].append(nodo.nombre)

    return Inventario(
        por_nivel=dict(sorted(por_nivel.items(), key=lambda kv: RANGOS.get(kv[0], 99))),
        por_nicho=dict(por_nicho.most_common()),
        nichos_sin_estrella=sin_estrella,
        niveles_vacios=vacios,
        huerfanos=[],
        niveles_de_relleno=relleno,
        rios_por_momento={momento: sorted(nombres) for momento, nombres in sorted(rios.items())},
        contrato_pueblos={clave: sorted(nombres) for clave, nombres in contrato.items()},
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

    if inv.rios_por_momento:
        lineas.extend(["", "  Ríos por momento (NUCLEO §2: los de mantenimiento se nombran sin describirse)"])
        for momento, nombres in inv.rios_por_momento.items():
            lineas.append(f"    {momento:<16} {len(nombres):>4}   {', '.join(nombres)}")

    if any(inv.contrato_pueblos.values()):
        total = inv.por_nivel.get("pueblo", 0)
        lineas.extend(["", "  Contrato de pueblo (spec/PUEBLO.md) — lo que E21 no bloquea y hay que saldar por tandas"])
        for clave, nombres in inv.contrato_pueblos.items():
            if nombres:
                muestra = ", ".join(nombres[:6]) + (f", … y {len(nombres) - 6} más" if len(nombres) > 6 else "")
                lineas.append(f"    {clave:<26} {len(nombres):>4} de {total}   {muestra}")

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
