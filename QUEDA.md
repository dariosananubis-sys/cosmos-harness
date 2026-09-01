# Lo que queda — estado medido, 2026-09-01

No es una lista de intenciones: cada línea sale de contar el repo. El comando que la produce está al
final, para que esto se pueda rehacer en vez de creerse.

## Lo que ya está

| | |
|---|---|
| Esqueleto | Validador de 20 invariantes, medidor, generador, compilador. **47 tests** |
| La prueba que vale | Saboteé el validador para que siempre dijera verde: **24 tests se pusieron rojos**. La batería no es decorativa |
| Galaxia | 21 oficios · 50 países · **127 herramientas** · 5 mares · 5 océanos |
| Compilación | `cosmos compilar` aplana las skills y resuelve que Claude Code no descubra las anidadas |
| Cosecha | 86 ficheros de los repos propios, verificados sin un solo nombre de cliente |
| Investigación | 22 barridos de GitHub, ~900 recursos evaluados con mecanismo, coste y viveza |

## Lo que falta, en orden

### 1. El catálogo por nicho — es el que desbloquea todo lo demás

Ahora mismo el árbol está **en rojo**: entrada 4.070, presupuesto 4.000. Y el rojo dice la verdad —
el catálogo lista los 127 pueblos **siempre**, aunque trabajes en uno solo, y son 3.206 de esos
4.070 tokens.

En curso (Codex). Cuando entre, la entrada baja a ~1.655 en el peor caso y **el sistema pasa a
escalar**: añadir cinco herramientas a `juegos` deja de costarle nada a quien trabaja en `web`.

Hasta que esto cierre, **no tiene sentido meter más herramientas**: cada una empeora el rojo.

### 2. Dieciséis nichos sin estrella

De 21 oficios, solo 5 tienen su contexto propio. Los otros 16 son una puerta que no dice nada al
entrar: `agentes-ia`, `analitica`, `audiovisual`, `automatizacion`, `blockchain`, `cientifico`,
`cumplimiento`, `documentos`, `embebidos`, `ingenieria-datos`, `juegos`, `modelos-locales`,
`moviles`, `rendimiento`, `saas`, `visibilidad`.

Una estrella dice **lo que es cierto en ese oficio y falso fuera de él** — en `trading`, que un
backtest sin comisiones es una ficción; en `ciberseguridad`, dónde está el límite ético. Sin ella, el
nicho es una carpeta.

No cuestan presupuesto: se cargan al entrar, no al arrancar.

### 3. Las 64 herramientas propias, sin integrar

`cosecha/` tiene 64 scripts limpios y **ningún pueblo los referencia**. Están en el repo sin estar en
el mapa: hoy no los encontraría nadie.

Cada uno necesita su pueblo, en su nicho, con un resumen que diga en qué se distingue de la
alternativa pública. Y varios compiten con herramientas que ya entraron — ahí hay que elegir, no
acumular.

### 4. Las cuatro piezas de VanguardIA-Harness

Decidido el 2026-09-01 (`registro/decisiones/universo/`), **ninguna migrada todavía**:

| Pieza | Qué aporta |
|---|---|
| `project.py` (511 líneas) | Proyecta a un repo externo conservando lo ajeno. Es `compilar` bien hecho |
| `precommit.py` | Verifica sobre la **instantánea del índice**, no sobre el árbol sucio |
| `secret_scan.py` + `redaction.py` | El segundo evita que un diagnóstico filtre lo que diagnostica |
| `retrieve_memory.py` | BM25 con presupuesto de bytes; nunca devuelve el cuerpo entero. Es la `lluvia` |

### 5. `usa:` y los vecinos

La decisión está tomada y el mapa escrito (`reorganizar.py`, constante `VECINOS`), pero el validador
todavía **rechaza el campo**: falta E20. Los `usa:` se retiraron de la galaxia para no dejarla en
rojo por eso.

Sin esto, un nicho no sabe que existen sus vecinos, y era la forma acordada de cruzar oficios sin
duplicar herramientas.

### 6. Los guardarraíles — la fase que casi todos se saltan

`spec/GUARDARRAILES.md` está escrito y **nada implementado**: los enganches (pre-commit, sesión, CI)
y la válvula de escape caducable.

Importa más de lo que parece, y hay una prueba en este mismo trabajo: el harness auditado tenía un
detector de fugas que funcionaba perfectamente y una fuga viva de 2.187 tokens por sesión. El
detector estaba bien; **nadie lo ejecutaba**.

Hoy COSMOS depende de que alguien escriba `cosmos validar`. Eso es exactamente lo mismo.

### 7. El remoto — **COSMOS no está en GitHub**

Todo este trabajo vive solo en el disco de esta máquina. Un fallo de disco lo borra entero.

Es lo más barato de arreglar y lo más caro de no haber arreglado.

### 8. Deudas menores, anotadas para que no se pierdan

- **Manifiesto compartido**: `destino` y `manifiesto` son globales, así que dos árboles del mismo
  repo se pisan. Medido: compilar la galaxia dejó el ejemplo con 68 errores. Parcheado con
  `galaxia.toml`; el arreglo de fondo es derivar el manifiesto de la raíz.
- **Calibración del medidor**: `aprox` publica `±desconocido` porque nadie ha medido su error contra
  un tokenizador real. Es honesto, pero es un hueco.
- **21 nichos, no 20**: salieron 21 oficios que pasan la prueba. Si se quieren 20 clavados, la fusión
  natural es `audiovisual` + `documentos`.
- **Reparto desigual**: `ciberseguridad` tiene 26 herramientas y `saas` 3. Con el catálogo por nicho
  deja de costar, pero sigue señalando que unos barridos se aprovecharon más que otros.

## Cómo rehacer este inventario

```bash
cd /Users/dariosatino/cosmos
for n in sistema-solar estrella pais pueblo oceano mar; do \
  printf "%-14s %s\n" "$n" "$(grep -rl "^cosmos: $n$" galaxia/ | wc -l)"; done
for f in galaxia/sistemas/*.md; do n=$(grep -m1 '^nombre:' "$f" | cut -c9-); \
  grep -rq "^ilumina: $n$" galaxia/estrellas/ || echo "sin estrella: $n"; done
echo "cosecha sin integrar: $(ls cosecha/*.py cosecha/*.sh | wc -l) ficheros, \
$(grep -rl 'cosecha/' galaxia/ | wc -l) referencias"
git remote -v
python3 -m cosmos validar galaxia --config galaxia.toml
python3 -m cosmos medir galaxia --config galaxia.toml
```
