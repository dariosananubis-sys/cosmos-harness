# La taxonomía — normativo

`GOAL.md` §3 define los niveles. Este fichero define **cómo se decide** en qué nivel va cada cosa.
Sin esa parte, una taxonomía es decorativa: todo el mundo entiende el dibujo y nadie sabe dónde
poner lo que tiene delante, así que cada uno improvisa y a los dos meses el árbol es un montón.

## La pregunta que separa las dos familias

Antes de elegir nivel, hay una sola pregunta:

> **¿Esto contiene cosas, o atraviesa cosas?**

Si contiene, es sólido y necesita un `padre`. Si atraviesa, es agua y necesita un `moja`.

Un error frecuente es meter una regla de estilo como si fuera un pueblo, dentro de una provincia.
Una regla no contiene nada: se aplica a lo que toque el path. Es agua. Ponerla como sólido la deja
invisible cuando hace falta y presente cuando estorba, que es lo peor de los dos mundos.

## Sólidos: la regla del agrupamiento real

**Un nivel existe cuando agrupa de verdad.** Si un nivel tiene un solo hijo, no está agrupando: está
estorbando, y encima cobra —su `resumen` se paga cada vez que alguien mira ese tramo del árbol.

Criterio operativo, y es tajante: **un nivel intermedio con un único hijo se borra y su hijo sube.**
El validador no puede exigirlo (hay excepciones legítimas cuando se sabe que llegan hermanos la
semana que viene), pero es el primer sitio donde mirar cuando la entrada se pasa de presupuesto.

### Qué es cada nivel, en una línea de decisión

| Nivel | Se elige cuando… |
|---|---|
| **galaxia** | Es la instalación entera. Hay una y no se decide: se es o no se es |
| **sistema-solar** | Cambia el **modo de trabajo**: otras herramientas, otro vocabulario, otro tipo de resultado |
| **planeta** | Es un **proyecto** con vida propia: se puede terminar, abandonar o entregar |
| **continente** | Es una **disciplina** dentro del proyecto: frontend, datos, seguridad, QA |
| **pais** | Es una **familia de capacidades** que comparten tecnología o modelo mental |
| **provincia** | Es un **grupo de skills hermanas** que casi siempre se usan juntas |
| **pueblo** | Es una skill **atómica**: se invoca entera o no se invoca. Es el suelo |

Un pueblo es el nivel más profundo: se invoca entero. Si necesita ficheros propios —configuración,
plantillas, guiones—, van **dentro de su directorio** y no son nodos: `compilar` exporta el
directorio completo, así que llegan con la skill sin que nadie tenga que declararlos.

### La frontera sistema-solar / planeta

Un sistema solar es un **modo**; un planeta es un **encargo**. «Trabajo web» es un modo: cambia el
vocabulario y las herramientas. «La web de tal proyecto» es un encargo: se acaba.

La prueba: si dentro de cinco años seguirá existiendo, es sistema solar. Si algún día se dará por
terminado y se archivará, es planeta.

Esto importa porque los planetas **nacen y mueren constantemente**, y los sistemas solares casi
nunca. Un árbol que confunde las dos cosas necesita reorganizarse cada vez que entra un proyecto
nuevo, y una estructura que hay que reorganizar a menudo acaba no reorganizándose nunca.

## Adjuntos: estrella y luna

No contienen ni atraviesan: **acompañan**.

- **Estrella** — el contexto permanente de un sólido, su `CLAUDE.md`. Se carga con él y solo con él.
  Una por sólido, como máximo.
- **Luna** — un subagente propio de un planeta.

La regla de oro de una estrella: **contiene lo que es cierto para todo su sólido y falso fuera de
él.** Si es cierto también fuera, sube (o es un mar). Si solo es cierto para un hijo, baja.

Este es, literalmente, el mecanismo por el que un `CLAUDE.md` raíz engorda hasta 17.000 bytes: se
va escribiendo ahí lo que en realidad solo aplicaba a un rincón, porque en el momento era el único
sitio que existía y escribirlo ahí funcionaba. **Funciona y por eso es tan caro**: el fallo no da
la cara nunca, solo cobra.

## Aguas: alcance no es importancia

| Nivel | Se elige cuando… |
|---|---|
| **oceano** | Es cierto siempre, en todas partes, y su incumplimiento es grave |
| **mar** | Es cierto en un sistema solar o en una disciplina entera |
| **lago** | Es cierto en un país o en una provincia |
| **rio** | Es un camino de ejecución que se invoca a propósito: un comando |
| **lluvia** | Es un hecho recordado que se consulta cuando hace falta: memoria |

**Un océano es caro y para siempre.** Cada uno se paga en cada sesión y en cada subagente, sin
excepción. Por eso el validador los cuenta y por eso hay un umbral.

La pregunta antes de crear uno: *«¿qué pasa si esto solo se carga cuando se toca su área?»* Si la
respuesta es «que a veces no se cargaría cuando hace falta», es océano de verdad. Si la respuesta
es «nada, pero me quedo más tranquilo», **no lo es**: eso es ansiedad, y la ansiedad en un harness
se paga en tokens en cada sesión, para siempre, a cambio de nada.

### Los tres océanos que casi siempre son legítimos

1. Los que evitan **daño irreversible** (borrar, pagar, publicar).
2. Los que fijan la **identidad de la instalación** (qué es esto, quién manda).
3. Los que definen **cómo se decide** cuando hay conflicto entre reglas.

