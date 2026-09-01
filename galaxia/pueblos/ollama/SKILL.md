---
cosmos: pueblo
nombre: ollama
padre: modelos-locales/servir
resumen: Gestor que descarga, versiona y sirve modelos con API compatible, sin compilar nada a mano.
---

La puerta de entrada: capas de descarga incremental y un servidor compatible con la API mas comun.
Por debajo lleva el motor en C, que es el estandar de hecho y define el formato de pesos cuantizados;
no entra como pueblo propio porque aqui nunca se usa suelto.

Descartado el todo en uno con backends modulares y el servidor de alto rendimiento: el primero se
solapa con este, el segundo pide GPU dedicada que aqui no hay.
