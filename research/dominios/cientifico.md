# Científico — barrido GitHub para COSMOS

Nicho 15 de `UNIVERSO.md`: cálculo numérico y álgebra, simulación, optimización, estadística y
ajuste de modelos, cuadernos y **reproducibilidad**, visualización científica, cómputo en paralelo.
Verificado en vivo el 2026-09-01 contra `api.github.com` con token autenticado (`security
find-internet-password -s github.com -w`, nunca impreso ni escrito a fichero). El endpoint
`/search/repositories` tiene límite real de **30 peticiones/minuto** (no 5.000/hora): el primer
intento sin pausa devolvió `403 API rate limit exceeded` a mitad de barrido — con `sleep 3-4s` entre
consultas no volvió a fallar. Candidatos ya identificados por nombre se resolvieron por `GET
/repos/{owner}/{repo}` (cuota de 5.000/hora, sin restricción de ráfaga) para confirmar estrellas,
licencia, `pushed_at` y estado `archived`. READMEs por `raw.githubusercontent.com`.

**El ángulo que pesa aquí es la reproducibilidad**, tal como pidió Darío: un resultado que no se
puede repetir no es un resultado. De los 10 puestos de "De primera", **cinco son directamente
herramientas de reproducibilidad** (entorno fijado, pipeline reejecutable, empaquetado de
experimento, configuración con semilla, seguimiento de corridas) y no cálculo puro — es la
priorización deliberada que pidió el encargo, no un accidente de qué apareció primero en la
búsqueda.

---

## De primera

