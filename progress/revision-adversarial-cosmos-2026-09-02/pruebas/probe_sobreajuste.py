"""PRUEBA ADVERSARIAL 5: la mejora de validacion, ¿generaliza o es punteria?"""
import json, subprocess, sys, re, unicodedata

def puntos(raiz):
    out = subprocess.run([sys.executable, "-m", "cosmos", "acertar", "--json"],
                         cwd=raiz, capture_output=True, text=True)
    return json.loads(out.stdout)

antes = puntos("/tmp/advcosmos/mix")        # codigo HEAD + galaxia a4f880e
ahora = puntos("/Users/dariosatino/cosmos") # codigo HEAD + galaxia HEAD

for cual in ("ajuste", "validacion"):
    a, b = antes[cual], ahora[cual]
    print(f"{cual:11s}  antes {a['aciertos']}/{a['total']}   ahora {b['aciertos']}/{b['total']}")
print()
for cual in ("ajuste", "validacion"):
    ra = {r["peticion"]: r for r in antes[cual]["resultados"]}
    rb = {r["peticion"]: r for r in ahora[cual]["resultados"]}
    flip = [p for p in ra if not ra[p]["acierta"] and rb[p]["acierta"]]
    caen = [p for p in ra if ra[p]["acierta"] and not rb[p]["acierta"]]
    print(f"--- {cual}: +{len(flip)} ganados, -{len(caen)} perdidos ---")
    for p in flip:
        print(f"   GANADO  «{p}»  -> {rb[p]['espera']}  (antes {ra[p]['posicion']}º)")
    for p in caen:
        print(f"   PERDIDO «{p}»")
    print()

# Palabras que 8479933 ANADIO a cada resumen de sistema, y su solape con los encargos
sys.path.insert(0, "/Users/dariosatino/cosmos")
from cosmos.acertar import _normalizar
def resumenes(base):
    import pathlib
    d = {}
    for f in pathlib.Path(base, "galaxia/sistemas").glob("*.md"):
        for l in f.read_text().splitlines():
            if l.startswith("resumen:"): d[f.stem] = l[8:].strip(); break
    return d
ra, rb = resumenes("/tmp/advcosmos/mix"), resumenes("/Users/dariosatino/cosmos")
val = json.load(open("/Users/dariosatino/cosmos/pruebas/encargos-validacion.json"))
print("=== palabras ANADIDAS al resumen del sistema esperado que ESTAN en la peticion de validacion ===")
total_lift = 0
for e in val:
    sistema = e["espera"].split("/")[0]
    if sistema not in ra: continue
    nuevas = set(_normalizar(rb[sistema])) - set(_normalizar(ra[sistema]))
    pet = set(_normalizar(e["peticion"]))
    lift = sorted(nuevas & pet)
    if lift:
        total_lift += 1
        print(f"  {sistema:16s} +{lift}   <- «{e['peticion']}»")
print(f"\n  {total_lift}/20 encargos de VALIDACION recibieron palabras suyas en el resumen de su destino.")
