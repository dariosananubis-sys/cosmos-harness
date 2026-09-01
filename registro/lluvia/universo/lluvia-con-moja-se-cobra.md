---
cosmos: lluvia
nombre: lluvia-con-moja-se-cobra
moja: []
resumen: Un alcance escrito en una memoria no la carga, pero si la cobra: 7.700 tokens invisibles.
---

# Una memoria con alcance se paga y no se lee

**Fecha:** 2026-09-01 · **Sintoma:** E16 en rojo, `entrada 2383 + agua condicional 8700 = 11083`,
justo despues de que el arbol empezara a ver el registro.

## Que era de verdad

Dos entradas del registro llevaban `moja` con contenido (`puente/**`, `spec/**`, `cosmos/**`).
Segun `GOAL.md` §4 una lluvia entra **solo por consulta explicita**, asi que ese alcance no la
carga nunca. Pero `agua_condicional` (NUCLEO §3) mete en el presupuesto **toda** agua que no sea
oceano y tenga `moja` no vacio. Resultado: 7.700 tokens cargados al presupuesto de cualquier
sesion que tocara ese terreno, por dos ficheros que no se abren jamas.

Lo peor no es el numero: es que **el coste solo aparecio al conectar el registro al arbol**. Antes
estaba igual de escrito y nadie lo medía.

## Que NO era

- No era el tamaño del cuerpo. Un cuerpo largo en una lluvia es gratis: no esta en la entrada.
  Lo que cobra es el `moja`, no el texto.
- No era el catalogo: la lluvia no aparece en el catalogo (NUCLEO §2).

## El arreglo

`moja: []` en las dos, y E10 lo exige ahora para todo nodo `lluvia`. La regla de
`spec/REGISTRO.md` —«el registro nunca entra en el contexto de entrada, ni una linea»— pasa de
parrafo a guardarrail.

## Como verlo rapido la proxima vez

Un E16 cuyo desglose nombra un nodo de `registro/` no es un problema de presupuesto: es un `moja`
donde no toca. `cosmos medir --detalle` da el nodo culpable en una linea.
