---
cosmos: pueblo
nombre: serena
padre: refactorizacion
resumen: Da al agente busqueda por simbolo y por referencia via LSP, para no leer ficheros enteros a ciegas.
---

https://github.com/oraios/serena · MIT · 28.703★ · push 2026-08-30 (comprobado 2026-09-01, v1.7.0)

```bash
uv tool install -p 3.13 serena-agent
serena init                              # comprueba la instalacion y elige el motor

# conectarlo a Claude Code, en el proyecto actual
claude mcp add serena -- serena start-mcp-server --context claude-code --project "$(pwd)"
# o para todos los proyectos, resolviendo el directorio en cada arranque
claude mcp add --scope user serena -- serena start-mcp-server --context claude-code --project-from-cwd
```

Una vez conectado, el agente deja de pedir ficheros y pide simbolos: localizar la definicion, listar
quien la referencia, sustituir el cuerpo de una funcion entera sin calcular desplazamientos de texto.
Lo contesta el servidor de lenguaje del proyecto, el mismo que usa un editor, con cobertura declarada
de mas de cuarenta lenguajes.

Gana a `ripgrep` en el unico punto que decide el coste de una sesion: **cuanto hay que leer para
estar seguro**. Un `rg nombre_funcion` devuelve la definicion, las llamadas, las menciones en
comentarios, las cadenas de texto que casan por casualidad y el fichero de pruebas que la nombra en
una descripcion; separarlas obliga a abrir ficheros enteros. El servidor de lenguaje ya sabe cual es
cual, asi que devuelve el fragmento exacto y nada mas.

**Es joven y su superficie se mueve: hay que decirlo.** El repositorio se creo en marzo de 2025 y ha
juntado 28.703 estrellas en ano y medio. Los propios autores avisan en su portada de que **no se
instale desde ningun mercado de complementos ni de servidores MCP**, porque los que circulan por ahi
llevan ordenes de arranque antiguas — sirve de aviso de cuanto ha cambiado la interfaz. Se fija la
version que se use y se relee la puesta en marcha al actualizar.

Ojo: el motor por defecto es el de **servidores de lenguaje**, libre, y es el que se usa aqui; el
motor alternativo de JetBrains es un **complemento de pago** y por tanto queda fuera. La calidad
depende por completo del servidor de cada lenguaje: donde ese servidor es flojo o exige que el
proyecto compile, serena hereda el problema entero. Y es un servidor MCP: sus definiciones de
herramientas ocupan contexto en **cada** turno de la sesion, se usen o no, asi que conectarlo «por si
acaso» a una sesion que no va a navegar codigo es exactamente la fuga que se pretendia evitar.
