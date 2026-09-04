import sys; sys.path.insert(0,'~/cosmos'); sys.path.insert(0,'~/cosmos/tests')
from tests.test_escala import _entrada_con_un_nicho, PRESUPUESTO
m = {n: _entrada_con_un_nicho(n) for n in (10,40,80)}
print("entradas:", m)
pb=(m[40]-m[10])/30; pa=(m[80]-m[40])/40
print(f"pendiente_baja={pb:.3f}  pendiente_alta={pa:.3f}  (docstring dice 'unos 23 tokens por oficio')")
print(f"  assertGreater(pb,15) -> {pb>15}   assertAlmostEqual(pa,pb,delta=5) -> {abs(pa-pb)<=5}  (|dif|={abs(pa-pb):.3f})")
rot = next((n for n in range(10,301,10) if _entrada_con_un_nicho(n)>PRESUPUESTO), None)
print(f"punto de rotura (paso 10) = {rot}   assertIn(rot, range(100,221)) -> {rot in range(100,221)}")
# grano fino: paso 1 alrededor
fino = next((n for n in range(rot-10, rot+1) if _entrada_con_un_nicho(n)>PRESUPUESTO), None)
print(f"punto de rotura exacto (paso 1) = {fino}")
for n in (100,140,150,160,220):
    print(f"   {n:3d} oficios -> entrada {_entrada_con_un_nicho(n)} tokens")
