---
cosmos: estrella
nombre: localizacion
ilumina: localizacion
resumen: Lo que es cierto cuando el mismo producto tiene que hablar varios idiomas.
---

Pegar trozos de frase no se traduce: el orden de las palabras cambia con el idioma, asi que la unidad minima es la frase entera con sus huecos dentro.
El plural no son dos casos: hay lenguas con seis, y decidirlo con un `si n == 1` deja texto roto en cuanto se sale del ingles.
Fecha, moneda y separador decimal los manda la region de quien lee, no el idioma ni el servidor: un numero compuesto a mano miente en medio mundo.
Una clave sin traducir tiene que verse: si el sistema cae al idioma de origen en silencio, lo que falta lo descubre un cliente y no una prueba.
Lo traducido crece: lo que cabe en ingles se sale de la caja en aleman, y por eso el ancho se comprueba en el idioma mas largo, no en el de partida.
El texto que un modelo o una persona traducen sin ver la pantalla sale correcto y fuera de sitio: el contexto de cada cadena viaja con ella o no viaja.
