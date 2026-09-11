# Guardarraíles — cómo COSMOS se hace inevitable

Escribe esta pieza **Codex**. Revisa **Claude**, con premisa invertida.

## El hallazgo que obliga a este fichero

De la auditoría de un harness real (`research/PATRONES-HARNESS.md`, antipatrón A1): ese repo tiene
un auditor de fugas de tokens, bien escrito y mecánico. Al ejecutarlo contra su propio estado, dijo:

```
FUGA revisor-adversarial.md (paths:**, ~2187 tok/sesión) -> pasar a lazy
VEREDICTO: FUGA NUEVA
```

El auditor funciona perfectamente. La fuga llevaba ahí lo bastante como para no ser la última regla
añadida. **Un validador que nadie ejecuta es exactamente igual de útil que no tenerlo**, y esa es la
lección más cara de toda la investigación.

Así que la conclusión para COSMOS es dura: `cosmos validar` **no puede depender de que alguien se
acuerde de correrlo**. Si dependiera de eso, COSMOS sería una exhortación con tests — precisamente
lo que el `GOAL.md` dice que no es.

## Los cuatro enganches

| Enganche | Cuándo corre | Qué hace |
|---|---|---|
| **pre-commit** | Antes de cada commit del repo que usa COSMOS | `puente.gate` sobre la **instantánea del índice**, no sobre el árbol sucio: `cosmos validar`, las dos suites, el escáner de secretos y los canarios del gate (`P01`, `P02`). Si rojo, el commit no ocurre |
| **pre-push** | Antes de cada push | `puente.secretos --todo`: la última puerta local antes de que un secreto salga del disco (un `--no-verify` salta el pre-commit, no esto) |
| **sesión** | Mientras un agente trabaja | Cinco guardarraíles, `puente/sesion.py`. Ver la sección siguiente |
| **CI** | En cada push, si hay CI | Todo lo anterior más las mutaciones y la calibración del medidor (`.github/workflows/cosmos.yml`) |

Ninguno es obligatorio para usar COSMOS. El pre-commit, el pre-push y el de sesión se instalan con
`cosmos enganchar` (el de sesión, con `--sesion`) y el de CI es un workflow que se copia. Pero el
que no instala ninguno **tiene el mismo sistema que el harness auditado**: uno que sabe detectar su
propia degradación y no lo hace nunca.

El vigilante de modelos (`cosmos configurar --modelos`) **no es un enganche**: no valida nada ni
participa del veredicto. Repone entradas en el selector del runtime y se nombra aquí solo para que
nadie lo confunda con uno.

`cosmos enganchar` es explícito y reversible: escribe el hook, dice exactamente qué escribió y
dónde, y `cosmos desenganchar` lo quita. Nada se instala solo al importar el paquete. Un sistema
que se engancha sin que se lo pidan es un sistema que la gente arranca de raíz a la primera
molestia, y con razón.

Pre-commit, pre-push y CI son **de repositorio**: miran lo que ya está escrito, cuando ya está
escrito. El de sesión es el único que actúa mientras se decide, y por eso se trató aparte.

## El enganche de sesión: seis mecanismos

Los otros dos enganches llegan tarde por construcción. El commit ya se escribió; el CI corre sobre
algo que alguien ya decidió. Un agente que se pasa siete horas trabajando **no cruza ninguno de los
dos** hasta el final, y para entonces el daño —un secreto en el contexto, un índice reescrito a
mano, un cierre dando por bueno un árbol rojo— ya ocurrió.

Los mecanismos vienen de auditar un harness real en producción (`research/PATRONES-HARNESS.md`,
sección «Guardarraíles: catálogo de mecanismos»). Se traen **las formas, nunca las políticas**: cómo
se deniega, cómo se prueba una lectura, cómo se bloquea un cierre. Qué buzón se abre o qué web se
toca es asunto de aquel repositorio y no entra aquí.

