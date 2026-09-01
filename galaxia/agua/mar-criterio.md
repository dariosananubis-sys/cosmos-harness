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
