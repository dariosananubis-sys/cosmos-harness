"""Lo que hace que COSMOS se ejecute solo: enganches y válvula de escape.

Dos mecanismos, y el segundo existe por el primero. `enganchar` instala el gate
de pre-commit para que nadie tenga que acordarse de teclear `cosmos validar`;
`saltar` es la válvula, porque un guardarraíl duro sin salida acotada acaba
arrancado de raíz un viernes por la tarde y ya no vuelve (spec/GUARDARRAILES.md).

La válvula es deliberadamente incómoda: código concreto, motivo escrito,
caducidad obligatoria de treinta días como mucho, registro que solo crece y una
salida que nunca dice «verde» a secas mientras haya un salto vivo.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

def _invariantes_vigentes() -> tuple[str, ...]:
    """Los códigos que el validador comprueba HOY, preguntándoselo a él.

    Era `range(20)`, escrito a mano, y por eso E20 quedó **viva y sin válvula**: se añadió
    la invariante y nadie tocó esta línea. `spec/GUARDARRAILES.md` dice de la válvula que
    es «obligatoria, no opcional», porque «todo guardarraíl duro sin válvula de escape
    acaba desactivado a la fuerza». Una invariante sin salida acotada es exactamente eso.

    El import va aquí dentro a propósito: `validar` importa de este módulo, y al revés
    sería un ciclo.
    """

    from .validar import codigos_comprobados

    return codigos_comprobados()


CODIGOS_INVARIANTES = _invariantes_vigentes()
# Guardarraíles de sesión (`puente/sesion.py`). Tienen código propio porque la
# válvula es obligatoria en TODO guardarraíl duro, no solo en el validador: uno
# sin salida acotada acaba arrancado de raíz un viernes, y ya no vuelve.
CODIGOS_SESION = ("G01", "G02", "G03", "G04", "G05")
CODIGOS = CODIGOS_INVARIANTES + CODIGOS_SESION
DIAS_MAXIMOS = 30
MARCA_HOOK = "cosmos-enganchar"
VERSION_HOOK = 1
NOMBRE_LOG = "saltos.log"

_DURACION = re.compile(r"^(?P<cantidad>\d+)\s*(?P<unidad>[dD])$")
# Vale para «COSMOS  verde  0 errores» y para «COSMOS  compilar  verde»: ninguna
# de las dos puede decir verde a secas habiendo un salto vivo.
_CABECERA = re.compile(r"^(?P<prefijo>COSMOS\s+(?:\w+\s+)?)(?P<estado>verde|rojo)(?P<resto>\s.*)?$")
_HALLAZGO = re.compile(r"^(?P<lugar>[^:]+?)(?::(?P<linea>\d+))?: (?P<descripcion>.+)$")


class ErrorSalto(ValueError):
    """La válvula se usó mal: sin motivo, sin caducidad o sobre un código inexistente."""


class ErrorEnganche(ValueError):
    """El enganche no se puede instalar o quitar sin pisar trabajo ajeno."""


@dataclass(frozen=True)
class Salto:
    codigo: str
    motivo: str
    creado: datetime
    caduca: datetime

    def activo(self, ahora: datetime) -> bool:
        return ahora < self.caduca

    def dias_restantes(self, ahora: datetime) -> int:
        """Días enteros que quedan, redondeando hacia arriba: 0 solo si ya venció."""

        restante = self.caduca - ahora
        if restante <= timedelta(0):
            return 0
        return -(-int(restante.total_seconds()) // 86400)

    def como_dict(self) -> dict[str, str]:
        return {
            "codigo": self.codigo,
            "motivo": self.motivo,
            "creado": self.creado.isoformat(),
            "caduca": self.caduca.isoformat(),
        }


def ahora_utc() -> datetime:
    return datetime.now(timezone.utc)


def analizar_duracion(texto: str) -> timedelta:
    """`7d` -> siete días. Sin unidad no hay caducidad, y sin caducidad no hay salto."""

    coincidencia = _DURACION.match(texto.strip())
    if coincidencia is None:
        raise ErrorSalto(f"--caduca debe ser un número de días como '7d'; llegó {texto!r}")
    dias = int(coincidencia.group("cantidad"))
    if not 1 <= dias <= DIAS_MAXIMOS:
        raise ErrorSalto(f"--caduca debe estar entre 1d y {DIAS_MAXIMOS}d; llegó {texto!r}")
    return timedelta(days=dias)


def normalizar_codigo(codigo: str) -> str:
    limpio = codigo.strip().upper()
    if limpio in {"TODO", "TODOS", "*", "ALL"}:
        raise ErrorSalto("un salto acota un código concreto; 'todo' no es un salto, es apagar COSMOS")
    if limpio not in CODIGOS:
        raise ErrorSalto(
            f"código desconocido: {codigo!r}; se esperaba una invariante (E00..E19)"
            f" o un guardarraíl de sesión ({'/'.join(CODIGOS_SESION)})"
        )
    return limpio


def ruta_saltos(base: Path) -> Path:
    """El registro vive junto al resto de artefactos generados, nunca versionado."""

    return Path(base) / ".cosmos" / NOMBRE_LOG


def registrar_salto(
    log: Path, codigo: str, motivo: str, duracion: timedelta, *, ahora: datetime | None = None
) -> Salto:
    """Añade una línea al final. El fichero jamás se reescribe ni se reordena."""

    momento = ahora or ahora_utc()
    texto = motivo.strip()
    if not texto:
        raise ErrorSalto("--motivo es obligatorio y no puede estar vacío")
    salto = Salto(normalizar_codigo(codigo), texto, momento, momento + duracion)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fichero:
        fichero.write(json.dumps(salto.como_dict(), ensure_ascii=False, sort_keys=True) + "\n")
    return salto


def leer_saltos(log: Path) -> list[Salto]:
    """Lee el registro entero. Una línea corrupta se ignora: nunca deja el árbol sin validar."""

    if not log.is_file():
        return []
    saltos: list[Salto] = []
    for linea in log.read_text(encoding="utf-8", errors="replace").splitlines():
        if not linea.strip():
            continue
        try:
            datos = json.loads(linea)
            salto = Salto(
                str(datos["codigo"]).upper(),
                str(datos["motivo"]),
                datetime.fromisoformat(str(datos["creado"])),
                datetime.fromisoformat(str(datos["caduca"])),
            )
        except (ValueError, KeyError, TypeError):
            continue
        if salto.codigo in CODIGOS:
            saltos.append(salto)
    return saltos


def estado_saltos(log: Path, *, ahora: datetime | None = None) -> tuple[list[Salto], list[Salto]]:
    """Devuelve (activos, caducados) mirando solo la última entrada de cada código.

    Renovar es escribir otra línea: la nueva manda y la vieja queda en el registro.
    """

    momento = ahora or ahora_utc()
    ultimos: dict[str, Salto] = {}
    for salto in leer_saltos(log):
        previo = ultimos.get(salto.codigo)
        if previo is None or salto.creado >= previo.creado:
            ultimos[salto.codigo] = salto
    activos = sorted((s for s in ultimos.values() if s.activo(momento)), key=lambda s: s.codigo)
    caducados = sorted((s for s in ultimos.values() if not s.activo(momento)), key=lambda s: s.codigo)
    return activos, caducados


def sufijo_saltos(activos: list[Salto], ahora: datetime) -> str:
    if not activos:
        return ""
    plural = "salto activo" if len(activos) == 1 else "saltos activos"
    detalle = "; ".join(f"{s.codigo}, caduca en {s.dias_restantes(ahora)} d" for s in activos)
    return f" ({len(activos)} {plural}: {detalle})"


def anotar_salida(
    texto: str, activos: list[Salto], caducados: list[Salto] | None = None, *, ahora: datetime | None = None
) -> str:
    """Marca la cabecera y recuerda los saltos vencidos con el motivo que se escribió.

    La palabra «verde» nunca queda sola habiendo saltos vivos: un verde que oculta
    un salto es una mentira, y basta una para que nadie se crea ninguna otra.
    """

    caducados = caducados or []
    if not activos and not caducados:
        return texto
    momento = ahora or ahora_utc()
    lineas = texto.split("\n")
    cabecera = _CABECERA.match(lineas[0]) if lineas else None
    if cabecera is not None:
        lineas[0] = (
            f"{cabecera.group('prefijo')}{cabecera.group('estado')}"
            f"{sufijo_saltos(activos, momento)}{cabecera.group('resto') or ''}"
        )
    avisos: list[str] = []
    for salto in caducados:
        avisos.extend(
            [
                "",
                f"SALTO CADUCADO  {salto.codigo}  venció el {salto.caduca.date().isoformat()}",
                f"     vuelve a exigirse; motivo que se escribió: «{salto.motivo}»",
                f"     Renueva con 'cosmos saltar {salto.codigo} --motivo \"...\" --caduca 7d' o arregla el árbol.",
            ]
        )
    if avisos:
        lineas[1:1] = avisos
    return "\n".join(lineas)


def clave_hallazgo(hallazgo: str) -> str:
    """Un hallazgo sin su número de línea: mover código no convierte lo viejo en nuevo."""

    coincidencia = _HALLAZGO.match(hallazgo.strip())
    if coincidencia is None:
        return hallazgo.strip()
    return f"{coincidencia.group('lugar')}: {coincidencia.group('descripcion')}"


# --- Enganches -------------------------------------------------------------


def instalacion() -> Path:
    """Directorio que contiene los paquetes `cosmos` y `puente`."""

    return Path(__file__).resolve().parent.parent


def raiz_git(base: Path) -> Path:
    resultado = subprocess.run(
        ["git", "-C", str(base), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado.returncode or not resultado.stdout.strip():
        raise ErrorEnganche(f"{base} no está dentro de un repositorio Git")
    return Path(resultado.stdout.strip()).resolve()


def ruta_hook(base: Path, nombre: str = "pre-commit") -> Path:
    """Respeta `core.hooksPath`: preguntar a Git es más barato que adivinar."""

    raiz = raiz_git(base)
    resultado = subprocess.run(
        ["git", "-C", str(raiz), "rev-parse", "--git-path", f"hooks/{nombre}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if resultado.returncode or not resultado.stdout.strip():
        return raiz / ".git" / "hooks" / nombre
    ruta = Path(resultado.stdout.strip())
    return ruta if ruta.is_absolute() else (raiz / ruta)


def contenido_hook(*, interprete: str | None = None, con_pruebas: bool = True) -> str:
    ejecutable = interprete or sys.executable
    argumentos = "" if con_pruebas else " --sin-pruebas"
    return "\n".join(
        [
            "#!/bin/sh",
            f"# {MARCA_HOOK} v{VERSION_HOOK} — generado por 'cosmos enganchar'.",
            "# No editar a mano: 'cosmos desenganchar' lo elimina y deja el repo como estaba.",
            f"COSMOS_INSTALACION='{instalacion()}'",
            'if [ -n "${PYTHONPATH:-}" ]; then',
            '  PYTHONPATH="$COSMOS_INSTALACION:$PYTHONPATH"',
            "else",
            '  PYTHONPATH="$COSMOS_INSTALACION"',
            "fi",
            "export PYTHONPATH",
            f"exec '{ejecutable}' -m puente.gate --silencioso{argumentos}",
            "",
        ]
    )


def es_nuestro(ruta: Path) -> bool:
    try:
        cabecera = ruta.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return MARCA_HOOK in cabecera


def enganchar(base: Path, *, interprete: str | None = None, con_pruebas: bool = True) -> tuple[Path, str]:
    """Instala el hook. Si ya hay uno ajeno no toca nada: lo dice y se va.

    Un enganche que pisa el hook de otro es exactamente el sistema que la gente
    arranca de raíz a la primera molestia, y con razón.
    """

    ruta = ruta_hook(base)
    if ruta.exists() and not es_nuestro(ruta):
        raise ErrorEnganche(
            f"ya hay un pre-commit ajeno en {ruta}; no se ha tocado nada.\n"
            "Encadénalo tú mismo añadiendo esta línea a ese hook:\n"
            f"  {sys.executable} -m puente.gate --silencioso"
        )
    estado = "actualizado" if ruta.exists() else "creado"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido_hook(interprete=interprete, con_pruebas=con_pruebas), encoding="utf-8")
    ruta.chmod(0o755)
    return ruta, estado


def desenganchar(base: Path) -> tuple[Path, str]:
    """Quita el hook propio y deja el repositorio exactamente como estaba."""

    ruta = ruta_hook(base)
    if not ruta.exists():
        return ruta, "ausente"
    if not es_nuestro(ruta):
        raise ErrorEnganche(f"el pre-commit de {ruta} no lo escribió COSMOS; no se ha tocado nada")
    ruta.unlink()
    return ruta, "eliminado"


# --- Enganche de sesión ----------------------------------------------------
#
# El tercer enganche de spec/GUARDARRAILES.md. Los otros dos son de repositorio
# —miran lo que ya está escrito—; este actúa mientras el agente trabaja.
#
# La LÓGICA de los guards no sabe quién la llama (`puente/sesion.py`: un evento
# JSON por la entrada, una decisión por la salida). Lo que sí depende del runtime
# concreto es este fichero de cableado, y por eso vive aquí solo, en una función
# que se puede sustituir entera el día que el runtime cambie de formato.

RUTA_AJUSTES = Path(".claude") / "settings.json"
MARCA_SESION = "puente.sesion"
NOMBRE_RESPALDO = "enganche-sesion.json"
# G05 tapa secretos y aparta salidas enormes DESPUÉS de que ocurran, y el guard
# ya sabe hacerlo con las cinco herramientas que traen texto ajeno al contexto
# (`puente.sesion.HERRAMIENTAS_VIGILADAS`). Aquí solo se enrutan tres de ellas —
# `Grep`, `Glob` y `Task` no llegaban al guard—, así que un secreto encontrado por
# `Grep` entraba en claro por una puerta que ya estaba construida y sin cablear.
# `tests/test_guardarrailes.py` compara esta lista con la del guard: no puede
# volver a quedarse corta en silencio.
HERRAMIENTAS_POSTERIORES = ("Bash", "Read", "Grep", "Glob", "Task")
EVENTOS_SESION = (
    ("SessionStart", None),
    ("PreToolUse", "Bash|Write|Edit|MultiEdit|NotebookEdit"),
    ("PostToolUse", "|".join(HERRAMIENTAS_POSTERIORES)),
    ("PreCompact", None),
    ("Stop", None),
)


def orden_sesion(interprete: str | None = None) -> str:
    ejecutable = interprete or sys.executable
    return (
        f"PYTHONPATH='{instalacion()}'\"${{PYTHONPATH:+:$PYTHONPATH}}\" "
        f"'{ejecutable}' -m {MARCA_SESION}"
    )


def bloque_sesion(orden: str) -> dict[str, list[dict]]:
    entradas: dict[str, list[dict]] = {}
    for evento, filtro in EVENTOS_SESION:
        entrada: dict[str, object] = {"hooks": [{"type": "command", "command": orden}]}
        if filtro:
            entrada["matcher"] = filtro
        entradas[evento] = [entrada]
    return entradas


def _es_entrada_nuestra(entrada: object) -> bool:
    if not isinstance(entrada, dict):
        return False
    hooks = entrada.get("hooks")
    if not isinstance(hooks, list):
        return False
    return any(
        isinstance(hook, dict) and MARCA_SESION in str(hook.get("command", "")) for hook in hooks
    )


def podar_sesion(datos: dict) -> dict:
    """Devuelve los ajustes sin NINGUNA entrada de COSMOS, dejando el resto intacto."""

    copia = json.loads(json.dumps(datos))
    hooks = copia.get("hooks")
    if not isinstance(hooks, dict):
        return copia
    for evento in list(hooks):
        entradas = hooks[evento]
        if not isinstance(entradas, list):
            continue
        restantes = [entrada for entrada in entradas if not _es_entrada_nuestra(entrada)]
        if restantes:
            hooks[evento] = restantes
        else:
            # Una lista vacía no dice nada: se quita a los dos lados de la
            # comparación, y el fichero original se devuelve tal cual estaba.
            del hooks[evento]
    if not hooks:
        del copia["hooks"]
    return copia


def ruta_respaldo(base: Path) -> Path:
    return Path(base) / ".cosmos" / NOMBRE_RESPALDO


def enganchar_sesion(base: Path, *, interprete: str | None = None) -> tuple[Path, str]:
    """Añade el cableado de sesión sin pisar el de nadie.

    Guarda los bytes exactos del fichero anterior para poder devolverlo idéntico:
    reescribir los ajustes de otra persona «con el mismo contenido pero mejor
    indentado» es la clase de cortesía por la que se desinstala un sistema.
    """

    raiz = raiz_git(base)
    ruta = raiz / RUTA_AJUSTES
    existia = ruta.is_file()
    original = ruta.read_text(encoding="utf-8") if existia else None
    if existia:
        try:
            datos = json.loads(original)
        except ValueError as exc:
            raise ErrorEnganche(f"{ruta} no es JSON válido; no se ha tocado nada ({exc})") from exc
        if not isinstance(datos, dict):
            raise ErrorEnganche(f"{ruta} no contiene un objeto JSON; no se ha tocado nada")
    else:
        datos = {}

    datos = podar_sesion(datos)
    hooks = datos.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ErrorEnganche(f"la clave 'hooks' de {ruta} no es un objeto; no se ha tocado nada")
    for evento, entradas in bloque_sesion(orden_sesion(interprete)).items():
        existentes = hooks.get(evento)
        hooks[evento] = (existentes if isinstance(existentes, list) else []) + entradas

    respaldo = ruta_respaldo(raiz)
    respaldo.parent.mkdir(parents=True, exist_ok=True)
    respaldo.write_text(
        json.dumps(
            {
                "esquema": 1,
                "existia": existia,
                "creo_directorio": not ruta.parent.exists(),
                "original": original,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ruta, "actualizado" if existia else "creado"


def desenganchar_sesion(base: Path) -> tuple[Path, str]:
    """Quita el cableado. Si el resto no cambió, devuelve el fichero byte a byte."""

    raiz = raiz_git(base)
    ruta = raiz / RUTA_AJUSTES
    respaldo = ruta_respaldo(raiz)
    if not ruta.is_file():
        respaldo.unlink(missing_ok=True)
        return ruta, "ausente"
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except ValueError:
        return ruta, "ilegible"
    if not isinstance(datos, dict):
        return ruta, "ilegible"
    podado = podar_sesion(datos)

    guardado = {}
    if respaldo.is_file():
        try:
            guardado = json.loads(respaldo.read_text(encoding="utf-8"))
        except ValueError:
            guardado = {}
    original = guardado.get("original")
    if "existia" in guardado:
        # «El resto no ha cambiado» se comprueba comparando los dos ficheros SIN
        # las entradas de COSMOS. Comparar contra el original tal cual daría falso
        # negativo cuando el original ya traía una lista vacía para el mismo
        # evento: podar la nuestra la deja vacía otra vez y no se distingue.
        try:
            previo = podar_sesion(json.loads(original)) if isinstance(original, str) else {}
        except ValueError:
            previo = None
        intacto = previo is not None and podado == previo
        if intacto and guardado["existia"] and isinstance(original, str):
            ruta.write_text(original, encoding="utf-8")
            respaldo.unlink(missing_ok=True)
            return ruta, "restaurado"
        if intacto and not guardado["existia"]:
            ruta.unlink()
            respaldo.unlink(missing_ok=True)
            if guardado.get("creo_directorio") and not any(ruta.parent.iterdir()):
                ruta.parent.rmdir()
            return ruta, "eliminado"

    ruta.write_text(json.dumps(podado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    respaldo.unlink(missing_ok=True)
    return ruta, "podado"
