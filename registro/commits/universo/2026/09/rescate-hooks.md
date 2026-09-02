# El enganche que faltaba: guardarraíles de sesión

Fecha: 2026-09-02 · Spec dueña: [`../../../../../spec/GUARDARRAILES.md`](../../../../../spec/GUARDARRAILES.md) ·
Origen de los mecanismos: [`../../../../../research/PATRONES-HARNESS.md`](../../../../../research/PATRONES-HARNESS.md),
sección «Guardarraíles: catálogo de mecanismos».

**Estado fijado** (el árbol muta mientras se escribe): base `cf7e10a`, con otros dos agentes
trabajando a la vez en `galaxia/`. Este parte cubre 9 ficheros, ninguno de los suyos. Se referencia
por símbolo, no por `fichero:línea`.

## El hueco

COSMOS se enganchaba en tres sitios —pre-commit, CI y arranque— y **los tres son de repositorio**:
miran lo que ya está escrito, cuando ya está escrito. Un agente que trabaja siete horas no cruza
ninguno hasta el final, y para entonces el daño ya ocurrió: un secreto que entró al contexto, un
índice reescrito a mano, una sesión cerrada dando por bueno un árbol rojo.

El propio parte anterior lo dejaba anotado como pendiente: *«El enganche de sesión que cita
`spec/GUARDARRAILES.md`: no implementado. Los otros dos —pre-commit y CI— sí»*. Esto lo implementa.

## Los cinco mecanismos traídos

Todos viven en `puente/sesion.py`, con código propio de válvula. La spec los documenta entero; aquí
va de dónde sale cada uno y qué efecto tiene.

| Código | Evento | Mecanismo del catálogo | Efecto real |
|---|---|---|---|
| **G01** | `SessionStart` | Medición en el primer turno | Dice la entrada medida (`entrada N / M tokens`) y en rojo si excede. **Nunca bloquea**: `SessionStart` no puede |
| **G02** | `Stop` | `decision: "block"` con contador propio y tope duro | No se cierra con el árbol en rojo. Insiste 3 veces, después deja cerrar y lo anota en `.cosmos/cierres.log` |
| **G03** | `PreToolUse` | `permissionDecision: "deny"` | La herramienta **no llega a ejecutarse**. Protege índice, vista plana, manifiesto, registro de la válvula y marcas de lectura |
| **G04** | `PreToolUse` + `PostToolUse` + `PreCompact` | Marca atada a `session_id` + SHA-256, borrada sin condiciones al compactar | No se escribe sin haber leído entero lo que el repositorio exija |
| **G05** | `PostToolUse` | `updatedToolOutput` | Reescribe lo que el modelo **ve** de una ejecución ya ocurrida: tapa valores con forma de secreto y aparta las salidas enormes |

Dos mecanismos más, que no son un guard sino la forma de escribirlos, y por eso no tienen código:

- **Segmentar el bloque de shell antes de mirar nada.** Cada orden se juzga sola, respetando el
  entrecomillado. Sin esto, `cosmos generar && echo falso >> COSMOS.md` cuela entero detrás del
  permiso de la primera orden — y eso es un test, no una suposición
  (`test_el_permiso_de_una_orden_no_cubre_a_la_siguiente`).
- **Dos formas de salida, un solo cerebro.** La lógica recibe un evento JSON por la entrada estándar
  y devuelve una `Decision`; el renderizado es aparte: JSON estructurado o bloqueo binario por
  `exit 2` con el motivo en `stderr`. `exit2` **no puede** reescribir una salida, así que G05 ahí no
  bloquea, y se dice en vez de fingir cobertura.

### Lo que se hizo mejor que en el original

1. **Redacción por patrón de VALOR reutilizando el catálogo que ya existía.** El escáner del índice
   (`puente.secretos`) ya tenía patrones y excepciones afinadas; se le añadió `redactar_texto`, que
   sustituye el valor y deja el resto del texto intacto. Dos catálogos separados garantizan que uno
   se queda atrás.
