#!/usr/bin/env python3
"""Declara que webs se pueden tocar en la tarea de ahora. Lo demas queda bloqueado.

Por que existe, con nombre y fecha: el 2026-08-03 el encargo hablaba de UNA web y
el arreglo del footer acabo aplicado a las 18 webs de <panel interno>. Tres se tocaron sin
punto de restauracion, asi que ya no se pueden revertir. No fue mala fe: cuando el
comando barre una lista de slugs, nada dice "oye, esta no entraba".

Esto lo dice. Se declara el alcance al empezar y `guard-web-sin-red.py` bloquea
(deny, no pregunta) cualquier escritura en una web que no este en la lista.

    python3 tools/alcance.py proyecto-a --tarea "footer de proyecto-a"
    python3 tools/alcance.py proyecto-a proyecto-b proyecto-c      # varias de una vez
    python3 tools/alcance.py --anadir proyecto-d       # ampliar sobre la marcha
    python3 tools/alcance.py --ver                      # que hay declarado
    python3 tools/alcance.py --quitar                   # al terminar

Sin fichero de alcance NO se bloquea nada: quien no lo declara trabaja como
siempre. Caduca a final del dia por lo mismo — un alcance olvidado de ayer no
puede paralizar el trabajo de hoy.

El fichero (`progress/gates/ALCANCE.json`) es de sesion y esta gitignorado.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ALCANCE = RAIZ / "progress/gates/ALCANCE.json"


def ahora():
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(momento):
    return momento.isoformat().replace("+00:00", "Z")


def fin_del_dia():
    """Local, no UTC: el dia de trabajo del usuario acaba cuando acaba aqui."""
    local = datetime.now().astimezone()
    return local.replace(hour=23, minute=59, second=59, microsecond=0)


def carga():
    try:
        return json.loads(ALCANCE.read_text(encoding="utf-8"))
    except Exception:
        return None


def guarda(datos):
    ALCANCE.parent.mkdir(parents=True, exist_ok=True)
    tmp = ALCANCE.with_suffix(f".json.tmp{os.getpid()}")
    tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, ALCANCE)


def caducado(datos):
    try:
        limite = datetime.fromisoformat((datos.get("caduca") or "").replace("Z", "+00:00"))
    except ValueError:
        return False
    if limite.tzinfo is None:
        limite = limite.replace(tzinfo=timezone.utc)
    return limite < ahora()


def pinta(datos):
    if not datos:
        print("Sin alcance declarado: no se bloquea ninguna web.")
        print('Declararlo:  python3 tools/alcance.py <slug> [<slug>...] --tarea "<que se hace>"')
        return
    estado = "CADUCADO (no bloquea)" if caducado(datos) else "vigente"
    print(f"Alcance {estado}")
    print(f"  webs   : {', '.join(datos.get('webs', [])) or '(ninguna)'}")
    print(f"  tarea  : {datos.get('tarea') or '(sin describir)'}")
    print(f"  creado : {datos.get('creado')}   caduca: {datos.get('caduca')}")
    print(f"  quien  : {datos.get('quien')}")


def main():
    p = argparse.ArgumentParser(
        description="Declara que webs se pueden tocar en esta tarea.",
        epilog='Ejemplos:\n'
               '  python3 tools/alcance.py proyecto-a --tarea "footer de proyecto-a"\n'
               '  python3 tools/alcance.py --anadir proyecto-b\n'
               '  python3 tools/alcance.py --ver\n'
               '  python3 tools/alcance.py --quitar',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("slugs", nargs="*", help="webs autorizadas para esta tarea")
    p.add_argument("--tarea", default="", help="que se esta haciendo (queda escrito)")
    p.add_argument("--quien", default=os.environ.get("CLAUDECLAW_VENTANA", "sesion Claude Code"))
    p.add_argument("--anadir", metavar="SLUG", action="append", default=[],
                   help="amplia el alcance vigente sin rehacerlo")
    p.add_argument("--quitar", action="store_true", help="borra el alcance (deja de bloquear)")
    p.add_argument("--ver", action="store_true", help="imprime el alcance vigente")
    args = p.parse_args()

    if args.ver:
        pinta(carga())
        return 0

    if args.quitar:
        if ALCANCE.exists():
            ALCANCE.unlink()
            print("Alcance borrado: ya no se bloquea ninguna web.")
        else:
            print("No habia alcance declarado.")
        return 0

    if args.anadir:
        datos = carga()
        if not datos or caducado(datos):
            print("No hay alcance vigente que ampliar. Declaralo entero:", file=sys.stderr)
            print('  python3 tools/alcance.py <slug> [<slug>...] --tarea "<que se hace>"',
                  file=sys.stderr)
            return 2
        for slug in args.anadir:
            if slug not in datos["webs"]:
                datos["webs"].append(slug)
        datos["ampliado"] = iso(ahora())
        guarda(datos)
        pinta(datos)
        return 0

    if not args.slugs:
        p.print_help()
        return 2

    datos = {
        "esquema": 1,
        "tarea": args.tarea,
        "webs": list(dict.fromkeys(args.slugs)),
        "creado": iso(ahora()),
        "caduca": fin_del_dia().isoformat(),
        "quien": args.quien,
    }
    guarda(datos)
    pinta(datos)
    print("\nA partir de ahora, escribir en cualquier otra web queda BLOQUEADO.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
