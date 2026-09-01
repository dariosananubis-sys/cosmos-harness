---
cosmos: mar
nombre: custodia
moja: ["**/*.env*", "**/*.sql", "**/*.csv", "**/migrations/**", "**/*.tf", "**/docker-compose*", "**/*.ipynb"]
resumen: Datos personales y RGPD: base legal, lo minimo necesario, borrado, y detectar el que se cuela.
---

Distinto del oceano de secretos: alli van credenciales, aqui van personas. Se recoge lo minimo, se
guarda donde ya estaba y no se copia a un tercero para hacer una prueba.

Antes de exportar, ensenar o mandar a un modelo un conjunto de datos, se pasa un detector de datos
personales y se sustituye. En codigo, el analisis de flujo dice por donde viajan; en datos, un
detector por reconocedores y sumas de control dice donde estan.
