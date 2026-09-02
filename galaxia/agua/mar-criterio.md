---
cosmos: mar
nombre: criterio
moja: ["**/*.py", "**/*.js", "**/*.ts", "**/*.tsx", "**/*.php", "**/*.go", "**/*.rs", "**/*.rb", "**/*.java", "**/*.sh"]
resumen: Que no se escriba de mas: lo mas simple que funciona, reutilizar antes que crear, tocar lo justo.
---

Se toca lo minimo. Un cambio grande se hace en pasos que se pueden verificar por separado. Antes de
escribir algo nuevo se busca si ya existe: duplicar es deuda. Las transformaciones sobre muchos
ficheros van con herramienta, no a mano, porque el error humano escala.

Lo mecanico lo mide un analizador con arbol sintactico, no la vista. Si una regla se puede escribir,
la comprueba una maquina y deja de gastarse tiempo en discutirla.

**Reutilizar antes que crear se busca, no se recuerda.** Se pregunta por el simbolo y por quien lo
referencia, en vez de adivinar desplazamientos de texto o barrer a ciegas.

**Tocar lo justo se demuestra midiendo el arbol, no leyendo el diff.** El cambio repetido se describe
como patron sintactico y se aplica igual en todas partes; luego se revisa comparando arboles, para
que lo reformateado no aparezca como cambio y su ruido no tape el error de verdad.

Un modelo no puede garantizar consistencia en cuatrocientos ficheros. Una regla determinista si; por
eso el criterio dice que se use la regla y no la paciencia.

Que herramienta ejecuta cada una de estas comprobaciones en cada lenguaje se decide en
`rendimiento/calidad`, no aqui: un mar fija la politica y no el catalogo.

Antes de empezar se escribe la lista de ficheros que el encargo puede tocar, y lo que caiga fuera
se para y pide permiso en vez de ampliarse solo: sin esa lista, un ayudante edito un fichero de
semilla que nadie le habia pedido y deshacerlo costo mas que el propio encargo.

Mover o partir codigo no es reescribirlo. El modelo borra el bloque y lo teclea de memoria, y por
ahi se pierden lineas sin que salga un solo rojo: se traslada con la herramienta que conserva el
historial y se comprueba que el conteo cuadra.