| Recurso | Estrellas | Último push | Licencia | Por qué gana |
|---|---:|---|---|---|
| `numpy/numpy` | 32.641 | 2026-09-01 | BSD-3-Clause (`NOASSERTION` en la API, licencia real confirmada en su `LICENSE.txt`) | El array N-dimensional en C que sostiene literalmente todo lo demás de esta lista (SciPy, pandas, scikit-learn, JAX y Numba se apoyan en su ABI). No hay alternativa real en Python: es la base, no una elección competitiva. |
| `scipy/scipy` | 14.976 | 2026-09-01 | BSD-3-Clause | Los algoritmos numéricos serios sobre NumPy: optimización (`scipy.optimize`), integración de EDOs, álgebra lineal dispersa, estadística. Es donde se resuelve el 90% de "cálculo numérico y álgebra" del nicho sin salir de la stdlib científica de facto. |
| `JuliaLang/julia` | 49.056 | 2026-09-01 | MIT | Lenguaje compilado JIT (LLVM) pensado desde cero para cómputo científico: resuelve el "problema de los dos lenguajes" (prototipar en Python/R, reescribir en C para que vaya rápido) porque el propio Julia ya es rápido. **Ventaja de reproducibilidad nativa**: cada proyecto lleva `Project.toml`/`Manifest.toml`, el equivalente a un lockfile *de fábrica* — no es un añadido de terceros como en Python, es como funciona el gestor de paquetes por defecto. |
| `dask/dask` | 13.910 | 2026-08-24 | BSD-3-Clause | Cómputo paralelo con la misma API que NumPy/pandas, escalando de un solo hilo en un portátil a un clúster sin cambiar código. Se prefiere aquí sobre `ray-project/ray` (43.672★, Apache-2.0, más popular) **por la restricción explícita de 8 GB de RAM**: Ray reserva por defecto ~30% de la memoria de la máquina para su *object store* (Plasma) nada más arrancar, lo cual es agresivo en 8 GB; Dask no reserva memoria por adelantado y escala hacia abajo sin fricción. Ray sigue siendo la opción correcta para clústeres de verdad (ver Segunda fila). |
| `prefix-dev/pixi` | 7.665 | 2026-09-01 | BSD-3-Clause | Gestor de paquetes/entornos en Rust sobre el ecosistema conda-forge + PyPI, con **lockfile reproducible multiplataforma de serie** (`pixi.lock`) — fija exactamente qué versión de qué paquete, en qué build, para qué SO, sin el paso extra que exige `conda-lock` sobre un `environment.yml` clásico. Un binario único, sin el runtime pesado de conda/mamba por debajo; en un Mac de 8 GB instala y resuelve entornos notablemente más rápido que `conda`. |
| `treeverse/dvc` (antes `iterative/dvc`) | 15.854 | 2026-08-31 | Apache-2.0 | "Git para datos y modelos": versiona datasets y pesos de modelo grandes fuera del repo Git, y define pipelines reproducibles en `dvc.yaml` donde cada etapa declara sus dependencias exactas — `dvc repro` solo reejecuta lo que cambió, igual que un Makefile pero consciente de hashes de datos, no de timestamps. Es la pieza que falta entre "tengo el código en Git" y "puedo demostrar de qué datos salió este resultado". Ver nota de traspaso de organización más abajo. |
| `snakemake/snakemake` | 2.854 | 2026-08-31 | MIT | Gestor de flujos de trabajo estilo Make para ciencia: cada regla declara sus entradas/salidas, y solo se reejecuta lo que depende de un cambio — con integración nativa de conda/contenedores por regla, así que el propio pipeline fija su entorno paso a paso. Estándar de facto en bioinformática, pero genérico: sirve para cualquier pipeline científico reproducible. |
| `VIDA-NYU/reprozip` | 362 | 2026-02-04 | BSD-3-Clause | El más literal de la lista: empaqueta una ejecución completa de línea de comandos —binarios, librerías del sistema, ficheros de datos que tocó— rastreando las *syscalls* reales del proceso (no una lista de dependencias declarada a mano), para reproducirla en otra máquina sin instalar nada más. Mecanismo distinto a un `requirements.txt`: captura lo que el programa **de verdad usó**, no lo que alguien recuerda declarar. |
| `hydra-ecosystem/hydra` (antes Facebook Research, ahora comunidad) | 10.626 | 2026-09-01 | MIT | Framework de configuración composicional para experimentos: cada corrida registra automáticamente su configuración completa y permite sobrescribir cualquier parámetro desde línea de comandos sin tocar código — la forma estándar de fijar y versionar los hiperparámetros/semillas que hacen que un experimento sea repetible por otra persona a partir del mismo YAML. |
| `mlflow/mlflow` | 27.761 | 2026-09-01 | Apache-2.0 | Seguimiento de experimentos con registro de parámetros, métricas, artefactos **y el commit de Git exacto** de cada corrida — el enlace entre "qué código" y "qué resultado" que exige la procedencia. Auto-hospedable con SQLite en local (coste cero real, no solo "hay tier gratis"). Se prefiere sobre `aimhubio/aim` (6.245★, Apache-2.0, más ligero) como pick único por ser el estándar con más integraciones ya construidas; Aim entra en Segunda fila para quien quiera algo más minimalista. |

---

## Segunda fila

- `ray-project/ray` — 43.672★, push 2026-09-01, Apache-2.0. Gana en escala real de clúster
  multi-nodo y en el ecosistema de ML distribuido (Ray Tune, Ray Serve); en un solo Mac de 8 GB,
  `dask` o `joblib` van mejor por defecto.
- `joblib/joblib` — 4.388★, push 2026-09-01, BSD-3-Clause. La opción más ligera para paralelismo
  "vergonzosamente paralelo" en un solo proceso (`Parallel(n_jobs=-1)`), sin el overhead de programar
  un clúster — cuando no hace falta Dask, esto sobra.
- `mpi4py/mpi4py` — 921★, push 2026-08-30, BSD-3-Clause. El estándar real de HPC (MPI) desde Python,
  necesario cuando el destino final es un clúster universitario/HPC de verdad, no un portátil.
