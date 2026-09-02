#!/usr/bin/env python3
"""Guardarrail: nadie escribe hasta haber leido el playbook EN ESTA sesion.

Un aviso en un fichero de contexto no impide nada, porque cumplirlo depende de
acordarse. Esto lo convierte en una precondicion que falla sola:

  1. `marca`  (PostToolUse) apunta que el playbook se ha leido en esta sesion.
     La marca guarda el SHA-256 del playbook: editarlo invalida todas las
     lecturas anteriores, asi que nadie trabaja con una version vieja.
  2. `guard`  (PreToolUse) deniega la escritura si esa marca no existe o su
     hash no cuadra. Sale con codigo 2, que es como se bloquea una llamada.
  3. `olvida` (PreCompact / SessionEnd) borra la marca: si el playbook salio
     del contexto al compactar, hay que volver a leerlo.

La marca se indexa por session_id, asi que una sesion NO puede prestarle a otra
el permiso, y se guarda con el id hasheado para no dejar identificadores en
claro en el disco.

Configuracion, toda por entorno (sin valores de nadie dentro del codigo):

  PLAYBOOK_OBLIGATORIO   ruta del fichero que hay que haber leido   (obligatorio)
  PLAYBOOK_ESTADO        carpeta de marcas       (por defecto .playbook-estado)
  PLAYBOOK_HERRAMIENTAS  regex de herramientas vigiladas  (Edit|Write|MultiEdit|NotebookEdit)
  PLAYBOOK_RUTAS         regex opcional: solo vigila si la ruta destino casa

Uso como enganche:

  {"PostToolUse": [{"matcher":"Read",
     "hooks":[{"type":"command","command":"python3 scripts/playbook_gate.py marca"}]}],
   "PreToolUse":  [{"matcher":"Edit|Write",
     "hooks":[{"type":"command","command":"python3 scripts/playbook_gate.py guard"}]}],
   "PreCompact":  [{"matcher":"*",
     "hooks":[{"type":"command","command":"python3 scripts/playbook_gate.py olvida"}]}]}

Comprobacion sin arnes: `python3 scripts/playbook_gate.py autotest`.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERRAMIENTAS_POR_DEFECTO = r"Edit|Write|MultiEdit|NotebookEdit"


def playbook() -> Path:
    ruta = os.environ.get("PLAYBOOK_OBLIGATORIO", "").strip()
    if not ruta:
        raise SystemExit("falta PLAYBOOK_OBLIGATORIO con la ruta del playbook")
    return Path(ruta).expanduser()


def carpeta_estado() -> Path:
    return Path(os.environ.get("PLAYBOOK_ESTADO", ".playbook-estado")).expanduser()


def id_seguro(session_id: str | None) -> str:
    """El id de sesion no se escribe en claro: solo su huella corta."""
    return hashlib.blake2s((session_id or "sin-id").encode(), digest_size=12).hexdigest()


def ruta_marca(session_id: str | None) -> Path:
    return carpeta_estado() / f"playbook-{id_seguro(session_id)}.json"


def huella_playbook() -> str | None:
    try:
        return hashlib.sha256(playbook().read_bytes()).hexdigest()
    except OSError:
        return None


def _ruta_leida(datos: dict) -> str:
    return str(datos.get("file_path") or datos.get("path") or datos.get("notebook_path") or "")


def lectura_valida(entrada: dict) -> bool:
    """Solo cuenta leer el playbook ENTERO desde el principio.

    Un `Read` con offset lee un trozo: no es haber leido el playbook, y dejarlo
    pasar reabre justo el agujero que esto cierra.
    """
    if str(entrada.get("tool_name") or "") != "Read":
        return False
    datos = entrada.get("tool_input") or {}
    try:
        if Path(_ruta_leida(datos)).expanduser().resolve() != playbook().resolve():
            return False
    except OSError:
        return False
    if datos.get("offset") not in (None, 0, 1, "0", "1"):
        return False
    return datos.get("limit") in (None, "")


def cmd_marca(entrada: dict) -> int:
    if not lectura_valida(entrada):
        return 0
    huella = huella_playbook()
    if huella is None:
        return 0
    destino = ruta_marca(entrada.get("session_id"))
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(
            {"sha256": huella, "cuando": datetime.now(timezone.utc).isoformat()},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return 0


def cmd_olvida(entrada: dict) -> int:
    ruta_marca(entrada.get("session_id")).unlink(missing_ok=True)
    return 0


def vigilada(entrada: dict) -> bool:
    herramienta = str(entrada.get("tool_name") or "")
    if not re.fullmatch(os.environ.get("PLAYBOOK_HERRAMIENTAS", HERRAMIENTAS_POR_DEFECTO), herramienta):
        return False
    rutas = os.environ.get("PLAYBOOK_RUTAS", "").strip()
    if not rutas:
        return True
    datos = entrada.get("tool_input") or {}
    candidata = _ruta_leida(datos) or json.dumps(datos, ensure_ascii=False)
    return re.search(rutas, candidata) is not None


def motivo_bloqueo(entrada: dict) -> str | None:
    """None = se puede escribir. Cadena = por que no."""
    esperada = huella_playbook()
    if esperada is None:
        return f"no se puede leer el playbook {playbook()}: sin el no se autoriza nada"
    try:
        marca = json.loads(ruta_marca(entrada.get("session_id")).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return f"lee {playbook()} entero en esta sesion antes de escribir"
    if marca.get("sha256") != esperada:
        return f"{playbook()} cambio desde que lo leiste: vuelve a leerlo entero"
    return None


def cmd_guard(entrada: dict) -> int:
    if not vigilada(entrada):
        return 0
    motivo = motivo_bloqueo(entrada)
    if motivo is None:
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": motivo,
    }}, ensure_ascii=False))
    print(f"BLOQUEADO: {motivo}", file=sys.stderr)
    return 2


def autotest() -> int:
    """Ejercita el ciclo entero, incluido el fallo. Una guarda que nunca se ha
    visto denegar es decorativa."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        libro = Path(tmp) / "PLAYBOOK.md"
        libro.write_text("como se hace aqui\n", encoding="utf-8")
        os.environ["PLAYBOOK_OBLIGATORIO"] = str(libro)
        os.environ["PLAYBOOK_ESTADO"] = str(Path(tmp) / "estado")
        escribir = {"session_id": "s1", "tool_name": "Write", "tool_input": {"file_path": "x.txt"}}
        leer = {"session_id": "s1", "tool_name": "Read", "tool_input": {"file_path": str(libro)}}
        casos = []

        casos.append(("sin leer bloquea", cmd_guard(escribir) == 2))
        cmd_marca(leer)
        casos.append(("tras leer deja pasar", cmd_guard(escribir) == 0))
        casos.append(("otra sesion no hereda", cmd_guard({**escribir, "session_id": "s2"}) == 2))
        libro.write_text("como se hace aqui, corregido\n", encoding="utf-8")
        casos.append(("editar el playbook invalida", cmd_guard(escribir) == 2))
        cmd_marca(leer)
        casos.append(("releer revalida", cmd_guard(escribir) == 0))
        cmd_olvida(escribir)
        casos.append(("compactar obliga a releer", cmd_guard(escribir) == 2))
        cmd_marca({**leer, "tool_input": {"file_path": str(libro), "offset": 40}})
        casos.append(("leer un trozo no marca", cmd_guard(escribir) == 2))
        cmd_marca(leer)
        casos.append(("herramienta no vigilada pasa", cmd_guard({**escribir, "tool_name": "Bash"}) == 0))

        for nombre, ok in casos:
            print(("  ok   " if ok else "  FALLA ") + nombre)
        return 0 if all(ok for _, ok in casos) else 1


def main(argv: list[str]) -> int:
    orden = argv[1] if len(argv) > 1 else ""
    if orden == "autotest":
        return autotest()
    if orden not in {"marca", "guard", "olvida"}:
        print(__doc__)
        return 2
    try:
        entrada = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        entrada = {}
    if not isinstance(entrada, dict):
        entrada = {}
    return {"marca": cmd_marca, "guard": cmd_guard, "olvida": cmd_olvida}[orden](entrada)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
