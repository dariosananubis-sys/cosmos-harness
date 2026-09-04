# COSMOS — GOAL

Contrato compartido entre **Claude** y **Codex**. Ambos lo leen antes de cada tanda de trabajo y
ambos revisan el trabajo del otro contra él. Si algo del repo contradice este fichero, gana este
fichero. Si este fichero está mal, se corrige aquí primero y luego se toca el código.

---

## 1. Qué se construye

Un **sistema de organización de contexto para agentes de código**, con una taxonomía cosmográfica
de contención estricta. No es documentación bonita: es el mecanismo real por el que un agente sabe
qué cargar y, sobre todo, **qué no existe todavía**.

Producto final: un repo que se puede clonar sobre cualquier proyecto y que deja el harness
organizado por niveles, con carga perezosa real y verificable.

Y encima de ese esqueleto, **un universo de oficios**, cada uno lleno de lo mejor que exista hoy
en GitHub para ese trabajo — herramientas que se ejecutan, no listas de consejos. El mapa está en
`spec/UNIVERSO.md`.

La prueba que decide si algo es un nicho: **¿alguien contrataría esto?** «Bots de trading» sí.
«Ciberseguridad» sí. «Datos» no — nadie contrata «datos»: contrata un pipeline que no se rompa, o un
cuadro de mando que no mienta. Lo que no pasa esa prueba es una categoría temática, y una categoría
no acota nada al entrar en ella.

Las dos mitades parecen tirar en contra: cuantos más oficios, más contexto. **Solo lo hacen si todo
lo que existe está cargado.** Con contención estricta, el universo puede crecer sin límite —más
oficios no cuestan nada al entrar— mientras lo que se paga se acota a **un oficio**: el coste de
entrada es el del oficio activo más poblado (≈28 tokens por herramienta, medido el 2026-09-03), no
el del universo. Ese es el proyecto entero, en una frase, y por eso hay sitio para unas pocas
herramientas por oficio, no cincuenta.

Dos exigencias que el encargo fija y que no son negociables:

- **Capacidad y criterio van separados.** Un oficio que sabe programar mucho y no sabe qué no
  escribir produce más código de más, no menos. Por eso **el código vive dentro de cada nicho** (el
  de un exploit no se parece al de un tema de WordPress) y **`criterio` es un mar** que los moja a
  todos: poda en todos los sitios a la vez sin que nadie tenga que invocarlo.
- **Los oficios se combinan.** La contención dice dónde vive algo y cuándo se carga, **nunca** con
  quién se junta. Detalle y mecanismo en `spec/COMPOSICION.md`.
- **Cada nicho apunta a sus vecinos y no duplica nada.** Un trabajo real cruza varios; el nicho lo
  declara con `usa:`, que sugiere sin arrastrar carga. Una herramienta vive en **un solo sitio**:
  cero repetidos es regla dura.
- **El catálogo es el coste real.** Lo que se paga por existir no se escribe aquí: se ejecuta
  `cosmos medir`. Un número copiado a mano en una spec envejece en silencio y acaba mintiendo —
  ya pasó una vez (hallazgo H11). Lo que sí es permanente: hay sitio para unas pocas herramientas
  por oficio, no cincuenta, y eso convierte «lo mejor del mundo» en una decisión y no en una
  acumulación.

## 2. El principio rector (lo que de verdad importa)

> **No se le pide al agente que gaste menos. Se elimina la razón para gastar de más.**

Y el matiz decide el proyecto entero, así que va antes que nada — corregido por Darío el
2026-09-02: *«yo no te dije que se centre en mínimo coste, sino que no hubiese costes innecesarios,
que es distinto»*.

**Coste mínimo** y **cero coste innecesario** llevan a sitios opuestos. Si la métrica es el mínimo,
el óptimo perfecto es un harness vacío: cero tokens, cero herramientas, cero utilidad. Un sistema
que solo mide lo que gasta acaba premiando al que no tiene nada.

Lo que se persigue es otra cosa: **que esté todo lo que hace falta, y nada que no lo haga**. Una
herramienta que se usa está bien pagada aunque cueste; una que nadie invoca es cara aunque cueste
poco. Por eso **lo que falta también es un fallo**, y por eso el presupuesto no es un objetivo a
batir sino un techo que obliga a elegir.

El listón, dicho por él: **el harness más completo que exista**. No el más barato.

Una regla que dice «sé breve», «no leas ficheros enteros», «usa pocas tools» es una **exhortación**:
depende de que el modelo se acuerde, y el modelo no se acuerda. Es la causa de que los harness
crezcan hasta 30k tokens de prólogo y nadie sepa por qué.

COSMOS es **estructural**: en cada nivel, lo que no toca todavía **no está cargado**, así que no hay
nada que leer de más, nada que resumir de más y nada que ignorar. La frugalidad no es una virtud
que se pide — es una propiedad de la forma.

Tres corolarios, y son de obligado cumplimiento en todo lo que se escriba aquí:

1. **Si una regla tiene que recordarse, está mal puesta.** Se convierte en estructura (un fichero
   que solo se carga en su ámbito) o en guardarraíl (algo que falla solo), nunca en un párrafo
   pidiendo buen comportamiento.
2. **Un nivel no describe a sus hijos, los nombra.** Describirlos es cargarlos. El índice de una
   galaxia dice qué sistemas hay, no qué hace cada skill de cada sistema.
3. **Lo caro se paga al bajar, no al entrar.** El coste de un nivel se asume cuando el agente
   decide entrar en él, y con el contexto ya justificado.

## 3. La taxonomía (aprobada por Darío, 2026-09-01)

