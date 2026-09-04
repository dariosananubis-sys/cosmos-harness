---
cosmos: lluvia
nombre: cosmos-sobre-el-arnes-de-origen
moja: []
resumen: COSMOS se construye encima de el arnés de origen; su maquinaria ya funciona y no se reescribe.
---

# COSMOS se construye encima de el arnés de origen

**Fecha:** 2026-09-01 · **Estado:** decidido · **Reversible:** sí, mientras no se migre `compilar`

## Qué se decide

COSMOS **no reescribe** la maquinaria de `<organización>/<arnés-de-origen>`. La adopta, y
aporta encima lo que ese repo no tiene: la taxonomía de once niveles, la distinción sólido/agua, los
veinte nichos y la disciplina de ver fallar cada invariante.

Se descartó absorber `packs/` como sustituto de la taxonomía, y se descartó seguir por separado.

## Por qué — medido, no opinado

Al encontrarlo parecía roto: **114 tests con 2 fallos y 1 error**, y su propia auditoría daba **87
problemas**. Eso habría justificado reescribirlo.

No era avería, era **falta del paso de arranque**. Tras `python3 scripts/bootstrap.py`, ejecutado y
comprobado por mí:

```
Ran 114 tests in 48.008s — OK
auditoría: limpia
secret_scan: limpio
contexto fijo: Codex ~1352 tok · Claude ~1419 tok · 15 skills
```

Esa distinción —roto de verdad frente a le falta arrancar— cambió la decisión entera. Sin
comprobarlo, se habrían tirado **3.283 líneas de scripts y 3.339 de tests que funcionan**, con cero
dependencias externas, para reescribir lo mismo peor.

Y el último número es el que cierra el caso: **~1.400 tokens de contexto fijo con 15 skills
activas**, frente a los ~27.000 del harness del que salió. El problema que COSMOS existe para
resolver, ese repo ya lo resuelve a medias.

## Qué aporta cada uno

| | el arnés de origen | COSMOS |
|---|---|---|
| Organización | `packs`: **dos niveles**, planos | Once niveles con contención estricta |
| Transversal | No distingue | Sólido contiene / agua atraviesa |
| Presupuesto | En bytes, ya vigilado | En tokens, con desglose por nodo |
| Validación | Estructura y esquema | 19 invariantes, **cada una vista fallar** |
| Proyección a repo externo | **`project.py`, 511 líneas, funcionando** | Especificado, sin escribir |
| Secretos | `secret_scan.py` sobre blobs del índice | No lo tiene |
| Integración real | Claude Code **y** Codex | Solo especificada |

Los packs resuelven mejor lo que resuelven: activar y desactivar sin tocar Git. Pero son **planos**,
y veinte nichos con continentes, países y provincias no caben en dos niveles. Ahí gana la taxonomía.

## Las cuatro piezas que se adoptan tal cual

1. **`project.py`** — proyecta a un repo externo conservando lo ajeno. Es exactamente lo que
   `spec/COMPILACION.md` especifica y nadie había escrito. La pieza más valiosa del repo.
2. **`precommit.py`** — verifica sobre una **instantánea del índice Git**, no sobre el árbol de
   trabajo sucio. Es la diferencia entre comprobar lo que se va a commitear y lo que casualmente hay
   en disco.
3. **`secret_scan.py` + `redaction.py`** — el segundo etiqueta rutas por hash para que un
   diagnóstico no filtre nombres de cliente. Trece líneas que resuelven un problema real que COSMOS
   ni se había planteado.
4. **`retrieve_memory.py`** — BM25 sobre un índice, con presupuesto de bytes, y **nunca devuelve el
   cuerpo completo** de una entrada. Es la `lluvia` de `spec/REGISTRO.md`, ya implementada.

## Riesgos

- **Dos vocabularios.** `packs` y `sistema solar` conviven mal si no se dice cuál manda. Manda la
  taxonomía; un pack pasa a ser la unidad de activación de un nicho, no un nivel del árbol.
- **Su auditor conoce su estructura.** `audit_harness.py` valida rutas propias; al montar la
  taxonomía encima habrá que ampliarlo o sus comprobaciones darán falsos positivos.
- **La copia portable arrastra referencias del harness de origen.** Los 87 problemas iniciales eran
  eso. Al integrarlo hay que limpiar lo que apunte al negocio concreto.

## Cómo se revierte

Mientras `compilar` siga siendo la especificación de COSMOS y no una copia de `project.py`, volver
atrás es dejar de usarlo. En cuanto se migre esa pieza, revertir cuesta reescribirla — y ahí la
decisión deja de ser barata.
