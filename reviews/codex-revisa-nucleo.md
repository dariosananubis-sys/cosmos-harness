# Revisión adversarial de `spec/NUCLEO.md`

**Premisa invertida:** `NUCLEO.md` está mal y mi trabajo es demostrarlo.

**Fecha:** 2026-09-01.  
**Pieza revisada:** las ocho secciones completas, contrastadas contra `FRONTMATTER.md`,
`MEDIDOR.md`, `VALIDADOR.md` y `COMPILACION.md`, y contra una implementación ejecutable.

## Veredicto

**No aprobada todavía como especificación cerrada.** Resuelve correctamente B1 y B2 de la revisión
anterior y elimina H1–H5, pero aún permite implementaciones conformes que discrepan en magnitudes o
artefactos observables. Los tres primeros hallazgos requieren una decisión normativa; los demás
pueden cerrarse con una frase cada uno.

## B1 — grave: `exacto` aún no identifica un tokenizador

La sección 4 fija `metodo = "exacto"`, pero no fija algoritmo, vocabulario ni versión. Un
implementador puede usar `cl100k_base`, otro el tokenizador del modelo activo y otro una biblioteca
local distinta. Los tres estarían ejecutando un método exacto y podrían discrepar sobre E16 para el
mismo árbol.

Esto conserva una variante del fallo H2: ya no depende de que exista *algún* tokenizador, pero sí de
cuál haya elegido la implementación. La configuración debe fijar también una identidad normativa,
por ejemplo `tokenizador = "tiktoken/cl100k_base"`, o declarar un único algoritmo exacto obligatorio.
La ausencia de ese tokenizador sí puede seguir fallando en voz alta.

La implementación de esta ronda elige `tiktoken/cl100k_base`; es una decisión de código, no una
conclusión que hoy se pueda deducir de `NUCLEO.md`.

## B2 — grave: no se define qué directorio pertenece a una skill

La sección 5 dice que cada ciudad/pueblo exporta su directorio completo, pero el modelo base define
un nodo como un fichero Markdown y no exige que se llame `SKILL.md`, que viva solo en su directorio
ni que dos nodos aplanables no compartan carpeta.

Con `skills/revisar.md`, son conformes al menos estas lecturas:

1. exportar el directorio `skills/` entero;
2. crear una carpeta sintética que contenga solo `revisar.md`;
3. rechazar el árbol porque falta `revisar/SKILL.md`.

La diferencia es material: cambia lo que llega a la vista plana. Hace falta fijar que el fichero de
una ciudad/pueblo sea `<directorio>/SKILL.md` y que ese directorio sea su unidad exportable, o definir
otra regla equivalente. Esta ronda adopta esa convención en el ejemplo y usa el directorio padre del
fichero como fuente, pero el validador no puede exigirla sin un código/invariante normativa.

## B3 — grave: el orden por rango no ordena `rio`

El catálogo incluye `rio`, pero la sección 1 dice que el agua no tiene ruta y la taxonomía no le da
rango. La sección 2 exige ordenar todo el catálogo por rango. Por tanto no hay una posición deducible
para los ríos, y tampoco es literal la forma `<ruta>: <resumen>` porque un río carece de ruta.

Esta ronda usa `rio/<nombre>` y coloca los ríos después de los sólidos. Otra implementación podría
ponerlos antes o entre pueblos y casas sin contradecir el texto. Hay que fijar ambas decisiones.

## M1 — medio: la unión byte a byte no fija los límites de bloque

`indice(árbol)` termina actualmente en salto de línea. A la vez, la sección 2 manda unir los bloques
con `\n`. No dice si hay que conservar ese terminador y añadir otro, quitarlo antes de unir, incluir
océanos de cuerpo vacío ni qué produce un árbol sin bloques. Con tokenización BPE, dos saltos y uno
pueden medir distinto.

La implementación quita solo los saltos finales del índice, omite bloques vacíos y pone exactamente
un `\n` entre los restantes. Esa secuencia debe escribirse en la norma si de verdad se quiere una
definición byte a byte.

## M2 — medio: “cuyo cuerpo no está” admite identidad o igualdad textual

