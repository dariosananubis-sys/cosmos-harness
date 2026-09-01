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

CODIGOS = tuple(f"E{numero:02d}" for numero in range(20))
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
        raise ErrorSalto(f"código desconocido: {codigo!r}; se esperaba uno de E00..E19")
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