| Código | Evento | Mecanismo | Efecto |
|---|---|---|---|
| **G01** | `SessionStart` | Medición real al arrancar | Dice la entrada medida y, si excede, lo dice en rojo. Y si el océano `autonomia` promete no pedir permiso y los ajustes de usuario arrancan en manual, lo dice también (trivalente: `desconocido` cuando no puede leer el modo; el evento no lo trae). Nunca bloquea |
| **G02** | `Stop` | `decision: "block"` con contador propio y tope duro | No se cierra la sesión con el árbol en rojo |
| **G03** | `PreToolUse` | `permissionDecision: "deny"` sobre rutas de veredicto | La herramienta no llega a ejecutarse |
| **G04** | `PreToolUse` | Marca de lectura atada a sesión + SHA-256, borrada en `PreCompact` | No se escribe sin haber leído lo que el repositorio exija |
| **G05** | `PostToolUse` | `updatedToolOutput`: redacción por patrón de VALOR y desvío de salidas enormes | Reescribe lo que el modelo VE de una ejecución ya ocurrida |
| **G06** | `Stop` | Ejecuta `[sesion] verificacion` con presupuesto de tiempo, **solo si el árbol de trabajo cambió** desde la última pasada en verde; contador propio y tope | No se cierra un turno con la verificación declarada en rojo |

### Lo que hace que cada uno no sea decorativo

**G01 y G02 — el presupuesto deja de ser un comando que alguien recuerda.** `cosmos medir` mide y
`validar` bloquea el commit, pero entre esos dos momentos no había nada. Ahora el número real
aparece en la primera línea de la sesión y vuelve a aparecer al intentar cerrarla.

El `Stop` lleva **contador propio y tope de tres**. Ni una sola vez —avisar y callarse no verifica
nada— ni infinitas —un bucle sin salida se desinstala el mismo día—. Al cuarto intento deja cerrar
y lo anota en `.cosmos/cierres.log`, que solo crece. Y el freno es **el contador, no la bandera
`stop_hook_active`** que trae el evento: esa la pone cualquier hook que haya bloqueado en el mismo
evento, así que fiarlo todo a ella deja mudo a un guard que no ha hablado nunca.

**G03 — anti-autocertificación.** El índice, la vista plana, el manifiesto, el registro de la
válvula y las marcas de lectura valen porque los produce COSMOS. Escritos a mano ponen en verde un
árbol que no lo está.

**No hay productor autorizado, y el hueco no se rellena con otro criterio.** Lo hubo: el guard
eximía la orden entera si el programa casaba `python|py|cosmos` y la palabra `cosmos` aparecía
suelta entre sus piezas, así que `python3 x.py cosmos > COSMOS.md` se llevaba permiso sobre TODAS
las rutas de veredicto. No existe criterio robusto que poner en su lugar —lo único que el guard ve
es una cadena de shell, y todo lo que se puede escribir en una cadena de shell se puede falsificar—
y **tampoco hacía falta**: `cosmos generar` y `cosmos compilar` escriben desde dentro de Python,
nunca como destino declarado de la orden, así que pasan por no declarar ninguno, no por un permiso.
Lo único que la excepción añadía era dejar pasar `cosmos medir > COSMOS.md`, que es exactamente lo
que G03 existe para impedir.

Para leer un bloque de shell, **cada orden se juzga por separado**, respetando el entrecomillado,
**los operadores compuestos** (`&>`, `&>>`, `>|`, `>&`, `|&`) y la continuación de línea: partiendo
por `&` y `|` a secas, `echo x &> COSMOS.md` se rompía en dos trozos y ninguno declaraba destino. Y
el reconocimiento de qué escribe una orden es **una función con alcance declarado** —redirecciones,
incluida la forma POSIX `> fichero orden` con la redirección delante; `tee`, `truncate`, `sed -i`,
`dd of=`, y el destino de `cp`/`mv`/`install`/`ln`/`rsync`—, no una regex que crece con cada «esto
se me escapaba».

Dos límites, declarados en vez de fingidos. Lo que escriba un intérprete que la orden arranque queda
fuera (`python -c "open(...)"` es indecidible sin ejecutar). Y **un destino que se calcula al
ejecutar** —`$(...)`, comillas invertidas, `$VAR`— **se deniega**: tampoco se puede resolver, y
dejarlo pasar sería fingir cobertura. Quien lo necesite escribe la ruta literal o abre la válvula.

