---
cosmos: lluvia
nombre: cierre-menores
moja: []
resumen: Cierre de la cola de tres revisiones - B03, B08-B11, T03-T05, A01/A02, C02 y la reescritura de COMPOSICION.
---

# Cierre de la cola de las tres revisiones del 2026-09-02

Fecha: 2026-09-02 · Base: `7fbcb94` (lo grave —B01, B02, B04–B07, T01, T02— ya estaba cerrado ahí) ·
Origen: `progress/revision-profunda-2026-09-02/INFORME.md` (principal),
`progress/revision-adversarial-cosmos-2026-09-02/INFORME.md` y el informe de coherencia
(`<arnés-de-origen>/progress/revision-coherencia-2026-09-02/INFORME.md`, del que quedaba COMPOSICION).

**Regla de la tanda: nada se declara arreglado sin haber saboteado el código y visto la prueba
ponerse roja.** Doce sabotajes entraron como mutaciones permanentes (M39–M50) y tres se ejecutaron
a mano con copia y restauración por fichero (S1–S3). Veredicto: **15/15 vistos fallar**, tabla al
final.

## Qué se cerró, y por qué importaba cada uno

### B08 — el cerrojo no era reentrante: la exclusión se evaporaba sin decirlo

La condición de robo llevaba `pid != os.getpid()`: el propio cerrojo era «rancio» para el mismo
proceso. Un `with` anidado sobre la misma ruta lo robaba y, al salir el interior, borraba el
fichero — el exterior seguía creyendo que tenía la exclusión y no la tenía nadie. Hoy no explotaba
porque los dos llamantes usan rutas distintas: era una mina para el día en que se unificaran, y
**nada se habría puesto rojo**. Ahora la reentrada da `ErrorCerrojo` explícito («este mismo proceso
ya tiene el cerrojo») y el exterior conserva fichero y PID. De paso se cerró la sospecha hermana:
el PID se escribe con el mismo descriptor de la creación, antes de ceder el control — un cerrojo
vacío se clasifica como rancio, y en esa ventana otro proceso robaba un cerrojo vivo.

### B09 — `cosmos acertar` reventaba con traceback crudo en el caso de estreno

`rio/acertar` se anuncia en cualquier proyecto sobre el que se clone COSMOS, y en todos menos éste
`pruebas/encargos.json` no existe: `FileNotFoundError` a la cara. La lección de `--validacion`
(mensaje entero, salida limpia) se aplicó al fichero que sí se lee siempre: `cargar_encargos`
valida en el borde (fichero ausente, JSON roto, esquema sin `peticion`/`espera`) y levanta
`ErrorEncargos` con la explicación — el estreno se nombra como lo esperable, no como fallo. El CLI
lo cobra con salida 2, como el examen ausente: error de uso, no rojo de la métrica.

### B10 — el presupuesto no distinguía «cabe» de «no había nada que medir»

`Veredicto.cabe` es ahora **trivalente** (`True`/`False`/`None`): sobre un árbol sin un token
—vacío, o un `--config` movido de sitio cuyo `arbol` relativo resuelve a un directorio que no
existe— decía «OK, quedan 4.000 tokens», porque `0 <= presupuesto` es verdad. Un cero que sale de
cero observaciones es «no lo sé», el mismo patrón que `descarga` ya publicaba como `no_definida` —
el módulo conocía la regla y la aplicaba a una cifra de las dos. Con `None`, la línea dice «SIN
MEDIR» y `medir` sale 1; además el comando comprueba `config.arbol.is_dir()` y dice el motivo
(«la raíz del árbol no existe»), como ya hacía `puente.sesion.decidir`. El guard de sesión publica
«entrada SIN MEDIR» en el mismo caso.

### B11 — G05 inventaba campos al reescribir la salida

La reescritura fabricaba `{"output": ..., "exit_code": 0}` siempre: el `exit_code: 0` no lo había
dicho nadie (lo ponía el `.get(..., 0)`) y una respuesta que solo traía `stderr` aparecía además
como salida estándar — el modelo leía como stdout, terminado «bien», algo que fue error. Ahora la
reescritura emite **solo los campos que la respuesta traía**: los canales presentes, `exit_code`
únicamente si vino (y es entero), y `output` como única vía de entrega cuando la respuesta llegó
como cadena o forma anidada. Es la regla 14 del arnés: lo no observado se publica como «no lo sé»,
nunca con el valor por defecto cómodo. Un test que consagraba el campo inventado
(`test_el_texto_redactado_vuelve_por_los_dos_canales` exigía `output` siempre) se corrigió a lo
medido.

### B03 — la vista plana huérfana era irrecuperable y el error empujaba al callejón

