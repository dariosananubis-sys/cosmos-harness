#!/usr/bin/env python3
"""Guardarraíles de SESIÓN: los que actúan mientras el agente trabaja.

COSMOS se enganchaba en tres sitios —pre-commit, CI y arranque— y los tres son
**de repositorio**: miran lo que ya está escrito. Entre medias, durante las horas
en que un agente edita, mide y decide, no había nada. Este módulo es el enganche
que faltaba en `spec/GUARDARRAILES.md`.

Cinco mecanismos, cada uno con su código de válvula (`cosmos saltar G0x`):

| Código | Evento | Efecto |
|---|---|---|
| G01 | `SessionStart` | Dice la entrada REAL medida, y en rojo si se pasó del presupuesto |
| G02 | `Stop` | Impide cerrar con el árbol en rojo, con contador propio y tope duro |
| G03 | `PreToolUse` | Deniega escribir a mano sobre las rutas de veredicto |
| G04 | `PreToolUse` | Exige haber leído entero lo que la configuración declare, en ESTA sesión |
| G05 | `PostToolUse` | Reescribe la salida ya ocurrida: tapa secretos y aparta lo enorme |

Contrato con el runtime, deliberadamente estrecho: **un evento JSON por la
entrada estándar, una decisión por la salida**. La decisión se renderiza en dos
formas —JSON estructurado (`--formato json`) o bloqueo binario por `exit 2` con
el motivo en `stderr` (`--formato exit2`)— y esas dos son toda la superficie que
depende de quién nos llame. Todo lo demás son funciones puras sobre rutas y texto.

Nada se instala solo al importar este módulo. El cableado lo pone
`cosmos enganchar --sesion` y lo quita `cosmos desenganchar`.

Presupuesto: los guards de `PreToolUse`/`PostToolUse` corren en CADA llamada a
una herramienta y no cargan el árbol; los de `SessionStart`/`Stop` sí lo cargan,
y corren una vez. Jamás red, jamás subprocesos.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import sys
import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from cosmos.guardarrailes import (
    Salto,
    ahora_utc,
    anotar_salida,
    estado_saltos,
    ruta_saltos,
)
from cosmos.medir import medir_casos
from cosmos.modelo import (
    ErrorConfiguracion,
    ErrorNicho,
    cargar_arbol,
    cargar_configuracion,
    normalizar_nichos,
)
from cosmos.validar import validar_arbol

from .secretos import redactar_texto

EVENTOS = ("SessionStart", "PreToolUse", "PostToolUse", "PreCompact", "Stop")

CODIGO_PRESUPUESTO = "G01"
CODIGO_CIERRE = "G02"
CODIGO_VEREDICTO = "G03"
CODIGO_LECTURA = "G04"
CODIGO_REDACCION = "G05"

# Ni una sola vez (avisar y callarse no verifica nada) ni infinitas (un bucle sin
# salida se desinstala el mismo día). Tres, y después se deja cerrar anotándolo.
TOPE_AVISOS = 3
MAX_BYTES = 50_000
MAX_LINEAS = 2_000

HERRAMIENTAS_ESCRITURA = ("Write", "Edit", "MultiEdit", "NotebookEdit")
DIRECTORIO_SESION = "sesion"
NOMBRE_LOG_CIERRES = "cierres.log"

_REDIRECCION = re.compile(r"^(?P<descriptor>[0-9]*)>>?(?P<destino>.*)$")
_ASIGNACION = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# Quien produce los artefactos de veredicto es COSMOS, no una redirección a mano.
_PRODUCTOR = re.compile(r"^(?:python[0-9.]*|py)$|^cosmos$")
_ESCRIBE_EN_EL_ULTIMO = frozenset({"cp", "mv", "install", "ln", "rsync"})
_ESCRIBE_EN_TODOS = frozenset({"tee", "truncate"})


class ErrorSesion(RuntimeError):
    """El evento no se puede atender: no hay árbol, o la configuración no carga."""


# --- Decisión y renderizado ------------------------------------------------


@dataclass(frozen=True)
class Decision:
    """Lo que el guard decide, sin saber quién lo va a leer.

    `accion` es una de: `pasar` (silencio), `denegar` (la herramienta no llega a
    ejecutarse), `bloquear` (no se cierra la sesión), `reescribir` (lo que el
    modelo ve de una ejecución ya ocurrida) e `informar` (mensaje sin efecto).
    """

    accion: str = "pasar"
    motivo: str = ""
    salida: str | None = None
    codigo_salida: int = 0
    contexto: str = ""

    @property
    def bloquea(self) -> bool:
        return self.accion in {"denegar", "bloquear"}


PASAR = Decision()


def como_json(decision: Decision, evento: str) -> str:
    """Envoltorio estructurado. Cadena vacía = pasar sin decir nada."""

    if decision.accion == "denegar":
        cuerpo = {
            "hookSpecificOutput": {
                "hookEventName": evento,
                "permissionDecision": "deny",
                "permissionDecisionReason": decision.motivo,
            }
        }
    elif decision.accion == "bloquear":
        cuerpo = {"decision": "block", "reason": decision.motivo}
    elif decision.accion == "reescribir":
        especifico: dict[str, object] = {
            "hookEventName": evento,
            "updatedToolOutput": {
                "output": decision.salida or "",
                "exit_code": decision.codigo_salida,
            },
        }
        if decision.contexto:
            especifico["additionalContext"] = decision.contexto
        cuerpo = {"hookSpecificOutput": especifico}
    elif decision.accion == "informar":
        cuerpo = {"systemMessage": decision.motivo}
        if evento == "SessionStart":
            cuerpo["hookSpecificOutput"] = {
                "hookEventName": evento,
                "additionalContext": decision.motivo,
            }
    else:
        return ""
    return json.dumps(cuerpo, ensure_ascii=False)


def como_exit2(decision: Decision) -> tuple[str, int]:
    """Bloqueo binario para un runtime que no lee JSON: motivo a stderr y código 2.

    Es el mínimo común denominador. No puede reescribir una salida ni matizar
    nada: o pasa, o corta. Por eso `reescribir` aquí no bloquea — tapar un
    secreto exige poder sustituir el texto, y sin JSON eso no existe.
    """

    if decision.bloquea:
        return decision.motivo, 2
    return (decision.motivo if decision.accion == "informar" else ""), 0


# --- Estado de sesión ------------------------------------------------------


def clave_sesion(session_id: str | None) -> str:
    """Identificador corto y opaco: el id real nunca acaba en un nombre de fichero."""

    return hashlib.blake2s((session_id or "sin-id").encode("utf-8"), digest_size=12).hexdigest()


def directorio_sesion(base: Path, session_id: str | None) -> Path:
    return Path(base) / ".cosmos" / DIRECTORIO_SESION / clave_sesion(session_id)


def ruta_marca(base: Path, session_id: str | None, ruta: Path) -> Path:
    huella = hashlib.blake2s(str(ruta).encode("utf-8"), digest_size=8).hexdigest()
    return directorio_sesion(base, session_id) / f"lectura-{huella}.json"


def ruta_avisos(base: Path, session_id: str | None) -> Path:
    return directorio_sesion(base, session_id) / "cierre.json"


def ruta_cierres(base: Path) -> Path:
    return Path(base) / ".cosmos" / NOMBRE_LOG_CIERRES


def _escribe_atomico(ruta: Path, datos: dict) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(f".{os.getpid()}.tmp")
    temporal.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporal, ruta)


def _lee_json(ruta: Path) -> dict:
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {}
    return datos if isinstance(datos, dict) else {}


def sha256_de(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def marcar_lectura(base: Path, session_id: str | None, ruta: Path) -> Path:
    """Convierte «afirmo que lo he leído» en un hecho que otro proceso comprueba.

    La marca ata tres cosas: la sesión, la ruta y el SHA-256 del contenido exacto.
    Editar el fichero invalida todas las lecturas anteriores, que es lo correcto:
    lo que se leyó ya no es lo que hay.
    """

    marca = ruta_marca(base, session_id, ruta)
    _escribe_atomico(
        marca,
        {
            "esquema": 1,
            "session_id": session_id or "",
            "ruta": str(ruta),
            "sha256": sha256_de(ruta),
            "leida": datetime.now(timezone.utc).isoformat(),
        },
    )
    return marca


def lectura_valida(base: Path, session_id: str | None, ruta: Path) -> bool:
    marca = ruta_marca(base, session_id, ruta)
    if not marca.is_file() or not ruta.is_file():
        return False
    datos = _lee_json(marca)
    try:
        return (
            datos.get("session_id") == (session_id or "")
            and datos.get("ruta") == str(ruta)
            and datos.get("sha256") == sha256_de(ruta)
        )
    except OSError:
        return False


def borrar_marcas(base: Path, session_id: str | None) -> int:
    """`PreCompact`: se borran TODAS, sin mirar nada. Es la pareja de la marca.

    Tras compactar, el contenido que se leyó puede haber salido del contexto: la
    marca seguiría siendo cierta como hecho histórico y falsa como afirmación
    sobre lo que el modelo tiene delante. Una prueba de lectura que sobrevive a
    la compactación certifica lo que ya no está.
    """

    borradas = 0
    for marca in directorio_sesion(base, session_id).glob("lectura-*.json"):
        try:
            marca.unlink()
            borradas += 1
        except OSError:
            continue
    return borradas


# --- Lectura de comandos ---------------------------------------------------


def ordenes(comando: str) -> list[str]:
    """Parte un bloque en órdenes sueltas sin romper dentro de comillas.

    Un bloque de shell trae varias órdenes y `[^;&|]*` cruza los saltos de línea:
    evaluando el texto entero, el objetivo inocente de una línea se empareja con
    el verbo peligroso de otra y el guard bloquea con un motivo falso — o al
    revés, y no bloquea nada. Cada orden se juzga por separado.

    Se respeta el entrecomillado en vez de borrarlo: borrar las comillas antes de
    partir hace que un `;` dentro de un mensaje parta la orden en dos.
    """

    piezas: list[str] = []
    actual: list[str] = []
    comilla = ""
    for caracter in comando:
        if comilla:
            actual.append(caracter)
            if caracter == comilla:
                comilla = ""
            continue
        if caracter in "'\"":
            comilla = caracter
            actual.append(caracter)
            continue
        if caracter in ";&|\n":
            piezas.append("".join(actual))
            actual = []
            continue
        actual.append(caracter)
    piezas.append("".join(actual))
    return [pieza.strip() for pieza in piezas if pieza.strip()]


def _piezas(orden: str) -> list[str]:
    try:
        return shlex.split(orden, posix=True)
    except ValueError:
        return orden.split()


def programa(orden: str) -> str:
    """Nombre del ejecutable, saltando asignaciones de entorno y `sudo`."""

    for pieza in _piezas(orden):
        if _ASIGNACION.match(pieza) or pieza in {"sudo", "command", "exec", "env", "nice"}:
            continue
        return Path(pieza).name
    return ""


def es_productor_autorizado(orden: str) -> bool:
    """`cosmos generar` SÍ escribe el índice; una redirección a mano, no.

    Sin esta excepción el guard bloquearía al único proceso que tiene derecho a
    producir esos ficheros, y lo primero que haría cualquiera es desinstalarlo.
    """

    piezas = _piezas(orden)
    nombre = programa(orden)
    if not _PRODUCTOR.match(nombre):
        return False
    if nombre == "cosmos":
        return True
    return "cosmos" in piezas or "puente.gate" in piezas or "puente.sesion" in piezas


def objetivos_de_escritura(orden: str) -> list[str]:
    """Rutas que ESTA orden escribe. Alcance declarado, no una regex que crece.

    Se reconocen: redirecciones (`>`, `>>`, `2>`), `tee`, `truncate`, `sed -i`,
    y el destino de `cp`/`mv`/`install`/`ln`/`rsync`. **No** se persigue lo que
    escribe un intérprete que la orden arranca (`python -c "open(...)"`): eso es
    indecidible sin ejecutar el programa, y perseguirlo con más regex es
    exactamente el montón de parches que este proyecto documentó como antipatrón.
    El canal principal es la herramienta de escritura, que llega estructurada; el
    gate de pre-commit es la red de abajo.
    """

    piezas = _piezas(orden)
    objetivos: list[str] = []
    argumentos: list[str] = []
    saltar_siguiente = False
    for indice, pieza in enumerate(piezas):
        if saltar_siguiente:
            saltar_siguiente = False
            continue
        if indice == 0 or _ASIGNACION.match(pieza):
            continue
        if pieza.startswith("<"):
            # Entrada, no salida. Sin esto `tee fichero < origen` declaraba el
            # origen como escrito, y `<` mismo como si fuera una ruta.
            if pieza == "<":
                saltar_siguiente = True
            continue
        redireccion = _REDIRECCION.match(pieza)
        if redireccion is not None and (">" in pieza):
            destino = redireccion.group("destino")
            if destino:
                objetivos.append(destino)
            elif indice + 1 < len(piezas):
                objetivos.append(piezas[indice + 1])
                saltar_siguiente = True
            continue
        if pieza.startswith("of="):
            objetivos.append(pieza[3:])
            continue
        if pieza.startswith("-"):
            continue
        argumentos.append(pieza)

    nombre = programa(orden)
    if nombre in _ESCRIBE_EN_TODOS:
        objetivos.extend(argumentos)
    elif nombre in _ESCRIBE_EN_EL_ULTIMO and len(argumentos) >= 2:
        objetivos.append(argumentos[-1])
    elif nombre == "sed" and any(p.startswith("-i") for p in piezas) and argumentos:
        objetivos.append(argumentos[-1])
    return [objetivo for objetivo in objetivos if objetivo]


# --- Configuración ---------------------------------------------------------


def _seccion_sesion(ruta: Path | None) -> dict:
    if ruta is None or not Path(ruta).is_file():
        return {}
    try:
        datos = tomllib.loads(Path(ruta).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return {}
    seccion = datos.get("sesion", {})
    return seccion if isinstance(seccion, dict) else {}


def lecturas_exigidas(config) -> list[Path]:
    """Ficheros que hay que haber leído enteros antes de escribir. Vacío por defecto.

    El mecanismo se trae; la política, no. Qué documento es imprescindible en un
    repositorio concreto lo decide ese repositorio, en su `[sesion]`.
    """

    base = config.ruta.parent if config.ruta is not None else config.arbol
    valores = _seccion_sesion(config.ruta).get("lecturas_exigidas", [])
    if not isinstance(valores, list):
        return []
    rutas = []
    for valor in valores:
        if isinstance(valor, str) and valor.strip():
            rutas.append((base / valor).resolve())
    return rutas


def rutas_de_veredicto(config) -> tuple[Path, ...]:
    """Artefactos cuyo valor entero es «los produjo COSMOS», no «alguien los escribió».

    El índice, la vista plana, el manifiesto y —sobre todo— el registro de la
    válvula. Un salto escrito a mano con la fecha que a uno le convenga no es una
    excepción registrada: es la firma de uno mismo. Un guardarraíl que no protege
    su propia válvula no es un guardarraíl.
    """

    base = config.ruta.parent if config.ruta is not None else config.arbol
    return (
        Path(config.indice),
        Path(config.destino_compilacion),
        Path(config.manifiesto_compilacion),
        ruta_saltos(base),
    )


def _dentro(objetivo: Path, contenedor: Path) -> bool:
    try:
        objetivo = objetivo.resolve()
        contenedor = contenedor.resolve()
    except OSError:
        return False
    return objetivo == contenedor or contenedor in objetivo.parents


# --- Estado del árbol ------------------------------------------------------


@dataclass(frozen=True)
class Revision:
    verde: bool
    titulo: str
    detalle: str


def revisar_arbol(config, saltados: frozenset[str]) -> Revision:
    """Valida y mide en el proceso, sin subprocesos ni red. ~1 s sobre el árbol real.

    Respeta la válvula igual que el resto de comandos: un salto vivo omite su
    código aquí también, o el guard de sesión contradiría a `cosmos validar`.
    """

    arbol = cargar_arbol(
        config.arbol,
        excluir=config.indice,
        excluir_directorios=(config.destino_compilacion,),
        tambien=(config.registro,) if config.registro else (),
    )
    resultado = validar_arbol(arbol, configuracion=config, omitir_codigos=saltados)
    nichos = normalizar_nichos(arbol, list(config.nichos) if config.nichos else None)
    medicion = medir_casos(
        arbol, metodo=config.metodo, presupuesto=config.entrada, nichos=nichos
    )
    entrada = medicion.evaluada.entrada
    # Mismo criterio que el código de salida de `cosmos medir`: si aquí fuese otro,
    # el guard y el comando dirían cosas distintas del mismo árbol.
    holgado = entrada <= config.entrada
    verde = resultado.valido and holgado
    presupuesto = (
        f"entrada {entrada} / {config.entrada} tokens"
        if holgado
        else f"entrada {entrada} / {config.entrada} tokens, EXCEDIDO en {entrada - config.entrada}"
    )
    titulo = f"COSMOS  sesion  {'verde' if verde else 'rojo'}  {presupuesto}"
    lineas = []
    if not resultado.valido:
        errores = list(resultado.errores)[:5]
        lineas.append(f"{len(resultado.errores)} error(es) de validación:")
        lineas.extend(f"  {error.codigo}  {error.ruta}: {error.mensaje}" for error in errores)
        if len(resultado.errores) > len(errores):
            lineas.append(f"  … y {len(resultado.errores) - len(errores)} más (cosmos validar)")
    if not holgado:
        lineas.append("El presupuesto de entrada se ha pasado: mira 'cosmos medir --detalle'.")
    return Revision(verde, titulo, "\n".join(lineas))


# --- Manejadores por evento ------------------------------------------------


def _saltados(base: Path) -> tuple[frozenset[str], list[Salto], list[Salto]]:
    activos, caducados = estado_saltos(ruta_saltos(base))
    return frozenset(salto.codigo for salto in activos), activos, caducados


def _con_valvula(texto: str, activos: list[Salto], caducados: list[Salto]) -> str:
    """Ninguna salida dice «verde» a secas habiendo un salto vivo, tampoco aquí."""

    return anotar_salida(texto, activos, caducados, ahora=ahora_utc())


def al_arrancar(entrada: dict, config, base: Path) -> Decision:
    """G01 — la primera línea de la sesión dice el número real, medido."""

    saltados, activos, caducados = _saltados(base)
    if CODIGO_PRESUPUESTO in saltados:
        return Decision("informar", _con_valvula("COSMOS  sesion  verde  medición saltada", activos, caducados))
    revision = revisar_arbol(config, saltados)
    cuerpo = revision.titulo if revision.verde else f"{revision.titulo}\n{revision.detalle}"
    return Decision("informar", _con_valvula(cuerpo, activos, caducados))


def al_cerrar(entrada: dict, config, base: Path) -> Decision:
    """G02 — no se cierra con el árbol en rojo. Contador propio y tope duro.

    El freno es el contador, no la bandera `stop_hook_active` que trae el evento:
    esa la pone cualquier hook que haya bloqueado en el mismo evento, así que
    fiarlo todo a ella deja mudo a un guard que no ha hablado nunca. El tope de
    `TOPE_AVISOS` es lo que garantiza que esto no es un bucle sin salida.
    """

    saltados, activos, caducados = _saltados(base)
    if CODIGO_CIERRE in saltados:
        return Decision("informar", _con_valvula("COSMOS  sesion  verde  cierre sin comprobar", activos, caducados))
    revision = revisar_arbol(config, saltados)
    ruta = ruta_avisos(base, entrada.get("session_id"))
    estado = _lee_json(ruta)
    if revision.verde:
        if estado:
            _escribe_atomico(ruta, {"avisos": 0})
        return Decision("informar", _con_valvula(revision.titulo, activos, caducados))

    avisos = int(estado.get("avisos", 0) or 0) + 1
    _escribe_atomico(ruta, {"avisos": avisos})
    if avisos <= TOPE_AVISOS:
        motivo = (
            "No cierres todavía: el árbol de COSMOS está en rojo.\n"
            f"{revision.titulo}\n{revision.detalle}\n"
            "Arréglalo con 'cosmos validar' / 'cosmos generar', o abre la válvula acotada:\n"
            f"  cosmos saltar {CODIGO_CIERRE} --motivo \"...\" --caduca 7d\n"
            f"(aviso {avisos} de {TOPE_AVISOS}; después se deja cerrar y queda anotado)"
        )
        return Decision("bloquear", _con_valvula(motivo, activos, caducados))

    anotar_cierre(base, entrada.get("session_id"), revision.titulo, avisos)
    return Decision(
        "informar",
        _con_valvula(
            f"{revision.titulo}\nSe cierra igualmente tras {TOPE_AVISOS} avisos; "
            f"queda anotado en {ruta_cierres(base)}.",
            activos,
            caducados,
        ),
    )


def anotar_cierre(base: Path, session_id: str | None, titulo: str, avisos: int) -> None:
    """Registro que solo crece, como el de la válvula: un cierre en rojo deja rastro."""

    log = ruta_cierres(base)
    log.parent.mkdir(parents=True, exist_ok=True)
    linea = {
        "momento": datetime.now(timezone.utc).isoformat(),
        "sesion": clave_sesion(session_id),
        "estado": titulo,
        "avisos": avisos,
    }
    with log.open("a", encoding="utf-8") as fichero:
        fichero.write(json.dumps(linea, ensure_ascii=False, sort_keys=True) + "\n")


def _ruta_de_herramienta(datos: dict) -> Path | None:
    for clave in ("file_path", "path", "notebook_path"):
        valor = datos.get(clave)
        if isinstance(valor, str) and valor.strip():
            return Path(valor)
    return None


def _lectura_completa(datos: dict, ruta: Path) -> bool:
    """Una lectura parcial no es una lectura: el trozo que falta es justo el que importa."""

    desplazamiento = datos.get("offset")
    if desplazamiento not in (None, "", 0, 1, "0", "1"):
        return False
    limite = datos.get("limit")
    if limite in (None, ""):
        return True
    try:
        with ruta.open(encoding="utf-8", errors="replace") as fichero:
            lineas = sum(1 for _ in fichero)
        return int(limite) >= lineas
    except (OSError, TypeError, ValueError):
        return False


def antes_de_la_herramienta(entrada: dict, config, base: Path) -> Decision:
    """G03 y G04, los dos por `deny`: la herramienta no llega a ejecutarse."""

    saltados, activos, caducados = _saltados(base)
    herramienta = str(entrada.get("tool_name") or "")
    datos = entrada.get("tool_input") or {}
    if not isinstance(datos, dict):
        return PASAR

    # Una ruta relativa se resuelve contra el directorio del evento, no contra el
    # del proceso del hook: no tienen por qué ser el mismo, y resolver contra el
    # equivocado deja pasar exactamente lo que se quería parar.
    directorio = Path(str(entrada.get("cwd") or base))

    def _resolver(objetivo: str | Path) -> Path:
        ruta = Path(objetivo).expanduser()
        return ruta if ruta.is_absolute() else directorio / ruta

    objetivos: list[Path] = []
    if herramienta in HERRAMIENTAS_ESCRITURA:
        ruta = _ruta_de_herramienta(datos)
        if ruta is not None:
            objetivos.append(_resolver(ruta))
    elif herramienta == "Bash":
        comando = str(datos.get("command") or "")
        for orden in ordenes(comando):
            if es_productor_autorizado(orden):
                continue
            objetivos.extend(_resolver(objetivo) for objetivo in objetivos_de_escritura(orden))
    if not objetivos:
        return PASAR

    if CODIGO_VEREDICTO not in saltados:
        veredicto = rutas_de_veredicto(config)
        for objetivo in objetivos:
            for protegida in veredicto:
                if _dentro(objetivo, protegida):
                    return Decision(
                        "denegar",
                        _con_valvula(
                            "COSMOS  sesion  rojo  escritura a mano sobre una ruta de veredicto\n"
                            f"  {objetivo}  (protegida: {protegida})\n"
                            "Ese fichero vale porque lo produce COSMOS. Escribirlo a mano hace verde "
                            "un árbol que no lo está.\n"
                            "Regenéralo con 'cosmos generar' / 'cosmos compilar', o abre la válvula:\n"
                            f"  cosmos saltar {CODIGO_VEREDICTO} --motivo \"...\" --caduca 7d",
                            activos,
                            caducados,
                        ),
                    )

    if CODIGO_LECTURA in saltados:
        return PASAR
    pendientes = [
        ruta
        for ruta in lecturas_exigidas(config)
        if not lectura_valida(base, entrada.get("session_id"), ruta)
    ]
    if not pendientes:
        return PASAR
    listado = "\n".join(f"  {ruta}" for ruta in pendientes)
    return Decision(
        "denegar",
        _con_valvula(
            "COSMOS  sesion  rojo  falta leer lo que este repositorio exige antes de escribir\n"
            f"{listado}\n"
            "Léelos enteros. La marca está ligada a ESTA sesión y al SHA-256 del contenido: "
            "no se hereda de otra ventana y se borra al compactar.\n"
            f"Si no procede: cosmos saltar {CODIGO_LECTURA} --motivo \"...\" --caduca 7d",
            activos,
            caducados,
        ),
    )


def _respuesta(entrada: dict) -> tuple[str, int]:
    respuesta = entrada.get("tool_response")
    if isinstance(respuesta, str):
        return respuesta, 0
    if not isinstance(respuesta, dict):
        return "", 0
    salida = respuesta.get("output")
    if not isinstance(salida, str):
        salida = respuesta.get("stdout")
    if not isinstance(salida, str):
        salida = ""
    bruto = respuesta.get("exit_code", respuesta.get("exitCode", 0))
    try:
        codigo = int(bruto or 0)
    except (TypeError, ValueError):
        codigo = 0
    return salida, codigo


def apartar_salida(base: Path, texto: str) -> Path:
    huella = hashlib.sha256(texto.encode("utf-8", "replace")).hexdigest()[:8]
    momento = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    destino = Path(base) / ".cosmos" / "salidas" / f"{momento}-{huella}.log"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    return destino


def despues_de_la_herramienta(entrada: dict, config, base: Path) -> Decision:
    """G05 — reescribe lo que el modelo VE de una ejecución que ya ocurrió.

    Es el único mecanismo que sirve contra una fuga hacia el contexto: cuando el
    comando ya corrió, impedirlo no está sobre la mesa; lo que sigue estándolo es
    que el valor no llegue a leerse. Y de paso, lo enorme se aparta a fichero:
    una salida de 200 KB entra íntegra en el contexto de todos los turnos
    siguientes, que es exactamente lo que COSMOS mide y limita.
    """

    saltados, activos, caducados = _saltados(base)
    if CODIGO_REDACCION in saltados:
        return PASAR
    herramienta = str(entrada.get("tool_name") or "")
    if herramienta == "Read":
        return _marcar_si_procede(entrada, config, base)
    if herramienta != "Bash":
        return PASAR
    texto, codigo = _respuesta(entrada)
    if not texto:
        return PASAR

    redactado, tapados = redactar_texto(texto)
    bytes_ = len(redactado.encode("utf-8", "replace"))
    lineas = len(redactado.splitlines())
    if bytes_ > MAX_BYTES or lineas > MAX_LINEAS:
        destino = apartar_salida(base, redactado)
        cola = "\n".join(redactado.splitlines()[-12:])
        aviso = (
            f"Salida grande apartada: {lineas} líneas / {bytes_} bytes -> {destino}\n"
            "Busca dentro con grep o lee rangos concretos; no la cargues entera.\n"
            f"Últimas líneas:\n{cola}"
        )
        contexto = f"[COSMOS G05] {tapados} valor(es) tapado(s) antes de entrar al contexto." if tapados else ""
        return Decision("reescribir", salida=aviso, codigo_salida=codigo, contexto=contexto)
    if tapados:
        return Decision(
            "reescribir",
            salida=redactado,
            codigo_salida=codigo,
            contexto=(
                f"[COSMOS G05] {tapados} valor(es) con forma de secreto tapado(s) antes de entrar "
                "al contexto. Los valores reales no llegaron aquí; si crees que se filtraron antes, "
                "rota esas credenciales."
            ),
        )
    return PASAR


def _marcar_si_procede(entrada: dict, config, base: Path) -> Decision:
    """Una lectura completa de un fichero exigido deja su marca comprobable."""

    datos = entrada.get("tool_input") or {}
    if not isinstance(datos, dict):
        return PASAR
    ruta = _ruta_de_herramienta(datos)
    if ruta is None:
        return PASAR
    try:
        resuelta = ruta.resolve()
    except OSError:
        return PASAR
    if resuelta not in lecturas_exigidas(config) or not resuelta.is_file():
        return PASAR
    if not _lectura_completa(datos, resuelta):
        return PASAR
    marcar_lectura(base, entrada.get("session_id"), resuelta)
    return PASAR


def al_compactar(entrada: dict, config, base: Path) -> Decision:
    borradas = borrar_marcas(base, entrada.get("session_id"))
    if not borradas:
        return PASAR
    return Decision(
        "informar",
        f"COSMOS  sesion  {borradas} marca(s) de lectura borrada(s) al compactar: "
        "lo que se leyó puede haber salido del contexto y hay que volver a leerlo.",
    )


MANEJADORES = {
    "SessionStart": al_arrancar,
    "Stop": al_cerrar,
    "PreToolUse": antes_de_la_herramienta,
    "PostToolUse": despues_de_la_herramienta,
    "PreCompact": al_compactar,
}


# --- Entrada ---------------------------------------------------------------


def base_de(entrada: dict, config) -> Path:
    del entrada
    return config.ruta.parent if config.ruta is not None else config.arbol


def decidir(entrada: dict, *, config_path: Path | None = None) -> tuple[Decision, str]:
    """Punto único: evento dentro, decisión fuera. Sin efectos sobre el runtime."""

    evento = str(entrada.get("hook_event_name") or "")
    manejador = MANEJADORES.get(evento)
    if manejador is None:
        return PASAR, evento
    ruta = Path(config_path) if config_path else Path(entrada.get("cwd") or Path.cwd()) / "cosmos.toml"
    config = cargar_configuracion(ruta)
    if not config.arbol.is_dir():
        raise ErrorSesion(f"no hay árbol COSMOS en {config.arbol}")
    return manejador(entrada, config, base_de(entrada, config)), evento


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardarraíles de sesión de COSMOS.")
    parser.add_argument("--formato", choices=("json", "exit2"), default="json")
    parser.add_argument("--config", type=Path, default=None, help="ruta de cosmos.toml")
    args = parser.parse_args(argv)
    try:
        entrada = json.load(sys.stdin)
    except (ValueError, TypeError):
        return 0
    if not isinstance(entrada, dict):
        return 0
    try:
        decision, evento = decidir(entrada, config_path=args.config)
    except (ErrorSesion, ErrorConfiguracion, ErrorNicho, OSError, ValueError, RecursionError):
        # Un guard de sesión que revienta rompe la herramienta que vigilaba. Ante
        # la duda calla: el gate de pre-commit y el CI siguen ahí abajo.
        return 0
    if args.formato == "exit2":
        texto, codigo = como_exit2(decision)
        if texto:
            sys.stderr.write(texto + "\n")
        return codigo
    cuerpo = como_json(decision, evento)
    if cuerpo:
        sys.stdout.write(cuerpo + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
