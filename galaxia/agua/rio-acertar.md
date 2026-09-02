---
cosmos: rio
nombre: acertar
moja: []
invoca: python3 -m cosmos acertar
momento: mantenimiento
resumen: La contra-metrica: mide si el catalogo lleva a la herramienta correcta, no solo lo que cuesta.
---

Todo lo demas mide **coste**. Sin esto, la forma mas barata de pasar el presupuesto es escribir
resumenes peores: recortarlos baja la entrada, pone verde E16 y no dispara ninguna invariante,
degradando justo aquello por lo que se paga el resumen.

Puntua con BM25 lexico sobre el indice y el catalogo, que es lo que un agente ve antes de decidir.
Es determinista y no cuesta nada: cero red, cero modelo. Y por eso mismo **no es un agente**: mide
si el resumen contiene las palabras del encargo, no si un modelo elegiria bien.

Publica dos cifras. Los encargos de **ajuste** se miran al trabajar y por eso se contaminan; los de
**validacion** no guian ninguna decision, y esa es la cifra que vale. Cuando se separan mas de diez
puntos, lo que ha mejorado no es el arbol sino la punteria sobre las preguntas conocidas.