Sin manifiesto (`.cosmos/` es generado y gitignored: «se puede borrar»), `compilar` clasificaba
**sus propias entradas** como ajenas y las respetaba para siempre; E19 recetaba «ejecuta cosmos
compilar», y compilar no hacía nada — el único camino de vuelta era borrar a mano lo que el mensaje
prohíbe tocar a mano. Ahora la ausencia de manifiesto es un caso distinto del de una entrada ajena:
una entrada **idéntica** a lo que se crearía (mismo hash de symlink o de contenido) **se adopta** y
entra al manifiesto — con hash igual no hay nada ajeno que perder. Lo divergente sigue siendo ajeno,
intacto y cantando E19. Reproducido el escenario literal del informe: `rm -rf .cosmos` → E19 →
`cosmos compilar` → «adoptadas 2» → `validar` verde y `arrancar` verde. La receta del error vuelve a
curar. (`ResultadoCompilacion` gana el contador `adoptadas` y la acción `ADOPTAR`, publicados.)

### T03 — el test del «único juez» no ejercitaba la configuración que produjo el fallo

Ningún test ponía `[nichos] activos` con contenido — justo la condición bajo la cual el fallo
original aparecía — y el sabotaje M02 del tercer revisor (cobrar `cabe` sobre la selección)
sobrevivía a la suite entera. Ahora `ElJuezCobraSobreElPeorAunqueHayaSeleccion` mide los nichos,
elige un presupuesto **estrictamente entre** el más barato y el más caro (y comprueba que ese hueco
existe: si el árbol degenera, la prueba lo canta), activa la selección barata y exige
`cabe is False` — el juez saboteado responde lo contrario. También se fija la línea humana de
`formatear_casos` («ROJO, excede», nunca «OK, quedan»), que era B02.

### T04 — el otro grep-como-contrato

`test_el_guard_de_sesion_usa_el_mismo_juez` comprobaba que una **cadena** aparecía en el fuente de
`puente/sesion.py`: incapaz de distinguir «no existe» de «existe con otro nombre» o de «existe y hay
otro juez al lado» (y lo había: B02). Sustituido por `LosCuatroLlamantesDicenLoMismo`, que
**ejecuta** los cuatro sobre la misma configuración con selección activa y presupuesto entre
nichos: E16 en `validar`, código de salida y línea impresa de `medir`, y `revisar_arbol` del guard
(«EXCEDIDO» en el título). Los cuatro en rojo o el test lo canta.

### T05 — dos ficheros perdían 11 pruebas al ejecutarse directos

`unittest.main()` estaba a media altura de `test_un_solo_veredicto.py` (5 de 7) y de
`test_cifras_de_las_specs.py` (4 de 13), con clases definidas después: `python3 tests/test_X.py`
—la forma natural de iterar— daba un OK sin haber ejercitado dos tercios del fichero. Movido al
final en los dos (medido: 16/16 y 13/13 por las dos vías), y un canario nuevo
(`tests/test_ejecucion_directa.py`) recorre las dos suites por AST y exige que el guard de
`__main__`, si existe, vaya después de la última clase — AST y no grep, porque lo afirmado es la
posición de una forma sintáctica.

### A01 — tres escritores atómicos, dos idénticos byte a byte

`escribir_atomico` se había **copiado** de `compilar` a `modelo`, no movido, y `puente/sesion`
tenía un tercero más flojo (sin `fsync`, `with_suffix` en vez de `mkstemp`) — el que escribe las
marcas de G04. Consecuencia ya medida por el revisor: el arreglo de permisos de B04 solo llegó a
una de las copias. Queda **uno** (`cosmos.modelo.escribir_atomico`); `compilar` lo importa y
`sesion._escribe_atomico` es un envoltorio que serializa JSON y delega. La prueba lo mide donde
dolía: el manifiesto conserva sus permisos al reescribirse (con la copia vieja quedaba en 0600).

### A02 — cuatro normalizadores de texto, tres casi iguales

`acertar._normalizar` prometía «la misma normalización que usa la búsqueda de memoria» y era una
copia de `puente/lluvia.normalizar` con destino a divergir. Ahora es la misma función por
construcción (`[_raiz(p) for p in normalizar(texto)]`); la métrica no se movió (66 % ajuste, 70 %
validación, idénticos antes y después). Los otros dos normalizadores **no** se unifican y se deja
dicho por qué: `secretos._cabecera_normalizada` devuelve una cadena y conserva palabras cortas y
guiones (fundirlo cambiaría qué secretos se detectan) y `validar._normalizar` usa
NFD+`casefold` con otro contrato de salida. Unificar contratos distintos no es desduplicar, es
romper dos detectores para ahorrar seis líneas.

### C02 — `web` era el único oficio con herramientas de rendimiento y el único sin la arista

`web` tiene `lighthouse` y `unlighthouse`; `rendimiento` recibía `usa:` de blockchain, científico,
embebidos, juegos, trading, móviles… y no de `web` — Core Web Vitals es el caso canónico y era el
único nicho desconectado. Añadida la arista `web -> rendimiento` (E20 verde, cero coste de entrada:
`usa:` no se carga ni se cuenta).

