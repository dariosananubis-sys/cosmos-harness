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

Y encima de ese esqueleto, **un universo de oficios**: mínimo veinte ámbitos especializados, cada
uno lleno de las mejores herramientas que existan hoy para ese trabajo — no listas de consejos,
herramientas que se ejecutan. El mapa está en `spec/UNIVERSO.md`.

Las dos mitades parecen tirar en contra: cuantos más oficios, más contexto. **Solo lo hacen si todo
lo que existe está cargado.** Con contención estricta, el universo puede crecer sin límite mientras
el coste de entrada se queda quieto. Ese es el proyecto entero, en una frase.

Dos exigencias que el encargo fija y que no son negociables:

- **Capacidad y criterio van separados.** Un oficio que sabe programar mucho y no sabe qué no
  escribir produce más código de más, no menos. Por eso `codigo` y `criterio` son dos sistemas
  distintos que se cargan juntos.
- **Los oficios se combinan.** La contención dice dónde vive algo y cuándo se carga, **nunca** con
  quién se junta. Detalle y mecanismo en `spec/COMPOSICION.md`.

## 2. El principio rector (lo que de verdad importa)

> **No se le pide al agente que gaste menos. Se elimina la razón para gastar.**

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
| **Sistema solar** | Un dominio de trabajo (Web, Datos, Infra, Estudio) | Planetas |
| **Estrella** | El contexto que ilumina ese sistema: su `CLAUDE.md` | — (irradia) |
| **Planeta** | Un proyecto concreto | Continentes |
| **Luna** | Un subagente que orbita ese planeta | — (orbita) |
| **Continente** | Una disciplina dentro del planeta (frontend, SEO, QA) | Países |
| **País** | Una familia de capacidades (WordPress, Elementor) | Provincias |
| **Provincia** | Un grupo de skills hermanas | Ciudades y pueblos |
| **Ciudad** | Una skill grande, con sub-skills y referencias propias | Pueblos, casas |
| **Pueblo** | Una skill atómica | Casas |
| **Casa** | Un fichero de referencia dentro de la skill | — |

Regla dura de contención: **ningún elemento existe fuera de un padre.** Un pueblo huérfano es un
error del sistema, no un caso aceptable, y el validador lo trata como tal.

### Agua — lo transversal

| Nivel | Qué es | Alcance |
|---|---|---|
| **Océano** | Regla global, innegociable | Toda la galaxia |
| **Mar** | Regla de un sistema solar o continente | Regional |
| **Lago** | Regla local, de un país o provincia | Acotado |
| **Río** | Un comando / slash: camino de ejecución que conecta ciudades | Recorre |
| **Lluvia** | Memoria: se evapora del contexto y precipita donde hace falta | Cae donde toca |

El agua **nunca** define jerarquía. Un lago no es «menos importante» que un océano: es que **moja
menos superficie**. Confundir alcance con importancia es el error clásico que convierte cualquier
regla local en un párrafo global, y así es como un prólogo llega a 30k tokens.

## 4. Reglas de carga (esto es el producto, no la tabla de arriba)

| Nivel | Cuándo entra en contexto | Qué se ve de él antes de entrar |
|---|---|---|
| Galaxia | Siempre | Todo (es minúsculo por diseño) |
| Océano | Siempre | Todo |
| Sistema solar | Al declararse el dominio activo | Su nombre y una línea |
| Estrella | Con su sistema | — |
| Planeta | Al tocar un path suyo | Su nombre |
| Continente / País / Provincia | Al descender | Su nombre |
| Ciudad / Pueblo | Al invocarse | Nombre + una línea |
| Casa | Solo si la skill la abre | Nada |
| Mar / Lago | Por `paths:` que matchea | Nada |
| Río | Por invocación explícita | Nombre + una línea |
| Lluvia | Por consulta explícita | Nada |

Lo que **nunca** ocurre: que el contexto inicial contenga la descripción de una casa, de un pueblo
de otro sistema solar, o de un lago que no moja el path que se está tocando.

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
2. El medidor da un número real de tokens de contexto inicial, medido, no estimado.
3. El otro (Claude o Codex) la ha revisado con premisa invertida y ha dicho qué intentó.
4. No hay ningún elemento huérfano ni ninguna regla que dependa de que alguien se acuerde.

## 8. Estado

El progreso vive en `PROGRESS.md`. Las revisiones cruzadas, en `reviews/`. Ninguna de las dos
partes declara nada terminado en el chat: se declara en el fichero, y el otro lo comprueba.