- `aimhubio/aim` — 6.245★, push 2026-08-31, Apache-2.0, y `gradio-app/trackio` — 1.668★, push
  2026-09-01, MIT (de Hugging Face, explícitamente *"lightweight, local-first, and free"*).
  Alternativas más ligeras a MLflow cuando el registro pesado del modelo no hace falta.
- `sympy/sympy` — 14.902★, push 2026-09-01, BSD (confirmado por conocimiento público del proyecto;
  API devuelve `NOASSERTION`). Sistema de álgebra computacional en Python puro: cálculo simbólico
  (derivadas, integrales, simplificación) sin salir del ecosistema. No entró en "De primera" solo
  por prioridad de espacio ante el peso de reproducibilidad exigido, no por calidad — sigue siendo el
  CAS libre de referencia en Python.
- `matplotlib/matplotlib` — 23.132★, push 2026-09-01. La visualización científica de base; casi
  todo lo demás en el ecosistema Python (incluido `rougier/scientific-visualization-book`, 11.466★,
  el libro de referencia sobre cómo usarlo bien) se construye encima o alrededor de él.
- `SciML/DifferentialEquations.jl` — 3.152★, push 2026-08-27, licencia `NOASSERTION` (MIT según su
  documentación). El paquete de referencia para simular EDOs/EDEs/EDAs en Julia — la pieza de
  "simulación" más seria del barrido cuando el problema es integrar ecuaciones diferenciales.
- `google/or-tools` — 13.973★, push 2026-09-01, Apache-2.0. Optimización combinatoria (rutas,
  programación de horarios, satisfacción de restricciones) con el solver CP-SAT de Google — gratis y
  sin cuenta, a diferencia de solvers comerciales tipo Gurobi/CPLEX.
- `casadi/casadi` | 2.284★, push 2026-08-31, LGPL-3.0. Framework simbólico de optimización numérica
  con diferenciación automática, especializado en control óptimo — más de nicho que `scipy.optimize`,
  gana cuando el problema es control/trayectorias, no optimización genérica.
- `pymc-devs/pymc` — 9.732★, push 2026-08-31, licencia `NOASSERTION` (Apache-2.0 real). Programación
  probabilística/inferencia bayesiana — el ajuste de modelos con incertidumbre explícita que pide el
  nicho, cuando un ajuste puntual de `scipy.optimize` no basta.
- `jax-ml/jax` — 36.233★, push 2026-09-01, Apache-2.0. Transformaciones componibles (autodiff, JIT,
  vectorización) sobre NumPy. **Aviso Mac 8 GB**: su ventaja real es JIT a GPU/TPU CUDA; los Mac no
  llevan GPU NVIDIA, así que en esta máquina corre en modo CPU puro — sigue siendo útil por el
  autodiff, pero no aporta la aceleración que lo hizo famoso.
- `numba/numba` — 11.142★, push 2026-08-31, BSD-2-Clause. JIT de funciones NumPy vía LLVM sin salir
  de Python; alternativa más ligera a JAX cuando solo hace falta acelerar un bucle numérico concreto.
- `JuliaPluto/Pluto.jl` — 5.368★, push 2026-09-01, MIT. Cuadernos **reactivos** para Julia: cambiar
  una celda reejecuta automáticamente todo lo que depende de ella, eliminando la clase de bug de
  Jupyter donde el orden de ejecución de celdas no coincide con el orden visual — un cuaderno Pluto
  es, por construcción, más difícil de hacer irreproducible.
- `nteract/papermill` — 6.477★, push 2026-07-06, BSD-3-Clause. Parametriza y ejecuta cuadernos
  Jupyter desde línea de comandos/pipeline — convierte un notebook interactivo en un paso reproducible
  de un flujo automatizado.
- `jupyter/nbdime` — 2.841★, push 2026-06-10, licencia `NOASSERTION` (BSD real). Diff/merge de verdad
  para notebooks `.ipynb` (compara celdas y salidas, no el JSON crudo) — sin esto, revisar un PR con
  un notebook es prácticamente imposible.
