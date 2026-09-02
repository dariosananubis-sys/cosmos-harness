#!/usr/bin/env python3
"""Manda un comando a las OTRAS terminales de Claude Code abiertas en VS Code.

Para lo que ClaudeClaw no puede: los comandos de la TUI (`/pre-compact`, `/compact`,
`/clear`, `/resume`) solo existen en una sesión interactiva. Para repartir TRABAJO no
uses esto — usa `tools/repartir-trabajo.py`, que habla por API con las ventanas de
ClaudeClaw y no depende de teclazos.

REGLA DURA: nunca se manda nada a la terminal desde la que corre
esto. Si pide "a todas incluida la tuya", la propia va SIEMPRE la última.

Uso:
    python3 tools/mandar-a-terminales.py --listar
    python3 tools/mandar-a-terminales.py --calibrar              # 1 vez por sesión
    python3 tools/mandar-a-terminales.py --enviar "/pre-compact" --mi-posicion 3
    python3 tools/mandar-a-terminales.py --enviar "..." --mi-posicion 3 --incluirme
    python3 tools/mandar-a-terminales.py --enviar "..." --dry-run

Por qué hace falta calibrar: no hay forma de preguntarle a VS Code qué terminal tiene
el foco (el árbol de Accesibilidad de Electron devuelve `missing value`, comprobado), y
el título de la pestaña lo reescribe Claude Code con el resumen de su tarea, así que
tampoco sirve para apuntar por nombre. Lo único fiable es ciclar con "Focus Next
Terminal" — y para no escribirse a uno mismo hay que saber en qué paso del ciclo cae la
propia terminal. `--calibrar` lo averigua: cicla una vuelta entera y guarda una captura
de la cabecera del panel en cada paso, donde se lee el nombre de la terminal activa.

Comprobado (no supuesto):
  - Escribir a `/dev/ttysNNN` va a la SALIDA del terminal, no a la entrada del proceso.
  - El ioctl TIOCSTI (el mecanismo diseñado para esto) da EPERM en macOS.
  - Hay que ACTIVAR la app con `tell application "Code" to activate`; poner `frontmost`
    del proceso NO basta. Y hace falta un CLIC dentro del panel antes de la 1ª paleta,
    si no, la paleta ni se abre.
  - Con eso, el ciclo paleta -> "Terminal: Focus Next Terminal" -> teclear -> Enter
    entrega el texto a la terminal enfocada (verificado con capturas).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

CLIC_TERMINAL = (900, 700)          # punto dentro del panel de terminal, en puntos
CABECERA = (0, 565, 2240, 45)       # franja donde VS Code pinta el nombre de la activa
ESPERA_DELTA = 8                    # segundos entre las dos fotos para ver quién escribe


def sh(*cmd: str) -> str:
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def terminales() -> list[dict]:
    """Procesos `claude` con tty: una entrada por terminal de VS Code."""
    out = []
    for linea in sh("ps", "-eo", "pid,ppid,tty,command").splitlines()[1:]:
        campos = linea.split(None, 3)
        if len(campos) < 4:
            continue
        pid, ppid, tty, cmd = campos
        if tty in ("??", "-") or cmd.strip() != "claude":
            continue
        out.append({"pid": int(pid), "ppid": int(ppid), "tty": tty})
    return sorted(out, key=lambda t: t["tty"])


def mi_tty() -> str | None:
    """El tty del claude del que cuelga este script (subiendo por los padres)."""
    pid = os.getpid()
    for _ in range(8):
        linea = sh("ps", "-o", "ppid=,tty=", "-p", str(pid)).strip()
        if not linea:
            return None
        partes = linea.split()
        padre, tty = int(partes[0]), (partes[1] if len(partes) > 1 else "??")
        if tty not in ("??", "-"):
            return tty
        pid = padre
        if pid <= 1:
            return None
    return None


def transcript(pid: int) -> str | None:
    for linea in sh("lsof", "-p", str(pid), "-Fn").splitlines():
        if linea.startswith("n") and linea.endswith(".jsonl"):
            return linea[1:]
    return None


def marca_ocupadas(ts: list[dict]) -> None:
    """Ocupada = su transcript crece entre dos fotos separadas unos segundos."""
    antes = {}
    for t in ts:
        f = transcript(t["pid"])
        t["transcript"] = f
        antes[t["tty"]] = os.path.getsize(f) if f and os.path.exists(f) else -1
    time.sleep(ESPERA_DELTA)
    for t in ts:
        f = t.get("transcript")
        ahora = os.path.getsize(f) if f and os.path.exists(f) else -1
        t["ocupada"] = ahora > antes[t["tty"]] >= 0


def osa(guion: str) -> str:
    """AppleScript. Si falla, se dice: un fallo mudo aquí significa teclazos perdidos
    (o peor, caídos en la ventana equivocada)."""
    r = subprocess.run(["osascript", "-e", guion], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  [!] osascript falló ({r.returncode}): {r.stderr.strip()[:160]}")
        print("      Suele ser permiso de Accesibilidad: Ajustes > Privacidad y "
              "seguridad > Accesibilidad, marca Terminal/VS Code.")
    return (r.stdout + r.stderr).strip()


def prepara_foco() -> None:
    osa('tell application "Code" to activate')
    time.sleep(0.6)
    osa(f'tell application "System Events" to click at '
        f'{{{CLIC_TERMINAL[0]}, {CLIC_TERMINAL[1]}}}')
    time.sleep(0.5)


def siguiente_terminal() -> None:
    osa('tell application "System Events"\n'
        '  keystroke "p" using {command down, shift down}\n'
        '  delay 0.6\n'
        '  keystroke "Terminal: Focus Next Terminal"\n'
        '  delay 0.6\n'
        '  key code 36\n'
        'end tell')
    time.sleep(0.6)


def teclea(texto: str) -> None:
    seguro = texto.replace("\\", "\\\\").replace('"', '\\"')
    osa('tell application "System Events"\n'
        f'  keystroke "{seguro}"\n'
        '  delay 0.4\n'
        '  key code 36\n'
        'end tell')
    time.sleep(0.8)


def captura(destino: Path) -> None:
    x, y, w, h = CABECERA
    subprocess.run(["screencapture", "-x", f"-R{x},{y},{w},{h}", str(destino)], check=False)


def calibrar(total: int, carpeta: Path) -> int:
    carpeta.mkdir(parents=True, exist_ok=True)
    prepara_foco()
    print(f"Calibrando {total} posiciones. Mira las capturas y quédate con el paso en\n"
          f"el que salga TU terminal; ese número es --mi-posicion.\n")
    for paso in range(1, total + 1):
        siguiente_terminal()
        destino = carpeta / f"calib-{paso}.png"
        captura(destino)
        print(f"  paso {paso}: {destino}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--listar", action="store_true", help="inventario y nada más")
    ap.add_argument("--calibrar", action="store_true",
                    help="cicla una vuelta y guarda una captura por paso")
    ap.add_argument("--enviar", metavar="TEXTO", help="qué mandar a cada terminal")
    ap.add_argument("--mi-posicion", type=int, metavar="N",
                    help="paso del ciclo en el que cae MI terminal (sale de --calibrar)")
    ap.add_argument("--incluirme", action="store_true",
                    help="manda también a la propia terminal, y SIEMPRE la última")
    ap.add_argument("--solo-libres", action="store_true",
                    help="no hagas nada si alguna terminal está trabajando")
    ap.add_argument("--dry-run", action="store_true", help="di qué harías, sin tocar teclas")
    ap.add_argument("--capturas", default=None, help="carpeta para las capturas de calibrado")
    args = ap.parse_args()

    ts = terminales()
    if not ts:
        print("No hay ninguna terminal de Claude Code abierta.")
        return 1
    mia = mi_tty()
    marca_ocupadas(ts)

    print(f"{len(ts)} terminales de Claude Code (la mía: {mia or 'no detectada'})\n")
    for t in ts:
        marca = "   <- LA MÍA" if t["tty"] == mia else ""
        print(f"  {t['tty']} pid={t['pid']} {'ocupada' if t['ocupada'] else 'libre'}{marca}")

    total = len(ts)
    if args.listar or (not args.enviar and not args.calibrar):
        return 0

    if total < 2:
        print("\nSolo está mi terminal: no hay a quién mandarle nada. No hago nada.")
        return 1

    carpeta = Path(args.capturas or (Path(os.environ.get("TMPDIR", "/tmp")) / "calib-terminales"))
    if args.calibrar:
        return calibrar(total, carpeta)

    ocupadas = [t["tty"] for t in ts if t["ocupada"] and t["tty"] != mia]
    if ocupadas:
        print(f"\nTrabajando ahora: {', '.join(ocupadas)} "
              "(el mensaje les quedaría en cola, no las corta)")
        if args.solo_libres:
            print("--solo-libres: no mando nada.")
            return 1

    if not args.mi_posicion:
        print("\nNo sé en qué paso del ciclo cae MI terminal: no mando nada para no\n"
              "escribirme a mí mismo. Saca el número con --calibrar y pásalo en\n"
              "--mi-posicion N. (Regla dura.)")
        return 1
    if not 1 <= args.mi_posicion <= total:
        print(f"\n--mi-posicion tiene que estar entre 1 y {total}.")
        return 1

    print(f"\nMandaría «{args.enviar}» a {total - 1} terminales "
          f"(salto el paso {args.mi_posicion}, que soy yo)"
          + (", y a la mía la última" if args.incluirme else "") + ".")
    if args.dry_run:
        print("(dry-run: no toco el teclado)")
        return 0

    prepara_foco()
    enviados = 0
    for paso in range(1, total + 1):
        siguiente_terminal()
        if paso == args.mi_posicion:
            print(f"  paso {paso}: soy yo, no escribo")
            continue
        teclea(args.enviar)
        enviados += 1
        print(f"  paso {paso}: enviado")

    if args.incluirme:
        for _ in range(args.mi_posicion):
            siguiente_terminal()
        teclea(args.enviar)
        enviados += 1
        print("  enviado a mi propia terminal (la última)")

    print(f"\n{enviados} envíos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
