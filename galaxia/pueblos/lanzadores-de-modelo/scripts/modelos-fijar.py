#!/usr/bin/env python3
"""Fija en el selector /model de Claude Code todos los modelos que acepta la cuenta.

Claude Code construye el menú de /model con las opciones nativas más el array
`additionalModelOptionsCache` de ~/.claude.json. Ese array lo rellena el propio CLI
desde el servidor en cada bootstrap, así que las entradas añadidas a mano se pierden.
Este script las repone de forma idempotente: respeta las que vengan del servidor y
solo añade las que faltan. Pensado para correr en bucle desde un scheduler (cron,
launchd, systemd timer).

Si usas sesiones aisladas por cuenta (cada una con su propio CLAUDE_CONFIG_DIR y por
tanto su propio .claude.json), exporta SESIONES_GLOB apuntando al directorio que las
contiene (glob de subdirectorios con un .claude.json cada uno); si no, solo se toca
el ~/.claude.json global.
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

CONFIG = Path.home() / ".claude.json"
SESIONES_GLOB = Path(os.environ["SESIONES_GLOB"]).expanduser() if os.environ.get("SESIONES_GLOB") else None

# value = id que se le pasa al modelo; label = lo que se ve en el menú.
# Ajusta esta lista a los modelos que tu cuenta/plan acepte.
MODELOS = [
    ("claude-opus-4-5", "Opus 4.5", "Opus 4.5"),
    ("claude-sonnet-4-5", "Sonnet 4.5", "Sonnet 4.5 · rápido y barato"),
    ("claude-haiku-4-5", "Haiku 4.5", "Haiku 4.5 · el más rápido"),
]


def entradas_deseadas():
    return [{"value": v, "label": l, "description": d} for v, l, d in MODELOS]


def configs() -> list[Path]:
    """El config global más el de cada sesión aislada por cuenta, si las hay."""
    todos = [CONFIG]
    if SESIONES_GLOB and SESIONES_GLOB.is_dir():
        todos += sorted(SESIONES_GLOB.glob("*/.claude.json"))
    return [p for p in todos if p.exists()]


def repone(config: Path) -> list[str]:
    """Añade las entradas que falten. Devuelve los ids añadidos (vacío si no tocaba nada)."""
    try:
        data = json.loads(config.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"{config}: ilegible ({e})", file=sys.stderr)
        return []

    actuales = data.get("additionalModelOptionsCache")
    actuales = actuales if isinstance(actuales, list) else []
    presentes = {o.get("value") for o in actuales if isinstance(o, dict)}

    faltan = [e for e in entradas_deseadas() if e["value"] not in presentes]
    if not faltan:
        return []

    data["additionalModelOptionsCache"] = actuales + faltan

    backup = config.with_suffix(".json.bak-modelos")
    if not backup.exists():
        shutil.copy2(config, backup)

    # Escritura atómica: el CLI lee este fichero constantemente y un JSON a medias lo
    # deja sin configuración.
    fd, tmp = tempfile.mkstemp(dir=str(config.parent), prefix=".claude.json.")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.chmod(tmp, 0o600)
        os.replace(tmp, config)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise

    return [e["value"] for e in faltan]


def main() -> int:
    encontrados = configs()
    if not encontrados:
        print("sin ningún .claude.json", file=sys.stderr)
        return 1

    for config in encontrados:
        anadidos = repone(config)
        if anadidos:
            print(f"{config}: añadidos {len(anadidos)} ({', '.join(anadidos)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