**G04 — «lo he leído» pasa a ser un hecho comprobable.** La marca ata sesión, ruta y SHA-256 del
contenido: otra ventana no la presta, y editar el documento invalida todas las lecturas anteriores.
Una lectura parcial no cuenta. Y en `PreCompact` **se borran todas, sin mirar nada**: tras compactar
lo leído puede haber salido del contexto, y una prueba de lectura que sobrevive a la compactación
certifica lo que ya no está.

Qué documentos son imprescindibles lo dice cada repositorio en su `[sesion] lecturas_exigidas`, y
por defecto está vacío. **Se trae el mecanismo, no la política.**

**G05 — la única defensa contra una fuga hacia el contexto.** Cuando el comando ya corrió, impedirlo
no está sobre la mesa; lo que sigue estándolo es que el valor no llegue a leerse. Se redacta **por
patrón de VALOR, no por nombre de campo**: una blocklist de nombres no acaba nunca (`sshPass`,
`SSH_PASSWORD`, `ssh_pwd`, `clave_ssh`) y el día que falta uno el valor pasa entero. El catálogo es
el mismo que usa el escáner del índice (`puente/secretos.py`), con sus mismas excepciones — dos
catálogos separados garantizan que uno se queda atrás.

De paso, una salida de más de 50 KB o 2.000 líneas se aparta a fichero y se entrega una muestra: esa
salida entra íntegra en el contexto de todos los turnos siguientes, que es exactamente lo que COSMOS
mide y limita.

**Qué canales cubre, exactamente.** Cubría `output`/`stdout` de `Bash` y nada más: `stderr` —que es
justo donde salen las fugas típicas, un `curl -v`, un `git push` con el token en la URL del remoto,
una traza con el entorno volcado— entraba en claro y sin contar para el desvío de salidas grandes.

| Canal | Estado |
|---|---|
| `Bash` · `stdout`, `stderr` | **Tapado, y comprobado en el runtime** (2026-09-11, Claude Code 2.1.268, sesión `-p` real): el modelo lee `[REDACTADO: …]` |
| `Read` (`file.content`) | **Tapado**: la respuesta anidada vuelve entera con solo el texto sustituido. Comprobado en el runtime el 2026-09-11 |
| `Grep`, `Glob`, `Task` | El cableado los enruta y el guard devuelve su forma con el texto tapado; **que el runtime honre la sustitución en estas tres no se ha comprobado** en una sesión real |

**Lo que se descubrió al comprobarlo, y por qué esta tabla decía «tapado» sin serlo.** Hasta el
2026-09-11 el guard devolvía en `updatedToolOutput` **solo el canal tapado** (`{"stdout": …}`), y el
runtime exige el esquema entero de la respuesta (`stdout`, `stderr`, `interrupted`, `isImage` en
`Bash`); lo que no lo respeta se descarta **en silencio**. El resultado, medido con una clave de
prueba en una sesión de verdad: el valor entraba en claro y, debajo, G05 anunciaba «los valores
reales no llegaron aquí». Un guardarraíl decorativo que además tranquiliza es peor que ninguno —
es la misma lección que el auditor de fugas que nadie ejecutaba (`research/PATRONES-HARNESS.md`,
A1), un piso más abajo. Desde entonces se devuelve la respuesta original con sus campos de texto
sustituidos, la prueba `test_la_reescritura_respeta_el_esquema_entero_de_la_respuesta` fija la forma
y la mutación M30 la ve fallar. La fila de `Grep`/`Glob`/`Task` sigue siendo límite declarado, no
cobertura: se cierra el día que se compruebe en el runtime, y hasta entonces se dice.

**Lo que G05 no tapa a propósito.** El catálogo es el del escáner del repositorio, que persigue
también correos, teléfonos y rutas absolutas de la máquina del autor (repo público-limpio). En
sesión esas tres etiquetas se omiten (`puente.secretos.SOLO_REPOSITORIO`): el modelo trabaja en la
máquina de esa persona y tapar `/Users/<yo>/…` en la salida de un `ls` lo deja ciego, y un aviso
por cada ruta enseña a ignorar los avisos que sí importan — medido el 2026-09-11: cuarenta avisos
de G05 en una sesión, ninguno por una credencial. Sigue siendo **un** catálogo con una lista de
exclusión, no dos catálogos.

