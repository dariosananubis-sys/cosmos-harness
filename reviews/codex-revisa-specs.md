# Revisión adversarial de GOAL.md y spec/*.md

Fecha: 2026-09-01. Revisor: Codex. Premisa de entrada: **las specs están mal hasta que resistan
intentos concretos de falsación**. Esta revisión no aprueba la implementación de Codex; por el
reparto de `GOAL.md`, esa aprobación corresponde a Claude.

## Veredicto

No apruebo aún el conjunto normativo. Hay dos bloqueos de arquitectura y varias ambigüedades que
permiten implementaciones incompatibles:

1. La referencia `<nivel>/<nombre>` no identifica un padre de forma unívoca cuando E06 permite el
   mismo nombre bajo padres distintos. El árbol puede ser ambiguo aun estando verde.
2. `compilar` debe fallar si el árbol no valida, pero E19 hace inválida precisamente la vista que
   `compilar` tendría que reparar. Sin una excepción explícita, el comando queda bloqueado por su
   propio guardarraíl.

E17 y E18 se pudieron implementar en esta ronda, pero fue necesario escoger criterios que la spec
no fija: qué cuenta como nodo siempre cargado, dónde configurar el umbral y qué niveles se aplanan.

## Hallazgos transversales

### B1 — La identidad de los nodos no alcanza para reconstruir un árbol

**Intento:** construí dos provincias `provincia/revision`, cada una bajo un planeta distinto, algo
permitido por E06 porque no son hermanas. Después añadí un pueblo con
`padre: provincia/revision`.

**Resultado:** las dos provincias tienen la misma referencia normativa. E02 no puede decidir cuál
es el padre; E03 ve dos candidatos y E04 puede recorrer uno u otro. La afirmación de
`FRONTMATTER.md` de que el árbol se deduce del frontmatter no se cumple de forma determinista.
E18 solo corrige la colisión futura de skills y no esta colisión presente del modelo.

**Corrección necesaria:** o bien la referencia incluye la ruta ancestral, o bien los nombres de
todos los sólidos que pueden ser destino son globalmente únicos, o existe un identificador estable
global separado de `nombre`.

### B2 — El conjunto de contexto inicial no tiene una única definición

**Intento:** enumeré literalmente lo marcado como siempre visible en `GOAL.md` y lo comparé con la
fórmula de `MEDIDOR.md`.

**Resultado:** `GOAL.md` dice que la galaxia entra entera y que una estrella se carga con su sólido.
`MEDIDOR.md` cuenta índice + océanos + catálogo, pero no dice si cuenta el cuerpo de la galaxia ni
una estrella que ilumina la galaxia. Además, el índice ya contiene nombres/resúmenes de sistemas y
el catálogo puede volver a contarlos. Dos implementadores obtendrían números distintos y ambos
podrían defenderlos con las specs.

**Corrección necesaria:** definir una función normativa `contexto_inicial(arbol) -> secuencia de
bytes`, con orden y ausencia/presencia de frontmatter, y reutilizarla en medidor y E17.

## GOAL.md

- **Dos familias frente a tres comportamientos.** Intenté clasificar estrella y luna con la regla
  “contiene o atraviesa”. No hacen ninguna de las dos cosas; otras specs las llaman adjuntos. La
  frase “dos familias” no cubre los 16 niveles.
- **“Ningún elemento existe fuera de un padre” es falsa para agua y adjuntos.** Probé a exigir
  `padre` a un océano, una luna y una estrella: contradice sus propios campos `moja`, `orbita` e
  `ilumina`. Debe decir “ningún sólido salvo galaxia”.
- **Regla recordada que no se vuelve estructura.** El objetivo prohíbe reglas que dependan de
  memoria, pero `TAXONOMIA.md` manda borrar niveles de un hijo y a la vez declara que el validador
  no puede exigirlo. Queda como exhortación normativa.
- **Privacidad interna contradictoria.** La taxonomía se atribuye a una persona por nombre mientras
  el mismo contrato exige un repo público genérico y sin datos personales. No copié ese nombre a
  código, ejemplo ni pruebas.
