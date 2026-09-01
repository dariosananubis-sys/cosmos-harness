---
cosmos: mar
nombre: criterio
moja: ["**/*.py", "**/*.js", "**/*.ts", "**/*.tsx", "**/*.php", "**/*.go", "**/*.rs", "**/*.rb", "**/*.java", "**/*.sh"]
resumen: Que no se escriba de mas: lo mas simple que funciona, reutilizar antes que crear, tocar lo justo.
---

Se toca lo minimo. Un cambio grande se hace en pasos que se pueden verificar por separado. Antes de
escribir algo nuevo se busca si ya existe: duplicar es deuda. Las transformaciones sobre muchos
ficheros van con herramienta, no a mano, porque el error humano escala.

Lo mecanico lo mide un analizador con arbol sintactico, no la vista: `ruff` en Python, `eslint` en
JavaScript y TypeScript, `golangci-lint` en Go, `jscpd` para duplicacion por tokenizacion. Ninguno
es un pueblo: son el mismo criterio aplicado a cada lenguaje.

**Reutilizar antes que crear se busca, no se recuerda.** Navegacion semantica por protocolo de
servidor de lenguaje —buscar el simbolo y quien lo referencia— antes que adivinar desplazamientos de
texto o barrer a ciegas. Lo hace `serena`; no es un pueblo porque sirve a los veinte nichos igual.

**Tocar lo justo se demuestra midiendo el arbol, no leyendo el diff.** La transformacion masiva se
describe como patron sintactico y se aplica igual a cuatrocientos ficheros: `ast-grep` sobre treinta
lenguajes, `openrewrite` cuando el ecosistema es de maquina virtual de Java y hay que preservar
formato y comentarios. Y se revisa con `difftastic`, que compara arboles: una linea reformateada no
aparece como cambio, asi que el ruido del codemod no tapa el error de verdad.

Un modelo no puede garantizar consistencia en cuatrocientos ficheros. Una regla determinista si; por
eso el criterio dice que se use la regla y no la paciencia.
