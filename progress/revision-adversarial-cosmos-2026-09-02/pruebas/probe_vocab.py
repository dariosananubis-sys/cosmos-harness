import json, sys, pathlib
sys.path.insert(0,"/Users/<usuario>/cosmos")
from cosmos.acertar import _normalizar
def resumenes(base):
    d={}
    for f in pathlib.Path(base,"galaxia/sistemas").glob("*.md"):
        for l in f.read_text().splitlines():
            if l.startswith("resumen:"): d[f.stem]=l[8:].strip(); break
    return d
ra,rb = resumenes("/tmp/advcosmos/mix"), resumenes("/Users/<usuario>/cosmos")
anadidas=set()
for s in rb:
    anadidas |= (set(_normalizar(rb[s])) - set(_normalizar(ra.get(s,""))))
aj = set(); 
for e in json.load(open("pruebas/encargos.json")): aj |= set(_normalizar(e["peticion"]))
va = set()
for e in json.load(open("pruebas/encargos-validacion.json")): va |= set(_normalizar(e["peticion"]))
print("palabras nuevas en los 21 resumenes:", len(anadidas))
print("  de ellas, en el vocabulario de VALIDACION :", len(anadidas & va), sorted(anadidas & va))
print("  de ellas, en el vocabulario de AJUSTE     :", len(anadidas & aj), sorted(anadidas & aj))
print("  en validacion y NO en ajuste              :", len(anadidas & va - aj), sorted(anadidas & va - aj))
print("  en ninguno de los dos                     :", len(anadidas - va - aj), sorted(anadidas - va - aj))
print()
print("tamano vocabularios: ajuste", len(aj), "validacion", len(va))