- `jupyterhub/repo2docker` — 1.732★, push 2026-08-21, BSD-3-Clause. Motor detrás de Binder/MyBinder:
  construye una imagen Docker reproducible a partir de un repo con `environment.yml`/`requirements.txt`
  — la forma estándar de dar a cualquiera un entorno ejecutable idéntico con un clic, sin que instale
  nada localmente.
- `mamba-org/mamba` — 8.082★, push 2026-08-25, BSD-3-Clause. Reimplementación en C++ del solver de
  conda, mucho más rápida resolviendo entornos; útil cuando el proyecto ya está comprometido con
  `conda`/`environment.yml` y cambiar a `pixi` no es una opción inmediata.
- `conda/conda-lock` — 562★, push 2026-08-31, licencia no confirmada (`NOASSERTION`). Genera
  lockfiles reproducibles multiplataforma sobre un `environment.yml` de conda existente — el paso
  intermedio para quien no quiere migrar todo a `pixi` pero sí quiere pines exactos.
- `IDSIA/sacred` — 4.376★, push 2025-10-22, MIT. Pionero histórico en captura automática de
  configuración/semilla/commit de Git por experimento; **más de 10 meses sin `push`**, comprobar
  viveza real antes de recomendarlo — Hydra + MLflow/Aim cubren hoy el mismo terreno con más
  actividad.
- `gems-uff/noworkflow` — 127★, push 2026-08-13, MIT. Único candidato que captura la procedencia de
  un script Python **sin modificarlo** (vía AST + reflexión + *profiling*, según su propio README) —
  mecanismo genuinamente distinto a declarar la procedencia a mano (Sacred/Hydra) o versionar datos
  (DVC). Tracción muy baja (127★, origen académico UFF/NYU) — probarlo en un caso real antes de
  apostar por él con un cliente.
- `trungdong/prov` — 138★, push 2026-08-28, MIT. Implementación Python del estándar **W3C PROV**, el
  modelo de datos formal para representar grafos de procedencia (quién generó qué, a partir de qué,
  cuándo) — la opción correcta cuando la procedencia tiene que ser interoperable con otras
  herramientas que hablen PROV, no solo un log interno.

---

## Humo

- Decenas de repos de "materiales de curso de computación científica" (`*-computing-for-*`,
  `intro-to-julia-*`, apuntes de universidad en Jupyter) que aparecen en cualquier búsqueda genérica
  de "scientific computing python/julia": son notas de clase, no herramienta ejecutable — cumplen el
  filtro "se ejecuta" solo en el sentido de que son notebooks que corren, no en el de resolver un
  problema nuevo. No se listan por nombre.
- `pgiri/dispy` — 265★, sin `push` desde 2023-11-04 (casi 3 años). Framework de cómputo distribuido
  de una época anterior a Dask/Ray; sin actividad, no recomendable para un proyecto nuevo.
- `MathInspector/MathInspector` — 897★, sin `push` desde 2021-06-16 (más de 5 años). Entorno visual
  para cómputo científico; abandonado.
- `zunzun/pyeq2` — 95★, sin `push` desde 2017-08-05 (9 años). Colección de ecuaciones para ajuste de
  curvas; muerto hace tiempo, `scipy.optimize.curve_fit` cubre el mismo terreno y está mantenido.

---

## Mapeo a COSMOS

