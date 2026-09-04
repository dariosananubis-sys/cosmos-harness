---
cosmos: pueblo
nombre: streamlit
padre: analitica/cuadros-de-mando
resumen: Convierte un guion en una aplicacion web con controles, sin escribir nada de interfaz.
---

https://github.com/streamlit/streamlit · Apache-2.0 · 45.655★ · último push 2026-09-01 (comprobado 2026-09-01)
(comprobado por API de GitHub el 2026-09-01).

```bash
pip install streamlit duckdb
```

```python
# panel.py
import streamlit as st, duckdb

st.title("Ventas por categoria")
desde = st.date_input("Desde")
minimo = st.slider("Importe minimo", 0, 1000, 0)

# la carga la hace DuckDB, no el guion: eso es lo que salva la memoria
consulta = (
    "SELECT categoria, count(*) n, sum(importe) total "
    "FROM 'datos/*.parquet' "
    "WHERE fecha >= ? AND importe >= ? "
    "GROUP BY 1 ORDER BY total DESC"
)
df = duckdb.execute(consulta, [desde, minimo]).df()

st.dataframe(df)
st.bar_chart(df.set_index("categoria")["total"])
```

```bash
streamlit run panel.py        # http://localhost:8501
```

Para el caso en que hace falta que alguien toque un filtro y vea el resultado, sin escribir nada de
interfaz. Frontera con `metabase` (pueblo vecino) y con `apache/superset`, las dos plataformas de
inteligencia de negocio con servidor: aquellas ganan cuando quien necesita el dato **no programa**
y quiere autoservicio —su propio corte, sin pedirlo— sobre un catálogo ya cargado y con permisos
por usuario; esto gana cuando el panel lo construye alguien que sí escribe código y quiere control
total sobre la lógica y la visualización, sin aprender el editor visual de una plataforma ajena.

Y lo que no hace bien, que es la trampa clasica: **reejecuta el guion entero en cada interaccion**.
Un `pandas.read_csv()` de 5 GB dentro del guion se vuelve a cargar cada vez que alguien mueve el
deslizador. El problema no es Streamlit, es no delegarle la lectura a DuckDB o Polars como arriba —
y para lo que si tenga que quedarse en memoria, `@st.cache_data`.

Y el otro aviso, de seguridad: `streamlit run` sirve en `localhost` por defecto, pero con
`--server.address 0.0.0.0` queda expuesto **sin autenticacion ninguna**. No es una aplicacion para
publicar en Internet tal cual.

Frontera con `evidence`: aqui cuando el informe se explora; alli cuando el informe se manda.

Ojo de maquina, como dato y no como criterio de eleccion: Metabase corre sobre JVM con su propia
base de metadatos, y Superset necesita varios servicios propios — dos procesos permanentes mas que
mantener frente a esto, que no anade ninguno. Eso pesa cuando la memoria del anfitrion ya esta
repartida entre otros procesos; no descarta a ninguno de los dos para el caso que resuelven mejor.
