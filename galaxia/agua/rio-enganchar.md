---
cosmos: rio
nombre: enganchar
moja: []
momento: mantenimiento
invoca: python3 -m cosmos enganchar
resumen: Cuelga la verificacion de cada commit sin pisar un hook ajeno.
---

Un validador que nadie ejecuta no se distingue de no tenerlo. Esto lo cuelga de cada commit,
sobre la instantanea del indice de Git y no sobre lo que haya sucio en disco.

Si ya hay un pre-commit de otro, lo dice y no toca nada. `cosmos desenganchar` lo revierte.
