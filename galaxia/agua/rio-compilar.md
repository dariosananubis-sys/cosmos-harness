---
cosmos: rio
nombre: compilar
moja: []
momento: mantenimiento
invoca: python3 -m cosmos compilar
resumen: Aplana las skills invocables con cerrojo y manifiesto atomico.
---

El runtime solo entiende un directorio plano de skills; el arbol es profundo. Esta es la
traduccion entre los dos, y la unica que puede tocar ese directorio.

Nunca borra lo que no creo: si una entrada obsoleta no coincide con su hash, avisa y la
suelta en vez de pisarla. `--seco` describe los cambios sin escribir; `--nicho` aplana un oficio.