**El umbral de «salida enorme» y el del runtime.** Claude Code corta la salida de `Bash` a 30.000
caracteres por defecto (`bashOutputMaxChars`) y las respuestas MCP a 25.000 tokens
(`MAX_MCP_OUTPUT_TOKENS`), guardando el resto a fichero con una vista previa: para `Bash`, el corte
nativo llega antes que los 50 KB de G05. El desvío de G05 sirve para `Read`, `Grep` y `Task`, y el
tope nativo se puede bajar en los ajustes de usuario (12.000 caracteres es un valor razonable): es
la palanca barata, y no es de COSMOS.

**G06 — el océano `verificar` deja de ser una exhortación.** «Nada se declara hecho sin haberlo
visto funcionar» se pagaba en cada sesión como océano y dependía de que el modelo se acordara en el
turno 40: es la definición de exhortación de `GOAL.md` §2, en el propio arnés que la proscribe. El
modo de fallo que Anthropic dice haber observado en sus agentes de sesión larga es justo ese («la
tendencia a marcar una funcionalidad como completa sin probarla»), y la regla de ejemplo del plugin
oficial `hookify` (`require-tests-stop`) lo ataca mal: comprueba que la palabra `pytest` **aparezca**
en el transcript, así que un `pytest` que falló la satisface. G06 exige el **código de salida**.

Qué comandos, lo dice cada repositorio en `[sesion] verificacion` (vacío por defecto: se trae el
mecanismo, no la política), con `verificacion_segundos` como presupuesto total de reloj (120 s si
no se dice). Cuándo: en cada `Stop`, **solo si el árbol de trabajo cambió** desde la última pasada
en verde de esa sesión —una huella de `git status --porcelain` más tamaño y fecha de cada fichero
listado—, así que un turno que solo leyó no paga nada y un árbol limpio tampoco (lo commiteado ya
pasó por el gate). Cómo falla: `decision: "block"` con el comando, su código de salida y las
últimas doce líneas de su salida; contador propio y tope de `TOPE_AVISOS`, como G02, y al cuarto
se deja cerrar y queda en `cierres.log`. Un comando que no termina en el presupuesto **bloquea
diciendo que no terminó**: una verificación que no acabó no es una verificación en verde. Y G02 va
antes: con el árbol de COSMOS en rojo no se gasta en verificar nada.

Este repositorio declara la suite del puente (ocho segundos); la del núcleo (más de un minuto)
sigue en el gate de pre-commit y en el CI, donde se paga una vez por commit y no una por turno.

### Válvula: los seis se saltan igual que las invariantes

`cosmos saltar G03 --motivo "..." --caduca 7d`. Mismas reglas: acotado a un código, motivo
obligatorio, caducidad de 30 días como máximo, registro que solo crece, y ninguna salida dice
«verde» a secas con un salto vivo. Un guard sin válvula acaba arrancado de raíz un viernes.

**Acotada quiere decir que abrir una no arranca otra.** G04 vivía detrás del cortacircuitos de G05,
así que saltar la *redacción* dejaba al marcado de lectura sin poder crear una sola marca y, con
`lecturas_exigidas` puesto, denegando **toda** escritura para siempre. Una válvula que obliga a
abrir un segundo guard no es acotada — y el que se abre de propina es justo el que impide
autocertificarse. Cada mecanismo mira su propio código y nada más; la marca de lectura se registra
incluso con G04 saltado, porque anotar un hecho no cuesta nada y el salto caduca antes que la sesión.

### Dos formas de salida, un solo cerebro