### COMPOSICION — reescritura, no parche (I2 del informe de coherencia)

La spec vivía en un universo anterior: componía con `codigo`, `datos`, `guardia`, `artesania` y
`mercados` (ninguno existe; `datos` fue expulsado explícitamente por UNIVERSO), llamaba a
`criterio` «sistema solar» contradiciendo la exigencia no negociable de GOAL §1 («`criterio` es un
mar»), y el ejemplo de `usa:` de la propia spec que define E20 habría dado E20. Reescrita sobre el
árbol real: la doctrina se conserva (contención ≠ exclusión, `usa:` sugiere sin arrastrar, E20), el
caso capacidad/criterio se resuelve como lo resuelve el repo (capacidad dentro de cada nicho,
criterio como mar que moja el código de todos a la vez, «ambas skills a la vez» por construcción),
y los ejemplos apuntan a nodos reales (`rendimiento/calidad`, `mar/criterio`, la receta de la
tienda con el vecindario que `web` declara). Tres canarios nuevos en
`tests/test_cifras_de_las_specs.py` vigilan que no vuelva a envejecer: las rutas del ejemplo
existen, los sistemas de la receta existen, y `criterio` sigue siendo un mar también en la spec.

### Verificación en verde que no era del encargo: `puente.secretos --todo`

Salía rojo **sobre el árbol limpio en la base**: el informe del tercer revisor reproduce B11 con la
clave de ejemplo de la documentación de AWS (la de `EXAMPLEKEY`), y el escáner la cazó — que es su
trabajo. Inventariada en `secretos-conocidos.txt` con el motivo (evidencia copiable del informe,
clave publicada por el fabricante, no credencial), igual que la que ya vivía en
`tests/test_guardarrailes.py`.

## Elevado, no decidido — C01 y C03 son taxonomía, no código

La regla de la tanda: lo que exige una decisión de diseño se deja **medido y anotado**, no se
decide aquí. Números sobre el árbol con C02 ya aplicada (2026-09-02, base `7fbcb94`):

- **C01 — el grafo `usa:` es más estrella que malla.** 46 aristas entre sistemas, 22 recíprocas,
  **24 no recíprocas**, y **7 oficios que nadie cita**: `automatizacion`, `blockchain`,
  `cientifico`, `embebidos`, `juegos`, `moviles`, `trading`. E20 garantiza que ningún destino
  miente; no garantiza vecindario navegable en las dos direcciones. Decidir qué aristas añadir (¿es
  verdad que `web` debe mandar a `moviles` porque `moviles` manda a `web`?) es diseño del
  universo: cada arista es una afirmación sobre cómo se cruza el trabajo real, no un cierre
  mecánico de simetría. La spec reescrita deja el límite declarado y apunta aquí.
- **C03 — herramientas medidas en el nicho que no les toca.** (1) `rendimiento` (18 pueblos) son
  dos oficios: perfilado (`py-spy`, `samply`, `bpftrace`, `hyperfine`, `rr`…) y calidad de código
  (`eslint`, `ruff`, `ast-grep`, `mutmut`, `stryker-js`…) — «que mi web vaya rápida» pasa la prueba
  de UNIVERSO, «que me pases eslint» no. (2) 4 de los 22 de `trading` son pruebas genéricas
  (`hypothesis`, `time-machine`, `toxiproxy`, `tenacity`) con `mar/pruebas` y los de mutación en
  `rendimiento`: tres sitios para lo mismo. (3) la mitad de `agentes-ia` (21) es instrumental de
  esta agencia (`auditar-gasto`, `quota-oficial`, `captura-recortada`…), no oficio contratable —
  tiene forma de `rio/` de mantenimiento. (4) `playwright` está en `extraccion` y `maestro` (E2E
  móvil) en `moviles`: dos criterios de colocación para los E2E. Partir un oficio, mover pueblos o
  crear un nivel de mantenimiento **cambia el universo de 21** que UNIVERSO fija con encargo
  explícito de Darío: se queda esperando esa decisión, con estos números delante.

## Nota para el trabajo «toda puerta tiene salida» (pedida por el coordinador)

Dos observaciones de esta cola que tocan esa invariante y que aquí NO se arreglan:

1. **El código de salida de `cosmos medir` no consulta la válvula.** Medido sobre el árbol de
   ejemplo con `entrada = 10` y un salto E16 vivo (`cosmos saltar E16 --motivo ... --caduca 1d`):

   ```
   cosmos validar --config pequeno.toml -> COSMOS verde (1 salto activo: E16) · EXIT=0
   cosmos medir   --config pequeno.toml -> ROJO, excede en 230 tokens        · EXIT=1
   ```

   La misma puerta, abierta en un comando y cerrada en el otro. Igual con el rojo nuevo de «SIN
   MEDIR» (B10) y el de «la raíz del árbol no existe»: ninguno tiene salida acotada. Si `medir` es
   medidor y no puerta, quizá sea lo correcto — pero entonces nada que corra en CI debería cobrar
   su código de salida; se deja la decisión a ese trabajo.
