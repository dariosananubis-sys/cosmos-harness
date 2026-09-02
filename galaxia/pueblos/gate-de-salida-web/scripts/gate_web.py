#!/usr/bin/env python3
"""Gate de salida de un sitio: el unico artefacto que dice PASA o FALLA. Mide, no arregla.

La regla que lo distingue de un guion de comprobaciones cualquiera:

    una comprobacion que NO se pudo ejecutar sale como `no_medido`
    y NO cuenta como aprobada.

Sin eso, cada capa que no corre —el navegador no esta, la referencia no se dio,
el sitio no responde— se lee como verde y el informe sale entero y es mentira.
Aqui `no_medido` en una comprobacion critica impide el PASA igual que un fallo.

La comparacion de PIXELES contra la referencia es critica a proposito: las sondas
de DOM solo cazan lo que a alguien se le ocurrio medir, y los defectos que canta
un cliente —«descuadrado», «movido», «el texto no acompana a la caja»— caen fuera
de esa lista. Sin referencia no hay PASA, y se dice por que.

Uso:

    python3 gate_web.py https://sitio.example --paginas / /contacto
    python3 gate_web.py https://sitio.example --referencia https://maqueta.example \
        --anchos 1440 390 --informe informe.json

Salida: 0 = PASA · 1 = FALLA. El informe JSON queda escrito y es la prueba.

Necesita `agent-browser` para las capas de render y `Pillow` para los pixeles.
Si falta cualquiera de los dos lo dice y esa capa queda `no_medido`, nunca en verde.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PASA, FALLA, NO_MEDIDO = "pasa", "falla", "no_medido"

SONDA_DOM = """(() => {
  const vis = e => { if (!e) return false; const r = e.getBoundingClientRect();
    const s = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && s.display !== 'none' &&
           s.visibility !== 'hidden' && e.offsetParent !== null; };
  const raiz = document.documentElement;
  return JSON.stringify({
    scrollWidth: raiz.scrollWidth,
    clientWidth: raiz.clientWidth,
    h1Visibles: [...document.querySelectorAll('h1')].filter(vis).length,
    imgsRotas: [...document.images].filter(i => i.complete && i.naturalWidth === 0).length,
    enlacesVacios: [...document.querySelectorAll('a[href=""],a[href="#"]')].length,
    textoVisible: (document.body.innerText || '').trim().length
  });
})()"""


def nav(sesion: str, *args: str, tiempo: int = 90) -> tuple[int, str]:
    try:
        p = subprocess.run(["agent-browser", "--session", sesion, *args],
                           capture_output=True, text=True, timeout=tiempo)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, str(exc)


class Informe:
    def __init__(self) -> None:
        self.filas: list[dict] = []

    def anota(self, codigo: str, estado: str, critica: bool, detalle: str = "") -> None:
        self.filas.append({"codigo": codigo, "estado": estado,
                           "critica": critica, "detalle": detalle})

    @property
    def veredicto(self) -> str:
        # no_medido en una critica pesa exactamente igual que un fallo.
        malas = [f for f in self.filas if f["critica"] and f["estado"] != PASA]
        return "FALLA" if malas else "PASA"


def http(url: str) -> tuple[int | None, str]:
    peticion = urllib.request.Request(url, headers={"User-Agent": "gate-web/1"})
    try:
        with urllib.request.urlopen(peticion, timeout=20) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as exc:  # DNS, TLS, red cortada: no es un 500, es no haber mirado
        return None, f"{type(exc).__name__}: {exc}"


def capa_http(inf: Informe, base: str, paginas: list[str]) -> None:
    fallos, sin_medir = [], []
    for pagina in paginas:
        url = base.rstrip("/") + "/" + pagina.lstrip("/")
        codigo, error = http(url)
        if codigo is None:
            sin_medir.append(f"{pagina} ({error})")
        elif codigo >= 400:
            fallos.append(f"{pagina} -> {codigo}")
    if fallos:
        inf.anota("C1-http", FALLA, True, "; ".join(fallos))
    elif sin_medir:
        inf.anota("C1-http", NO_MEDIDO, True, "; ".join(sin_medir))
    else:
        inf.anota("C1-http", PASA, True, f"{len(paginas)} paginas responden")


def capa_dom(inf: Informe, sesion: str, base: str, paginas: list[str], anchos: list[int]) -> None:
    if shutil.which("agent-browser") is None:
        for codigo in ("C2-desborde", "C3-un-h1", "C4-imagenes", "C5-contenido"):
            inf.anota(codigo, NO_MEDIDO, True, "agent-browser no esta instalado")
        return
    desborde, h1, imgs, vacias = [], [], [], []
    medido = False
    for pagina in paginas:
        url = base.rstrip("/") + "/" + pagina.lstrip("/")
        for ancho in anchos:
            nav(sesion, "open", url)
            nav(sesion, "set", "viewport", str(ancho), "900")
            nav(sesion, "open", url)
            rc, salida = nav(sesion, "eval", SONDA_DOM)
            datos = None
            for linea in reversed(salida.splitlines()):
                linea = linea.strip().strip('"').replace('\\"', '"')
                if linea.startswith("{"):
                    try:
                        datos = json.loads(linea)
                        break
                    except ValueError:
                        continue
            if rc != 0 or not datos:
                continue
            medido = True
            etiqueta = f"{pagina}@{ancho}"
            if datos["scrollWidth"] > datos["clientWidth"] + 2:
                desborde.append(f"{etiqueta} sw={datos['scrollWidth']} cw={datos['clientWidth']}")
            if datos["h1Visibles"] != 1:
                h1.append(f"{etiqueta} h1={datos['h1Visibles']}")
            if datos["imgsRotas"]:
                imgs.append(f"{etiqueta} rotas={datos['imgsRotas']}")
            if datos["textoVisible"] < 200:
                vacias.append(f"{etiqueta} texto={datos['textoVisible']}")
    nav(sesion, "close")
    if not medido:
        for codigo in ("C2-desborde", "C3-un-h1", "C4-imagenes", "C5-contenido"):
            inf.anota(codigo, NO_MEDIDO, True, "el navegador no devolvio ninguna medicion")
        return
    for codigo, malos, texto in (
        ("C2-desborde", desborde, "desborde horizontal"),
        ("C3-un-h1", h1, "no hay exactamente un h1 visible"),
        ("C4-imagenes", imgs, "imagenes que no cargan"),
        ("C5-contenido", vacias, "pagina practicamente vacia"),
    ):
        inf.anota(codigo, FALLA if malos else PASA, True,
                  f"{texto}: {'; '.join(malos)}" if malos else "")


def capa_pixeles(inf: Informe, sesion: str, base: str, referencia: str | None,
                 paginas: list[str], anchos: list[int], salida: Path, umbral: float) -> None:
    if not referencia:
        inf.anota("C6-pixeles", NO_MEDIDO, True,
                  "no se dio --referencia: sin comparar contra la maqueta no hay PASA")
        return
    try:
        from PIL import Image, ImageChops
    except ImportError:
        inf.anota("C6-pixeles", NO_MEDIDO, True, "falta Pillow")
        return
    if shutil.which("agent-browser") is None:
        inf.anota("C6-pixeles", NO_MEDIDO, True, "agent-browser no esta instalado")
        return

    salida.mkdir(parents=True, exist_ok=True)
    peores: list[str] = []
    medido = False
    for pagina in paginas:
        for ancho in anchos:
            fotos = []
            for etiqueta, raiz in (("wp", base), ("ref", referencia)):
                url = raiz.rstrip("/") + "/" + pagina.lstrip("/")
                destino = salida / f"{pagina.strip('/') or 'home'}-{ancho}-{etiqueta}.png"
                nav(sesion, "open", url)
                nav(sesion, "set", "viewport", str(ancho), "900")
                nav(sesion, "open", url)
                rc, _ = nav(sesion, "screenshot", str(destino), "--full", tiempo=120)
                if rc != 0 or not destino.exists():
                    rc, _ = nav(sesion, "screenshot", str(destino), tiempo=120)
                fotos.append(destino if destino.exists() else None)
            if not all(fotos):
                continue
            medido = True
            a = Image.open(fotos[0]).convert("RGB")
            b = Image.open(fotos[1]).convert("RGB")
            alto = min(a.height, b.height)
            a, b = a.crop((0, 0, ancho, alto)), b.crop((0, 0, ancho, alto))
            dif = ImageChops.difference(a, b).convert("L")
            # Franjas de 40 px: dice DONDE difiere, no solo cuanto.
            franjas = []
            for y in range(0, alto, 40):
                trozo = dif.crop((0, y, ancho, min(y + 40, alto)))
                datos_franja = getattr(trozo, "get_flattened_data", trozo.getdata)
                pixeles = list(datos_franja())
                distintos = sum(1 for v in pixeles if v > 24) / max(len(pixeles), 1)
                if distintos > umbral:
                    franjas.append(f"y={y} ({distintos:.0%})")
            if franjas:
                peores.append(f"{pagina}@{ancho}: " + ", ".join(franjas[:6]))
    nav(sesion, "close")
    if not medido:
        inf.anota("C6-pixeles", NO_MEDIDO, True, "no se pudo capturar ninguna pareja de imagenes")
    elif peores:
        inf.anota("C6-pixeles", FALLA, True, "franjas que difieren -> " + " | ".join(peores))
    else:
        inf.anota("C6-pixeles", PASA, True, f"capturas en {salida}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base", help="URL raiz del sitio a juzgar")
    ap.add_argument("--referencia", help="URL de la maqueta contra la que comparar pixeles")
    ap.add_argument("--paginas", nargs="+", default=["/"])
    ap.add_argument("--anchos", nargs="+", type=int, default=[1440, 390])
    ap.add_argument("--sesion", default="gate-web")
    ap.add_argument("--umbral", type=float, default=0.06,
                    help="fraccion de pixeles distintos que hace mala una franja")
    ap.add_argument("--capturas", type=Path, default=Path(tempfile.gettempdir()) / "gate-web")
    ap.add_argument("--informe", type=Path)
    ap.add_argument("--sin-pixeles", action="store_true",
                    help="declara a proposito que hoy no se compara: sigue sin poder PASAR")
    args = ap.parse_args(argv)

    inf = Informe()
    capa_http(inf, args.base, args.paginas)
    capa_dom(inf, args.sesion, args.base, args.paginas, args.anchos)
    if args.sin_pixeles:
        inf.anota("C6-pixeles", NO_MEDIDO, True, "desactivada a mano con --sin-pixeles")
    else:
        capa_pixeles(inf, args.sesion, args.base, args.referencia,
                     args.paginas, args.anchos, args.capturas, args.umbral)

    documento = {
        "cuando": datetime.now(timezone.utc).isoformat(),
        "base": args.base,
        "referencia": args.referencia,
        "veredicto": inf.veredicto,
        "comprobaciones": inf.filas,
    }
    if args.informe:
        args.informe.parent.mkdir(parents=True, exist_ok=True)
        args.informe.write_text(json.dumps(documento, ensure_ascii=False, indent=2), encoding="utf-8")

    ancho_cod = max(len(f["codigo"]) for f in inf.filas)
    for fila in inf.filas:
        marca = {PASA: "  ok  ", FALLA: " FALLA", NO_MEDIDO: " ?????"}[fila["estado"]]
        print(f"{marca}  {fila['codigo']:<{ancho_cod}}  {fila['detalle']}".rstrip())
    sin_medir = [f["codigo"] for f in inf.filas if f["estado"] == NO_MEDIDO]
    print(f"\n{inf.veredicto}", end="")
    if sin_medir:
        print(f" — {len(sin_medir)} sin medir ({', '.join(sin_medir)}); "
              "sin medir NO es aprobado", end="")
    print()
    return 0 if inf.veredicto == "PASA" else 1


if __name__ == "__main__":
    raise SystemExit(main())