2. **El reconocimiento de «qué escribe esta orden» es una función con alcance declarado**
   (`objetivos_de_escritura`: redirecciones, `tee`, `truncate`, `sed -i`, destino de
   `cp`/`mv`/`install`/`ln`/`rsync`), no una regex que crece con cada «esto se me escapaba». Lo que
   escriba un intérprete que la orden arranque queda **fuera y declarado**: un límite declarado se
   puede tener en cuenta, uno oculto no.
3. **El guard protege su propia válvula.** `.cosmos/saltos.log` y las marcas de lectura están en la
   lista de rutas de veredicto. Un salto escrito a mano con la fecha que a uno le convenga no es una
   excepción registrada: es la firma de uno mismo.
4. **El freno del `Stop` es el contador propio, no `stop_hook_active`.** Esa bandera la pone
   cualquier hook que haya bloqueado en el mismo evento, así que fiarlo todo a ella deja mudo a un
   guard que no ha hablado nunca. El tope duro es lo que impide el bucle.
5. **`cosmos desenganchar` devuelve el fichero de ajustes byte a byte** cuando nadie tocó el resto,
   y si lo tocaron quita solo lo suyo y lo dice. Reescribir los ajustes de otro «con el mismo
   contenido pero mejor indentado» es la clase de cortesía por la que se desinstala un sistema.

## Mecanismo, no política

Los guards de origen ejecutan reglas de un negocio concreto. **Nada de eso entra.** Lo que se decidió
NO portar está en la spec con su motivo, y en resumen:

| No portado | Por qué |
|---|---|
| `permissionDecision: "ask"` | En modo autónomo no hay nadie al otro lado: es un `pasar` con buena conciencia |
| Ventana nativa del sistema para confirmar | Depende del sistema operativo y de una persona mirando; rompe «solo biblioteca estándar» y no se prueba en CI |
| Guardas de shell destructivo (`rm -rf`, `reset --hard`, `push --force`) | Seguridad de puesto de trabajo, no de COSMOS. Y arrastra el antipatrón de la regex que crece |
| Corte del 4.º intento tras 3 fallos idénticos | Buen mecanismo, problema ajeno: COSMOS organiza contexto, no vigila la depuración de nadie |
| Prohibición de capturas de pantalla completas | Política de gasto de un puesto, con nombres de herramientas de un sistema operativo concreto |
| Qué buzón, qué web, qué cliente se toca | Política de un negocio: exactamente lo que `GOAL.md` §5 prohíbe aquí |
| Exigir la lectura de un documento concreto por su nombre | El mecanismo sí se trae (G04); la lista la pone cada repositorio en `[sesion] lecturas_exigidas`, **vacía por defecto** |

**Y lo que no se PUEDE portar**, distinto de lo que no se quiere: el nombre de los eventos, la forma
del envoltorio JSON y la ruta del fichero de cableado son del runtime que llame a los hooks. Están
aislados en dos funciones (`bloque_sesion` y `como_json`) para poder sustituirlas enteras el día que
el runtime cambie; el resto del módulo son funciones puras sobre rutas y texto.

## Toda válvula, con caducidad

Los cinco se saltan igual que las invariantes: `cosmos saltar G03 --motivo "..." --caduca 7d`.
Acotado a un código, motivo obligatorio, 30 días como máximo, registro que solo crece, y **ninguna
salida dice «verde» a secas** con un salto vivo — también las de sesión, que pasan por
`anotar_salida` como el resto.

`CODIGOS` pasa de `E00..E19` a `E00..E19 + G01..G05`. `todo`, `todos`, `*` y `all` se siguen
rechazando por su nombre: apagar COSMOS no es un salto.

## Reversible y explícito

```
cosmos enganchar --sesion      # pre-commit + cableado de sesión
cosmos desenganchar            # quita los dos y deja el repo igual
```

