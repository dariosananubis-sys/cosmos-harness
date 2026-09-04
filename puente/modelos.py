#!/usr/bin/env python3
"""Mantiene el selector de modelos de Claude Code con todas las entradas de la cuenta.

Claude Code arma el menú de `/model` con sus opciones nativas MÁS el array
`additionalModelOptionsCache` de `~/.claude.json`, que el propio CLI rellena desde el
servidor en cada arranque: lo añadido a mano se pierde al reiniciar. Aquí se repone, de
forma idempotente y atómica, sin tocar lo que venga del servidor. Y se instala lo que hace
que vuelva a ocurrir solo: un agente de launchd (al arrancar, cuando el CLI pisa su fichero y
cada cinco minutos) y un hook `SessionStart` en los ajustes de usuario, porque launchd agrupa
eventos y un `/model` abierto a los pocos segundos de arrancar aún no las veía.

Es alta de MÁQUINA (`cosmos configurar --modelos instalar|estado|quitar`), no de repositorio:
todo lo que escribe vive en `~/.cosmos/`, `~/.local/bin/` y `~/Library/LaunchAgents/`.
Ninguna ruta de este fichero nombra una máquina ni una organización; los ficheros a vigilar
salen de `$HOME`, de `$CLAUDE_CONFIG_DIR` y de la tabla `[modelos]` del perfil.

Nada de esto corre al importar el módulo: son funciones, y `instalar()` recibe quién ejecuta
`launchctl` para que las pruebas anoten la orden sin lanzarla.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from cosmos.configurar import (
    DIRECTORIO,
    abreviar_home,
    ajustes_usuario,
    escribir_privado,
    leer_ajustes,
    leer_modelos,
)

ETIQUETA = "com.cosmos.modelos"
MARCA = "generado-por-cosmos-modelos"
MODELO_DURO_POR_DEFECTO = "claude-opus-5"
INTERVALO_SEGUNDOS = 300


@dataclass(frozen=True)
class Modelo:
    valor: str  # el id que se le pasa al CLI
    etiqueta: str  # lo que se ve en el menú
    nota: str  # una línea


# ÚNICA fuente de verdad de la lista. El río `configurar` y el README la citan y un test
# (`tests/test_modelos.py`) compara los ids: una tabla escrita a mano se desincroniza.
# Que la cuenta acepte cada id NO se puede comprobar sin red: `estado` lo publica como
# `no_comprobado` y da la orden que sí lo comprueba (`claude --model <id> -p ok`).
MODELOS: tuple[Modelo, ...] = (
    Modelo("claude-fable-5-1", "Fable 5.1", "Fable 5.1 · el más capaz"),
    Modelo("claude-opus-5", "Opus 5", "Opus 5 · razonamiento duro"),
    Modelo("claude-sonnet-5", "Sonnet 5", "Sonnet 5 · rápido y barato"),
    Modelo("claude-haiku-4-5-20251001", "Haiku 4.5", "Haiku 4.5 · el más rápido"),
    Modelo("claude-fable-5-1[1m]", "Fable 5.1 · 1M", "Fable 5.1 con ventana de un millón de tokens"),
    Modelo("claude-opus-5[1m]", "Opus 5 · 1M", "Opus 5 con ventana de un millón de tokens"),
    Modelo("claude-sonnet-5[1m]", "Sonnet 5 · 1M", "Sonnet 5 con ventana de un millón de tokens"),
)


def entradas_deseadas() -> list[dict[str, str]]:
    return [{"value": m.valor, "label": m.etiqueta, "description": m.nota} for m in MODELOS]


# --- Rutas: todas derivadas de $HOME, nunca escritas a mano ------------------------------


def directorio_bin() -> Path:
    return DIRECTORIO / "bin"


def ruta_reponedor() -> Path:
    return directorio_bin() / "modelos-reponer.py"


def ruta_log() -> Path:
    return DIRECTORIO / "logs" / "modelos.log"


def ruta_rastro() -> Path:
    return DIRECTORIO / "logs" / "esfuerzo.log"


def ruta_plist() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{ETIQUETA}.plist"


def ruta_respaldo_ajustes() -> Path:
    return DIRECTORIO / "modelos-ajustes.json"


def directorio_atajos() -> Path:
    return Path.home() / ".local" / "bin"


def configs_vigilados(perfil: dict | None = None) -> list[Path]:
    """Los `.claude.json` a reponer: el global, el de `CLAUDE_CONFIG_DIR` y los del perfil.

    Un directorio declarado en `[modelos] configs` se expande a sus `*/.claude.json`; un
    fichero se toma tal cual. No se comprueba que existan: launchd ignora un `WatchPaths`
    ausente y `repone` anota el que no puede leer.
    """
    vistos: dict[Path, None] = {Path.home() / ".claude.json": None}
    aislado = os.environ.get("CLAUDE_CONFIG_DIR")
    if aislado:
        vistos.setdefault(Path(aislado).expanduser() / ".claude.json", None)
    for extra in (perfil or {}).get("configs") or []:
        if not isinstance(extra, str):
            continue
        ruta = Path(extra).expanduser()
        if ruta.is_dir():
            for hijo in sorted(ruta.glob("*/.claude.json")):
                vistos.setdefault(hijo, None)
        else:
            vistos.setdefault(ruta, None)
    return list(vistos)


def modelo_duro(perfil: dict | None = None) -> str:
    valor = (perfil or {}).get("duro")
    return valor if isinstance(valor, str) and valor.strip() else MODELO_DURO_POR_DEFECTO


# --- Reponer: idempotente y atómico --------------------------------------------------------


def _atomico(ruta: Path, texto: str) -> None:
    """Temporal en el MISMO directorio + `os.replace`. Nunca en el sitio (NUCLEO §7).

    El CLI lee `~/.claude.json` constantemente: un JSON a medias lo deja sin configuración.
    """
    fd, tmp = tempfile.mkstemp(dir=str(ruta.parent), prefix=f".{ruta.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fichero:
            fichero.write(texto)
        os.chmod(tmp, 0o600)
        os.replace(tmp, ruta)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def repone(config: Path) -> tuple[list[str], str | None]:
    """Añade las entradas que falten. Devuelve `(ids añadidos, motivo si no se pudo leer)`.

    Respeta lo que venga del servidor: solo añade, nunca reordena ni quita. Un fichero
    ilegible no aborta el resto de configs; se devuelve el motivo para decirlo.
    """
    try:
        datos = json.loads(config.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [], "no existe"
    except (OSError, UnicodeError, ValueError) as exc:
        return [], f"ilegible ({exc.__class__.__name__})"
    if not isinstance(datos, dict):
        return [], "no es un objeto JSON"
    actuales = datos.get("additionalModelOptionsCache")
    actuales = actuales if isinstance(actuales, list) else []
    presentes = {o.get("value") for o in actuales if isinstance(o, dict)}
    faltan = [e for e in entradas_deseadas() if e["value"] not in presentes]
    if not faltan:
        return [], None
    datos["additionalModelOptionsCache"] = actuales + faltan
    _atomico(config, json.dumps(datos, indent=2, ensure_ascii=False))
    return [e["value"] for e in faltan], None


def presentes_en(config: Path) -> tuple[list[str], list[str]] | None:
    """`(presentes, faltan)` de los ids deseados en un config; ``None`` si no se puede leer."""
    datos = leer_ajustes(config)
    if datos is None:
        return None
    actuales = datos.get("additionalModelOptionsCache")
    actuales = actuales if isinstance(actuales, list) else []
    ids = {o.get("value") for o in actuales if isinstance(o, dict)}
    deseados = [m.valor for m in MODELOS]
    return [v for v in deseados if v in ids], [v for v in deseados if v not in ids]


# --- Lo que se escribe en disco: generado desde aquí, comparable por hash ------------------


def contenido_reponedor(configs: list[Path]) -> str:
    """El guion autónomo que corre launchd y el hook. No importa `puente`: launchd no tiene el
    clon en el PYTHONPATH y un agente que apunta al clon se rompe el día que el clon se mueve.
    Lleva la lista de modelos y los configs resueltos al instalar; `estado` compara su hash
    con el que se generaría hoy y dice `desactualizado` si difieren."""
    lista = json.dumps(entradas_deseadas(), ensure_ascii=False, indent=4)
    rutas = json.dumps([str(c) for c in configs], ensure_ascii=False, indent=4)
    return f'''#!/usr/bin/env python3
# {MARCA}: lo escribe 'cosmos configurar --modelos instalar' y lo quita '--modelos quitar'.
# Repone en cada .claude.json vigilado las entradas de modelo que falten, sin tocar las que
# vengan del servidor. Escritura atómica: temporal en el mismo directorio + os.replace.
import json, os, sys, tempfile
from pathlib import Path

DESEADAS = {lista}
CONFIGS = {rutas}
# El hook SessionStart pasa el CLAUDE_CONFIG_DIR de la sesión: launchd no lo conoce.
if os.environ.get("CLAUDE_CONFIG_DIR"):
    CONFIGS.append(os.path.join(os.path.expanduser(os.environ["CLAUDE_CONFIG_DIR"]), ".claude.json"))


def repone(ruta):
    try:
        datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as exc:
        print(f"{{ruta}}: ilegible ({{exc.__class__.__name__}})", file=sys.stderr)
        return None
    if not isinstance(datos, dict):
        return None
    actuales = datos.get("additionalModelOptionsCache")
    actuales = actuales if isinstance(actuales, list) else []
    presentes = {{o.get("value") for o in actuales if isinstance(o, dict)}}
    faltan = [e for e in DESEADAS if e["value"] not in presentes]
    if not faltan:
        return []
    datos["additionalModelOptionsCache"] = actuales + faltan
    fd, tmp = tempfile.mkstemp(dir=str(Path(ruta).parent), prefix="." + Path(ruta).name + ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        os.chmod(tmp, 0o600)
        os.replace(tmp, ruta)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
    return [e["value"] for e in faltan]


for ruta in dict.fromkeys(CONFIGS):
    anadidos = repone(ruta)
    if anadidos:
        print(f"{{ruta}}: añadidos {{len(anadidos)}} ({{', '.join(anadidos)}})")
'''


def contenido_plist(interprete: str, reponedor: Path, configs: list[Path], log: Path) -> str:
    vigilados = "\n".join(f"        <string>{c}</string>" for c in configs)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- {MARCA} -->
    <key>Label</key>
    <string>{ETIQUETA}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{interprete}</string>
        <string>{reponedor}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>WatchPaths</key>
    <array>
{vigilados}
    </array>
    <key>StartInterval</key>
    <integer>{INTERVALO_SEGUNDOS}</integer>
    <key>StandardOutPath</key>
    <string>{log}</string>
    <key>StandardErrorPath</key>
    <string>{log}</string>
</dict>
</plist>
"""


