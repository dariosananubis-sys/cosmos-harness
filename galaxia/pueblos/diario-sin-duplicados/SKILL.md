---
cosmos: pueblo
nombre: diario-sin-duplicados
padre: agentes-ia/memoria
resumen: Quita los bloques que un enganche roto repitio, y prueba antes de escribir que lo escrito a mano sigue intacto.
---

`cosecha/dedupe-daily-autocapture.py` — cuando un enganche de captura automatica deja de reconocer
su propio marcador, en vez de actualizar su bloque lo vuelve a anadir entero: el mismo dia acaba con
la sesion repetida tantas veces como se guardo. Esto deja uno solo por identificador de sesion, el
mas completo segun su propio metadato de tamano.

Lo que lo hace fiable no es el deduplicado sino la guarda: antes de escribir comprueba que todo lo
que NO es bloque generado —las notas a mano, los cierres escritos por una persona— sigue siendo byte
por byte lo mismo, y aborta si no. Una limpieza destructiva que no demuestra lo que ha conservado es
una perdida de datos que todavia no se ha notado.

Es idempotente y por defecto no escribe. Las tres expresiones que reconocen el bloque se ajustan al
formato del enganche que lo genere.
