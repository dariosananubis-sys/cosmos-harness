"""PRUEBA ADVERSARIAL 10: ¿E17 ve la duplicacion que de verdad se paga siempre?"""
import sys, subprocess, shutil, os
sys.path.insert(0,'/Users/<usuario>/cosmos')
from pathlib import Path
from tempfile import TemporaryDirectory
from cosmos.modelo import cargar_arbol, cargar_configuracion
from cosmos.validar import validar_arbol

FRASE = "Ninguna credencial se escribe nunca dentro de un fichero versionado del repositorio"

def esc(b,r,fm,c=""):
    d=b/r; d.parent.mkdir(parents=True,exist_ok=True)
    d.write_text("---\n"+"\n".join(f"{k}: {v}" for k,v in fm.items())+"\n---\n\n"+c+"\n",encoding="utf-8")

def montar(base, variante):
    esc(base,"galaxia.md",{"cosmos":"galaxia","nombre":"t","resumen":"Arbol para probar el limite de E17."})
    esc(base,"agua/oceano-secretos.md",{"cosmos":"oceano","nombre":"secretos","moja":'["**"]',
        "resumen":"Las credenciales se leen al vuelo y jamas se guardan."}, FRASE + ".")
    if variante == "otro-oceano":
        esc(base,"agua/oceano-custodia.md",{"cosmos":"oceano","nombre":"custodia","moja":'["**"]',
            "resumen":"Datos personales tratados con base legal."}, FRASE + ".")
    if variante == "resumen-de-sistema":
        # El resumen de un sistema viaja en el INDICE, que esta en la entrada SIEMPRE.
        esc(base,"sistemas/web.md",{"cosmos":"sistema-solar","nombre":"web","padre":'""',
            "resumen": FRASE}, "Cuerpo del oficio, distinto de todo lo demas.")
    if variante == "dos-estrellas":
        esc(base,"sistemas/web.md",{"cosmos":"sistema-solar","nombre":"web","padre":'""',"resumen":"Sitios que cargan y convierten."},"cuerpo a")
        esc(base,"sistemas/movil.md",{"cosmos":"sistema-solar","nombre":"movil","padre":'""',"resumen":"Apps que caben en la mano."},"cuerpo b")
        esc(base,"estrellas/web.md",{"cosmos":"estrella","nombre":"web","ilumina":"web","resumen":"Cierto en web."}, FRASE + ".")
        esc(base,"estrellas/movil.md",{"cosmos":"estrella","nombre":"movil","ilumina":"movil","resumen":"Cierto en movil."}, FRASE + ".")

for variante, que_es in [
    ("otro-oceano", "CONTROL: la misma frase en dos oceanos (los dos SIEMPRE cargados)"),
    ("resumen-de-sistema", "la misma frase en un oceano y en el RESUMEN de un oficio (indice: siempre cargado)"),
    ("dos-estrellas", "la misma frase en DOS estrellas (que NUNCA coinciden en contexto)"),
]:
    with TemporaryDirectory() as t:
        b=Path(t); montar(b, variante)
        (b.parent/"x").mkdir(exist_ok=True)
        toml = b.parent/f"c-{variante}.toml"
        toml.write_text(f"[presupuesto]\nentrada = 4000\nresumen = 120\noceanos = 7\ngalaxia_lineas = 40\nsolapamiento = 0.25\n[raiz]\narbol = \"{b}\"\nindice = \"{b}/COSMOS.md\"\n")
        cfg = cargar_configuracion(toml)
        res = validar_arbol(cargar_arbol(b), configuracion=cfg)
        e17 = [e for e in res.errores if e.codigo=="E17"]
        print(f"{variante:20s} {que_es}")
        print(f"                     -> E17 dispara: {'SI' if e17 else 'NO'}  {e17[0].mensaje[:90] if e17 else ''}")