Dos familias. **Lo sólido contiene** — todo está dentro de otra cosa, sin excepción.
**El agua atraviesa** — no contiene a nadie, baña a varios.

### Sólido — la jerarquía de contención

| Nivel | Qué es | Contiene |
|---|---|---|
| **Universo** | Todo. Hay uno. | Galaxias |
| **Galaxia** | Una familia de oficios afines | Sistemas solares |
| **Sistema solar** | Un oficio por el que te contratan (los de `spec/UNIVERSO.md`) | Planetas |
| **Estrella** | El contexto que ilumina ese sistema: su `CLAUDE.md` | — (irradia) |
| **Planeta** | Un proyecto concreto | Continentes |
| **Luna** | Un subagente que orbita ese planeta | — (orbita) |
| **Continente** | Una disciplina dentro del oficio (ofensiva, defensiva, análisis) | Países |
| **País** | Una familia de capacidades, incluido el **código propio del nicho** | Provincias |
| **Provincia** | Un grupo de skills hermanas | Pueblos |
| **Pueblo** | Una skill atómica. Es el suelo del árbol | — |

Regla dura de contención: **ningún elemento existe fuera de un padre.** Un pueblo huérfano es un
error del sistema, no un caso aceptable, y el validador lo trata como tal.

### Agua — lo transversal

| Nivel | Qué es | Alcance |
|---|---|---|
| **Océano** | Regla global, innegociable | Todo el universo |
| **Mar** | Regla transversal a varios oficios (`criterio`, `pruebas`…) | Regional |
| **Lago** | Regla local, de un país o provincia | Acotado |
| **Río** | Un comando: camino de ejecución que se invoca a propósito | Recorre |
| **Lluvia** | Memoria: se evapora del contexto y precipita donde hace falta | Cae donde toca |

El agua **nunca** define jerarquía. Un lago no es «menos importante» que un océano: es que **moja
menos superficie**. Confundir alcance con importancia es el error clásico que convierte cualquier
regla local en un párrafo global, y así es como un prólogo llega a 30k tokens.

## 4. Reglas de carga (esto es el producto, no la tabla de arriba)

| Nivel | Cuándo entra en contexto | Qué se ve de él antes de entrar |
|---|---|---|
| Universo / Galaxia | Siempre | Todo (es minúsculo por diseño) |
| Océano | Siempre | Todo |
| Sistema solar | Al entrar en ese oficio | Su nombre y una línea |
| Estrella | Con su sistema | — |
| Planeta | Al tocar un path suyo | Su nombre |
| Continente / País / Provincia | Al descender | Su nombre |
| Pueblo | Al invocarse | Nombre + una línea |
| Mar / Lago | Por `paths:` que matchea | Nada |
| Río | Por invocación explícita | Nombre + una línea |
| Lluvia | Por consulta explícita | Nada |

Lo que **nunca** ocurre: que el contexto inicial contenga el cuerpo de un pueblo, la descripción de
un pueblo de otro sistema solar, o un lago que no moja el path que se está tocando.

`ciudad` y `casa` estaban en esta tabla y se retiraron el 2026-09-01: nunca tuvieron un nodo en
ninguno de los dos árboles del repositorio. El motivo y el camino de vuelta, en
`spec/TAXONOMIA.md`. Un nivel sin un solo nodo no es una reserva: es una promesa que el lector se
cree.

## 5. Prohibiciones duras del repo

Este repo es **público-limpio y genérico**. Fuera de cualquier organización, cliente o negocio.

- Cero credenciales, tokens, claves, cookies o rutas de vault. Ni de ejemplo.
- Cero nombres de cliente, dominios de cliente, datos personales o de facturación.
- Cero skills de negocio importadas tal cual. Si un patrón vale, se **reescribe genérico**.
- Cero dependencias de pago y cero servicios que pidan tarjeta.
- Cero red en el camino crítico: el validador corre offline.

## 6. Reparto Claude / Codex

Nadie valida su propio trabajo. El que escribe una pieza **no** es el que la aprueba.

| | Claude | Codex |
|---|---|---|
| **Escribe** | Taxonomía, contratos, esquemas, especificación del validador, documentación | Implementación: validador, generador de índices, medidor, tests |
| **Revisa** | Todo lo que escribe Codex, con premisa invertida | Todo lo que escribe Claude, con premisa invertida |
| **No puede** | Aprobar su propia especificación | Aprobar su propia implementación |

**Premisa invertida**: el revisor entra dando por hecho que la pieza está mal y su trabajo es
demostrarlo. Solo puede aprobarla **después** de haber intentado tumbarla y no haber podido, y
tiene que decir qué intentó.

## 7. Definición de terminado

Una pieza está hecha cuando, y solo cuando:

1. El validador pasa en verde y **se ha visto fallar a propósito** (existe una prueba que lo rompe
   y confirma que el rojo sale).
2. El medidor da un número de tokens de contexto inicial obtenido con el método declarado en
   `cosmos.toml`, con su margen calibrado publicado y aplicado al veredicto, y nunca un
   `no_medido` sumado como cero. «Medido, no estimado» exigía un tokenizador que §5 prohíbe
   pagar y dejaba toda pieza del repo sin poder estar terminada (auditoría A-03, 2026-09-03).
3. El otro (Claude o Codex) la ha revisado con premisa invertida y ha dicho qué intentó.
4. No hay ningún elemento huérfano ni ninguna regla que dependa de que alguien se acuerde.

## 8. Estado

El progreso vive en `PROGRESS.md`. Las revisiones cruzadas, en `reviews/`. Ninguna de las dos
partes declara nada terminado en el chat: se declara en el fichero, y el otro lo comprueba.
