---
cosmos: pueblo
nombre: gspread
padre: analitica/hojas
resumen: Lee y escribe hojas de calculo en la nube por su API oficial, como si fueran una tabla mas.
---

https://github.com/burnash/gspread · MIT · 7.506★ · último push 2026-07-30 (comprobado por API de GitHub el 2026-09-01).

```bash
pip install gspread google-auth
```

```python
import gspread

# cuenta de servicio: la ruta de la clave se pasa por variable de entorno, nunca en el codigo
gc = gspread.service_account(filename=os.environ["GOOGLE_SA_KEY_PATH"])

hoja = gc.open_by_key("<id-de-la-hoja>").worksheet("Datos")
filas = hoja.get_all_records()                       # lista de diccionarios
hoja.update("A2:C2", [["ejemplo", 12, "ok"]])        # escribe
hoja.append_row(["nuevo", 34, "pendiente"])
```

```python
import polars as pl
df = pl.DataFrame(hoja.get_all_records())            # y ya es una tabla mas
```

Via oficial, no raspado: habla con la API de Google Sheets con credenciales propias, asi que no se
rompe cuando cambia la interfaz web y no depende de una sesion de navegador. Es la fuente real de
muchos datos de trabajo aqui. Frente a exportar a CSV a mano —la alternativa que la gente usa por
defecto— gana en que se automatiza y en que puede escribir de vuelta.

Descartado el servidor de herramientas para hojas de calculo de escritorio: resuelve el formato de
oficina, pero un servidor de herramientas cuesta contexto en cada sesion y aqui la fuente esta en la
nube. Queda anotado para cuando el fichero llegue por correo. De la cosecha propia no entran tres
clientes del mismo proveedor: `scripts/gsheet_sa.py` y `scripts/gsheets.py` —el mismo trabajo por
cuenta de servicio y por autorizacion de usuario, con menos mantenimiento detras que este— y
`scripts/gdoc-read.py`, que lee un documento de texto a plano: caso demasiado estrecho para ocupar
linea de catalogo.

Y lo que no hace bien:

- **El limite de cuota de la API se agota rapido** (del orden de decenas de peticiones por minuto y
  por usuario). Un bucle que llama a `hoja.cell(f, c)` fila a fila lo revienta en segundos y devuelve
  429. Se lee en bloque con `get_all_records()` y se escribe en bloque con `batch_update`.
- **`get_all_records()` devuelve todo como cadena o como numero segun lo que Google haya inferido.**
  Una columna de codigos con ceros a la izquierda llega mutilada. Si el tipo importa, se valida
  despues con `pandera`.
- Una hoja de calculo no es una base de datos: sin transacciones, sin bloqueo, y si alguien tiene la
  hoja abierta y edita a la vez, gana el ultimo.

Cero credenciales en el repositorio: el JSON de la cuenta de servicio va fuera del arbol y su ruta
por variable de entorno.
