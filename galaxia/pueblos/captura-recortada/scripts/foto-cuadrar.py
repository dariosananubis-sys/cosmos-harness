#!/usr/bin/env python3
"""Re-encuadra una foto de producto a lienzo cuadrado sin costura visible.

El relleno lateral se muestrea del FONDO REAL de cada fila (mediana recortada de
las columnas del borde), se valida contra la tendencia vertical para descartar las
filas donde la figura toca el borde, y se extiende hacia fuera continuando la
pendiente horizontal amortiguada. Así el color coincide exacto en la junta y no
aparece ni linea blanca ni banda de tono distinto.
"""
import sys
from PIL import Image


def mediana(vs):
    vs = sorted(vs)
    n = len(vs)
    return (vs[n // 2] if n % 2 else (vs[n // 2 - 1] + vs[n // 2]) / 2)


def muestrear_borde(px, h, xs):
    """Color mediano del fondo por fila en la banda de columnas xs."""
    return [tuple(mediana([px[x, y][c] for x in xs]) for c in range(3)) for y in range(h)]


def tendencia(raw, ventana=25):
    h = len(raw)
    out = []
    for y in range(h):
        y0, y1 = max(0, y - ventana), min(h, y + ventana + 1)
        out.append(tuple(mediana([raw[k][c] for k in range(y0, y1)]) for c in range(3)))
    return out


def limpiar(raw, umbral=8.0):
    """Sustituye por la tendencia las filas contaminadas por la figura."""
    tr = tendencia(raw)
    fuera = [y for y in range(len(raw))
             if max(abs(raw[y][c] - tr[y][c]) for c in range(3)) > umbral]
    lim = [tr[y] if y in set(fuera) else raw[y] for y in range(len(raw))]
    return lim, fuera


def suavizar(vals, ventana=9):
    h = len(vals)
    out = []
    for y in range(h):
        y0, y1 = max(0, y - ventana), min(h, y + ventana + 1)
        n = y1 - y0
        out.append(tuple(sum(vals[k][c] for k in range(y0, y1)) / n for c in range(3)))
    return out


def pendiente(px, h, xs, hacia_fuera):
    """Pendiente horizontal por fila (unidades/px) en la banda, robustecida."""
    xs = list(xs)
    x0, x1 = xs[0], xs[-1]
    span = x1 - x0
    out = []
    for y in range(h):
        s = []
        for c in range(3):
            a = mediana([px[x, y][c] for x in xs[:6]])
            b = mediana([px[x, y][c] for x in xs[-6:]])
            m = (b - a) / span            # variacion segun x creciente
            s.append(m * hacia_fuera)     # signo hacia el exterior del lienzo
        out.append(tuple(s))
    return out


def cuadrar(entrada, salida, recorte_izq=0, modo="centrado", calidad=93):
    im = Image.open(entrada).convert("RGB")
    if recorte_izq:
        im = im.crop((recorte_izq, 0, im.size[0], im.size[1]))
    w, h = im.size
    px = im.load()
    lado = max(w, h)
    total = lado - w
    if modo == "centrado":
        pad_izq = total // 2
    elif modo == "derecha":          # todo el relleno a la derecha
        pad_izq = 0
    else:
        raise SystemExit("modo desconocido")
    pad_der = total - pad_izq

    lienzo = Image.new("RGB", (lado, lado), (255, 255, 255))
    lienzo.paste(im, (pad_izq, (lado - h) // 2))
    lp = lienzo.load()
    dy = (lado - h) // 2

    informe = {}
    for lado_nombre, ancho in (("izq", pad_izq), ("der", pad_der)):
        if ancho <= 0:
            continue
        if lado_nombre == "izq":
            xs = range(0, 10)
            slope = pendiente(px, h, range(0, 34), hacia_fuera=-1)
        else:
            xs = range(w - 10, w)
            slope = pendiente(px, h, range(w - 34, w), hacia_fuera=+1)
        raw = muestrear_borde(px, h, xs)
        lim, contaminadas = limpiar(raw)
        col = suavizar(lim)
        informe[lado_nombre] = len(contaminadas)
        borde_x = 0 if lado_nombre == "izq" else w - 1
        FUNDIDO = 8   # 12 dejaba estela visible; 8 remata la punta sin rastro
        for y in range(h):
            base = col[y]
            m = slope[y]
            # si la figura llega al borde de la foto (p.ej. la punta del zapato),
            # un corte seco canta; se funde en 12 px hacia el fondo de esa fila.
            borde = px[borde_x, y]
            corta = max(abs(borde[c] - base[c]) for c in range(3)) > 10
            for d in range(1, ancho + 1):
                # continua el degradado horizontal, pero con deriva acotada:
                # sin tope la extrapolacion se dispara a blanco en 90 px.
                deriva = tuple(max(-4.0, min(4.0, m[c] * min(d, 40))) for c in range(3))
                px_col = tuple(
                    max(0, min(255, int(round(base[c] + deriva[c]))))
                    for c in range(3)
                )
                if corta and d <= FUNDIDO:
                    t = d / (FUNDIDO + 1.0)
                    t = t * t * (3 - 2 * t)          # smoothstep
                    px_col = tuple(
                        max(0, min(255, int(round(borde[c] * (1 - t) + px_col[c] * t))))
                        for c in range(3)
                    )
                x = (pad_izq - d) if lado_nombre == "izq" else (pad_izq + w - 1 + d)
                lp[x, y + dy] = px_col
        # tapa las filas del lienzo por encima/debajo si hubiera (aqui no hay)
    # bandas superior/inferior no aplican: h == lado
    lienzo.save(salida, "JPEG", quality=calidad, subsampling=0, optimize=True)
    return lienzo.size, informe


AYUDA = """Uso: foto-cuadrar.py <entrada.jpg> <salida.jpg> [recorte_izq] [modo]

  recorte_izq  columnas a tirar por la izquierda antes de cuadrar (artefactos de
               escaneo: banda blanca/dorada). 0 por defecto.
  modo         centrado (por defecto) | derecha

Cuando usar cada modo:
  centrado  la figura NO toca ningun borde lateral -> relleno simetrico.
  derecha   la figura toca el borde izquierdo (se veria cortada flotando):
            todo el relleno va a la derecha y el corte queda pegado al borde
            del lienzo, como en la foto original.

Comprueba siempre despues:
  salto en la junta y salto vertical dentro del relleno <= 10/255 (invisible).
"""

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print(AYUDA)
        raise SystemExit(0)
    ent, sal = sys.argv[1], sys.argv[2]
    rec = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    modo = sys.argv[4] if len(sys.argv) > 4 else "centrado"
    tam, filas = cuadrar(ent, sal, rec, modo)
    print(f"{sal}: {tam[0]}x{tam[1]} | filas con figura en el borde: {filas}")
