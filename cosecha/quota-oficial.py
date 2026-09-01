#!/usr/bin/env python3
"""Refresca los porcentajes REALES de cuota (5 h y semanal) de la consola de ClaudeClaw.

Por qué existe
--------------
La consola tenía dos fuentes para las barras de cuota y las dos fallan solas:

1. **Estimación por transcripts** (`tools/claudeclaw-ui/src/quota.ts`): cuenta tokens de
   los `.jsonl` contra un techo puesto a mano. Los `.jsonl` no dicen de qué cuenta salió
   cada mensaje, así que mezcla el consumo de todas las sesiones de `claude-cuenta.py`, y
   el techo (40M / 350M) es un suelo observado, no el límite real. Medido el 2026-08-13:
   la barra de 5 h marcaba **100 %** cuando la real era **13 %**, y la semanal 23 % frente
   al 37 % real.
2. **`.claude/statusline.cjs`**: sí vuelca los porcentajes de verdad, pero solo corre
   cuando hay una sesión INTERACTIVA pintando su statusline. Con el daemon trabajando solo
   —que es lo normal— `rate-limits.json` envejece, pasa de los 45 min que `quota.ts` da por
   buenos y la consola vuelve a estimar. Justo lo que se veía: fichero de las 10:58 a las
   13:41.

Aquí el dato sale de la fuente oficial sin depender de que haya nadie mirando una terminal:
`GET https://api.anthropic.com/api/oauth/usage`, el mismo endpoint que alimenta el `/usage`
del CLI. Devuelve `five_hour.utilization` y `seven_day.utilization` **sin consumir ni un
token** (no es inferencia). Se escribe en el MISMO fichero y con el MISMO formato que ya lee
`quota.ts`, así que la consola lo coge sin tocar el daemon ni reiniciarlo.

Descartado a propósito: sondear con un `POST /v1/messages` de `max_tokens: 1` y leer las
cabeceras `anthropic-ratelimit-unified-*`. Funciona, pero cuesta ~20 tokens facturables por
sondeo (a 1 s serían ~1,7M al día de la cuota de la cuenta). Las peticiones que fallan
—modelo inexistente, cuerpo vacío— NO traen esas cabeceras (probado: 404 y 400 pelados), así
que no hay atajo gratis por esa vía. `/v1/messages/count_tokens` tampoco las trae.

Uso
---
    python3 tools/quota-oficial.py                  # un sondeo y sale
    python3 tools/quota-oficial.py --dry-run        # lo enseña sin escribir
    python3 tools/quota-oficial.py --dry-run --config-dir /ruta/cuenta
    python3 tools/quota-oficial.py --watch          # bucle cada segundo (lo del LaunchAgent)
    python3 tools/quota-oficial.py --watch --intervalo 5

Detalles que NO son obvios
--------------------------
* La cuenta que se mide es la del **daemon**, no la del `~/.claude` global: desde que cada
  cuenta vive en su `CLAUDE_CONFIG_DIR` aislado (`tools/claude-cuenta.py`), el daemon puede
  estar gastando 'webmaster' mientras el global dice otra cosa. Se saca del entorno del
  proceso del daemon (`ps eww $(cat daemon.pid)`), y en `--watch` se recomprueba en cada
  vuelta: si el usuario cambia de cuenta, la barra pasa a medir la nueva sin reiniciar nada.
* El token OAuth vive en el llavero, en el servicio `Claude Code-credentials-<hash>` donde
  `<hash>` son los **8 primeros hex del sha256 del CLAUDE_CONFIG_DIR** (verificado con las
  tres cuentas de la máquina). Sin sufijo para el `~/.claude` de siempre. En `--watch` se
  relee cada 60 s, que es como se entera de que Claude Code lo ha renovado.
* El token **no se renueva aquí a propósito**: el refresh token rota y persistirlo mal
  dejaría la cuenta sin sesión. Si está caducado, el script no escribe nada; lo renueva
  Claude Code en su siguiente sesión y el bucle se recupera solo.
* El fichero solo se reescribe si cambia algún porcentaje o si han pasado 30 s desde la
  última escritura. A un sondeo por segundo, escribir siempre serían ~86.000 escrituras al
  día para un dato que se mueve cada varios minutos; con el refresco de 30 s `medidoAt`
  nunca se acerca a los 45 min que `quota.ts` considera rancios.
* Ante 429 o error de red el intervalo sube en progresión (hasta 60 s) y vuelve al normal en
  cuanto la API responde: un bucle de un segundo no puede convertirse en un martilleo si
  Anthropic empieza a quejarse.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

PROYECTO = Path(__file__).resolve().parents[1]
CLAW = PROYECTO / ".claude" / "claudeclaw"
DESTINO = CLAW / "rate-limits.json"
PID_FILE = CLAW / "daemon.pid"
LOG = CLAW / "quota-oficial.log"
LOG_MAX_BYTES = 256 * 1024

USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
UA = "claude-cli/2.1.231 (external, cli)"

REFRESCO_FORZADO_S = 30
CREDENCIAL_TTL_S = 60
BACKOFF_MAX_S = 60
RESPUESTA_MAX_BYTES = 1024 * 1024


def log(msg: str) -> None:
    linea = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n"
    try:
        if LOG.exists() and LOG.stat().st_size > LOG_MAX_BYTES:
            LOG.write_text(LOG.read_text(encoding="utf-8")[-LOG_MAX_BYTES // 2 :], encoding="utf-8")
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(linea)
    except OSError:
        pass


class ErrorCuota(RuntimeError):
    """Fallo esperable (token caducado, red caída, 429): se reintenta, no se rompe."""


# ---------------------------------------------------------------- cuenta y token


def config_dir(explicito: str | Path | None = None) -> Path:
    """El CLAUDE_CONFIG_DIR de la cuenta que GASTA.

    Orden: el del daemon (la verdad mientras esté vivo) -> la cuenta ELEGIDA -> el del entorno
    -> el global. La elegida va ANTES que el entorno a propósito: si el daemon se cae, el
    LaunchAgent trae un `CLAUDE_CONFIG_DIR` fijo en su plist (el que tuviera el día que se
    instaló) y el medidor se ponía a medir esa cuenta para siempre, enseñando en la consola el
    uso de una cuenta que no está gastando nada. Pasó el 2026-08-17: plist con `webmaster`,
    daemon caído, y las barras marcando 97% cuando la cuenta viva iba al 6%.
    Un valor explicito siempre gana. Lo usa ``claude-cuenta.py elegir`` para
    consultar una cuenta concreta sin cambiar antes la elegida ni depender del
    entorno del daemon.
    """
    if explicito is not None:
        return Path(explicito).expanduser()

    try:
        pid = int(PID_FILE.read_text().strip())
        entorno = subprocess.run(
            ["ps", "eww", str(pid)], capture_output=True, text=True, timeout=10
        ).stdout
        for trozo in entorno.split():
            if trozo.startswith("CLAUDE_CONFIG_DIR="):
                return Path(trozo.split("=", 1)[1])
    except (OSError, ValueError, subprocess.SubprocessError):
        pass

    store = Path.home() / ".secrets" / "claude-accounts"
    try:
        elegida = (store / "elegida").read_text(encoding="utf-8").strip()
        if elegida and (store / "sessions" / elegida).is_dir():
            return store / "sessions" / elegida
    except OSError:
        pass

    env = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(env) if env else Path.home() / ".claude"


def servicio_llavero(cfg: Path) -> str:
    if cfg == (Path.home() / ".claude"):
        return "Claude Code-credentials"
    sufijo = hashlib.sha256(str(cfg).encode()).hexdigest()[:8]
    return f"Claude Code-credentials-{sufijo}"


def token(cfg: Path, timeout_s: float = 20) -> str:
    """Access token OAuth de esa cuenta. ErrorCuota si falta o está caducado."""
    svc = servicio_llavero(cfg)
    try:
        res = subprocess.run(
            ["security", "find-generic-password", "-s", svc, "-w"],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.SubprocessError as err:
        raise ErrorCuota(f"no se pudo leer el llavero: {err}") from err
    if res.returncode != 0:
        raise ErrorCuota(f"sin credenciales en el llavero para {svc}")
    try:
        oauth = json.loads(res.stdout).get("claudeAiOauth") or {}
    except ValueError as err:
        raise ErrorCuota(f"credencial ilegible en {svc}") from err
    tok = oauth.get("accessToken")
    if not tok:
        raise ErrorCuota(f"{svc} no tiene accessToken")
    caduca = oauth.get("expiresAt")
    if isinstance(caduca, (int, float)) and caduca < time.time() * 1000 + 60_000:
        raise ErrorCuota("token caducado; lo renovará Claude Code en su próxima sesión")
    return tok


def cuenta_email(cfg: Path) -> str | None:
    try:
        raw = json.loads((cfg / ".claude.json").read_text(encoding="utf-8"))
        return (raw.get("oauthAccount") or {}).get("emailAddress")
    except (OSError, ValueError):
        return None


# ---------------------------------------------------------------- sondeo


def sondear(tok: str, timeout_s: float = 20) -> dict:
    """GET /api/oauth/usage — lo mismo que enseña /usage. No consume tokens."""
    url = urlsplit(USAGE_URL)
    if url.scheme != "https" or not url.hostname:
        raise ErrorCuota("URL de cuota inválida")
    ruta = url.path or "/"
    if url.query:
        ruta = f"{ruta}?{url.query}"

    conexion: http.client.HTTPSConnection | None = None
    try:
        conexion = http.client.HTTPSConnection(
            url.hostname,
            port=url.port,
            timeout=timeout_s,
        )
        conexion.request(
            "GET",
            ruta,
            headers={
                "authorization": f"Bearer {tok}",
                "anthropic-beta": "oauth-2025-04-20",
                "user-agent": UA,
            },
        )
        respuesta = conexion.getresponse()
        cuerpo = respuesta.read(RESPUESTA_MAX_BYTES + 1)
    except (OSError, http.client.HTTPException) as err:
        # No interpolar ``err``: algunas capas HTTP incluyen datos de la petición
        # en sus mensajes y aquí vive el bearer OAuth.
        raise ErrorCuota(f"HTTPS no respondió ({type(err).__name__})") from None
    finally:
        if conexion is not None:
            try:
                conexion.close()
            except (OSError, http.client.HTTPException):
                pass

    if respuesta.status != 200:
        raise ErrorCuota(f"la API devolvió HTTP {respuesta.status}")
    if len(cuerpo) > RESPUESTA_MAX_BYTES:
        raise ErrorCuota("respuesta demasiado grande")
    try:
        return json.loads(cuerpo)
    except (UnicodeDecodeError, ValueError) as err:
        raise ErrorCuota("respuesta no era JSON") from err


def iso_a_ms(valor) -> int | None:
    if not isinstance(valor, str) or not valor:
        return None
    try:
        return int(datetime.fromisoformat(valor).timestamp() * 1000)
    except ValueError:
        return None


def ventana(bruto: dict, clave: str) -> dict | None:
    v = bruto.get(clave)
    if not isinstance(v, dict) or not isinstance(v.get("utilization"), (int, float)):
        return None
    return {"usadoPct": round(float(v["utilization"]), 1), "reseteaEn": iso_a_ms(v.get("resets_at"))}


def severidad(bruto: dict, grupo: str) -> str | None:
    for lim in bruto.get("limits") or []:
        if isinstance(lim, dict) and lim.get("group") == grupo:
            return lim.get("severity")
    return None


def construir(bruto: dict, email: str | None) -> dict | None:
    cinco = ventana(bruto, "five_hour")
    if cinco is None:
        return None
    extra = bruto.get("extra_usage")
    creditos_extra = None
    if isinstance(extra, dict) and isinstance(extra.get("is_enabled"), bool):
        creditos_extra = extra["is_enabled"]
    return {
        # Lo que ya lee quota.ts, con el formato de statusline.cjs:
        "cincoHoras": cinco,
        "semana": ventana(bruto, "seven_day"),
        "medidoAt": int(time.time() * 1000),
        "sesion": None,
        # Trazas propias: quota.ts las ignora, pero dicen de dónde salió la cifra.
        "fuente": "api",
        "cuenta": email,
        "severidad5h": severidad(bruto, "session"),
        "severidadSemana": severidad(bruto, "weekly"),
        # Solo un booleano explícito de Anthropic permite decidir. Ausente, null,
        # string o número queda desconocido para que el selector falle cerrado.
        "creditosExtra": creditos_extra,
    }


def mismo_dato(a: dict | None, b: dict) -> bool:
    """Compara solo lo que se ve en pantalla: `medidoAt` cambia en cada vuelta."""
    if not a:
        return False
    campos = ("cincoHoras", "semana", "severidad5h", "severidadSemana", "cuenta")
    return all(a.get(c) == b.get(c) for c in campos)


def escribir(datos: dict) -> None:
    tmp = DESTINO.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(datos), encoding="utf-8")
    os.replace(tmp, DESTINO)


def resumen(datos: dict) -> str:
    sem = datos.get("semana")
    return (
        f"5h {datos['cincoHoras']['usadoPct']}% · semana "
        f"{sem['usadoPct'] if sem else '?'}% · {datos.get('cuenta') or 'cuenta desconocida'}"
    )


# ---------------------------------------------------------------- modos


def una_vez(args) -> int:
    cfg = config_dir(args.config_dir)
    try:
        datos = construir(
            sondear(token(cfg, args.request_timeout), args.request_timeout),
            cuenta_email(cfg),
        )
    except ErrorCuota as err:
        # No se pisa el fichero: mejor un dato oficial viejo (que quota.ts descarta solo por
        # edad) que ninguno.
        log(f"ERROR {err}")
        print(f"quota-oficial: {err}", file=sys.stderr)
        return 3
    if datos is None:
        log("ERROR respuesta sin five_hour.utilization")
        print("quota-oficial: la respuesta no traía la ventana de 5 h", file=sys.stderr)
        return 4
    if args.dry_run:
        print(json.dumps(datos, indent=2, ensure_ascii=False))
        return 0
    escribir(datos)
    log(resumen(datos))
    print(f"quota-oficial: {resumen(datos)}")
    return 0


def vigilar(args) -> int:
    parar = {"si": False}

    def adios(*_):
        parar["si"] = True

    signal.signal(signal.SIGTERM, adios)
    signal.signal(signal.SIGINT, adios)

    log(f"watch arranca (cada {args.intervalo}s)")
    cfg = config_dir(args.config_dir)
    tok: str | None = None
    tok_at = 0.0
    ultimo: dict | None = None
    ultima_escritura = 0.0
    fallos = 0
    ultimo_fallo = ""

    while not parar["si"]:
        ahora = time.time()
        try:
            if tok is None or ahora - tok_at > CREDENCIAL_TTL_S:
                # Recomprobar la cuenta activa también: el daemon puede haber cambiado de
                # sesión desde la vuelta anterior.
                cfg = config_dir(args.config_dir)
                tok = token(cfg)
                tok_at = ahora
            datos = construir(sondear(tok), cuenta_email(cfg))
            if datos is None:
                raise ErrorCuota("respuesta sin five_hour.utilization")

            if not mismo_dato(ultimo, datos) or ahora - ultima_escritura > REFRESCO_FORZADO_S:
                escribir(datos)
                if not mismo_dato(ultimo, datos):
                    log(resumen(datos))
                ultima_escritura = ahora
            ultimo = datos
            if fallos:
                log(f"recuperado tras {fallos} fallo(s): {ultimo_fallo}")
            fallos = 0
            espera = args.intervalo
        except ErrorCuota as err:
            fallos += 1
            if str(err) != ultimo_fallo:
                log(f"ERROR {err}")
                ultimo_fallo = str(err)
            tok = None  # por si el fallo fue el token
            espera = min(BACKOFF_MAX_S, max(args.intervalo, 2 ** min(fallos, 6)))

        # Dormir a trocitos para atender la señal de parada sin esperar el intervalo entero.
        fin = time.time() + espera
        while not parar["si"] and time.time() < fin:
            time.sleep(min(0.25, max(0.0, fin - time.time())))

    log("watch para")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Cuota real de Claude Code para la consola.")
    ap.add_argument("--dry-run", action="store_true", help="enseña el dato sin escribirlo")
    ap.add_argument(
        "--config-dir",
        help="consulta exactamente este CLAUDE_CONFIG_DIR, sin inferirlo del daemon",
    )
    ap.add_argument(
        "--request-timeout",
        type=float,
        default=20.0,
        help="limite por consulta de llavero/API; elegir usa 5 s para responder a la web",
    )
    ap.add_argument("--watch", action="store_true", help="bucle continuo en vez de un sondeo")
    ap.add_argument(
        "--intervalo", type=float, default=1.0, help="segundos entre sondeos en --watch (1 por defecto)"
    )
    args = ap.parse_args()
    if args.intervalo < 0.5:
        args.intervalo = 0.5
    if args.request_timeout < 1:
        args.request_timeout = 1
    return vigilar(args) if args.watch else una_vez(args)


if __name__ == "__main__":
    sys.exit(main())
