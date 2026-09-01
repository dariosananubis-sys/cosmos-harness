---
cosmos: pueblo
nombre: ast-grep
padre: rendimiento/calidad
resumen: Busca y reescribe por forma del arbol sintactico, no por texto: un patron vale para cuatrocientos ficheros.
---

https://github.com/ast-grep/ast-grep · MIT · 15.718★ · push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install ast-grep          # o: npm i -g @ast-grep/cli   (v0.45.3)

# buscar: toda llamada a console.log, este como este partida en lineas
ast-grep run --lang ts --pattern 'console.log($$$ARGS)' src/

# reescribir en todo el arbol, revisando antes de aplicar
ast-grep run --lang ts --pattern 'foo($A, $B)' --rewrite 'bar($B, $A)' src/
ast-grep run --lang ts --pattern 'foo($A, $B)' --rewrite 'bar($B, $A)' --update-all src/

# regla con condiciones, para lo que un patron suelto no expresa
ast-grep scan --rule regla.yml src/
```

Un patron no es una cadena: `$A` captura un nodo entero, `$$$ARGS` una lista de ellos, y la
coincidencia ocurre sobre el arbol que produce tree-sitter. Por eso encuentra la misma llamada
partida en tres lineas, con comentarios en medio o con espaciado distinto, y por eso no encuentra
esa palabra dentro de una cadena de texto ni de un comentario — que es justo el ruido con el que un
`sed` o un `grep -r` convierten una transformacion masiva en una tarde de revision.

Gana a `comby` (2.672★, push 2026-06-08, tambien vivo) cuando el lenguaje tiene gramatica y la regla
depende de la estructura: solo ast-grep puede decir «esto es una llamada a funcion y no una
propiedad con el mismo nombre», encadenar condiciones (`inside`, `has`, `follows`) en un fichero de
reglas y correrlo como analizador propio en integracion continua. `comby` gana en el caso contrario
y no es raro: trabaja por delimitadores equilibrados sin gramatica, asi que se mete donde ningun
analizador entra —un dialecto de plantillas, un fichero de configuracion, un lenguaje sin gramatica
publicada— y ahi ast-grep sencillamente no arranca.

Ojo: **no reformatea**. El texto de sustitucion se inserta tal cual, asi que la indentacion del
resultado la pone el patron y no el estilo del proyecto; despues de un cambio masivo hay que pasar
el formateador del lenguaje o el diff sale lleno de ruido. `--update-all` escribe sin preguntar:
sin el arbol limpio en git, no hay vuelta atras. Y los metavariables no cruzan tipos de nodo: un
`$A` que casa con una expresion no va a casar con una sentencia, de modo que hay reescrituras que
parecen triviales y necesitan dos reglas.
