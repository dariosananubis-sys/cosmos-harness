---
cosmos: rio
nombre: validar
moja: []
invoca: python3 -m cosmos validar
resumen: Comprueba todas las invariantes del arbol y sale en rojo con la linea exacta.
---

Es la puerta antes de dar nada por terminado. Cada error trae su codigo, el fichero, la linea
y una accion concreta. Sale 1 si hay algo mal, asi que sirve tal cual en un enganche.

Con `--nicho` mide el presupuesto contra ese oficio en vez de contra el peor. Con `--json`
emite el mismo veredicto en forma legible por otra herramienta.
