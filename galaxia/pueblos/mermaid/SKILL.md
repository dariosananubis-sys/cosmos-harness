---
cosmos: pueblo
nombre: mermaid
padre: documentos/diagramas
resumen: El diagrama vive dentro del propio Markdown y lo pintan las plataformas sin biblioteca.
---

https://github.com/mermaid-js/mermaid · MIT · 90.024★ · push 2026-09-01 (comprobado 2026-09-01)

````bash
# no hace falta instalar nada para que se vea: GitHub, GitLab, Obsidian y Notion lo
# pintan de serie dentro de un bloque ```mermaid del propio Markdown.
#
# ```mermaid
# flowchart LR
#   navegador --> proxy --> api --> base[(datos)]
# ```

# para exportar a imagen desde la linea de comandos:
npm install -g @mermaid-js/mermaid-cli
mmdc -i diagrama.mmd -o diagrama.svg
````

Se elige cuando el diagrama y el texto que lo explica **tienen que viajar juntos**: nadie tiene que
instalar nada ni abrir otro fichero para verlo, y en una revisión de código el diagrama cambia en el
mismo diff que el código que describe. Esa es la ventaja sobre `d2` y `diagrams`, que producen un
artefacto aparte.

Ojo: la colocación automática es **la peor de las tres**. Pasado el par de docenas de nodos, o con
etiquetas largas, salen cruces que no hay forma de arreglar desde la sintaxis — ahí toca `d2`. Y las
plataformas van por detrás de la versión del proyecto: un tipo de diagrama recién añadido puede
pintarse en local con `mmdc` y salir como bloque de código en bruto en el repositorio. Antes de usar
un tipo nuevo, comprobarlo en la plataforma donde va a leerse.