def orden_hook(interprete: str, reponedor: Path) -> str:
    # En segundo plano y con tres segundos de espera: el CLI reescribe su fichero justo al
    # arrancar, y reponer antes de eso es reponer para nada (medido en el origen de esto).
    return (
        f"bash -c 'nohup bash -c \"sleep 3; {interprete} {reponedor}\" >/dev/null 2>&1 &'  # {MARCA}"
    )


def contenido_atajo(nombre: str, esfuerzo: str, modelo: str, rastro: Path) -> str:
    """`maxcode` (opus + effort max) y `ultracode` (opus + effort ultracode).

    No se suman: son puntos distintos de la misma escala de esfuerzo del CLI. Si el usuario
    pasa su propio `--model` o `--effort`, mandan los suyos. `maxcode -p` puede hacer una
    segunda pasada de revisión con `COSMOS_VERIFICA=1`; APAGADA por defecto porque duplica el
    gasto, y un doble silencioso es lo contrario de lo que este proyecto persigue.
    """
    verificacion = ""
    if nombre == "maxcode":
        verificacion = '''
# Segunda pasada de revisión, solo en `maxcode -p "texto"` y solo con COSMOS_VERIFICA=1.
if [ "${COSMOS_VERIFICA:-0}" = "1" ] && [ "$#" -eq 2 ] && { [ "$1" = "-p" ] || [ "$1" = "--print" ]; }; then
  echo "maxcode: revisión en segunda pasada (COSMOS_VERIFICA=1, ~2x tokens)" 1>&2
  R1="$(claude --model "$MODELO" --effort "$ESFUERZO" -p "$2")"
  exec claude --model "$MODELO" --effort "$ESFUERZO" -p "Revisa esta respuesta a fondo (errores de hecho, huecos, código que no correría) y devuelve SOLO la versión final para el usuario, en su idioma, sin comentar la revisión.

PREGUNTA:
$2

RESPUESTA A REVISAR:
$R1"
fi
'''
    return f'''#!/usr/bin/env bash
# {MARCA}: lo escribe 'cosmos configurar --modelos instalar' y lo quita '--modelos quitar'.
# {nombre}: Claude Code con el modelo duro y --effort {esfuerzo}. El modelo sale de
# [modelos] duro en ~/.cosmos/perfil.toml al instalar; si cambia, vuelve a instalar.
set -euo pipefail
MODELO={json.dumps(modelo)}
ESFUERZO={json.dumps(esfuerzo)}

# Rastro de cada invocación (una línea JSON, best-effort): cuántas veces se tiró del modo caro.
mkdir -p {json.dumps(str(rastro.parent))} 2>/dev/null || true
printf '{{"at":"%s","modo":"%s","cwd":"%s"}}\\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "{nombre}" "$PWD" >> {json.dumps(str(rastro))} 2>/dev/null || true
{verificacion}
for arg in "$@"; do
  case "$arg" in
    --effort|--effort=*|--model|--model=*) exec claude "$@" ;;
  esac
done
exec claude --model "$MODELO" --effort "$ESFUERZO" "$@"
'''


