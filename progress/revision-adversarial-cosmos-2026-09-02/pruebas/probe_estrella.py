"""PRUEBA ADVERSARIAL 2: la estrella, ¿solo por ruta completa?"""
import sys; sys.path.insert(0, '/Users/<usuario>/cosmos')
from pathlib import Path
from tempfile import TemporaryDirectory
from cosmos.abrir import abrir
from cosmos.modelo import cargar_arbol

def esc(base, ruta, fm, cuerpo=""):
    d = base/ruta; d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text("---\n"+"\n".join(f"{k}: {v}" for k,v in fm.items())+"\n---\n\n"+cuerpo+"\n", encoding="utf-8")

with TemporaryDirectory() as t:
    b = Path(t)
    esc(b,"galaxia.md",{"cosmos":"galaxia","nombre":"t","resumen":"Arbol de prueba adversarial."})
    esc(b,"sistemas/web.md",{"cosmos":"sistema-solar","nombre":"web","padre":'""',"resumen":"Sitios que cargan."},"cuerpo web")
    esc(b,"paises/web--calidad.md",{"cosmos":"pais","nombre":"calidad","padre":"web","resumen":"Que no se rompa al soltarlo."},"cuerpo pais calidad")
    # estrella que ilumina el NOMBRE suelto 'calidad', no la ruta 'web/calidad'
    esc(b,"estrellas/calidad.md",{"cosmos":"estrella","nombre":"calidad","ilumina":"calidad","resumen":"Lo cierto en calidad."},"NO DEBERIA ENGANCHARSE")
    a = cargar_arbol(b)
    ap = abrir(a,"web/calidad")
    print("A) ilumina='calidad' vs nodo referencia 'web/calidad' -> estrella:", None if ap.estrella is None else ap.estrella.nombre)
    print("   referencia real del pais:", [n.referencia for n in a.nodos if n.cosmos=='pais'])

with TemporaryDirectory() as t:
    b = Path(t)
    esc(b,"galaxia.md",{"cosmos":"galaxia","nombre":"t","resumen":"Arbol de prueba adversarial."})
    esc(b,"sistemas/web.md",{"cosmos":"sistema-solar","nombre":"web","padre":'""',"resumen":"Sitios que cargan."},"cuerpo web")
    esc(b,"sistemas/movil.md",{"cosmos":"sistema-solar","nombre":"movil","padre":'""',"resumen":"Apps que caben en la mano."},"cuerpo movil")
    esc(b,"paises/web--calidad.md",{"cosmos":"pais","nombre":"calidad","padre":"web","resumen":"Que no se rompa al soltarlo."},"c1")
    esc(b,"paises/movil--calidad.md",{"cosmos":"pais","nombre":"calidad","padre":"movil","resumen":"Que no se caiga en la mano."},"c2")
    esc(b,"estrellas/calidad.md",{"cosmos":"estrella","nombre":"calidad","ilumina":"web/calidad","resumen":"Lo cierto en calidad web."},"ESTRELLA DE WEB")
    a = cargar_arbol(b)
    for r in ("web/calidad","movil/calidad"):
        ap = abrir(a,r)
        print(f"B) abrir {r} -> estrella:", None if ap.estrella is None else ap.estrella.nombre)
