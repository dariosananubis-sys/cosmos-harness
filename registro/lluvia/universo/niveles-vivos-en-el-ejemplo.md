---
cosmos: lluvia
nombre: niveles-vivos-en-el-ejemplo
moja: []
resumen: El inventario mira un arbol cada vez; planeta, luna, provincia y lago viven en ejemplo/.
---

# «Ese nivel no lo usa nadie» suele significar «no en este arbol»

**Fecha:** 2026-09-01 · **Sintoma:** `cosmos estado` sobre la galaxia lista ocho niveles sin un
solo nodo, y de ahi se concluyo que media taxonomia era decoracion (hallazgo H20).

## Que era de verdad

De esos ocho, **seis tenian nodos vivos**: `ejemplo/` es un arbol completo, valido y validado en
cada push del CI (`cosmos validar --config ejemplo.toml`, mas
`test_ejemplo_completo_es_verde`), y contiene planeta, provincia, luna, lago, lluvia y rio.
`cosmos estado` carga una raiz, la de la configuracion que se le pase, y no puede saber si un
nivel esta muerto o simplemente no hace falta en el arbol que esta mirando.

Los dos que si estaban muertos —`ciudad` y `casa`— tampoco estaban en el ejemplo. Esa fue la
señal util: **quien monto el arbol de muestra para ejercitar la taxonomia los dejo fuera.**

## Que NO era

- No era «la spec se pudrio». Seis de los ocho se ejercitan en CI en cada push.
- No era que faltaran nodos en la galaxia. Crearlos ahi habria sido relleno: `spec/TAXONOMIA.md`
  prohibe el nivel de un solo hijo y el descenso completo por obligacion.

## Como verlo rapido la proxima vez

Antes de retirar un nivel por vacio, contar sus nodos en **todos** los arboles del repositorio,
no en uno. Hoy lo hace `tests/test_niveles_vivos.py`, que se pone rojo si un nivel se queda sin
un solo nodo en cualquiera de ellos.
