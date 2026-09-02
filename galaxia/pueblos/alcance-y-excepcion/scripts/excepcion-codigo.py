#!/usr/bin/env python3
"""Pase de 24 h para tocar codigo en una web, con el motivo escrito.

Por que existe: el guardia `guard-web-sin-codigo.py` bloquea meter codigo a medida
en una web de cliente, y esta bien que lo haga. Pero hace falta poder BORRAR el
codigo heredado que ya esta dentro (los widgets `html` del mockup, el CSS del
Customizer, un mu-plugin viejo), y para eso hay que ejecutar comandos que el
guardia ve iguales que los de meterlo. Sin valvula, el guardia acabaria desactivado
a martillazos, que es como mueren los controles que no dejan trabajar.

    python3 tools/excepcion-codigo.py <slug> "Quitar el bloque legacy" \\
        --nativo-descartado "ninguno: esto es para BORRAR codigo, no para anadirlo"

Dos cosas que NO hace, y conviene tenerlas claras:

  - NO hace pasar el gate. `tools/web-gate.py` sigue contando ese codigo como FALLA.
    Quitar el FALLA es otra decision, vive en `webs/excepciones-codigo.json`, dura
    seis meses y la autoriza el humano responsable, no el agente.
  - NO vale sin motivo. `--nativo-descartado` es obligatorio y no puede ir vacio:
    la mitad del valor de esto es que quede escrito que se busco el control nativo
    y por que no servia.

El fichero (`progress/gates/pase-codigo-<slug>.json`) es de sesion y esta gitignorado.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "progress/gates"


def iso(momento):
    return momento.isoformat().replace("+00:00", "Z")


def main():
    p = argparse.ArgumentParser(
        description="Pase de 24 h para que el hook deje tocar codigo en una web.",
        epilog='Ejemplos:\n'
               '  python3 tools/excepcion-codigo.py <slug> "Quitar el switcher heredado" \\\n'
               '      --nativo-descartado "ninguno: es para borrar codigo"\n'
               '  python3 tools/excepcion-codigo.py <slug> --ver\n'
               '  python3 tools/excepcion-codigo.py <slug> --revocar',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("slug", help="web a la que aplica el pase")
    p.add_argument("motivo", nargs="?", default="", help="que se va a hacer y por que")
    p.add_argument("--nativo-descartado", default="",
                   help="que control nativo se probo y por que no sirve (obligatorio)")
    p.add_argument("--horas", type=int, default=24, help="duracion del pase (por defecto 24)")
    p.add_argument("--ver", action="store_true", help="ver el pase vigente de esa web")
    p.add_argument("--revocar", action="store_true", help="borrar el pase")
    args = p.parse_args()

    ruta = CARPETA / f"pase-codigo-{args.slug}.json"

    if args.ver:
        if not ruta.exists():
            print(f"No hay pase de codigo para {args.slug}.")
            return 1
        print(ruta.read_text(encoding="utf-8").strip())
        return 0

    if args.revocar:
        if ruta.exists():
            ruta.unlink()
            print(f"Pase de codigo de {args.slug} revocado.")
            return 0
        print(f"No habia pase de codigo para {args.slug}.")
        return 1

    if not args.motivo.strip():
        print("Falta el motivo. Un pase sin motivo escrito no vale para nada:", file=sys.stderr)
        print(f'  python3 tools/excepcion-codigo.py {args.slug} "<motivo>" '
              '--nativo-descartado "<que probaste>"', file=sys.stderr)
        return 2
    if not args.nativo_descartado.strip():
        print("Falta --nativo-descartado. Es obligatorio: hay que dejar escrito que control",
              file=sys.stderr)
        print("nativo se probo y por que no sirve. Si es para BORRAR codigo, ponlo tal cual.",
              file=sys.stderr)
        return 2

    ahora = datetime.now(timezone.utc).replace(microsecond=0)
    datos = {
        "esquema": 1,
        "slug": args.slug,
        "motivo": args.motivo.strip(),
        "nativo_descartado": args.nativo_descartado.strip(),
        "creado": iso(ahora),
        "caduca": iso(ahora + timedelta(hours=args.horas)),
        "quien": os.environ.get("CLAUDECLAW_VENTANA", "sesion Claude Code"),
    }
    CARPETA.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_suffix(f".json.tmp{os.getpid()}")
    tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, ruta)

    print(f"Pase de codigo creado para {args.slug}, caduca {datos['caduca']} ({args.horas} h).")
    print(f"  motivo            : {datos['motivo']}")
    print(f"  nativo descartado : {datos['nativo_descartado']}")
    print("\nEsto SOLO abre el hook. El gate de salida sigue contando ese codigo como FALLA:")
    print("  para quitar el FALLA hace falta una excepcion en webs/excepciones-codigo.json,")
    print("  que dura 6 meses y la autoriza el humano responsable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
