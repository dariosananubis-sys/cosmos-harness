---
cosmos: pueblo
nombre: difftastic
padre: refactorizacion
resumen: Compara dos versiones por su arbol sintactico, asi que reindentar o mover una llave no sale como cambio.
---

https://github.com/Wilfred/difftastic · MIT · 25.847★ · push 2026-08-28 (comprobado 2026-09-01, v0.70.0)

```bash
brew install difftastic

difft viejo.py nuevo.py

# en git, para una sola invocacion
GIT_EXTERNAL_DIFF=difft git diff
GIT_EXTERNAL_DIFF=difft git show <sha>

# permanente pero sin secuestrar el diff normal: queda como 'git dft'
git config --global alias.dft '!GIT_EXTERNAL_DIFF=difft git diff'
```

Es la herramienta de revisar lo que sale de un cambio masivo. El diff por lineas no distingue entre
«esto se movio de sitio» y «esto ahora hace otra cosa», asi que una reindentacion, el renombrado de
un parametro o un envoltorio nuevo tiñen de rojo y verde cuatrocientos ficheros y el error de verdad
—el unico que importaba— se pierde dentro. Al comparar arboles, lo que solo cambio de forma
desaparece del informe y queda el cambio de significado.

Gana a `delta`, con el que en realidad no compite: `delta` colorea y alinea mejor **el mismo diff por
lineas** que produce git, mientras que difftastic produce **otro diff**. Y gana a `git diff
--word-diff`, que sigue siendo textual y se pierde con cualquier movimiento de bloque.

Donde **no** ayuda, y conviene saberlo antes de instalarlo:

- **Ficheros grandes.** Cae a diff por lineas si cualquiera de los dos lados pasa de `--byte-limit`,
  que por defecto es **1 MB**, o si el grafo interno pasa de `--graph-limit`, por defecto **3.000.000
  de vertices**. Un paquete minificado, un fichero generado de diez mil lineas o un `lock` grande
  entran en ese caso casi siempre — y son justo los ficheros donde un cambio masivo hace mas ruido.
- **Lenguajes sin gramatica.** Trae gramaticas para unas cuantas decenas de lenguajes; con cualquier
  otra cosa —un dialecto de plantillas, un formato propio, un fichero sin extension reconocida— vuelve
  al diff textual. Y ese retroceso es **silencioso a efectos practicos**: escribe el lenguaje en la
  cabecera de cada fichero, y si nadie lee esa palabra se cree estar revisando el arbol cuando no es
  asi. Lo mismo pasa con un fichero que no parsea: `--parse-error-limit` es 0 por defecto, o sea que
  **un solo error de sintaxis** manda el fichero entero al diff por lineas.
- **No es un parche.** Su salida es para leerla, no para `git apply`, y como herramienta de fusion no
  sirve.