- **Intento que resistió:** intenté crear un sólido válido con padre de rango igual o inferior; la
  regla estricta de rangos lo rechaza de forma clara y permite saltar niveles sin relleno. Esa parte
  sí es consistente entre GOAL, FRONTMATTER y E03.

## spec/FRONTMATTER.md

- **Límite fijo o configurable.** Aquí `resumen` tiene máximo 120; `VALIDADOR.md` dice que el umbral
  es configurable. Con `resumen = 200`, una implementación literal de una spec acepta 150
  caracteres y otra los rechaza.
- **Lago no operativo.** Intenté distinguir mecánicamente “glob acotado” de “raíz de un sistema
  entero”. No hay asociación normativa entre paths y sistemas, ni patrón prohibido aparte de `**`,
  ni código de error para esta regla. `foo/**` puede ser un lago o un mar según una interpretación
  humana.
- **Esquema incompleto.** Un río “lleva `invoca`”, pero E10 solo exige `moja`; no se asignaba código
  a `invoca` ausente hasta añadir E00. Tampoco se aclara si campos desconocidos deben rechazarse ni
  si estrella/luna/agua comparten alguna regla de unicidad de nombres.
- **Prohibiciones semánticas no validables offline.** Intenté detectar que un resumen describe a sus
  hijos y que un cuerpo contiene nombres reales sin listas externas o un modelo. No existe criterio
  mecánico suficiente. Hoy son políticas editoriales, no invariantes inevitables.
- **Intento que resistió:** el subconjunto YAML restringido (escalares, listas de escalares y
  comentarios) es implementable con stdlib y permite devolver fichero/línea ante sintaxis inválida.

## spec/TAXONOMIA.md

- **Mandato tajante con excepción temporal ilimitada.** Intenté aplicar “un nivel de un hijo se
  borra” al ejemplo mínimo. La frase siguiente permite conservarlo si se esperan hermanos “la
  semana que viene”, sin fecha ni comprobación. Cualquier nivel de relleno puede justificarse así.
- **Sistema frente a planeta depende de una predicción.** La prueba de “existirá dentro de cinco
  años” no produce un resultado verificable para modos experimentales o proyectos permanentes.
  Dos autores razonables clasificarían distinto el mismo nodo.
- **Agua con varios alcances.** Intenté clasificar una regla que moja dos países de sistemas
  distintos, pero no toda la galaxia. No queda claro si es mar, dos lagos o océano; la pregunta
  “dónde deja de ser cierto” no selecciona un único nivel.
- **Intento que resistió:** la frontera ciudad/pueblo basada en carga parcial o total es más
  operativa que una frontera por tamaño y no contradice la posibilidad de saltar niveles.

## spec/VALIDADOR.md

- **Faltaba código para sintaxis/esquema.** Hice un Markdown con lista sin cerrar. El cargador sabe
  que falla, pero E01–E16 no tenían código donde reportarlo. Esta ronda añade E00 en implementación;
  la tabla normativa aún debe incorporarlo expresamente.
- **E04 no se puede aislar de E03.** Intenté crear un ciclo que respetase rangos estrictos. Es
  imposible: los rangos aumentarían en cada arista y tendrían que volver al inicial. E04 es una
  defensa útil, pero todo caso suyo viola también E03; la exigencia “un árbol que viole cada
  invariante” no puede significar “solo esa invariante”.
- **E06 no define su dominio.** Agua y adjuntos no tienen `padre`. Aplicar “todo `nombre` es único
  dentro de su padre” a los 16 niveles no tiene significado único. La implementación lo aplica a
  sólidos no raíz; la spec debe decirlo.
- **E10 no recoge el océano mal declarado.** Probé `cosmos: oceano` con `moja: ["src/**"]`: declara
  lista no vacía y pasa la redacción de E10, pero viola FRONTMATTER, que exige exactamente `["**"]`.