```
sistema-solar  cientifico
├── continente  calculo-y-algebra
│   └── pais  fundacion-numerica
│          provincias: arrays N-dimensionales · algoritmos numéricos · álgebra simbólica
│          pueblos: NumPy, SciPy, SymPy
├── continente  lenguajes-y-aceleracion
│   ├── pais  lenguaje-cientifico-nativo
│   │      provincias: JIT compilado · gestión de entornos de fábrica
│   │      pueblos: Julia, DifferentialEquations.jl, Pluto.jl
│   └── pais  aceleracion-sobre-python
│          provincias: autodiff y JIT · JIT de bucles numéricos
│          pueblos: JAX, Numba
├── continente  simulacion-y-optimizacion
│   ├── pais  optimizacion-numerica
│   │      provincias: optimización combinatoria · control óptimo · programación probabilística
│   │      pueblos: OR-Tools, CasADi, PyMC
│   └── pais  computo-en-paralelo
│          provincias: paralelismo de escritorio · escalado a clúster · HPC estándar
│          pueblos: Joblib, Dask, Ray, mpi4py
├── continente  reproducibilidad                ← el código propio del nicho vive aquí
│   ├── pais  entornos-fijados
│   │      provincias: gestor de paquetes con lockfile · lockfile sobre conda existente
│   │      pueblos: pixi, mamba, conda-lock
│   ├── pais  pipelines-reejecutables
│   │      provincias: pipeline consciente de datos · pipeline estilo Make
│   │      pueblos: DVC, Snakemake
│   ├── pais  empaquetado-y-configuracion
│   │      provincias: captura de ejecución completa · configuración composicional con semilla
│   │      pueblos: ReproZip, Hydra, Sacred
│   ├── pais  procedencia-de-datos
│   │      provincias: captura automática sin tocar el script · estándar interoperable
│   │      pueblos: noWorkflow, W3C PROV (prov)
│   └── pais  seguimiento-de-experimentos
│          provincias: registro con commit de Git · seguimiento ligero local-first
│          pueblos: MLflow, Aim, Trackio
├── continente  cuadernos-y-flujo
│   └── pais  reproducibilidad-de-notebooks
│          provincias: ejecución reactiva · parametrización desde CLI · diff real · imagen reproducible
│          pueblos: Pluto.jl, Papermill, nbdime, repo2docker
└── continente  visualizacion-cientifica
    └── pais  graficos-y-3d
           provincias: 2D de referencia · 3D/VTK
           pueblos: Matplotlib, Mayavi, vedo, pyqtgraph
```

---

## Lo que falta

1. **Traspaso de organización de DVC**: `iterative/dvc` redirige hoy a `treeverse/dvc` (Treeverse,
   la empresa detrás de lakeFS). No verificado en vivo el motivo exacto ni si cambia la gobernanza
   del proyecto a medio plazo — usar la URL nueva al documentarlo con un cliente.
2. **Límite gratuito de DVC Studio / MLflow gestionado**: ambas herramientas son gratis y
   autohospedables tal como se documentan aquí (SQLite/disco local, coste cero real), pero sus
   versiones "cloud" gestionadas de pago no se auditaron — si un cliente pide la capa hospedada,
   comprobar precio en el momento.
3. **`IDSIA/sacred` sin confirmar si sigue vivo**: 10+ meses sin `push` es la frontera exacta donde
   "vivo" empieza a ser dudoso según el propio criterio de `UNIVERSO.md` ("lo que no se invoca en
   tres meses se archiva"). Se dejó en Segunda fila con el aviso en vez de excluirlo del todo porque
   sigue siendo instalable y funcional hoy — revisar de nuevo en el próximo barrido.
4. **Bioinformática y química computacional no se cubrieron como categoría propia** (BioPython,
   RDKit, OpenMM…): quedaron fuera porque las consultas del encargo no las mencionaban explícitamente
   y el barrido ya cubre 22 consultas; si un cliente concreto trabaja en esas verticales, merece un
   barrido dedicado.
5. **Ningún candidato de "De primera" resuelve procedencia de datos de forma automática y con
   tracción alta a la vez**: `noWorkflow` tiene el mecanismo correcto (automático, sin tocar el
   script) pero 127★ y origen académico; W3C PROV (`trungdong/prov`) es la especificación seria pero
   es una librería de bajo nivel, no una herramienta lista para usar. Hoy la procedencia real de un
   pipeline se resuelve mejor componiendo DVC (datos) + Hydra/Sacred (configuración) que con una sola
   herramienta — no hay "ganador único" honesto en esta subcategoría todavía.
