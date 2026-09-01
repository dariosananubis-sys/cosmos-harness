---
cosmos: pueblo
nombre: diagrams
padre: documentos/diagramas
resumen: Arquitectura de nube dibujada como codigo, con los iconos oficiales de cada proveedor y del orquestador.
---

`mermaid` vive dentro del texto y `d2` compone mejor el diagrama autonomo, pero ninguno de los dos
tiene el catalogo de iconos oficiales. Cuando el diagrama es de infraestructura y tiene que
reconocerse de un vistazo, ese catalogo es la diferencia.

Se escribe en Python y sale imagen reproducible en integracion continua, asi que el diagrama se
regenera con el codigo en vez de envejecer en una carpeta.