Todo lo demás, empieza siendo mar o lago y **sube solo si se demuestra** que hizo falta y no estaba.
El sentido de la prueba importa: se sube por una fuga observada, no por una que se imagina.

## Antipatrones

| Antipatrón | Cómo se reconoce | Qué hacer |
|---|---|---|
| **Océano encubierto** | Un mar o lago con `moja: ["**"]` | El validador lo rechaza (E11). Acotar el glob o asumir el coste |
| **Nivel de relleno** | Un nivel con un solo hijo | Borrarlo, subir el hijo |
| **Resumen que describe hijos** | «Provincia de navegación: contiene agent-browser, playwright y curl» | Describir el **grupo**, no la lista. La lista está un nivel abajo |
| **Estrella que ha engordado** | Un `CLAUDE.md` con secciones que solo aplican a un hijo | Bajar cada sección a su sitio |
| **Pueblo huérfano** | Una skill sin `padre` | El validador lo rechaza (E01) |
| **Taxonomía completa por obligación** | Cadenas de 7 niveles con provincias de un hijo | Saltar niveles: `rango(padre) < rango(hijo)` lo permite |
| **Agua como sólido** | Una regla puesta como pueblo dentro de una provincia | Convertirla en lago con su `moja` |

## Cómo se decide, en la práctica

Ante algo nuevo, cuatro preguntas en orden:

1. **¿Contiene o atraviesa?** → sólido o agua.
2. Si atraviesa: **¿dónde deja de ser cierto?** → ahí está su alcance, y de ahí sale `moja`.
3. Si contiene: **¿qué es lo más pequeño que lo contiene entero?** → ese es su padre.
4. **¿Agrupa de verdad?** Si es un nivel nuevo con un solo hijo, no lo crees todavía.

La cuarta se salta siempre y es la que mantiene el árbol sano. Es la que impide que la taxonomía se
convierta en un ejercicio de rellenar casillas, que es la forma más común en que una buena
estructura se vuelve una mala.

## Lo que se retiró, y qué haría falta para traerlo de vuelta

**`ciudad` y `casa`, el 2026-09-01 (hallazgo H20).** La taxonomía tenía nueve sólidos; tiene siete.

El motivo no es de gusto, es de cuenta: ninguno de los dos tenía **un solo nodo** ni en la galaxia
ni en el árbol de ejemplo, ninguno aparecía en un test que lo creara, y las 209 skills montadas entonces (hoy las cuenta `cosmos estado`) son
un único fichero cada una —la mayor, 3,5 KB—. La prueba objetiva que separaba ciudad de pueblo
(«¿hay algo que se pueda no cargar?») no la había ganado nadie nunca, y estaba documentada aquí
mismo como la frontera «que se discute a menudo»: una duda recurrente que no resolvía ningún caso
real.

Lo que costaban no era contexto —ni `ciudad` ni `casa` aparecen jamás en el catálogo— sino
**crédito**: quien leía esta tabla creía que había skills compuestas, y no las hay.

Qué haría falta para traerlas de vuelta, en este orden y no en otro:

1. **Una skill concreta** cuyo contenido se pueda no cargar entero: partes que se abren según el
   caso, no un fichero largo. El nodo primero, el nivel después.
2. Volver a meter `"ciudad"` y `"casa"` en `NIVELES_SOLIDOS` (`cosmos/modelo.py`), `ciudad` en
   `NIVELES_APLANADOS` (`cosmos/compilar.py`, `cosmos/validar.py`, `puente/proyectar.py`) y en
   `con_resumen`/`invocables` de `catalogo_visible` (`cosmos/medir.py`).
3. Reponer las filas en `GOAL.md` §3, `spec/FRONTMATTER.md` (rangos), `spec/NUCLEO.md` §2 y §5 y
   `README.md`, y ajustar el número de niveles en `spec/VALIDADOR.md` (E09).

Mientras eso no exista, la regla de arriba manda: **un nivel existe cuando agrupa de verdad**, y
tener sitio reservado por si acaso es la versión lenta del mismo error.

## Lo que se necesita desde varios sitios es agua, no una copia

Si algo hace falta a menudo desde varios sitios del árbol, **es agua y quiere un `moja`**, no una
copia en cada sitio. Esta regla vivía en `oceano/descender` y se pagaba en toda sesión y todo
subagente (144 tokens); es taxonomía, y su sitio es este fichero (auditoría A-11, revisión R-05).
Lo que la hace estructural no es leerla: es E17, que pone en rojo la afirmación repetida con otras
palabras entre dos nodos que se pagan a la vez, y E18, que impide dos pueblos con el mismo nombre.

## `cosecha/` se retiró: una herramienta vive en un solo sitio

`cosecha/` fue la cantera de importación de las herramientas propias (2026-09-01/02) y ninguna spec la
nombraba. Al cerrar el ciclo 2 de la auditoría (2026-09-03) duplicaba byte a byte 76 de sus 80 ficheros
dentro de `galaxia/pueblos/*/scripts`, y la corrección de seguridad F-08 hubo que aplicarla dos veces
por esa duplicación (revisión §4.3). GOAL §1: «una herramienta vive en un solo sitio». El guion de
cada pueblo vive en el directorio del pueblo; los cuatro ficheros que no eran de ningún pueblo eran
lanzadores de una máquina concreta, fuera de un repo genérico. Retirada a la papelera, no borrada.