ATAJOS = (("maxcode", "max"), ("ultracode", "ultracode"))


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def es_nuestro(ruta: Path) -> bool:
    try:
        return MARCA in ruta.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return False


# --- El hook SessionStart en los ajustes de usuario, sin pisar nada -----------------------


def _es_hook_nuestro(entrada: object) -> bool:
    if not isinstance(entrada, dict) or not isinstance(entrada.get("hooks"), list):
        return False
    return any(isinstance(h, dict) and MARCA in str(h.get("command", "")) for h in entrada["hooks"])


def podar_hook(datos: dict) -> dict:
    copia = json.loads(json.dumps(datos))
    hooks = copia.get("hooks")
    if not isinstance(hooks, dict):
        return copia
    entradas = hooks.get("SessionStart")
    if isinstance(entradas, list):
        restantes = [e for e in entradas if not _es_hook_nuestro(e)]
        if restantes:
            hooks["SessionStart"] = restantes
        else:
            del hooks["SessionStart"]
    if not hooks:
        del copia["hooks"]
    return copia


def fijar_hook(orden: str, ruta: Path | None = None, respaldo: Path | None = None) -> str:
    ruta = ruta or ajustes_usuario()
    respaldo = respaldo or ruta_respaldo_ajustes()
    existia = ruta.is_file()
    original = ruta.read_text(encoding="utf-8") if existia else None
    datos = leer_ajustes(ruta)
    if existia and datos is None:
        raise ValueError(f"{ruta} no es un objeto JSON legible; no se ha tocado nada")
    datos = podar_hook(datos or {})
    hooks = datos.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError(f"la clave 'hooks' de {ruta} no es un objeto; no se ha tocado nada")
    existentes = hooks.get("SessionStart")
    hooks["SessionStart"] = (existentes if isinstance(existentes, list) else []) + [
        {"hooks": [{"type": "command", "command": orden, "timeout": 5}]}
    ]
    guardado = leer_ajustes(respaldo) or {}
    if guardado.get("marca") == MARCA and "original" in guardado:
        existia, original = bool(guardado.get("existia")), guardado.get("original")
        creo_directorio = bool(guardado.get("creo_directorio"))
    else:
        creo_directorio = not ruta.parent.exists()
    escribir_privado(respaldo, json.dumps({
        "esquema": 1, "marca": MARCA, "existia": existia, "creo_directorio": creo_directorio, "original": original,
    }, ensure_ascii=False, indent=2) + "\n")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return "actualizado" if existia else "creado"


