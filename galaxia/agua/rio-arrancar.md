---
cosmos: rio
nombre: arrancar
moja: []
momento: mantenimiento
invoca: python3 -m cosmos arrancar
resumen: Deja un clon recien bajado en verde: vista plana y validacion.
---

Lo primero que se ejecuta tras clonar. La vista plana es un artefacto generado y no viaja en
el repositorio, asi que sin este paso el runtime no ve ninguna skill.

No regenera el indice a proposito: si el indice miente, sale en rojo y manda a generar. Un
arranque que repara en silencio lo que el validador deberia denunciar es un encubrimiento.
