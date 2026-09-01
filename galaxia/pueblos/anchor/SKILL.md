---
cosmos: pueblo
nombre: anchor
padre: blockchain
resumen: La otra cadena: genera la validacion de cuentas y el cliente desde la interfaz, que es donde esta el fallo tipico.
---

Es a esa cadena lo que `foundry` es a la primera. Sus macros generan la comprobacion de cuentas, la
serializacion y el cliente a partir de la interfaz declarada.

Entra porque el nicho no puede ser de una sola cadena, y porque en esa el error mas repetido en
auditoria es exactamente el que este marco elimina por construccion: aceptar una cuenta que no se ha
comprobado. El repositorio cambio de organizacion; el antiguo redirige.
