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

## Los tres enganches

| Enganche | Cuándo corre | Qué hace |
|---|---|---|
| **pre-commit** | Antes de cada commit del repo que usa COSMOS | `cosmos validar`. Si rojo, el commit no ocurre |
| **sesión** | Mientras un agente trabaja | Cinco guardarraíles, `puente/sesion.py`. Ver la sección siguiente |
| **CI** | En cada push, si hay CI | `cosmos validar` completo |

Ninguno es obligatorio para usar COSMOS. El pre-commit y el de sesión se instalan con
`cosmos enganchar` (el de sesión, con `--sesion`) y el de CI es un workflow que se copia. Pero el
que no instala ninguno **tiene el mismo sistema que el harness auditado**: uno que sabe detectar su
propia degradación y no lo hace nunca.

`cosmos enganchar` es explícito y reversible: escribe el hook, dice exactamente qué escribió y
dónde, y `cosmos desenganchar` lo quita. Nada se instala solo al importar el paquete. Un sistema
que se engancha sin que se lo pidan es un sistema que la gente arranca de raíz a la primera
molestia, y con razón.

Los tres primeros son **de repositorio**: miran lo que ya está escrito, cuando ya está escrito. El
de sesión es el único que actúa mientras se decide, y por eso se trató aparte.

## El enganche de sesión: cinco mecanismos

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
| **G01** | `SessionStart` | Medición real al arrancar | Dice la entrada medida y, si excede, lo dice en rojo. Nunca bloquea |
| **G02** | `Stop` | `decision: "block"` con contador propio y tope duro | No se cierra la sesión con el árbol en rojo |
| **G03** | `PreToolUse` | `permissionDecision: "deny"` sobre rutas de veredicto | La herramienta no llega a ejecutarse |
| **G04** | `PreToolUse` | Marca de lectura atada a sesión + SHA-256, borrada en `PreCompact` | No se escribe sin haber leído lo que el repositorio exija |
| **G05** | `PostToolUse` | `updatedToolOutput`: redacción por patrón de VALOR y desvío de salidas enormes | Reescribe lo que el modelo VE de una ejecución ya ocurrida |

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
árbol que no lo está. `cosmos generar` y `cosmos compilar` siguen pudiendo escribirlos: el guard
reconoce al productor autorizado por el programa que arranca la orden.

Para leer un bloque de shell, **cada orden se juzga por separado**, respetando el entrecomillado.
Sin eso, `cosmos generar && echo falso >> COSMOS.md` cuela entero detrás del permiso de la primera
orden. Y el reconocimiento de qué escribe una orden es **una función con alcance declarado**
(redirecciones, `tee`, `truncate`, `sed -i`, destino de `cp`/`mv`/`install`/`ln`/`rsync`), no una
regex que crece con cada «esto se me escapaba»: lo que escriba un intérprete que la orden arranque
queda fuera y se dice, porque un límite declarado se puede tener en cuenta y uno oculto no.

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

### Válvula: los cinco se saltan igual que las invariantes

`cosmos saltar G03 --motivo "..." --caduca 7d`. Mismas reglas: acotado a un código, motivo
obligatorio, caducidad de 30 días como máximo, registro que solo crece, y ninguna salida dice
«verde» a secas con un salto vivo. Un guard sin válvula acaba arrancado de raíz un viernes.

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

Y lo que **no se puede** portar, distinto de lo que no se quiere: el nombre de los eventos, la forma
del envoltorio JSON y la ruta del fichero de ajustes son del runtime que llame a los hooks. COSMOS
los aísla en `bloque_sesion` y en `como_json`; el resto del módulo son funciones puras sobre rutas y
texto, que es lo que sobrevive a un cambio de runtime.

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

Un salto **nunca** se convierte en permanente por inercia. Si al caducar sigue haciendo falta, se
renueva a mano, con motivo nuevo, y el log guarda las dos entradas. Que renovar cueste un minuto es
el punto: es lo que distingue una excepción de una costumbre.

La palabra «verde» no aparece nunca sola habiendo saltos activos. Un verde que oculta un salto es
una mentira, y basta una para que nadie vuelva a creerse ninguno.

## E17 — duplicación por paráfrasis

La investigación encontró el punto ciego exacto del auditor auditado, y es instructivo: su detector
de duplicación compara frases **literales** de más de 70 caracteres. En ese repo, dos políticas
están explicadas tres veces cada una —6.343 bytes en canales siempre cargados— y el detector dice
«cero duplicación», porque las tres versiones están **parafraseadas**.

Es un fallo perfectamente comprensible: nadie copia y pega dos veces la misma política. Se
reescribe con otras palabras, en otro sitio, meses después, sin recordar que ya estaba. Por eso la
duplicación real de un harness es **casi siempre** paráfrasis, y por eso un detector literal está
ciego justo donde hace falta que vea.

COSMOS añade una invariante a las 16 de `VALIDADOR.md`:

> **E17** — Dos nodos que están simultáneamente en el contexto de entrada no pueden solaparse por
> encima del umbral configurado.

Mecanismo, con biblioteca estándar y sin red:

1. Normalizar: minúsculas, sin acentos, sin puntuación, sin palabras vacías del idioma.
2. Trocear en **n-gramas de 4 palabras** (shingles).
3. Comparar por similitud de Jaccard, por pares, **solo entre los nodos siempre cargados**.
4. Por encima de `umbral_solapamiento` (por defecto 0,25), error con las frases que más pesan.

Los n-gramas cazan la paráfrasis que la comparación literal no ve, porque una reescritura conserva
casi siempre tramos de cuatro palabras. No caza una reformulación completa con vocabulario distinto
—eso necesitaría semántica, y la semántica necesita un modelo, y un modelo cuesta dinero, que este
proyecto no gasta (`GOAL.md` §5). Se dice claramente en la salida y en la documentación: **E17 caza
la paráfrasis, no la reformulación total.** Un límite declarado se puede tener en cuenta; uno
oculto, no.

La comparación se hace **solo entre los siempre-cargados**. Dos pueblos de sistemas distintos pueden
parecerse todo lo que quieran: nunca coinciden en contexto, así que su parecido no cuesta nada. El
coste solo existe cuando las dos copias se pagan a la vez, y ahí es donde mira la invariante.

## Verificación exigida

1. Un test por enganche: instalarlo, romper el árbol, comprobar que **efectivamente** bloquea. Un
   hook instalado que no bloquea es peor que ninguno, porque además tranquiliza.
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
