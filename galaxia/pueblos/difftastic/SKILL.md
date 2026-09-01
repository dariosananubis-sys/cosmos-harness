---
cosmos: pueblo
nombre: difftastic
padre: rendimiento/calidad
resumen: Compara dos versiones por su arbol sintactico, asi que reindentar o mover una llave no sale como cambio.
---

https://github.com/Wilfred/difftastic · MIT · 25.847★ · push 2026-08-28 (comprobado 2026-09-01, v0.70.0)

```bash
brew install difftastic

difft viejo.py nuevo.py

# en git, para una sola invocacion
GIT_EXTERNAL_DIFF=difft git diff
GIT_EXTERNAL_DIFF=difft git show <sha>

# permanente, sin secuestrar el diff normal: queda como 'git dft'
git config --global diff.external difft            # o bien:
git config --global alias.dft '!GIT_EXTERNAL_DIFF=difft git diff'
```

Es la herramienta de revisar lo que sale de un cambio masivo. El diff por lineas no distingue entre
«esto se movio de sitio» y «esto ahora hace otra cosa», asi que una reindentacion, un renombrado de
un parametro o un envoltorio nuevo tiñen de rojo y verde cuatrocientos ficheros y el error de verdad
—el unico que importaba— se pierde dentro. Al comparar arboles, lo que solo cambio de forma
desaparece del informe y queda el cambio de significado.

Gana a `delta` en esto y no compiten de verdad: `delta` colorea y alinea mejor **el mismo diff por
lineas** que produce git; difftastic produce **otro diff**. Y gana a `git diff --word-diff`, que
sigue siendo textual y se pierde con cualquier movimiento de bloque.

Donde **no** ayuda, y hay que saberlo antes de instalarlo:

- **Lenguajes sin gramatica.** Trae unas cuantas decenas de gramaticas; con cualquier otra cosa
  —un dialecto de plantillas, un formato propio, un fichero sin extension reconocida— cae a
  comparacion textual. No falla ni avisa a gritos: pone `Text` en la cabecera y da un diff normal.
  Si nadie mira esa palabra, se cree que se esta revisando el arbol y no es cierto.
- **Ficheros enormes.** El algoritmo explora un grafo cuyo tamano crece con el producto de los dos
  lados; hay un limite duro (`DFT_GRAPH_LIMIT`) y al superarlo abandona y vuelve al diff textual.
  Un paquete minificado, un fichero generado de diez mil lineas o un `lock` gigante caen ahi casi
  siempre, y son justo los ficheros en los que un cambio masivo produce mas ruido.
- **No es un parche.** Su salida es para leerla, no para `git apply`. Y no resuelve fusiones: como
  herramienta de conflicto no sirve.