La lógica no sabe quién la llama: recibe un evento JSON por la entrada estándar y devuelve una
decisión. Esa decisión se renderiza como **JSON estructurado** (`--formato json`) o como **bloqueo
binario por `exit 2` con el motivo en `stderr`** (`--formato exit2`), para un runtime que no lea
JSON. `exit2` no puede reescribir una salida, así que G05 ahí no bloquea: cortar un comando que ya
corrió no arregla nada, y se dice en vez de fingir cobertura.

Lo único atado a un runtime concreto es el **fichero de cableado** que escribe
`cosmos enganchar --sesion`, aislado en una función (`bloque_sesion`) para poder sustituirlo entero
el día que cambie el formato. `cosmos desenganchar` lo quita y, si nadie tocó el resto, devuelve el
fichero **byte a byte** como estaba; si lo tocaron, quita solo lo suyo y lo dice.

## Cuando el guard no puede decidir

Un guardarraíl tiene tres respuestas, no dos: permitir, denegar y **no haber podido
mirar**. Confundir la tercera con la primera es el fallo más silencioso que puede tener
un sistema de vigilancia, porque no deja huella: un guard reventado y un guard que aprobó
se ven exactamente igual desde fuera.

Dos formas de caer en él, las dos medidas en este repositorio:

1. **Por dónde se busca la configuración.** `cosmos.toml` se buscaba solo en el `cwd` del
   evento. Con el directorio de trabajo en cualquier subcarpeta, los cinco guards estaban
   apagados: el mismo evento de escritura sobre el índice daba `deny` desde la raíz y
   pasaba desde `galaxia/`. Se busca **subiendo** hasta la raíz, como hace `git` — y no
   solo desde el `cwd`, sino desde **la ruta del fichero que se va a tocar**, porque lo que
   decide es dónde cae el daño, no desde dónde se lanza el comando.

2. **Por cómo se tratan los errores.** Todo se capturaba devolviendo 0. La política ahora
   se parte según lo que el guard hace:

   | | Si el guard no puede evaluar |
   |---|---|
   | `PreToolUse` (G03, G04) | **Deniega**, diciendo que deniega porque no pudo mirar |
   | El resto (G01, G02, G05, G06) | Pasa, y **escribe la línea** en `.cosmos/cierres.log` |

   La asimetría no es capricho. G03 y G04 existen **para denegar**: si no pueden decidir,
   lo único coherente con su trabajo es negarse, y la válvula sigue ahí para seguir
   adelante a propósito. Los otros tres avisan, resumen o tapan secretos, y romper la
   herramienta que vigilan es peor que no avisar — pero dejan rastro, siempre.

Y hay un silencio que se conserva entero: **un repositorio que no usa COSMOS no oye nada**,
sin rastro tampoco. No hay nada que vigilar, y escribir un registro dentro del repositorio
de otro sería peor que callar.

## Lo que NO se trae, y por qué

Que un mecanismo exista en el harness auditado no lo hace de COSMOS. Esto se decidió no portar, para
que nadie lo reabra dentro de tres meses:

| No portado | Por qué |
|---|---|
| `permissionDecision: "ask"` | Pide confirmación humana. En modo autónomo no hay nadie al otro lado y no bloquea a nadie — es un `pasar` con buena conciencia. COSMOS deniega o pasa |
| Ventana nativa del sistema operativo para confirmar | Depende del sistema operativo y de que haya una persona mirando. Rompe «solo biblioteca estándar, cero red» y no se puede probar en CI |
| Guardas de shell destructivo (`rm -rf /`, `git reset --hard`, `git push --force`) | Es seguridad de puesto de trabajo, no de COSMOS. Además arrastra el antipatrón que el propio informe señala: una regex que crece con cada sintaxis nueva. Quien la quiera, que la ponga en su repositorio |
| Bloqueo del cuarto intento tras tres fallos idénticos | Buen mecanismo, ajeno al problema: COSMOS organiza contexto, no vigila la depuración de nadie. Y guardar el estado por comando pide un almacén que aquí no tiene dueño |
| Prohibición de capturas de pantalla completas | Política de gasto de un puesto concreto, con nombres de herramientas de ese sistema operativo |
| Reglas de qué buzón, qué web o qué cliente se toca | Política de un negocio. Es exactamente lo que este repositorio prohíbe en `GOAL.md` §5 |
| Verificar la lectura de una skill concreta por su nombre | El mecanismo sí se trae (G04); la lista de documentos la pone cada repositorio en su configuración, vacía por defecto |
| Decidir los permisos del runtime desde el repositorio | El océano `autonomia` es la política («se ejecuta sin pedir permiso»); que la máquina la cumpla es el alta (`cosmos configurar --autonomia`, ajustes de **usuario**: el runtime ignora `bypassPermissions` desde el `.claude/settings.json` de un repositorio). Un guard que escribiera ahí saldría en verde sin haber podido mirar. G01 solo comprueba que las dos cosas digan lo mismo |