- **E11 admite equivalentes globales.** Probé `moja: ["**/*"]` y `moja: [".", "**/*"]`. La spec
  ordena igualdad literal, así que el océano encubierto puede eludir el guardarraíl dependiendo de
  la semántica glob futura.
- **`galaxia_lineas` no alimenta ninguna invariante.** Subí el índice por encima del umbral: E15 solo
  compara sincronización y E16 solo tokens. La configuración promete un umbral que no pone rojo.
- **Presupuesto con error desconocido.** En ausencia de calibración, E16 toma una decisión dura con
  una estimación `±desconocido`. Probé el borde 3.999/4.001: no existe regla para falsos verdes o
  falsos rojos dentro del margen. Un tokenizador local tampoco implica que sea el del modelo real.
- **`--rapido` está citado por GUARDARRAILES pero no definido aquí.** No se sabe qué invariantes
  omite ni si un rojo E15/E16/E17 puede ocultarse al inicio de sesión.
- **Intento que resistió:** E15 es determinista si índice y serialización están fijados; editar un
  byte del índice genera un rojo reparable mediante regeneración.

## spec/MEDIDOR.md

- **Doble conteo posible.** El índice de galaxia nombra sistemas con su resumen y el catálogo de
  visibles también los puede incluir. Sumarlos como piezas independientes paga dos veces la misma
  cadena salvo que el runtime realmente inyecte ambos artefactos, algo no especificado.
- **Descarga fuera de rango.** Construí un árbol diminuto cuyo índice generado es mayor que la suma
  de contenidos. `1 - entrada/arbol` da un valor negativo. La spec solo trata división por cero y
  no define si una descarga negativa se conserva, se limita a cero o revela una métrica mal
  planteada.
- **Calibración exigida pero no entregable en todos los entornos.** Si no hay tokenizador local, el
  método aproximado debe publicar `±desconocido`, pero el test 2 exige comparar contra exacto y solo
  permite saltar por falta de tokenizador. Esto es coherente como salto visible, aunque deja la
  heurística sin margen hasta que aparezca un entorno con tokenizador.
- **Unidad exacta indefinida.** “tiktoken u otro” no fija modelo/codificación. Dos métodos exactos
  pueden dar números distintos y ambos cumplir la spec.
- **Intentos que resistieron:** `no_medido` en lugar de cero y `no_definida` para árbol vacío son
  requisitos inequívocos; los rompí en pruebas conceptuales y los tests los detectan.

## spec/GUARDARRAILES.md

- **Inevitable pero opcional.** Intenté una instalación sin enganches: está permitida, aunque la
  propia spec dice que equivale al sistema fallido que motivó el documento. El producto sigue
  dependiendo de que alguien ejecute `enganchar` una vez.
- **Enganches sin contrato de plataforma.** No se define cómo insertar el arranque de sesión, cómo
  convivir con un pre-commit existente, ni qué ejecutable/ruta funciona en un clon sin instalar.
- **“Append-only” no es una propiedad.** Un fichero local ordinario puede truncarse o editarse. No
  hay bloqueo para escritores concurrentes, formato canónico, zona horaria ni defensa ante reloj
  atrasado. Intenté dos saltos simultáneos y el resultado no está especificado.
- **Ámbito de salto peligroso.** “Un código concreto” permite en teoría saltar E00, E02 o E05. No se
  define qué códigos son insaltables ni cómo identificar una instancia si hay veinte errores E16.
- **E17 no detecta paráfrasis general.** Reescribí “conserva una copia antes de cambiar” como
  “garantiza la reversión previa a cualquier modificación”: Jaccard de 4-gramas es cero. El método
  detecta texto parcialmente compartido, no paráfrasis semántica; la propia limitación sobre
  reformulación total admite el hueco, pero el lema “E17 caza la paráfrasis” lo exagera.
- **Documentos cortos y dilución.** Dos políticas idénticas de tres palabras producen cero shingles.
  Una política duplicada dentro de dos documentos largos puede quedar bajo 0,25 porque Jaccard
  divide por todo el documento. Ambos costes escapan.