def retirar_hook(ruta: Path | None = None, respaldo: Path | None = None) -> str:
    ruta = ruta or ajustes_usuario()
    respaldo = respaldo or ruta_respaldo_ajustes()
    if not ruta.is_file():
        respaldo.unlink(missing_ok=True)
        return "ausente"
    datos = leer_ajustes(ruta)
    if datos is None:
        return "ilegible"
    podado = podar_hook(datos)
    guardado = leer_ajustes(respaldo) or {}
    if guardado.get("marca") == MARCA and "existia" in guardado:
        original = guardado.get("original")
        try:
            previo = podar_hook(json.loads(original)) if isinstance(original, str) else {}
        except ValueError:
            previo = None
        intacto = previo is not None and podado == previo
        if intacto and guardado["existia"] and isinstance(original, str):
            ruta.write_text(original, encoding="utf-8")
            respaldo.unlink(missing_ok=True)
            return "restaurado"
        if intacto and not guardado["existia"]:
            ruta.unlink()
            respaldo.unlink(missing_ok=True)
            if guardado.get("creo_directorio") and not any(ruta.parent.iterdir()):
                ruta.parent.rmdir()
            return "eliminado"
    if podado == datos:
        respaldo.unlink(missing_ok=True)
        return "ausente"
    ruta.write_text(json.dumps(podado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    respaldo.unlink(missing_ok=True)
    return "podado"


def tiene_hook(ruta: Path | None = None) -> bool:
    datos = leer_ajustes(ruta or ajustes_usuario()) or {}
    hooks = datos.get("hooks")
    if not isinstance(hooks, dict) or not isinstance(hooks.get("SessionStart"), list):
        return False
    return any(_es_hook_nuestro(e) for e in hooks["SessionStart"])


# --- Las tres acciones -------------------------------------------------------------------

Ejecutor = Callable[[list[str]], subprocess.CompletedProcess]


def _ejecutar_real(orden: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(orden, capture_output=True, text=True, check=False)


def _uid() -> int:
    return os.getuid() if hasattr(os, "getuid") else 0


def instalar(*, perfil: dict | None = None, interprete: str | None = None, ejecutor: Ejecutor = _ejecutar_real,
             seco: bool = False, forzar: bool = False, plataforma: str | None = None) -> list[str]:
    """Escribe el reponedor, el agente de launchd (solo macOS), el hook y los atajos.

    Devuelve las líneas del informe. Exige Python ≥ 3.11 (lo que COSMOS pide por `tomllib`):
    el intérprete se resuelve al instalar, nunca `/usr/bin/python3` a pelo, que en un Mac sin
    herramientas de línea de comandos dispara el instalador de Xcode.
    """
    if sys.version_info < (3, 11):
        raise ValueError(f"hace falta python3 >= 3.11 y este es {sys.version.split()[0]}")
    perfil = leer_modelos() if perfil is None else perfil
    interprete = interprete or sys.executable
    plataforma = plataforma or sys.platform
    configs = configs_vigilados(perfil)
    reponedor, plist, log = ruta_reponedor(), ruta_plist(), ruta_log()
    lineas: list[str] = []

    if seco:
        lineas.append(f"  (seco) escribiría {reponedor} con {len(configs)} config(s) vigilado(s):")
        lineas.extend(f"      {c}" for c in configs)
        lineas.append(f"  (seco) hook SessionStart en {ajustes_usuario()}")
        if plataforma == "darwin":
            lineas.append(f"  (seco) agente {ETIQUETA} en {plist} (RunAtLoad + WatchPaths + cada {INTERVALO_SEGUNDOS} s)")
        else:
            lineas.append("  (seco) sin agente launchd: solo macOS; en esta plataforma queda el hook")
        for nombre, _ in ATAJOS:
            lineas.append(f"  (seco) atajo {directorio_atajos() / nombre}")
        return lineas

    escribir_privado(reponedor, contenido_reponedor(configs))
    reponedor.chmod(0o700)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.parent.chmod(0o700)
    lineas.append(f"  Reponedor ......... {reponedor}  ({len(configs)} config(s) vigilado(s))")
    for config in configs:
        lineas.append(f"      {config}")

    estado_hook = fijar_hook(orden_hook(interprete, reponedor))
    lineas.append(f"  Hook SessionStart . {estado_hook} en {ajustes_usuario()}")

    if plataforma == "darwin":
        plist.parent.mkdir(parents=True, exist_ok=True)
        plist.write_text(contenido_plist(interprete, reponedor, configs, log), encoding="utf-8")
        destino = f"gui/{_uid()}"
        ejecutor(["launchctl", "bootout", f"{destino}/{ETIQUETA}"])
        ejecutor(["launchctl", "enable", f"{destino}/{ETIQUETA}"])
        resultado = ejecutor(["launchctl", "bootstrap", destino, str(plist)])
        if resultado.returncode:
            lineas.append(f"  Agente launchd .... ESCRITO en {plist} pero no se pudo cargar: {(resultado.stderr or '').strip() or 'launchctl devolvió ' + str(resultado.returncode)}")
        else:
            lineas.append(f"  Agente launchd .... cargado ({ETIQUETA}: al arrancar, al cambiar cada config y cada {INTERVALO_SEGUNDOS} s)")
    else:
        lineas.append("  Agente launchd .... no instalado: solo existe en macOS; en esta plataforma repone el hook")

    modelo = modelo_duro(perfil)
    for nombre, esfuerzo in ATAJOS:
        ruta = directorio_atajos() / nombre
        if ruta.exists() and not es_nuestro(ruta) and not forzar:
            lineas.append(f"  Atajo {nombre:<10} .. {ruta} existe y NO es nuestro: no se toca (--forzar para pisarlo)")
            continue
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido_atajo(nombre, esfuerzo, modelo, ruta_rastro()), encoding="utf-8")
        ruta.chmod(0o755)
        lineas.append(f"  Atajo {nombre:<10} .. {ruta}  (claude --model {modelo} --effort {esfuerzo})")
    if str(directorio_atajos()) not in os.environ.get("PATH", "").split(os.pathsep):
        lineas.append(f"  Ojo: {directorio_atajos()} no está en el PATH de esta terminal.")

    anadidos_total = 0
    for config in configs:
        anadidos, motivo = repone(config)
        anadidos_total += len(anadidos)
        if motivo and motivo != "no existe":
            lineas.append(f"  {config}: {motivo}; no se ha tocado")
    lineas.append(f"  Repuesto ahora .... {anadidos_total} entrada(s) de modelo")
    return lineas


def quitar(*, ejecutor: Ejecutor = _ejecutar_real, plataforma: str | None = None) -> list[str]:
    """Quita todo lo que `instalar` escribió. NO borra las entradas ya presentes en los menús:
    quitar el vigilante no es borrar datos ajenos; siguen hasta el próximo arranque del CLI."""
    plataforma = plataforma or sys.platform
    lineas: list[str] = []
    plist = ruta_plist()
    if plataforma == "darwin":
        ejecutor(["launchctl", "bootout", f"gui/{_uid()}/{ETIQUETA}"])
    if plist.is_file() and es_nuestro(plist):
        plist.unlink()
        lineas.append(f"  Agente launchd .... descargado y {plist} borrado")
    elif plist.exists():
        lineas.append(f"  Agente launchd .... {plist} existe y no es nuestro: no se toca")
    estado = retirar_hook()
    explicacion = {
        "restaurado": "quitado; ajustes devueltos byte a byte",
        "eliminado": "quitado; el fichero no existía antes y se elimina",
        "podado": "quitado; el resto de los ajustes lo cambió alguien y se conserva",
        "ausente": "no estaba",
        "ilegible": "los ajustes no son JSON legible: NO se han tocado",
    }[estado]
    lineas.append(f"  Hook SessionStart . {explicacion} ({ajustes_usuario()})")
    reponedor = ruta_reponedor()
    if reponedor.exists() and es_nuestro(reponedor):
        reponedor.unlink()
        lineas.append(f"  Reponedor ......... {reponedor} borrado")
    for nombre, _ in ATAJOS:
        ruta = directorio_atajos() / nombre
        if ruta.exists() and es_nuestro(ruta):
            ruta.unlink()
            lineas.append(f"  Atajo {nombre:<10} .. {ruta} borrado")
        elif ruta.exists():
            lineas.append(f"  Atajo {nombre:<10} .. {ruta} no es nuestro: no se toca")
    lineas.append("  Las entradas ya presentes en /model siguen ahí hasta el próximo arranque del CLI: no se borran.")
    return lineas


@dataclass(frozen=True)
class Fila:
    nombre: str
    estado: str  # ok | falta | desactualizado | ajeno | no_comprobado
    detalle: str


def estado(*, perfil: dict | None = None, interprete: str | None = None, ejecutor: Ejecutor = _ejecutar_real,
           plataforma: str | None = None) -> list[Fila]:
    """Qué hay instalado en ESTA máquina, trivalente: nunca `ok` por no haber podido mirar."""
    perfil = leer_modelos() if perfil is None else perfil
    interprete = interprete or sys.executable
    plataforma = plataforma or sys.platform
    configs = configs_vigilados(perfil)
    filas: list[Fila] = []

    reponedor = ruta_reponedor()
    if not reponedor.is_file():
        filas.append(Fila("reponedor", "falta", f"{reponedor} no existe -> cosmos configurar --modelos instalar"))
    elif not es_nuestro(reponedor):
        filas.append(Fila("reponedor", "ajeno", f"{reponedor} existe y no lleva la marca"))
    elif _sha(reponedor.read_text(encoding="utf-8")) != _sha(contenido_reponedor(configs)):
        filas.append(Fila("reponedor", "desactualizado", "la copia instalada no coincide con la que se generaría hoy -> volver a instalar"))
    else:
        filas.append(Fila("reponedor", "ok", str(reponedor)))

    if plataforma != "darwin":
        filas.append(Fila("agente launchd", "no_comprobado", "solo existe en macOS"))
    else:
        plist = ruta_plist()
        if not plist.is_file():
            filas.append(Fila("agente launchd", "falta", f"{plist} no existe"))
        else:
            resultado = ejecutor(["launchctl", "print", f"gui/{_uid()}/{ETIQUETA}"])
            if resultado.returncode:
                filas.append(Fila("agente launchd", "falta", f"{plist} existe pero no está cargado"))
            else:
                salida = resultado.stdout or ""
                estado_txt = next((l.strip() for l in salida.splitlines() if "state =" in l), "cargado")
                filas.append(Fila("agente launchd", "ok", f"{ETIQUETA} ({estado_txt})"))

    filas.append(Fila("hook SessionStart", "ok" if tiene_hook() else "falta", str(ajustes_usuario())))

    modelo = modelo_duro(perfil)
    for nombre, esfuerzo in ATAJOS:
        ruta = directorio_atajos() / nombre
        if not ruta.is_file():
            filas.append(Fila(f"atajo {nombre}", "falta", str(ruta)))
        elif not es_nuestro(ruta):
            filas.append(Fila(f"atajo {nombre}", "ajeno", f"{ruta} existe y no lleva la marca"))
        elif ruta.read_text(encoding="utf-8") != contenido_atajo(nombre, esfuerzo, modelo, ruta_rastro()):
            filas.append(Fila(f"atajo {nombre}", "desactualizado", f"{ruta} no coincide con el perfil actual (duro = {modelo})"))
        else:
            filas.append(Fila(f"atajo {nombre}", "ok", f"{ruta}  ({modelo}, --effort {esfuerzo})"))

    for config in configs:
        cuenta = presentes_en(config)
        if cuenta is None:
            filas.append(Fila(f"config {config}", "no_comprobado", "no existe o no es JSON legible"))
        else:
            presentes, faltan = cuenta
            detalle = f"{len(presentes)}/{len(MODELOS)} presentes" + (f"  (faltan {', '.join(faltan)})" if faltan else "")
            filas.append(Fila(f"config {config}", "ok" if not faltan else "falta", detalle))

    filas.append(Fila("acceso de la cuenta", "no_comprobado",
                      "hace falta red: claude --model <id> -p ok  (responde -> el id vale)"))
    return filas


def formatear(filas: list[Fila]) -> str:
    nombres = [abreviar_home(f.nombre) for f in filas]
    ancho = max(len(n) for n in nombres) if filas else 10
    return "\n".join(f"  {n:<{ancho}}  {f.estado:<15} {abreviar_home(f.detalle)}" for n, f in zip(nombres, filas))
