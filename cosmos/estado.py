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


# --- La máquina: qué falta en ESTE ordenador ---------------------------------------------
#
# El inventario de arriba cuenta el árbol; este cuenta la máquina en la que se instaló, y es
# lo que hace verificable el alta en un ordenador nuevo. Cada fila es trivalente —`ok`,
# `falta`, `no_comprobado`— y jamás dice `ok` por no haber podido mirar: un `ok` en el
# llavero por haber encontrado el binario sería una bandera de seguridad que mide una
# ausencia. No cambia el veredicto de `validar`: es inventario, como el resto de `estado`.


@dataclass(frozen=True)
class FilaMaquina:
    nombre: str
    estado: str  # ok | falta | inseguro | no_comprobado | desactualizado | ajeno | auto | libre | manual | desconocido
    detalle: str


def _version_de(orden: list[str]) -> str | None:
    import subprocess

    try:
        resultado = subprocess.run(orden, capture_output=True, text=True, check=False, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if resultado.returncode:
        return None
    salida = (resultado.stdout or resultado.stderr).strip().splitlines()
    return salida[0].strip() if salida else ""


def inventariar_maquina(arbol: Arbol, *, directorio=None, raiz_clon=None) -> list[FilaMaquina]:
    import os
    import shutil
    import sys
    from pathlib import Path

    from . import configurar as cfg

    directorio = Path(directorio) if directorio else cfg.DIRECTORIO
    filas: list[FilaMaquina] = []

    version = ".".join(str(v) for v in sys.version_info[:3])
    filas.append(FilaMaquina("python3", "ok" if sys.version_info >= (3, 11) else "falta",
                             f"{version}  (>= 3.11 exigido por tomllib)"))
    for nombre, orden, nota in (("git", ["git", "--version"], "obligatorio: el gate, el juez y el escáner preguntan a git"),
                                ("claude", ["claude", "--version"], "el runtime al que se engancha COSMOS"),
                                ("tmux", ["tmux", "-V"], "opcional; solo para el pueblo de consola interactiva")):
        if shutil.which(nombre) is None:
            filas.append(FilaMaquina(nombre, "falta", nota))
        else:
            salida = _version_de(orden)
            filas.append(FilaMaquina(nombre, "ok" if salida is not None else "no_comprobado",
                                     (salida or "instalado; no respondió a --version") + f"  ({nota})"))
    if sys.platform != "darwin":
        filas.append(FilaMaquina("llavero", "no_comprobado", "solo macOS (security add-generic-password)"))
    elif shutil.which("security") is None:
        filas.append(FilaMaquina("llavero", "falta", "no está `security`"))
    else:
        filas.append(FilaMaquina("llavero", "no_comprobado", "`security` existe; no se prueba una escritura sin permiso"))

    perfil = directorio / cfg.PERFIL.name
    datos = cfg.leer_perfil(perfil)
    if datos is None:
        filas.append(FilaMaquina("perfil", "falta", f"{perfil} no existe -> cosmos configurar"))
        herramientas: list[str] = []
    else:
        oficios = [o for o in datos.get("oficios", []) if isinstance(o, str)]
        herramientas = [h for h in datos.get("herramientas", []) if isinstance(h, str)]
        filas.append(FilaMaquina("perfil", "ok", f"{perfil}  ({len(oficios)} oficio(s), {len(herramientas)} herramienta(s))"))
    credenciales = directorio / cfg.CREDENCIALES.name
    esperadas = cfg.credenciales_de(arbol, herramientas) if herramientas else []
    if not esperadas:
        filas.append(FilaMaquina("credenciales", "ok" if datos is not None else "no_comprobado",
                                 "ninguna herramienta elegida pide credenciales" if datos is not None else "sin perfil no se sabe cuáles hacen falta"))
    elif not credenciales.is_file():
        filas.append(FilaMaquina("credenciales", "falta", f"{credenciales} no existe -> cosmos configurar"))
    elif _permisos_flojos(directorio, credenciales):
        # «ok» con el fichero en 644 era un verde que mentía sobre lo único que el README
        # promete de las credenciales: 700 el directorio, 600 el fichero (revisión C-11).
        filas.append(FilaMaquina("credenciales", "inseguro", _permisos_flojos(directorio, credenciales)))
    else:
        faltan, sospechosas = cfg.comprobar_credenciales(esperadas, cfg.leer_credenciales(credenciales))
        total = len({c.variable for c in esperadas})
        if faltan or sospechosas:
            filas.append(FilaMaquina("credenciales", "falta",
                                     f"{len(faltan)} vacía(s) y {len(sospechosas)} sospechosa(s) de {total} -> cosmos configurar --comprobar"))
        else:
            filas.append(FilaMaquina("credenciales", "ok", f"{total} de {total} rellenas ({credenciales})"))

    grado, detalle = cfg.grado_vigente()
    filas.append(FilaMaquina("autonomia", grado, f"{cfg.ajustes_usuario()}  {detalle}"
                             + ("" if grado in ("auto", "libre") else "  -> cosmos configurar --autonomia auto")))

    from puente import modelos as mod

    de_modelos = mod.estado(perfil=cfg.leer_modelos(perfil))
    reponedor = next((f for f in de_modelos if f.nombre == "reponedor"), None)
    if reponedor is None or reponedor.estado == "falta":
        filas.append(FilaMaquina("modelos", "falta", "vigilante no instalado -> cosmos configurar --modelos instalar"))
    else:
        malos = [f for f in de_modelos if f.estado in ("falta", "desactualizado", "ajeno")]
        if malos:
            filas.append(FilaMaquina("modelos", malos[0].estado, f"{malos[0].nombre}: {malos[0].detalle}  -> cosmos configurar --modelos estado"))
        else:
            filas.append(FilaMaquina("modelos", "ok", f"vigilante instalado ({len(mod.MODELOS)} modelos; acceso de la cuenta no_comprobado)"))

    lanzador = cfg.LANZADOR
    if not lanzador.exists():
        filas.append(FilaMaquina("lanzador", "falta", f"{lanzador} no existe -> cosmos configurar --lanzador"))
    elif not cfg.es_lanzador_nuestro(lanzador):
        filas.append(FilaMaquina("lanzador", "ajeno", f"{lanzador} existe y no es nuestro"))
    else:
        apunta = cfg.raiz_del_lanzador(lanzador)
        if apunta is None or not (apunta / "cosmos" / "__main__.py").is_file():
            filas.append(FilaMaquina("lanzador", "falta", f"{lanzador} apunta a un clon que ya no existe ({apunta}) -> cosmos configurar --lanzador"))
        elif raiz_clon is not None and Path(raiz_clon).resolve() != apunta.resolve():
            filas.append(FilaMaquina("lanzador", "desactualizado", f"{lanzador} apunta a {apunta}, no a este clon"))
        elif lanzador.read_text(encoding="utf-8") != cfg.contenido_lanzador(apunta):
            # Decía «ok» con un shim de una plantilla anterior: el 2026-09-12 el instalado no
            # exportaba COSMOS_RAIZ y `cosmos buscar` desde otro directorio decía «sin resultados»
            # mientras el inventario daba verde. Se compara con lo que este clon escribiría hoy.
            filas.append(FilaMaquina("lanzador", "desactualizado",
                                     f"{lanzador} no es el shim que este clon escribiría hoy -> cosmos configurar --lanzador"))
        else:
            en_path = str(lanzador.parent) in os.environ.get("PATH", "").split(os.pathsep)
            filas.append(FilaMaquina("lanzador", "ok" if en_path else "falta",
                                     f"{lanzador} -> {apunta}" + ("" if en_path else f"  ({lanzador.parent} no está en el PATH)")))

    puntero = cfg.PUNTERO
    vigente = cfg.puntero_vigente(puntero)
    if vigente is None:
        filas.append(FilaMaquina("puntero", "falta", f"{puntero} sin el bloque de COSMOS -> cosmos configurar --puntero"))
    elif raiz_clon is None:
        filas.append(FilaMaquina("puntero", "no_comprobado", f"{puntero} lleva el bloque; sin clon de referencia no se compara"))
    else:
        oceanos = sorted(n.nombre for n in arbol.nodos if n.cosmos == "oceano")
        if vigente == cfg.contenido_puntero(oceanos, Path(raiz_clon).resolve()):
            filas.append(FilaMaquina("puntero", "ok", f"{puntero} apunta a este clon y nombra sus océanos"))
        else:
            filas.append(FilaMaquina("puntero", "desactualizado", f"{puntero} no coincide con lo que este clon escribiría -> cosmos configurar --puntero"))
    return filas


def _permisos_flojos(directorio, credenciales) -> str | None:
    import stat

    try:
        modo_dir = stat.S_IMODE(directorio.stat().st_mode)
        modo_fich = stat.S_IMODE(credenciales.stat().st_mode)
    except OSError:
        return None
    problemas = []
    if modo_dir & 0o077:
        problemas.append(f"{directorio} es {modo_dir:o}, debería ser 700 -> chmod 700 {directorio}")
    if modo_fich & 0o077:
        problemas.append(f"{credenciales} es {modo_fich:o}, debería ser 600 -> chmod 600 {credenciales}")
    return "; ".join(problemas) or None


def formatear_maquina(filas: list[FilaMaquina]) -> str:
    from .configurar import abreviar_home

    lineas = ["COSMOS  estado  maquina", ""]
    for fila in filas:
        lineas.append(f"  {fila.nombre + ' ':.<20} {fila.estado:<15} {abreviar_home(fila.detalle)}")
    return "\n".join(lineas) + "\n"


def maquina_json(filas: list[FilaMaquina]) -> str:
    return json.dumps([{"nombre": f.nombre, "estado": f.estado, "detalle": f.detalle} for f in filas],
                      ensure_ascii=False, indent=2) + "\n"
