# Patrones de un harness real — auditoría para COSMOS

Auditoría de solo lectura de un harness de Claude Code en producción (workspace de una agencia,
~230 sesiones de historia, 22 reglas de contexto, 39 ficheros en `hooks/`). Objetivo: extraer
MECANISMOS reutilizables para un sistema nuevo (COSMOS), no el contenido de negocio.

Todas las cifras de este informe son medidas directas (`wc -c`, `grep -c`, ejecución real de un
script), no estimaciones. Cuando algo es estimación se marca explícitamente.

**Nota de anonimización**: el harness auditado pertenece a una agencia que monta webs de cliente
con WordPress/Elementor. Todo nombre de cliente, dominio, IP, correo o ruta de credenciales se ha
omitido o descrito en abstracto. Los incidentes citados (p. ej. "un footer se aplicó a 18 webs a
la vez") son casos reales documentados en el propio repo, citados solo por lo que enseñan del
mecanismo, no por quién los sufrió.

---

## Patrones que funcionan

### 1. Auditor de fugas de tokens, mecánico y con veredicto binario

**Mecanismo exacto**: un script de ~200 líneas, solo stdlib (`re`, `subprocess`, `json`, `pathlib`),
que hace 5 comprobaciones y termina con `exit 1` si encuentra algo nuevo, `exit 0` si está limpio:

1. **Coste por-turno**: ejecuta de verdad los hooks `UserPromptSubmit` con un payload sintético
   (`{"hook_event_name":"UserPromptSubmit"}`) y mide bytes de su stdout. No es teoría — es la
   salida real del hook, dividida por una constante (`TOK = 4 bytes/token`, aproximación explícita
   y documentada como tal).
2. **Reglas mal-alcanzadas**: recorre `.claude/rules/*.md`, extrae el frontmatter con una regex
   (`^---\n(.*?)\n---`), y clasifica cada regla como "global" si tiene `paths: "**"` O si no tiene
   `paths:` en absoluto. Compara el resultado contra una **lista blanca explícita** de globales
   aceptadas (constante en el propio script, con el motivo de cada una comentado). Cualquier
   regla global que no esté en la lista blanca es una FUGA nueva.
3. **Footprint del catálogo completo**: suma los bytes de frontmatter/descripción de TODAS las
   skills, agentes y comandos instalados (se listan enteros en cada sesión, se usen o no), y
   además detecta lo que meten los **plugins habilitados** mirando su caché real en disco
   (`~/.claude/plugins/cache`) — esto es lo más interesante del script: sin esto, un plugin
   encendido aporta contexto invisible a cualquier conteo que solo mire el repo.
4. **Duplicación literal**: parte tanto `CLAUDE.md` como cada regla en frases (por `.` o `\n`,
   umbral >70 caracteres) y calcula la intersección de conjuntos. Detecta contenido pagado dos
   veces por coincidencia LITERAL, no por similitud semántica (limitación reconocida más abajo).
5. **Huérfanos de memoria**: ficheros en `memory/` sin línea correspondiente en el índice.

**Por qué funciona**: no es una opinión ("esto parece que pesa mucho"), es un número con un umbral
duro y una lista blanca versionada. El propio operador puede correrlo y obtener `VEREDICTO: limpio`
o `VEREDICTO: FUGA NUEVA` sin interpretación.

**Verificación en vivo durante esta auditoría** — ejecutar el script contra el estado real del
repo dio:
```
[rules] 7 globales = ~7518 tok/sesión
  FUGA revisor-adversarial.md (paths:**, ~2187 tok/sesión) -> pasar a lazy
[catálogo system prompt] skills/agentes/comandos:
  skills ~7179 tok · agentes ~1584 tok · comandos ~1185 tok · plugins ~496 tok = ~10444 tok/sesión
VEREDICTO: FUGA NUEVA (ver arriba)
```
Es decir: el auditor está ahora mismo, en el repo real, devolviendo `exit 1` — hay una regla
(8.749 bytes, `paths: "**"`) que se coló globalmente sin pasar por la lista blanca. Ver más abajo.

**Cómo se generaliza a COSMOS**: un auditor de este tipo necesita solo tres piezas — (a) una forma
de listar qué se carga siempre vs. qué se carga condicionalmente, (b) una lista blanca EXPLÍCITA y
comentada de las excepciones deliberadas (no una heurística), y (c) un techo numérico (presupuesto)
contra el que comparar el total. Nada de esto depende del dominio de negocio; es aplicable a
cualquier sistema de contexto por capas.

### 2. `paths:` con glob matching como mecanismo de carga perezosa

**Mecanismo**: cada fichero de reglas lleva un frontmatter YAML con `name`, `description` y
`paths:` (lista de globs). El harness solo inyecta la regla cuando el trabajo toca un fichero que
matchea alguno de esos globs. `paths: "**"` es el escape hatch explícito para "esto es
verdaderamente universal".

**Medido**: de 22 reglas, **todas (22/22) llevan `paths:`** — no hay ninguna regla huérfana sin el
campo (buena higiene de base). Pero **7 de 22 (31.8%) usan `paths: "**"`** y por tanto se cargan
en cada sesión sin excepción: `development.md` (5.372 B), `git.md` (2.360 B),
`correo-solo-buzon-propio.md` (2.975 B), `informes-casos-raros.md` (4.221 B),
`nunca-pagar-sin-orden.md` (2.743 B), `search-first.md` (3.663 B) y `revisor-adversarial.md`
(8.749 B). Solo las primeras 6 están en la lista blanca del auditor; la séptima es la fuga
detectada en vivo (ver antipatrones).

**Por qué funciona**: separa "lo que hay que saber siempre" de "lo que hay que saber al tocar X",
con un mecanismo de matching estándar (glob) en vez de una taxonomía ad-hoc. El coste de "siempre"
queda medible y acotado a una lista explícita en vez de crecer por inercia.

**Cómo se generaliza**: es superior al patrón de nivel fijo (ver HAM más abajo) porque el glob
puede apuntar a cualquier profundidad de directorio, a un patrón de nombre de fichero, o a un tipo
de artefacto (`**/feature_list.json`, `**/design.md`) — no está atado a "una carpeta = un contexto".

### 3. Guardarraíles que fallan solo, no piden por favor

**El patrón central del harness**: cualquier instrucción escrita en prosa ("no hagas X") se
degrada con el contexto — hay un caso documentado en el propio repo de un hook (`post-edit-verify.sh`)
que llevaba desde su creación sin ejecutar NINGÚN test porque usaba un binario (`timeout`) que no
existe en macOS, y nadie lo notó porque el fallo era silencioso. La respuesta del harness a este
tipo de fallo no es "recordarlo mejor", es "hacer que sea imposible pasar por alto":

- **PreToolUse → deny**: el hook imprime `{"hookSpecificOutput":{"permissionDecision":"deny",...}}`
  y la herramienta NUNCA se ejecuta. No hay ambigüedad de "se me olvidó preguntar".
- **PreToolUse → ask**: pide confirmación — pero el propio repo documenta que en modo headless/
  autónomo un `ask` no bloquea a nadie (nadie contesta), así que las reglas verdaderamente
  irreversibles usan `deny` siempre, y `ask` se reserva para lo sospechoso-pero-legítimo.
- **PostToolUse → reescritura de contenido**: `hookSpecificOutput.updatedToolOutput` sustituye lo
  que el modelo va a leer ANTES de que llegue a su contexto (usado para redactar secretos de la
  salida de un comando ya ejecutado — no bloquea la ejecución, bloquea la FUGA de datos).
- **Stop → decision:block**: fuerza que la sesión no pueda cerrarse sin que se cumpla una
  condición, con contador propio de reintentos y tope duro (ver patrón 12).

**Cómo se generaliza**: la lección de fondo es que un harness debería clasificar cada regla de
negocio en una de tres cajas — (1) mecánicamente forzable con `deny` (mejor opción siempre que se
pueda), (2) forzable con reescritura de contenido post-hoc, o (3) solo enseñable por prosa (cuando
de verdad no hay señal mecánica que detectar). La caja 3 debería ser la más pequeña posible.

### 4. Gate de salida que recalcula el veredicto en vez de leerlo

**Mecanismo**: un `Stop` hook (`gate-salida-webs.py`) no confía en el campo `"veredicto": "PASA"`
de un fichero JSON. Lo **recalcula** desde el array de `comprobaciones` que ese mismo fichero
contiene (si alguna dice `"falla"` → FALLA; si alguna dice `"no_medido"` → NO_CONCLUYENTE; si no
hay ninguna comprobación real dentro → rechaza el fichero entero como "¿escrito a mano?"). Si el
campo declarado no coincide con el recalculado, lo trata como inválido.

**Por qué existe**: el propio repo documenta el incidente que lo motivó — un veredicto en verde se
falsificó escribiendo un JSON de tres claves a mano, y nada lo comprobaba. La respuesta no fue
"prohibir escribir ese fichero" (aunque ESO también se hizo, ver patrón 13) sino además dejar de
fiarse de lo que el fichero DICE que es su conclusión.

**Cómo se generaliza**: cualquier sistema de "gates" (CI, checklists, DoD) debería separar el
DATO (comprobaciones individuales, cada una con su estado) del VEREDICTO (una función pura sobre
esos datos) — y el enforcement debe llamar a la función, nunca leer un campo de resumen que el
propio productor del fichero también controla.

### 5. Prueba de lectura fresca atada a sesión + hash de contenido

**Mecanismo**: para exigir "has leído la guía obligatoria ANTES de escribir", un `PostToolUse`
hook detecta cuándo el evento es efectivamente una lectura completa de ese fichero concreto
(coincide la ruta resuelta, y si hay `limit` es `>=` al número de líneas del fichero — o sea, no
vale leer solo el principio) y escribe una marca: `{session_id, skill, sha256_del_fichero,
timestamp}`. El guard que exige la lectura comprueba las TRES cosas: que la marca exista, que el
`session_id` coincida con la sesión actual (no se hereda de otra ventana), y que el hash coincida
con el contenido ACTUAL del fichero (si alguien edita la guía, todas las lecturas previas quedan
invalidadas). Un hook en `PreCompact` borra la marca sin condiciones — tras compactar, hay que
releer, porque el contenido pudo salir del contexto real.

**Por qué funciona**: resuelve el problema de "el modelo dice que ya lo leyó" sin poder verificarlo
— convierte una afirmación en un hecho comprobable por un tercero (el propio harness), y lo ata a
exactamente el contenido que importa (si la guía cambia, la prueba caduca sola).

**Cómo se generaliza**: aplicable a cualquier "gate de conocimiento previo" — playbooks, políticas
de seguridad, contratos de tarea — sin depender de que el modelo recuerde haberlo leído.

### 6. Segmentación de comandos compuestos antes de aplicar regex

**Mecanismo**: un guard sobre `Bash` no evalúa el string completo del comando de un tirón. Primero
quita el contenido de cadenas entrecomilladas y de heredocs (para que escribir DOCUMENTACIÓN sobre
un patrón peligroso no dispare el guard), y luego **parte el comando por separadores de shell**
(`;`, `&`, `|`, salto de línea) y evalúa **cada segmento por separado**.

**Por qué existe**: el propio repo documenta dos bugs reales encontrados así — (a) un
`rm -rf /ruta/segura` en la línea 1 se emparejaba por accidente con el `.` de un `git init .` en
la línea 9 de un bloque bash de varias líneas, bloqueando un script inocente con un motivo falso;
y (b) al revés, un `screencapture` en la segunda línea de un bloque se escapaba del guard porque la
regex solo reconocía el inicio del texto completo como "principio de orden". Evaluar segmento a
segmento cierra ambos huecos a la vez.

**Cómo se generaliza**: cualquier guard basado en regex sobre `Bash` en un agente que puede
encadenar comandos en un solo bloque necesita este paso — es la diferencia entre un guard que
funciona en el 90% de los casos triviales y uno que resiste bloques reales de varias líneas.

### 7. Redacción de secretos por valor, no por nombre de campo

**Mecanismo**: en vez de una lista negra de nombres de campo ("bloquea si el campo se llama
`password`"), el hook busca el PATRÓN clave→valor (`clave: valor`, `"clave": "valor"`,
`CLAVE=valor`) donde la clave *suena* a credencial (una regex amplia: `pass|secret|token|
api[_-]?key|credentials?|bearer|auth...`) y redacta el VALOR adyacente, con una lista de
excepciones explícita (`null`, `true`, rutas de fichero, URLs completas, valores ya redactados,
valores por debajo de un umbral de longitud).

**Por qué funciona**: el propio repo documenta que la estrategia por nombre exacto de campo no
basta — un campo puede llamarse `sshPass`, `SSH_PASS` o `sshpassword` y una blocklist por nombre
literal se queda corta. Redactar por VALOR con una regex de clave amplia cubre variantes de
nomenclatura sin mantener una lista infinita de alias.

**Cómo se generaliza**: aplicable a cualquier hook de post-procesado de salida de comandos antes
de que entre al contexto de un modelo — el criterio "¿el valor PARECE un secreto?" generaliza
mejor que "¿el campo se llama como creo que se llama?".

### 8. Inyección graduada por evento (completa en los bordes, compacta en cada turno)

**Mecanismo**: para hacer que una instrucción puntual ("aplaza esto", "recuerda aquello") sobreviva
tanto a la compactación de contexto como al paso de muchos turnos sin diluirse, el mismo contenido
se inyecta con DOS formatos distintos según el evento: **completo** en `SessionStart` y
`PostCompact` (los bordes, donde hace falta contexto rico), y **compacto** (recortado a ~220
caracteres) en `UserPromptSubmit` — es decir, en CADA turno. El propio hook documenta su coste:
"8 notas como mucho, ~200 tokens por turno" — y si no hay nada pendiente, no imprime nada y no
cuesta nada (el coste es proporcional al estado real, no una tarifa fija).

**Por qué funciona**: resuelve dos fallos a la vez con un solo mecanismo — (a) una instrucción dada
a mitad de sesión que un `/compact` posterior olvidaría, y (b) una instrucción que sigue viva en el
contexto pero que el modelo deja de "escuchar" pasados diez mensajes porque quedó enterrada.

**Cómo se generaliza**: cualquier sistema de recordatorios persistentes en un agente de contexto
largo debería separar "la versión completa, para cuando se reconstruye el estado" de "la versión
mínima, para cuando solo hace falta un empujón cada turno" — y that el coste sea condicional a que
haya algo que decir.

### 9. Válvulas de escape documentadas, auditadas y con caducidad — en todo guardarraíl duro

**Mecanismo**: cada guardarraíl "duro" del sistema (el gate de salida de una tarea, por ejemplo)
tiene una vía de override explícita — una variable de entorno, un fichero-marca con caducidad de
24h, o un flag `--omitir "<motivo>"` que exige texto — y CADA vez que se usa una válvula, queda
escrito en un log append-only (`VALVULAS.log`) con qué válvula, sobre qué, y con qué motivo.
Además, el propio bloqueo tiene un tope de reintentos (constante explícita) — pasado ese tope, deja
cerrar la sesión igualmente, pero lo anota como excepción, en vez de convertirse en un bucle sin
salida.

**Por qué existe**: el repo documenta explícitamente la alternativa que descartaron — una válvula
"apaga TODO el gate para TODAS las tareas" resultaba en que el agente que hacía exactamente lo que
se le pedía (usar la válvula fina, `--omitir` con motivo, sobre UNA tarea concreta) acababa en la
práctica usando la válvula gorda porque era la única que conocía o la más a mano.

**Cómo se generaliza**: un guardarraíl sin vía de escape acaba desactivado a la fuerza (editando
el propio hook, o el fichero de configuración) — lo cual es peor, porque esa desactivación no
queda registrada. La regla de diseño es: toda prohibición dura necesita una salida FINA (afecta
solo a lo mínimo necesario) y AUDITADA (queda un rastro de quién la usó y por qué), nunca una
salida gorda sin registro.

### 10. Contrato "anti-teléfono-descompuesto" en orquestación multi-agente

**Mecanismo**: cuando un agente orquestador lanza subagentes, la instrucción explícita es que cada
subagente **escribe su resultado a un fichero** y responde al padre con **una sola línea**
(`done -> <ruta>` o `blocked -> <ruta>`) — nunca un diff completo ni una parrafada en el chat. El
padre solo lee el fichero si de verdad necesita el contenido.

**Por qué funciona**: la razón dada es medible — si el hijo devuelve 3.000 líneas, el padre las
"traga" aunque no las necesite, y eso degrada la calidad de la sesión padre entre un 20% y un 40%.
Separar "dónde vive el resultado" de "qué se comunica hacia arriba" evita que cada nivel de la
jerarquía pague el coste íntegro de los niveles de abajo.

**Cómo se generaliza**: es el patrón más directamente aplicable a cualquier orquestador
multi-agente, independientemente del dominio — el contrato de retorno de un subagente debería ser
SIEMPRE "ubicación + resumen de una línea", con la información completa recuperable bajo demanda.

### 11. Registro de intento vs. registro de ejecución, separados por fase del hook

**Mecanismo**: el mismo guard que decide si permite o bloquea una escritura (`PreToolUse`) también
apunta el INTENTO en un registro de sesión, pero solo el mismo guard corriendo en `PostToolUse`
—momento en el que consta que el comando SÍ se ejecutó— suma la escritura como confirmada. Antes
de esta separación, un comando que el guard de código BLOQUEABA dejaba igualmente constancia de
"se escribió", falseando el registro que luego usa el gate de salida.

**Cómo se generaliza**: cualquier sistema de auditoría de efectos (qué se tocó, para decidir qué
verificar después) necesita distinguir explícitamente "se intentó" de "se ejecutó de verdad",
porque el propio mecanismo de guard puede interceptar el intento antes de que ocurra el efecto.

### 12. Freno de bucle con contador propio, no solo la bandera nativa

**Mecanismo**: el harness de Claude Code ofrece una bandera nativa (`stop_hook_active`) para que
un hook de `Stop` sepa que ya está en un ciclo de reintento y no debería repetirse. El repo
documenta que fiarse SOLO de esa bandera falla cuando hay DOS hooks distintos escuchando el mismo
evento `Stop`: si el primero (`context-watch.sh`) también devuelve `block`, el segundo
(`gate-salida-webs.py`) recibe la bandera activa en su siguiente disparo y se queda mudo aunque su
propia condición siga sin cumplirse. La solución fue llevar el contador de reintentos en el propio
registro de datos del segundo hook (`avisos_gate`, incrementado cada vez, con tope explícito), en
vez de derivarlo de una señal compartida con otros hooks del mismo evento.

**Cómo se generaliza**: en cualquier sistema con múltiples hooks sobre el mismo punto de enganche,
el estado de "¿ya he insistido bastante?" debe vivir en el propio hook, no en una señal global que
otros hooks también consumen y mutan.

### 13. Escritura de "papeles del gate" restringida a un solo proceso autorizado

**Mecanismo**: además de recalcular el veredicto (patrón 4), un segundo `PreToolUse` guard,
totalmente independiente, bloquea CUALQUIER escritura directa —por `Write`/`Edit`/`MultiEdit` o por
`Bash` (`>`, `tee`, `sed -i`, `cp`, `open(...,'w')`)— sobre un conjunto reducido y explícito de
rutas protegidas (los ficheros de veredicto, el registro de sesión, el fichero de alcance). Lectura
(`Read`, `cat`, `jq`) queda expresamente permitida; solo la escritura de mano está bloqueada. Las
herramientas legítimas del propio harness que SÍ generan esos ficheros lo hacen desde su propio
proceso (no pasan por la ruta de herramientas interceptada), así que el guard no las ve ni las
bloquea.

**Cómo se generaliza**: "recalcular el veredicto" (patrón 4) y "prohibir falsificar el insumo"
(este patrón) son dos capas independientes y las DOS hacen falta — el propio repo lo dice
explícitamente: una sin la otra deja un agujero. Es el equivalente de separación de privilegios
aplicado a ficheros de estado que un agente puede escribir.

### 14. Ejecución stdlib-only y presupuesto de latencia declarado en el propio guard

**Mecanismo**: los guards de coste más alto en frecuencia (los que corren en CADA llamada a `Bash`)
declaran en su propio docstring un presupuesto de latencia (`< 30 ms`, `< 20 ms`) y la promesa de
"jamás red, jamás subprocesos" — y en la práctica solo usan `re`, `json`, `hashlib`, `pathlib` de
la librería estándar. No hay una sola dependencia externa instalada para ningún guard auditado.

**Cómo se generaliza**: un guard que corre en el camino crítico de cada tool call debe tratarse
como código de latencia baja obligatoria — cero llamadas de red, cero subprocesos pesados, solo
regex y lectura de ficheros pequeños. Es una restricción de diseño, no un detalle de implementación.

---

## Antipatrones medidos

### A1 — Regla global sin pasar por la lista blanca (fuga activa, confirmada en vivo)

`revisor-adversarial.md` tiene `paths: "**"` (se carga en TODAS las sesiones) pero **no está** en
la lista blanca (`GLOBALES_OK`) del propio auditor del repo. Al ejecutar el auditor contra el
estado real del repo en el momento de esta auditoría, el resultado fue:

```
FUGA revisor-adversarial.md (paths:**, ~2187 tok/sesión) -> pasar a lazy
VEREDICTO: FUGA NUEVA (ver arriba)
```

8.749 bytes (~2.187 tokens con la aproximación de 4 bytes/token que usa el propio script) inyectados
en cada sesión y cada subagente, sin que nadie lo haya decidido explícitamente como excepción — es
justo el tipo de fuga que el auditor está diseñado para cazar, y lo está cazando ahora mismo. Es la
prueba de que el mecanismo funciona (detecta la fuga) Y de que un auditor mecánico no basta si nadie
lo corre — la fuga llevaba ahí el tiempo suficiente para no ser la última regla añadida.

### A2 — Sección condicional-por-canal inyectada incondicionalmente

La sección "Canal [ejecución autónoma]" del `CLAUDE.md` raíz mide **1.920 bytes (11.5% de los
16.752 bytes totales del fichero)**. Su primera línea dice literalmente que "aplica SOLO cuando el
system prompt dice [modo autónomo]" y que en sesión interactiva NO aplica. Y sin embargo, el
propio `CLAUDE.md` se inyecta ENTERO en cada sesión —interactiva o no— según su propia cabecera
("Este fichero se inyecta ENTERO en cada sesión y en cada subagente"). El resultado medible: en
una sesión interactiva normal, se paga el coste íntegro de una política que el propio texto declara
inaplicable ahí mismo.

### A3 — Misma política enseñada en tres canales globales a la vez

Dos políticas (una de gasto, una de acceso a correo) están descritas en el `CLAUDE.md` raíz
(**625 bytes** en un bloque dedicado dentro de una sección) Y ADEMÁS tienen cada una su propio
fichero de regla, TAMBIÉN con `paths: "**"` (**2.743 + 2.975 = 5.718 bytes**). El comprobador de
duplicación literal del propio auditor no lo detecta ("cero duplicación") porque compara frases
idénticas carácter a carácter, y las dos versiones están parafraseadas — pero conceptualmente es
el mismo contenido, enseñado por triplicado (resumen en `CLAUDE.md` + regla A + su glosa en la
sección de auto-trigger de `CLAUDE.md`), y las TRES copias se pagan en TODAS las sesiones. Total
mínimo de bytes dedicados a estas dos políticas en canales siempre-globales: **6.343 bytes**, sin
contar las menciones dispersas en otras secciones.

**Punto débil del propio auditor**: su detector de duplicación solo atrapa coincidencia LITERAL de
frases largas (>70 caracteres). Una paráfrasis funcional del mismo contenido, como esta, pasa su
comprobación sin ser detectada — es el hueco más claro del script.

### A4 — Código muerto dentro del directorio de hooks

`anti-derroche.py` (285 bytes) no tiene **ninguna referencia** en el resto del repo (ni en
`settings.json`, ni en otro script, ni en documentación) fuera de su propio test
(`test-anti-derroche.py`). No está wireado a ningún evento en `settings.json`. Es código huérfano
que sigue viajando en cada checkout del repo. `popup-confirm.py` (116 líneas) está superado por
`ask-popup.py` (que reutiliza explícitamente su motor, según el propio docstring de otro hook) pero
no se ha borrado — sus únicas referencias activas son en logs históricos de sesiones pasadas
(`progress/...`), no en código vivo.

### A5 — Sección de dominio inline en el nivel más caro, cuando ya existe una regla `paths:`-scoped equivalente

La sección sobre trabajo en sitios web de cliente mide **823 bytes (4.9%)** del `CLAUDE.md` raíz —
se paga en TODAS las sesiones, incluidas las que no tocan absolutamente nada de ese dominio — y
sin embargo el mismo dominio ya tiene una regla dedicada con `paths:` correctamente scoped a las
rutas que le corresponden. Es contenido que el propio `CLAUDE.md` ya reconoce como candidato a
mover ("Si detectas aquí contenido que solo aplica a un tipo de tarea, muévelo a una rule con
paths:") pero que no se ha movido.

### A6 — Cobertura de tests desproporcionadamente baja frente al riesgo de los guards

De **39 ficheros** en el directorio de hooks, solo **4** son tests
(`test-anti-derroche.py`, `test-ask-popup.py`, `test-web-skill-obligatoria.py`,
`tests/test-post-edit-verify.sh`) — el 10%. Los guards más complejos y con más historial de bugs
documentados en sus propios comentarios (el que impide escribir en una web sin red de seguridad, el
que impide meter código a medida en un sitio, el que recalcula el veredicto de salida, el que
protege los ficheros de gate contra escritura a mano) **no tienen test visible** en el directorio.
La evidencia de que funcionan es, en su mayoría, narrativa dentro del propio docstring ("el
2026-08-03 pasó X, ahora ya no pasa") — verificación por incidente pasado, no por suite repetible.

### A7 — Un binario ausente puede desactivar un guard entero en silencio, y el fallo puede durar meses

El hook de verificación post-edición dependía de `timeout`, que **no existe en macOS de serie**.
El propio comentario del script documenta que esto llevaba "desde siempre" sin ejecutar una sola
prueba en la máquina real, porque el error (`timeout: command not found`) se leía como si fuera
la salida del programa que se quería probar, en vez de como un fallo del propio mecanismo de
verificación. Nada en la ejecución del hook distinguía "los tests pasaron" de "el hook nunca llegó
a intentarlo". Es el mismo antipatrón, de fondo, que el circuit-breaker #3 de las reglas de
desarrollo del propio repo describe como error genérico y ya corregido — pero el hecho de que
existiera y tardara en detectarse es la evidencia de por qué hace falta ese circuit-breaker.

---

## Guardarraíles: catálogo de mecanismos

Formas concretas, verificadas en el código real, de hacer que un harness FALLE SOLO en vez de
depender de que el modelo se acuerde:

| Mecanismo | Evento | Efecto | Cuándo usarlo |
|---|---|---|---|
| `permissionDecision: "deny"` en `hookSpecificOutput` (stdout, JSON) | `PreToolUse` | La herramienta nunca se ejecuta | Irreversible o catastrófico — la opción por defecto |
| `permissionDecision: "ask"` | `PreToolUse` | Pide confirmación humana | Solo si hay un humano de verdad al otro lado (en modo autónomo headless, `ask` no bloquea a nadie — medido y documentado) |
| Bloqueo simple por `exit 2` + mensaje a stderr | `PreToolUse` | Bloqueo binario, sin JSON estructurado | Reglas simples de "fichero prohibido" sin necesidad de explicar niveles |
| `updatedToolOutput` en `hookSpecificOutput` | `PostToolUse` | Reescribe lo que el modelo VE de una ejecución que ya ocurrió | Fuga de datos hacia el contexto (secretos), no para impedir la acción en sí |
| Escritura de marca atada a `session_id` + hash de contenido | `PostToolUse` (lectura) | Convierte "afirmo que lo leí" en un hecho comprobable por otro proceso | Gates de conocimiento previo (playbooks, contratos) |
| Borrado incondicional de esa marca | `PreCompact` | Fuerza releer tras compactar, porque el contenido real puede haber salido del contexto | Cualquier prueba de lectura que dependa de contexto vivo |
| `decision: "block"` con motivo | `Stop` | Impide cerrar la sesión sin cumplir una condición | Checklists de cierre — con contador propio de reintentos y tope duro, nunca sin límite |
| Prohibición de escritura directa sobre rutas de "veredicto" (Write/Edit/Bash) | `PreToolUse` | Solo el proceso autorizado (fuera del camino de herramientas interceptado) puede producir el fichero | Anti-autocertificación — siempre junto con recalcular el veredicto, nunca solo esto |
| Recálculo del veredicto desde datos crudos, ignorando el campo-resumen | Cualquiera que lea un "gate" | El campo declarado no vale nada si no coincide con lo recalculado | Cualquier sistema de gates/DoD |
| Válvula de escape con caducidad + log append-only | Todos los guards "duros" | Permite el override necesario sin abrir la puerta de par en par ni perder el rastro | Obligatorio en todo guardarraíl sin excepción, o acaba desactivado a la fuerza |
| Segmentación de comandos compuestos antes de aplicar regex | Guards sobre `Bash` | Evita falsos positivos/negativos cruzados entre líneas de un mismo bloque | Cualquier guard sobre comandos que pueden encadenar varias órdenes |
| Redacción por patrón de VALOR (no por nombre de campo) | `PostToolUse` sobre salida de comandos | Cubre variantes de nomenclatura de credenciales sin blocklist infinita | Prevención de fuga de secretos hacia el contexto del modelo |
| Ventana nativa del sistema operativo sustituyendo un selector de terminal roto | Intercepta la petición de confirmación nativa del propio harness | Garantiza que la confirmación humana LLEGA de verdad, en vez de fallar en silencio | Cuando el mecanismo nativo de confirmación del harness no es fiable en el entorno real |

---

## Lo que NO hay que llevarse

- **Regex acumulada por rondas sucesivas de "esto se me escapaba".** Los guards más complejos
  auditados llevan en su propio docstring el historial de 3-4 rondas de parches ("esto colaba y
  ahora no", "esto se rompía y ahora no") en vez de un parser de comandos diseñado una vez. Funciona
  hoy, pero cada sintaxis nueva de comando (un wrapper nuevo, una variable sin expandir, un
  `eval-file` con nombre inocente) es un hueco potencial hasta que alguien lo encuentra por daño
  real. Para un sistema nuevo: diseñar el parser de intención de un comando (¿escribe? ¿dónde?
  ¿qué tipo de contenido?) como un componente propio y testeado, no como una colección creciente de
  regex con comentarios de "por qué se añadió esta".

- **39 ficheros en un directorio plano, mezclando hooks wireados, tests y librerías compartidas.**
  Sin mirar `settings.json` no hay forma de saber qué de esos 39 ficheros está realmente enganchado
  a un evento y qué es código muerto, legado o una librería auxiliar (`webs_comun.py`) importada por
  otros. Un sistema nuevo debería separar por convención (o por manifiesto explícito) qué es
  handler-activo, qué es test, y qué es utilidad compartida.

- **Cobertura de tests desproporcionadamente baja frente al riesgo.** El 10% de los ficheros del
  directorio de guards tiene test — y no son precisamente los guards más simples los que carecen de
  él. La verificación de que un guard sigue funcionando descansa, en la mayoría de los casos, en la
  narrativa del propio docstring sobre un incidente pasado, no en una suite repetible.

- **Un mecanismo de nombres y dominio de negocio muy específico, en castellano, mezclado con el
  mecanismo genérico.** El VALOR de este harness para COSMOS está en el CÓMO (glob matching, deny
  vs ask, recalcular veredictos, segmentar comandos), nunca en el QUÉ (nombres de skills concretas,
  nombres de scripts de un dominio de negocio de una agencia). Extraer el mecanismo sin arrastrar
  el vocabulario específico exige una reescritura deliberada, no una copia.

- **Una skill de terceros (HAM) instalada pero sin evidencia de uso activo en el flujo real.** Su
  coste de catálogo se paga en cada sesión (entra en el conteo del auditor de fugas) exista o no
  beneficio, si no se invoca. Cualquier sistema con catálogo de skills "siempre listado" debería
  archivar, no simplemente ignorar, lo que no se ha invocado en un periodo razonable — el propio
  repo auditado tiene esta política para sus PROPIAS skills, pero no se ha aplicado a esta importada.

### HAM (`hierarchical-agent-memory`): qué propone y dónde se queda corto

**Lo que propone de verdad** (leído el `SKILL.md` completo): un CLAUDE.md raíz mínimo (~200
tokens) más un CLAUDE.md por subdirectorio de primer nivel (~250 tokens cada uno), con una sección
de "Context Routing" en el raíz que es una tabla manual (`→ api: src/api/CLAUDE.md`) que el agente
debe seguir por instrucción, no por mecanismo. Además, una carpeta `.memory/` plana con cuatro
ficheros fijos (`decisions.md`, `patterns.md`, `inbox.md`, `audit-log.md`) y un dashboard web
(Node.js) que compara tokens estimados con y sin el sistema.

**Dónde se queda corto frente a lo que este mismo repo ya construyó por su cuenta**:

1. **Profundidad fija de dos niveles.** El diseño es "raíz + un nivel de subdirectorios". No hay
   mecanismo para un tercer nivel (`src/api/v2/CLAUDE.md`) ni para reglas que dependan de un patrón
   de fichero en vez de una carpeta (`**/design.md`, `**/feature_list.json`). El mecanismo
   `paths:`-con-glob de este repo es estrictamente más general: cualquier profundidad, cualquier
   patrón, no solo "una carpeta = un contexto".
2. **Enrutado por instrucción, no por enforcement.** "El agente lee el raíz, luego CARGA
   inmediatamente el subcontexto relevante" es una instrucción de comportamiento esperado, no algo
   que un hook compruebe o fuerce. No hay equivalente al guard que bloquea escribir sin haber leído
   la guía correspondiente (patrón 5 de este informe). El propio historial de incidentes de este
   repo (un veredicto en verde que ocultaba el 66% de contenido perdido) es precisamente la
   evidencia de que "confiar en que el agente sigue la tabla de rutas" no es suficiente sin un
   mecanismo que lo verifique.
3. **Memoria plana, sin jerarquía ni caducidad por confianza.** Los cuatro ficheros de `.memory/`
   no tienen el equivalente de `confidence` + `last_used` por hecho individual que sí tiene la capa
   de memoria de este repo, ni el concepto de "huérfano" (hecho guardado pero no indexado, y por
   tanto invisible) que el propio auditor de fugas detecta como categoría aparte.
4. **Estimación de tokens explícitamente reconocida como aproximación** ("~4 chars = 1 token, no
   un tokenizador real") — la misma simplificación que usa el auditor de este repo (`TOK = 4`), así
   que no es un punto débil exclusivo de HAM, pero tampoco es un diferencial a favor: ambos comparten
   la misma limitación de medición.
5. **Dependencia extra para el dashboard** (Node.js 18+, proceso propio en `localhost:7777`) frente
   a la filosofía de "cero dependencias, solo stdlib, <30ms" que sí cumplen los guards nativos de
   este mismo repo.

**Conclusión para COSMOS**: el ENROUTING por directorio de HAM es una idea razonable de punto de
partida (dar a cada zona del código su propio contexto mínimo), pero el mecanismo real que hace que
algo así no se degrade con el tiempo — glob matching de profundidad arbitraria, un auditor que mide
el coste real y compara contra una lista blanca, y guards que fuerzan el cumplimiento en vez de
pedirlo — no viene de la skill importada. Viene de lo que este mismo repo construyó por necesidad
propia, después de daño real documentado.
