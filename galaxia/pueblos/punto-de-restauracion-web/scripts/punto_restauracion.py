#!/usr/bin/env python3
"""Punto de restauracion del maquetado de un WordPress con Elementor, por wp-cli.

Sin esto, un cambio que empeora una pagina se queda ahi: el maquetado vive en el
postmeta `_elementor_data`, no en ficheros, asi que no hay `git checkout` que valga
y la copia de la base de datos entera es demasiado cara para hacerla antes de cada
retoque. Esto guarda solo lo que se va a tocar y lo devuelve.

    punto_restauracion.py guardar   --wp "wp --path=/ruta/al/wordpress"
    punto_restauracion.py listar
    punto_restauracion.py restaurar --wp "wp --path=/ruta/al/wordpress"
    punto_restauracion.py restaurar --wp "..." --punto 20260902-1030
    punto_restauracion.py autotest        # ejercita el ciclo con un wp de mentira

`--wp` es el prefijo entero, asi que vale igual en local, por SSH
(`--wp "ssh usuario@servidor wp --path=/ruta"`) o dentro de un contenedor.

Dos cosas que casi nadie hace y son justo las que rompen la restauracion:

1. **Vaciar el CSS generado.** Elementor compila cada pagina a un CSS en disco. Si
   restauras el postmeta y no lo vacias, el sitio sigue sirviendo el CSS viejo y
   parece que la restauracion no ha hecho nada — se pierde media hora buscando un
   fallo que no existe. Por eso `restaurar` termina siempre vaciandolo.
2. **`wp_slash` al escribir.** El maquetado es JSON con barras invertidas dentro.
   `update_post_meta` sin `wp_slash` se las come y Elementor abre la pagina en
   blanco. Se escribe por `wp eval` con el valor en base64 para no pelearse ademas
   con el escapado del shell.
"""
from __future__ import annotations

import argparse
import base64
import json
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CLAVES = ("_elementor_data", "_elementor_page_settings")


def wp(prefijo: list[str], *args: str) -> tuple[int, str]:
    p = subprocess.run([*prefijo, *args], capture_output=True, text=True)
    return p.returncode, (p.stdout or "").strip() or (p.stderr or "").strip()


def ids_con_elementor(prefijo: list[str]) -> list[str]:
    rc, salida = wp(prefijo, "post", "list", "--post_type=any", "--post_status=any",
                    "--meta_key=_elementor_edit_mode", "--format=ids")
    if rc != 0:
        raise SystemExit(f"wp-cli fallo al listar: {salida}")
    return [x for x in salida.split() if x.strip()]


def cmd_guardar(args: argparse.Namespace) -> int:
    prefijo = shlex.split(args.wp)
    ids = ids_con_elementor(prefijo)
    if not ids:
        print("nada que guardar: ninguna entrada usa Elementor")
        return 1
    punto = {"cuando": datetime.now().isoformat(timespec="seconds"), "entradas": {}}
    for pid in ids:
        fila = {}
        for clave in CLAVES:
            rc, valor = wp(prefijo, "post", "meta", "get", pid, clave)
            fila[clave] = valor if rc == 0 else None
        punto["entradas"][pid] = fila
    args.estado.mkdir(parents=True, exist_ok=True)
    destino = args.estado / f"{datetime.now():%Y%m%d-%H%M}.json"
    destino.write_text(json.dumps(punto, ensure_ascii=False), encoding="utf-8")
    print(f"punto {destino.stem}: {len(ids)} entradas guardadas en {destino}")
    return 0


def puntos(estado: Path) -> list[Path]:
    return sorted(estado.glob("*.json"))


def cmd_listar(args: argparse.Namespace) -> int:
    filas = puntos(args.estado)
    if not filas:
        print(f"sin puntos en {args.estado}")
        return 1
    for f in filas:
        try:
            datos = json.loads(f.read_text(encoding="utf-8"))
            print(f"  {f.stem}  {len(datos.get('entradas', {}))} entradas  {datos.get('cuando','')}")
        except ValueError:
            print(f"  {f.stem}  ILEGIBLE")
    return 0


def cmd_restaurar(args: argparse.Namespace) -> int:
    filas = puntos(args.estado)
    if args.punto:
        filas = [f for f in filas if f.stem == args.punto]
    if not filas:
        print("no hay punto que restaurar", file=sys.stderr)
        return 1
    origen = filas[-1]
    datos = json.loads(origen.read_text(encoding="utf-8"))
    prefijo = shlex.split(args.wp)
    escritas = 0
    for pid, fila in datos["entradas"].items():
        for clave, valor in fila.items():
            if valor is None:
                continue
            codificado = base64.b64encode(valor.encode("utf-8")).decode("ascii")
            php = (f'update_post_meta({int(pid)}, "{clave}", '
                   f'wp_slash(base64_decode("{codificado}")));')
            if args.simular:
                print(f"wp eval {php[:60]}...")
            else:
                rc, salida = wp(prefijo, "eval", php)
                if rc != 0:
                    print(f"  fallo en {pid}/{clave}: {salida}", file=sys.stderr)
                    return 1
            escritas += 1
    # El paso que casi todo el mundo se salta. Sin esto la web se ve igual que antes.
    vaciado = vaciar_css(prefijo, list(datos["entradas"]), args.simular)
    print(f"restaurado {origen.stem}: {escritas} valores · CSS generado: {vaciado}")
    return 0


