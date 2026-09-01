---
cosmos: pueblo
nombre: trufflehog
padre: ciberseguridad/analisis/vulnerabilidades
resumen: Encuentra credenciales en el historico y ademas intenta usarlas para saber si siguen vivas.
---

El unico de su hueco que verifica de verdad: intenta autenticarse contra el proveedor y dice si el
secreto sigue activo. Eso convierte una lista de sospechas en una lista de trabajo.

Descartado el detector mas adoptado: su propio fichero de presentacion avisa de los limites de la
deteccion por entropia, y sin verificacion la lista se llena de falsos positivos.
