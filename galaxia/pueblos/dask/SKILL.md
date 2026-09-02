---
cosmos: pueblo
nombre: dask
padre: cientifico
resumen: Paraleliza con la interfaz de siempre y no reserva memoria por adelantado al arrancar.
---

https://github.com/dask/dask · BSD-3-Clause · 13.910★ · último push 2026-08-24 (comprobado por API de GitHub el 2026-09-01).

```bash
pip install "dask[complete]"
```

```python
import dask.dataframe as dd
from dask.distributed import Client

cliente = Client(n_workers=2, threads_per_worker=2, memory_limit="2GB")
print(cliente.dashboard_link)          # http://127.0.0.1:8787/status

df = dd.read_parquet("datos/*.parquet")           # no lee nada todavia
resumen = df.groupby("categoria").importe.mean()  # sigue sin leer
print(resumen.compute())                          # aqui ejecuta, por trozos
```

Se prefiere a `ray-project/ray` (43,7k estrellas, Apache-2.0, mucho mas popular) por una razon
medible en esta maquina concreta: Ray aparta por defecto cerca de un tercio de la memoria de la
maquina para su almacen de objetos nada mas arrancar, que en 8 GB es agresivo; Dask no reserva nada
por adelantado y baja de escala sin friccion. Para un grupo de maquinas de verdad y para el
ecosistema de aprendizaje distribuido, Ray sigue siendo la eleccion correcta. Y frente a `joblib`,
que es mas ligero todavia: si el trabajo es vergonzosamente paralelo en un solo proceso, `joblib`
sobra y Dask estorba.

Y lo que no hace bien: la interfaz es la de siempre, pero el comportamiento no. `df.compute()` trae
el resultado entero a memoria — un `compute()` sobre algo que no cabe mata el proceso igual que
`pandas`, solo que despues de una hora de trabajo. Y el particionado importa: `read_parquet` sobre
un unico fichero grande crea una sola particion y el paralelismo no existe, sin ningun aviso.

Aviso de maquina: por defecto arranca tantos procesos como nucleos, cada uno con su copia del
interprete. En un Mac de 8 GB conviene fijar `n_workers` y `memory_limit` a mano, como arriba, en vez
de dejar el automatico.