def vaciar_css(prefijo: list[str], ids: list[str], simular: bool) -> str:
    if simular:
        print("wp elementor flush-css")
        return "simulado"
    rc, salida = wp(prefijo, "elementor", "flush-css")
    if rc == 0:
        return "vaciado con `elementor flush-css`"
    # Sin el comando de Elementor disponible, se borra el meta a mano: es lo mismo.
    for pid in ids:
        wp(prefijo, "post", "meta", "delete", pid, "_elementor_css")
    return f"`elementor flush-css` no disponible ({salida[:60]}); borrado _elementor_css a mano"


def autotest() -> int:
    """Ejercita el ciclo con un `wp` de mentira que graba lo que se le pide.

    Se dobla el borde mas externo —el binario— y no la logica: asi el guion que se
    prueba es el mismo que corre de verdad.
    """
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        raiz = Path(tmp)
        falso = raiz / "bin" / "wp"
        falso.parent.mkdir(parents=True)
        falso.write_text(
            "#!/usr/bin/env python3\n"
            "import json, pathlib, sys\n"
            f"reg = pathlib.Path({str(raiz / 'llamadas.log')!r})\n"
            f"alm = pathlib.Path({str(raiz / 'metas.json')!r})\n"
            "a = sys.argv[1:]\n"
            "reg.open('a').write(' '.join(a) + '\\n')\n"
            "m = json.loads(alm.read_text()) if alm.exists() else {}\n"
            "if a[:2] == ['post', 'list']: print('11 12')\n"
            "elif a[:3] == ['post', 'meta', 'get']: print(m.get(a[3] + '/' + a[4], ''))\n"
            "elif a[:1] == ['eval']: sys.exit(0)\n"
            "elif a[:2] == ['elementor', 'flush-css']: print('Done')\n"
            "else: sys.exit(0)\n",
            encoding="utf-8")
        falso.chmod(0o755)
        (raiz / "metas.json").write_text(json.dumps({
            "11/_elementor_data": '[{"id":"a1","settings":{"t":"con \\\\ barra"}}]',
            "11/_elementor_page_settings": '{"padding":"20px"}',
            "12/_elementor_data": '[{"id":"b2"}]',
            "12/_elementor_page_settings": "",
        }), encoding="utf-8")

        estado = raiz / "puntos"
        base = argparse.Namespace(wp=f"{falso}", estado=estado, punto=None, simular=False)
        casos = []
        casos.append(("guardar devuelve 0", cmd_guardar(base) == 0))
        guardado = json.loads(next(iter(puntos(estado))).read_text())
        casos.append(("guarda las dos entradas", set(guardado["entradas"]) == {"11", "12"}))
        casos.append(("conserva la barra invertida",
                      "\\\\" in guardado["entradas"]["11"]["_elementor_data"]))
        casos.append(("listar devuelve 0", cmd_listar(base) == 0))
        casos.append(("restaurar devuelve 0", cmd_restaurar(base) == 0))
        registro = (raiz / "llamadas.log").read_text()
        casos.append(("escribe con wp_slash", "wp_slash" in registro))
        casos.append(("escribe en base64", "base64_decode" in registro))
        casos.append(("vacia el CSS generado", "elementor flush-css" in registro))
        casos.append(("sin punto que restaurar avisa",
                      cmd_restaurar(argparse.Namespace(**{**vars(base), "punto": "no-existe"})) == 1))
        for nombre, ok in casos:
            print(("  ok    " if ok else "  FALLA ") + nombre)
        os.environ.pop("WP_CLI_CACHE_DIR", None)
        return 0 if all(ok for _, ok in casos) else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("orden", choices=("guardar", "listar", "restaurar", "autotest"))
    ap.add_argument("--wp", default="wp", help="prefijo completo de wp-cli")
    ap.add_argument("--estado", type=Path, default=Path(".puntos-elementor"))
    ap.add_argument("--punto", help="identificador de un punto concreto")
    ap.add_argument("--simular", action="store_true", help="enseña los comandos, no escribe")
    args = ap.parse_args(argv)
    return {"guardar": cmd_guardar, "listar": cmd_listar, "restaurar": cmd_restaurar,
            "autotest": lambda _a: autotest()}[args.orden](args)


if __name__ == "__main__":
    raise SystemExit(main())
