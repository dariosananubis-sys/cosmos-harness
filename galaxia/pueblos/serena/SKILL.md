---
cosmos: pueblo
nombre: serena
padre: rendimiento/calidad
resumen: Da al agente busqueda por simbolo y por referencia via LSP, para no leer ficheros enteros a ciegas.
---

https://github.com/oraios/serena · MIT · 28.703★ · push 2026-08-30 (comprobado 2026-09-01, v1.7.0)

```bash
# se arranca como servidor MCP, sin instalar nada permanente
uvx --from git+https://github.com/oraios/serena serena start-mcp-server \
  --context ide-assistant --project /ruta/al/proyecto

# comprobar que el proyecto indexa antes de conectarlo a nada
uvx --from git+https://github.com/oraios/serena serena project index /ruta/al/proyecto
```

Una vez conectado, el agente deja de pedir ficheros y pide simbolos: `find_symbol` para localizar la
definicion, `find_referencing_symbols` para saber quien la usa, `replace_symbol_body` para cambiarla
entera sin calcular desplazamientos de texto. Todo eso lo contesta el servidor de lenguaje del
proyecto, que es el mismo que usa el editor.

Gana a `ripgrep` en el unico punto que decide el coste de una sesion: **cuanto hay que leer para
estar seguro**. Un `rg nombre_funcion` devuelve la definicion, las llamadas, las menciones en
comentarios, las cadenas de texto que casan por casualidad y el fichero de pruebas que la nombra en
una descripcion; separarlas obliga a abrir ficheros. El servidor de lenguaje ya sabe cual es cual,
asi que devuelve el fragmento exacto y nada mas.

**Es joven: hay que decirlo.** El repositorio se creo en marzo de 2025 y ha juntado 28.703 estrellas
en ano y medio, lo que significa adopcion rapida y tambien que la superficie de herramientas todavia
se mueve entre versiones menores — una receta escrita hace tres meses puede nombrar una herramienta
que ya se llama de otra forma. Se fija la version que se use y se revisa al actualizar.

Ojo: **no funciona igual en todos los lenguajes**, porque delega en el servidor de lenguaje de cada
uno; donde ese servidor es flojo o necesita que el proyecto compile, serena hereda el problema entero.
El primer indexado de un repositorio grande tarda y hay que hacerlo antes, no durante la tarea. Y es
un servidor MCP: sus definiciones de herramientas ocupan contexto en **cada** turno de la sesion, se
usen o no, asi que conectarlo «por si acaso» a una sesion que no va a navegar codigo es exactamente
la fuga que se estaba intentando evitar.