2. **`ErrorCerrojo` por reentrada (B08) es un bloqueo duro sin válvula, a propósito.** No es un
   G0x: es un cerrojo interno de proceso, y su «salida» es no anidar sobre la misma ruta. Si la
   invariante nueva alcanza también a los bloqueos internos, este es el caso límite a clasificar.

## Los sabotajes, uno a uno, con su veredicto

Permanentes (entran en `puente/tests/mutaciones.py` y se ven fallar en cada ejecución):

| id | Sabotaje | Prueba que se puso roja | Veredicto |
|---|---|---|---|
| M39 | vuelve el `pid != os.getpid()` al cerrojo | `test_la_reentrada_se_rechaza_y_el_exterior_conserva_la_exclusion` | ROJO |
| M40 | el PID deja de escribirse antes de ceder | `test_el_pid_esta_dentro_antes_de_ceder_el_control` | ROJO |
| M41 | la adopción de huérfanas se apaga | `test_la_vista_huerfana_identica_se_adopta_y_e19_sana` | ROJO |
| M42 | el escritor único deja de conservar el modo | `test_el_manifiesto_conserva_sus_permisos_al_reescribirse` | ROJO |
| M43 | `cargar_encargos` deja pasar el `FileNotFoundError` | `test_el_estreno_no_es_un_traceback` | ROJO |
| M44 | el veredicto deja de ser trivalente | `test_sobre_un_arbol_vacio_cabe_es_none_y_la_linea_no_dice_ok` | ROJO |
| M45 | el juez cobra sobre la selección (el M02 del revisor) | `test_cabe_es_falso_con_la_seleccion_barata_activa` | ROJO |
| M46 | vuelve el cuarto juez al formateador (B02) | `test_la_linea_que_lee_una_persona_dice_lo_mismo_que_el_codigo_de_salida` | ROJO |
| M47 | la reescritura vuelve a fabricar `output`/`exit_code` | `test_la_reescritura_no_inventa_exit_code_ni_output` | ROJO |
| M48 | el `exit_code` por defecto vuelve a ser 0 | `test_la_reescritura_no_inventa_exit_code_ni_output` | ROJO |
| M49 | `_normalizar` diverge de la memoria (sin acentos) | `test_acertar_tokeniza_como_la_busqueda_de_memoria` | ROJO |
| M50 | `medir` deja de comprobar la raíz del árbol | `test_medir_sale_1_cuando_la_raiz_del_arbol_no_existe` | ROJO |

Manuales (copia del fichero, sabotaje, prueba, restauración desde la copia — nunca
`git checkout -- <directorio>`):

| id | Sabotaje | Prueba que se puso roja | Veredicto |
|---|---|---|---|
| S1 | `unittest.main()` vuelve a media altura del fichero | `test_ejecucion_directa` (canario AST) | ROJO (`71 not greater than 304`) |
| S2 | el guard vuelve a un juez propio sin agua sobre la selección | `test_el_guard_de_sesion_da_el_mismo_rojo_ejecutandolo` | ROJO (`'EXCEDIDO' not found in 'COSMOS sesion rojo entrada 1528 / 3404'`) |
| S3 | la adopción se traga también lo divergente | `test_la_huerfana_divergente_sigue_siendo_ajena` | ROJO (`0 != 1`) |

Además, un test existente se corrigió **a lo medido** (afirmaba lo deseado): el de los dos canales
de G05 exigía un `output` que la respuesta no traía — era la consagración del propio B11.

## Verificación final (todo sobre el árbol con los cambios)

```
python3 -m cosmos validar                       -> COSMOS verde, 0 errores
python3 -m unittest discover -s tests -t .      -> Ran 218 — OK (skipped=2)   [base: 198]
python3 -m unittest discover -s puente/tests    -> Ran 116 — OK               [base: 113]
python3 puente/tests/mutaciones.py              -> 50/50 invariantes vistas fallar   [base: 38/38]
python3 -m cosmos medir                         -> OK, quedan 65 tokens (ciberseguridad)
python3 -m puente.secretos --todo               -> limpio de nuevos; 3 inventariados
```

Y las dos reproducciones de los informes, repetidas en verde: el callejón de B03 (extracción
limpia, `rm -rf .cosmos`, receta de E19, `arrancar` verde) y el estreno de B09 (directorio sin
encargos, mensaje y salida 2, cero tracebacks).

Sin credenciales, sin nombres de cliente, sin datos personales.