- **Conjunto de comparación y configuración indefinidos.** “Nodos siempre cargados” no enumera
  galaxia, estrella de galaxia, resúmenes del catálogo ni índice. Tampoco dice en qué tabla TOML
  vive `umbral_solapamiento`. Esta ronda usa cuerpos de galaxia/océanos/estrella de galaxia y
  `[guardarrailes].umbral_solapamiento`, como decisión provisional.
- **“Frases que más pesan” carece de peso.** Todos los shingles tienen cuatro palabras y no se
  define frecuencia, longitud de corrida o ponderación. Ordenarlos de varias formas cumpliría la
  frase.
- **Intento que resistió:** limitar E17 a contenido simultáneo evita falsos positivos entre skills
  perezosas; el control con dos pueblos de contenido idéntico no genera E17.

## spec/COMPILACION.md

- **Interbloqueo E19/compilar.** Edité conceptualmente una copia plana. E19 vuelve rojo el árbol;
  la regla 1 obliga a `compilar` a fallar antes de tocar nada; por tanto no puede reparar la vista.
  Debe validar E00–E18 antes de compilar, regenerar y comprobar E19 después, o definir una excepción
  equivalente. El mismo patrón debe aclararse para `generar` frente a E15.
- **No se define qué se aplana.** Probé ciudad, pueblo, casa y río. El texto habla de skills y pone
  pueblos como ejemplo, pero no enumera niveles ni archivos que se exportan. E18 no tiene dominio
  matemático hasta hacerlo. Esta ronda adopta provisionalmente `ciudad` y `pueblo`.
- **Faltan claves TOML de compilación.** `--destino` dice usar lo indicado en `cosmos.toml`, pero la
  configuración normativa no contiene destino, modo ni ruta del manifiesto.
- **Ciclo de vida de entradas antiguas.** Si una skill compilada se elimina del árbol, el manifiesto
  dice que el compilador la creó, pero “nunca borra lo que no ha creado” no dice explícitamente si
  debe borrar esa entrada obsoleta. Sin hacerlo, E19 queda permanente; haciéndolo, falta definir la
  comprobación de que nadie la reemplazó.
- **Atomicidad y concurrencia.** Interrumpí conceptualmente la compilación entre crear entradas y
  escribir manifiesto. No hay staging, rename atómico ni recuperación. Dos compiladores simultáneos
  también pueden perder el manifiesto.
- **Symlink sin semántica completa.** No se fija si el enlace es relativo/absoluto, qué ocurre si el
  destino está dentro del árbol, cómo tratar enlaces contenidos por una skill, ni si editar a
  través del enlace cuenta como editar verdad o artefacto.
- **Modo copia sin definición de identidad.** No se especifica si copia un `SKILL.md`, un directorio
  entero, permisos, ficheros ocultos o enlaces. Por ello E19 tampoco puede definir igualdad byte a
  byte de la vista.
- **Intentos que resistieron:** el mensaje E18 con ambas rutas elimina una ambigüedad operativa real;
  la preservación de archivos ajenos y el modo seco son criterios verificables una vez definidos
  manifiesto y dominio de copia.

## Cambios normativos mínimos que desbloquean la siguiente ronda

1. Hacer globalmente inequívocas las referencias de padre.
2. Definir `contexto_inicial` byte a byte y reutilizarlo en medición/E17.
3. Incorporar E00 y precisar dominio de E06, océano en E10 y efecto de `galaxia_lineas`.
4. Enumerar nodos siempre cargados y ubicación TOML de E17.
5. Enumerar exactamente qué se aplana y qué bytes/directorios produce cada entrada.
6. Permitir que `compilar` repare E19 sin ignorar E00–E18 y definir actualización atómica del
   manifiesto.

Hasta resolver 1 y 2, dos validadores conformes pueden discrepar sobre el mismo árbol. Hasta
resolver 5 y 6, E19 y `compilar` no tienen una implementación única y segura.