Y lo que **no se puede** portar, distinto de lo que no se quiere: el nombre de los eventos, la forma
del envoltorio JSON y la ruta del fichero de ajustes son del runtime que llame a los hooks. COSMOS
los aísla en `bloque_sesion` y en `como_json`; el resto del módulo son funciones puras sobre rutas y
texto, que es lo que sobrevive a un cambio de runtime.

## Toda puerta tiene salida — y se comprueba abriéndola

Decisión de Darío (2026-09-02): **en COSMOS, todo guardarraíl tiene siempre vía de escape.**
Sin excepciones y sin «este es tan importante que no».

No es una preferencia de estilo, es lo que mantiene vivo al resto del sistema. Un guardarraíl
del que no se puede salir de forma acotada no se respeta: se rodea. Y cuando alguien lo rodea,
el sistema pierde las dos cosas a la vez — la protección y el registro de que se saltó.

Dos casos medidos el mismo día, y por eso esto deja de ser costumbre:

1. **E20 estuvo viva y sin válvula.** La lista de códigos que la válvula aceptaba era un
   `range(20)` escrito a mano: se añadió la invariante y esa línea no se tocó. Nada lo dijo
   durante días; lo encontró una persona leyendo. Ahora la lista se **deriva** de las
   comprobaciones que el validador ejecuta, así que una invariante nueva trae su salida puesta.

2. **Un guardarraíl ajeno sin salida bloqueó trabajo legítimo.** Un hook del arnés vecino
   deniega `git push --force` siempre, y su mensaje remite a *«pedir confirmación explícita»*.
   Se pidió, se dio, y el hook siguió denegando: compara texto y no sabe leer una conversación.
   La salida que su propio mensaje prometía no existía. Se resolvió por el camino largo —una
   rama nueva que no necesita forzar— y esa es la señal de alarma: **cuando la salida no está,
   aparece el rodeo**.

### Qué exige, en concreto

- Todo código que pueda bloquear —invariantes `E*` y guardarraíles de sesión `G*`— aceptado por
  `cosmos saltar`. La lista no se escribe a mano en ningún sitio.
- La salida es **acotada**: un código concreto, nunca «todo». Saltarlo todo no es una salida,
  es apagar COSMOS, y por eso `TODO`/`*`/`ALL` se rechazan explícitamente.
- Tiene **precio**: motivo escrito y caducidad. Una válvula gratis es un interruptor de apagado,
  y se acaba usando como tal.
- Y se verifica **abriéndola**: `tests/test_toda_puerta_tiene_salida.py` abre la válvula de G03,
  comprueba que el guard deja de bloquear, la cierra y comprueba que vuelve a proteger. Que un
  código esté en una lista no demuestra que la puerta abra — igual que una invariante que nadie
  ha visto fallar no demuestra que vigile.

## La válvula de escape (obligatoria, no opcional)

Del catálogo de mecanismos (patrón 9): **todo guardarraíl duro sin válvula de escape acaba
desactivado a la fuerza.** No es una posibilidad: es lo que pasa. Alguien tiene una urgencia real un
viernes, el guard le estorba, y lo desactiva entero — y ya no vuelve.

Por eso COSMOS trae la suya, y está diseñada para que usarla sea más cómodo que saltarse el sistema:

```
cosmos saltar E16 --motivo "importando 40 skills, se reorganiza el lunes" --caduca 7d
```

