---
cosmos: mar
nombre: criterio
moja: ["**/*.py", "**/*.js", "**/*.ts", "**/*.tsx", "**/*.php", "**/*.go", "**/*.rs", "**/*.rb", "**/*.java", "**/*.sh"]
resumen: Que no se escriba de mas: lo mas simple que funciona, reutilizar antes que crear, tocar lo justo.
---

Se toca lo minimo; un cambio grande va en pasos verificables por separado. Antes de escribir
algo nuevo se busca si ya existe: duplicar es deuda. Reutilizar se busca por simbolo y por quien lo
referencia, no adivinando desplazamientos ni barriendo a ciegas.

Lo mecanico lo mide un analizador con arbol sintactico, no la vista: la regla que se puede
escribir la comprueba una maquina y deja de discutirse. Un modelo no garantiza consistencia en
cientos de ficheros; una regla determinista si: el cambio repetido se declara como patron
sintactico y lo aplica la herramienta, nunca la mano, porque el error humano escala.

Tocar lo justo se demuestra comparando arboles, no leyendo el diff: lo reformateado no cuenta
como cambio ni su ruido tapa el error real.

Antes de empezar se lista que ficheros puede tocar el encargo; lo de fuera se para y pide
permiso, no se amplia solo.

Mover o partir codigo no es reescribirlo de memoria: se traslada con la herramienta que conserva
el historial y se cuadra el conteo.

La herramienta concreta de cada comprobacion y lenguaje se decide en `refactorizacion`: el mar
fija la politica, no el catalogo.
