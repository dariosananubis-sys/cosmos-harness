---
cosmos: pueblo
nombre: reprozip
padre: cientifico
resumen: Empaqueta lo que la ejecucion uso de verdad rastreando sus llamadas al sistema, no lo que alguien declaro.
---

Es el mecanismo mas literal de reproducibilidad del nicho: observa el proceso real y recoge binarios,
bibliotecas del sistema y ficheros de datos que toco.

La diferencia con un fichero de dependencias o con `pixi` no es de comodidad, es de naturaleza:
aquellos declaran lo que se cree necesario, este captura lo que hizo falta. Para volver a correr en
otra maquina algo que ya funciono una vez, es la via corta.
