---
cosmos: pueblo
nombre: validadores-frontera
padre: saas
resumen: Validadores puros de entrada: identificador, slug, URL segura, subcarpeta sin travesia e identidad fiscal.
---

`cosecha/input-validators.js` — funciones sin dependencias para el unico sitio donde hay que validar:
la frontera. Identificador unico, slug, URL forzada a https (que es lo que evita el enlace con
javascript embebido), rango de lote y, la mas util, subcarpeta contenida dentro de un punto de
montaje — resuelta comparando rutas ya normalizadas, no con una comprobacion de prefijo, que es como
se cuela el salto de directorio.

`cosecha/nif-cif-validator.js` — normaliza y comprueba la letra de un identificador fiscal espanol y
resuelve con el a que cuenta pertenece. Es el dato de entrada de `gobl` cuando toca emitir factura:
si entra mal aqui, la factura sale mal y ya emitida.

No sustituye a nada del nicho de seguridad: `coraza` filtra peticiones desde fuera y `libsodium` hace
la criptografia. Esto es la capa de dentro, la que decide si el dato entra al dominio.