| Propiedad | Regla |
|---|---|
| **Acotada** | Se salta un código concreto, nunca "todo" |
| **Con motivo** | Obligatorio y libre. Sin motivo no hay salto |
| **Caducable** | Obligatorio. Máximo 30 días. Sin caducidad no hay salto |
| **Registrada** | Log append-only en `.cosmos/saltos.log`, que nunca se reescribe |
| **Visible** | Con un salto activo, toda salida dice `verde (1 salto activo: E16, caduca en 5 d)` |
| **Ruidosa al caducar** | Al vencer vuelve el rojo, y el mensaje recuerda el motivo que se escribió |
| **Cerrable** | `cosmos saltar G03 --cerrar --motivo "..."` cuando el motivo desaparece antes de vencer: una línea más en el registro, con `cerrado`, y ese código deja de estar activo y de avisar |

Un salto **nunca** se convierte en permanente por inercia. Si al caducar sigue haciendo falta, se
renueva a mano, con motivo nuevo, y el log guarda las dos entradas. Que renovar cueste un minuto es
el punto: es lo que distingue una excepción de una costumbre.

Y un salto caducado **tampoco avisa para siempre**. Hasta el 2026-09-11 la única salida de un salto
era dejarlo vencer, y al vencer avisaba en cada arranque, cada cierre y cada `validar` («vuelve a
exigirse») aunque el árbol estuviera en verde y el motivo llevara días resuelto — medido con el
G03 de un guion de alta de máquina: dos días de aviso sin nada que arreglar. Un aviso que no pide
nada se aprende a ignorar, y con él los que sí piden. Por eso cerrar es un verbo: exige lo mismo
que abrir (código concreto y motivo), no borra nada y el propio aviso de caducado dice cómo hacerlo.

La palabra «verde» no aparece nunca sola habiendo saltos activos. Un verde que oculta un salto es
una mentira, y basta una para que nadie vuelva a creerse ninguno.

## E17 — duplicación por paráfrasis

La investigación encontró el punto ciego exacto del auditor auditado, y es instructivo: su detector
de duplicación compara frases **literales** de más de 70 caracteres. En ese repo, dos políticas
están explicadas tres veces cada una —6.343 bytes en canales siempre cargados— y el detector dice
«cero duplicación», porque las tres versiones están **parafraseadas**.

Es un fallo perfectamente comprensible, y tiene dos formas que conviene no mezclar. La primera es
la **reedición**: la misma política, reescrita al copiarla a otro sitio, cambiando el orden, el
conector y algún sinónimo, pero conservando tramos enteros de la frase original. La segunda es la
**reformulación**, redactada de cero meses después y sin recordar que ya estaba, que no comparte ni
una palabra rara con la primera.

E17 existe contra la primera, que es la que un detector literal deja pasar por un carácter de
diferencia. La segunda queda fuera, y más abajo se dice con números por qué.

COSMOS añade una invariante a las 16 de `VALIDADOR.md`:

> **E17** — Dos nodos que están simultáneamente en el contexto de entrada no pueden solaparse por
> encima del umbral configurado.

Mecanismo, con biblioteca estándar y sin red. La unidad de comparación es **la afirmación**, no el
documento: dos nodos pueden hablar del mismo tema sin repetir nada, y lo que molesta es la frase
dicha dos veces.

1. Partir el cuerpo en frases y quedarse con las de **4 o más palabras con contenido**
   (`MINIMO_PALABRAS_AFIRMACION`). Una frase corta no afirma nada que merezca vigilarse.
2. Normalizar cada una: minúsculas, sin acentos, sin puntuación, sin palabras vacías del idioma, y
   reducirla a un **conjunto** de palabras — el orden no cuenta, porque reordenar es la forma más
   barata de esquivar un detector literal.
3. Comparar por similitud de Jaccard **frase contra frase**, por pares y **solo entre los nodos
   siempre cargados**, exigiendo al menos 3 palabras en común (`MINIMO_PALABRAS_COMPARTIDAS`) para
   que dos frases con un par de palabras banales no puntúen.
4. Se queda con el par que más se parece. Por encima de `umbral_solapamiento` (por defecto 0,25),
   error citando las dos frases.