Nada se instala al importar. `enganchar --sesion` sin `--sesion` sigue haciendo exactamente lo de
antes, así que quien no lo quiera no lo tiene.

## Verificación

Todo desde la raíz del repositorio, con `python3` (3.11+, solo biblioteca estándar, cero red).

### Las dos suites y las mutaciones

```
$ python3 -m unittest discover -s puente/tests
Ran 80 tests — OK                      (eran 74; 45 nuevas en test_sesion.py)

$ python3 -m unittest discover -s tests
Ran 89 tests — OK (skipped=1)

$ python3 puente/tests/mutaciones.py | tail -1
18/18 invariantes vistas fallar        (eran 8; 10 nuevas)
```

Las diez mutaciones nuevas, cada una rompiendo **una** línea y exigiendo el rojo de su prueba dueña:

| | Qué se rompe | Qué deja de vigilar |
|---|---|---|
| M9 | la segmentación del bloque | el permiso de `cosmos generar` cubre la escritura a mano de detrás |
| M10 | la comprobación de contención de rutas | el índice se reescribe a mano y nadie lo impide |
| M11 | la lectura de saltos en los guards | un guard de sesión que no se puede abrir acaba arrancado de raíz |
| M12 | la sustitución del valor redactado | el secreto entra entero en el contexto |
| M13 | el SHA-256 de la marca de lectura | la marca certifica una versión del documento que ya no existe |
| M14 | la sesión guardada dentro de la marca | copiarla a otra carpeta la convierte en lectura ajena |
| M15 | el borrado en `PreCompact` | la prueba de lectura sobrevive al contenido que probaba |
| M16 | el tope de avisos (a 0) | el cierre en rojo no se bloquea nunca |
| M17 | el tope duro (siempre bloquea) | el `Stop` se vuelve un bucle sin salida |
| M18 | la restauración byte a byte | `desenganchar` reformatea los ajustes de otro |

### El árbol real, en verde

```
$ python3 -m cosmos validar
COSMOS  verde  0 errores

$ python3 -m cosmos medir | grep Presupuesto
  Presupuesto ..... 4.000     OK, quedan 119 tokens en el peor caso con agua

$ python3 -m puente.gate --silencioso ; echo "EXIT=$?"
secretos: limpio
EXIT=0
```

### Enganchar y desenganchar, de verdad

Sobre un repositorio Git temporal con árbol COSMOS real, medido:

```
eventos cableados: ['PostToolUse', 'PreCompact', 'PreToolUse', 'SessionStart', 'Stop']
hook pre-commit existe tras desenganchar: False
settings.json existe tras desenganchar:   False
árbol idéntico tras desenganchar:         True
```

### El hook corre de verdad, no solo compila

Tres pruebas arrancan el módulo como proceso aparte, con el JSON por la entrada estándar, en los dos
formatos. Un hook que se instala y no corre es peor que ninguno: además tranquiliza.

```
$ echo '{"hook_event_name":"PreToolUse","tool_name":"Bash",
         "tool_input":{"command":"echo falso >> galaxia/COSMOS.md"},"cwd":"<repo>"}' \
  | python3 -m puente.sesion
{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", ...}}

$ ... | python3 -m puente.sesion --formato exit2 ; echo "EXIT=$?"
COSMOS  sesion  rojo  escritura a mano sobre una ruta de veredicto
EXIT=2
```

## Juicio: cuántos de esos hooks eran mecanismo

Medido sobre el fichero de cableado del harness auditado, no estimado:

- **36 ficheros** en su directorio de hooks (`.py` + `.sh`).
- **23 ficheros distintos** enganchados de verdad, repartidos en 8 eventos. Los otros 13 son tests,
  librerías compartidas o código que ya no llama nadie — y sin abrir el fichero de ajustes no hay
  forma de saber cuál es cuál.
