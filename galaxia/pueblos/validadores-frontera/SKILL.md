---
cosmos: pueblo
nombre: validadores-frontera
padre: saas
resumen: Validadores puros de entrada: identificador, slug, URL segura, subcarpeta sin travesia e identidad fiscal.
---

`cosecha/input-validators.js` y `cosecha/nif-cif-validator.js` — herramientas propias, no hay
repositorio público. Las rutas SON la referencia. Sin dependencias (solo `node:path`), puras y
testeables.

```bash
node --input-type=module -e "
import { isValidUuid, isValidSlug, isSafeHttpsUrl, validateBatchRange, safeSubdir }
  from './cosecha/input-validators.js';
import { normalizeNif, resolveSlugFromList } from './cosecha/nif-cif-validator.js';

console.log(isValidSlug('cliente-ejemplo'));                 // true
console.log(isSafeHttpsUrl('javascript:alert(1)'));          // false
console.log(safeSubdir('/datos', '../../etc'));              // null  -> salto de directorio
console.log(validateBatchRange(1, 500, { max: 200 }));       // fuera de rango
console.log(normalizeNif(' b-039.72221 '));                  // B00000000
console.log(resolveSlugFromList([{ slug: 'ejemplo', nif: 'B00000000' }], 'b00000000'));
"
```

Se prefieren a `zod` o `joi` —los validadores de esquema del ecosistema— para este uso concreto por
dos motivos: son **cinco funciones sin dependencias**, así que entran en un servicio pequeño sin
arrastrar un árbol de paquetes ni una superficie de suministro; y resuelven casos que un esquema
genérico no cubre bien. `safeSubdir` contiene una ruta dentro de un punto de montaje **comparando
rutas ya normalizadas, no con una comprobación de prefijo**, que es exactamente por donde se cuela el
salto de directorio; e `isSafeHttpsUrl` fuerza `https://`, que es lo que evita que una URL venida de
un registro o de un formulario acabe siendo un enlace `javascript:` al pintarla.

`nif-cif-validator.js` normaliza un identificador fiscal español (mayúsculas, sin guiones ni puntos)
y resuelve con él a qué cuenta pertenece. Es el dato de entrada de `gobl` cuando toca emitir factura:
**si entra mal aquí, la factura sale mal y ya emitida**.

No sustituye a nada del nicho de seguridad: `coraza` filtra peticiones desde fuera y `libsodium` hace
la criptografía. Esto es la capa de dentro, la que decide si el dato entra al dominio.

Ojo: `normalizeNif` **normaliza, no valida la letra de control**. Dos identificadores distintos con la
misma normalización se resuelven a la misma cuenta si la lista está mal; y un NIF inventado con
formato correcto pasa. Para validar de verdad la letra hay que añadir el cálculo del módulo 23 (NIF)
y el dígito de control del CIF. Y el `isValidUuid` es laxo a propósito (36 caracteres hexadecimales y
guiones): acepta cosas que no son UUID v4 — vale para identificadores de PostgreSQL, no como garantía
de aleatoriedad.