Comparar conjuntos de palabras caza la reedición que la comparación literal no ve, porque reordenar
y cambiar un conector no cambia el conjunto. Medido con la propia función de E17, umbral 0,25
(`tests/test_e17_limite.py` reproduce la tabla):

| Similitud | Veredicto | Par |
|---|---|---|
| 1,000 | salta | copia literal |
| 0,750 | salta | reedición: sinónimos y otro orden |
| 0,000 | **pasa** | «Antes de tocar producción se deja escrito el camino de vuelta» / «No se modifica un entorno vivo sin haber redactado antes cómo deshacerlo» |
| 0,000 | **pasa** | «Los secretos jamás se escriben en claro dentro del repositorio» / «Las credenciales nunca van sin cifrar en el código versionado» |

Las dos últimas filas son la misma política dicha con otro vocabulario, y **E17 no las ve**: sin una
sola palabra con contenido en común no hay nada que intersecar, y su similitud es exactamente cero — no baja,
es cero. Cazarlas necesitaría semántica, la semántica necesita un modelo y un modelo cuesta dinero,
que este proyecto no gasta (`GOAL.md` §5).

Así que el límite se declara con su forma exacta, no como un «puede que se escape algo»: **E17 caza
la reedición, no la reformulación con vocabulario distinto.** Contra la segunda no hay invariante,
hay una costumbre —escribir una política en un solo sitio y enlazarla— y el aviso de que ahí el
sistema no vigila. Un límite declarado se puede tener en cuenta; uno oculto, no.

La comparación se hace **solo entre los siempre-cargados**. Dos pueblos de sistemas distintos pueden
parecerse todo lo que quieran: nunca coinciden en contexto, así que su parecido no cuesta nada. El
coste solo existe cuando las dos copias se pagan a la vez, y ahí es donde mira la invariante.

## Verificación exigida

1. Un test por enganche: instalarlo, romper el árbol, comprobar que **efectivamente** bloquea. Un
   hook instalado que no bloquea es peor que ninguno, porque además tranquiliza.
   Y para la coherencia de G01 con el océano `autonomia`, la pareja obligatoria: el aviso sale
   con `permissions.defaultMode` en manual, **no** sale con `auto` o `bypassPermissions`, y dice
   `desconocido` —nunca «manual»— cuando no hay fichero legible.
2. Un test de que la válvula caduca: con caducidad vencida, vuelve el rojo.
3. Un test de que un salto activo **nunca** produce una salida que diga solo «verde».
4. Un test de E17 con un par parafraseado de verdad —no dos copias literales— que exija el rojo.
5. Un test de que E17 **no** salta entre dos nodos que nunca coinciden en contexto.
6. Un test de que `cosmos desenganchar` deja el repo exactamente como estaba.
7. Un test **por cada guardarraíl de sesión**, viéndolo actuar: `deny` que llega a `deny`, `block`
   que impide cerrar, valor sustituido en la salida. Y su pareja siempre: el caso vecino que **no**
   debe dispararlo, porque un guard que bloquea todo tampoco prueba nada.
8. Una mutación por mecanismo en `puente/tests/mutaciones.py`: se rompe la línea a propósito y la
   prueba dueña tiene que ponerse roja. Un verde que nunca ha dado rojo no distingue una
   comprobación que funciona de una rota.
9. Un test que ejecute el manejador **como proceso aparte**, con el JSON por la entrada estándar,
   en los dos formatos de salida. Todo lo demás llama a funciones; esto prueba que el hook corre.
10. Un test de que `cosmos desenganchar` devuelve el fichero de ajustes **byte a byte** cuando
    nadie tocó el resto, y de que no pisa las entradas de otro.
11. **Una prueba por forma de evasión conocida, nunca una genérica.** Siete formas de shell
    esquivaban G03 —`&>`, la redirección delante del programa, `>|`, la continuación de línea, la
    palabra `cosmos` de argumento, la sustitución de órdenes y `dd of=`— y ninguna estaba cubierta.
    Un test genérico se pone verde con la primera arreglada y deja las otras seis abiertas.