- De esos 23, **6 traían un mecanismo reutilizable**: la denegación por `PreToolUse`, la segmentación
  de comandos compuestos, la redacción por `updatedToolOutput`, la marca de lectura con su borrado
  al compactar, el bloqueo de `Stop` con contador y tope, y la prohibición de escribir sobre rutas de
  veredicto. Cinco de los seis viven en los mismos tres eventos.
- Los **17 restantes** son regla de negocio (qué buzón, qué web, qué cliente) o arranque del puesto
  de trabajo (abrir programas, inyectar notas del día, comprobar herramientas locales). Nada de eso
  sobrevive fuera de esa máquina.

Es decir: **uno de cada seis ficheros del directorio** llevaba algo que valiera la pena traerse, y
ninguno se podía traer copiando — el vocabulario del negocio está trenzado con el mecanismo en el
mismo fichero, y separarlos exige reescribir, que es lo que se ha hecho.

**Un hallazgo que no esperaba:** el fichero mejor escrito del directorio en cuanto a mecanismo
genérico —el que corta el cuarto intento de un comando que ya falló tres veces igual, y el que
aparta a fichero las salidas de más de 50 KB— **no está enganchado a ningún evento**. No aparece ni
en el fichero de ajustes del proyecto ni en el del usuario ni en sus variantes locales; sí tiene su
propio fichero de tests. Es el mismo antipatrón que motivó `spec/GUARDARRAILES.md` —un validador
impecable que nadie ejecuta— un nivel más adentro: un guard impecable que nadie cablea. De ahí que
COSMOS meta el cableado en `cosmos enganchar` y lo pruebe en CI: escribir el guard es la mitad fácil.

## Lo que queda abierto

- **`[sesion] lecturas_exigidas` está vacío en este repositorio.** El mecanismo G04 no se dispara
  hasta que alguien declare qué documento es imprescindible aquí. Es deliberado: la política la pone
  quien conoce el repositorio, no quien trae el mecanismo.
- **`objetivos_de_escritura` no persigue lo que escriba un intérprete que la orden arranque.** Está
  declarado en la spec y en el docstring. El canal principal es la herramienta de escritura, que
  llega estructurada, y el gate de pre-commit es la red de abajo.
- **G01 no puede bloquear.** `SessionStart` no admite denegación en ningún runtime conocido: solo
  informa. Quien quiera que un presupuesto excedido pare el trabajo, lo tiene en G02 al cerrar y en
  el gate al commitear.
- **El cableado escrito es de un formato de runtime concreto.** Aislado en `bloque_sesion`, pero si
  aparece un segundo runtime habrá que escribir su función hermana; la lógica no se toca.

## Cómo diagnosticarlo rápido la próxima vez

1. **«El guard está escrito y no pasa nada»** → antes de leer el guard, mira el fichero de cableado.
   Que el fichero exista y tenga tests no significa que ningún evento lo llame. Medida barata:
   `grep -c <nombre> <ajustes>` en el fichero del proyecto **y** en el del usuario.
2. **«El guard bloquea con un motivo que nadie escribió»** → casi siempre es una regex evaluada sobre
   un bloque de varias órdenes. Parte el bloque y vuelve a juzgar orden por orden.
3. **«El guard deja pasar lo que debía parar»** → mira si una orden anterior del mismo bloque tiene
   permiso. Un permiso que no se acota a su orden cubre a las que van detrás.
4. **«Una ruta relativa se cuela»** → comprueba contra qué directorio se resuelve. El proceso del
   hook y el directorio del evento no tienen por qué ser el mismo, y resolver contra el equivocado
   deja pasar exactamente lo que se quería parar.
5. **«El test del secreto falso bloquea su propio commit»** → compón el valor en tiempo de ejecución
   (`"AKIA" + "0123..."`). La forma se ejercita igual y el literal no existe en el fichero. Meterlo
   en el inventario de hallazgos conocidos sería lo contrario de lo que ese inventario es para.