Si un océano y un nodo local tienen cuerpos byte a byte idénticos, `resto` puede interpretarse de dos
formas: excluir solo el nodo océano, o excluir todo cuerpo cuyo texto ya aparezca en el contexto. La
primera mide unidades de carga; la segunda deduplica por contenido. Esta ronda excluye por identidad
de nodo —solo océanos— porque encaja con “no vuelven a contarse”, pero conviene decirlo.

## M3 — medio: el hash de un symlink no está definido

Para una copia, “contenido actual” sugiere los bytes copiados. Para un symlink puede significar el
texto del enlace o los bytes de su destino. La elección cambia dos casos normativos:

- si se borra el directorio fuente, el enlace queda roto y ya no se pueden hashear sus bytes;
- editar a través del enlace cambia los bytes destino, aunque la sección 7 declara esa edición válida.

Esta ronda hashea el texto del enlace en modo symlink y el árbol de bytes en modo copia. Así puede
borrar un enlace obsoleto roto y no marca como ajena una edición de la verdad. La norma debe fijarlo.

## M4 — medio: un lock huérfano bloquea para siempre

`O_CREAT|O_EXCL` impide dos escritores simultáneos, pero una caída entre crear y retirar el lock deja
un fichero permanente. `NUCLEO.md` no permite distinguir “otra compilación en curso” de un PID muerto
ni define recuperación manual. La implementación falla cerrada y no borra locks ajenos; es segura,
pero operativamente puede exigir intervención sin que el mensaje explique cómo verificarla.

## M5 — medio: una colisión con una entrada ajena no es reparable automáticamente

Si el árbol añade la skill `revisar` y ya existe `destino/revisar` fuera del manifiesto, la regla de
no borrar trabajo ajeno obliga a conservarla. E19 seguirá roja después de `compilar`. No es el
interbloqueo resuelto en la sección 6 —aquí sí falta autoridad—, pero la salida normativa debería
decir que la compilación termina roja y requiere mover o adoptar manualmente la entrada ajena.

## L1 — leve: E04 queda inalcanzable tras E02 con rutas canónicas

Si cada sólido tiene ruta `padre + "/" + nombre`, seguir un padre siempre acorta una ruta válida.
Por tanto un árbol que supera E02 no puede contener un ciclo. E04 sigue siendo defensa útil para un
modelo construido en memoria o corrupto, pero ya no tiene un contraejemplo representable mediante
frontmatter canónico. Conviene documentar que se mantiene como defensa redundante; de lo contrario,
la exigencia histórica de verlo fallar desde disco ya no es satisfacible.

## Lo que intenté tumbar y aguantó

- **Identidad con homónimos.** Construí dos provincias `revision` bajo `modo/uno` y `modo/dos`, y
  casas homónimas debajo. Las rutas completas resolvieron cada referencia una sola vez; B1 anterior
  está realmente cerrado.
- **Descarga negativa.** Repetí el árbol mínimo galaxia + océano que daba `-0.5510204081632653`.
  Con `universo = entrada + resto`, `entrada <= universo` y la descarga queda en `[0, 1]`.
- **Frontmatter contado.** Introduje metadata mucho mayor que el cuerpo. `contexto_inicial` y E17
  consumen la misma función `cuerpo`; el frontmatter no entra en la medición.
- **Interbloqueo E19.** Desincronicé una copia compilada. `validar` dio E19 y `compilar` la reparó
  porque su prevalidación excluyó solo E19; la validación posterior quedó verde.
- **Interbloqueo E15.** Desincronicé el índice. `generar` lo reparó excluyendo solo E15, pero se negó
  a escribir cuando además estaba viva E19.
- **Obsoletos y trabajo ajeno.** Una copia obsoleta intacta se borró por hash; una modificada se
  conservó y salió del manifiesto. Un fichero nunca registrado sobrevivió y fue reportado.
- **Movilidad.** Los symlinks y las rutas escritas en el manifiesto son relativas; mover el árbol no
  incrusta `/Users/...` en el artefacto.

El núcleo es mucho más fuerte que las specs anteriores y sus dos decisiones principales funcionan.
No lo apruebo aún porque B1–B3 vuelven a permitir dos resultados observables para una misma entrada,
que es precisamente el criterio con el que se rechazó la versión anterior.
