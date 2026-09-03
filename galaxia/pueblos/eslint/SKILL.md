---
cosmos: pueblo
nombre: eslint
padre: refactorizacion/reglas
resumen: El linter de JavaScript y TypeScript con reglas para cada marco de trabajo; la cobertura es su ventaja.
---

https://github.com/eslint/eslint · MIT · 27.495★ · push 2026-09-01 (comprobado 2026-09-01, v10.9.1)

```bash
npm init @eslint/config      # crea eslint.config.js (configuracion plana, v9+) e instala eslint

npx eslint .
npx eslint . --fix
npx eslint . --cache         # imprescindible en repositorios grandes
```

## Contra `biome`, que es la decision viva

`biome` (https://github.com/biomejs/biome · Apache-2.0 · 25.695★ · push 2026-09-01, v2.5.11) esta a
un paso de igualarlo en estrellas y lo supera en todo lo mecanico: un binario de Rust que hace
analisis y formateo en la misma pasada, entre diez y veinte veces mas rapido, con una sola
configuracion y sin arbol de dependencias. Si el proyecto es JavaScript o TypeScript sin marco de
trabajo, o si la revision tarda tanto que ya nadie la mira, la respuesta correcta es `biome` y no
hay mucho que debatir.

**La recomendacion aqui sigue siendo `eslint`, y por una sola razon: la cobertura de reglas.** Lo
que hoy no se puede reemplazar no es el motor, es el ecosistema — las reglas de los ganchos de React
y de su compilador, el juego completo de reglas con informacion de tipos de `typescript-eslint`, la
resolucion real de importaciones, y los complementos con analizador propio de los marcos de trabajo
que traen su propio formato de fichero. Biome cubre una parte creciente de eso y en la version 2
anadio reglas con informacion de tipos sin exigir el comprobador completo, pero **no** el conjunto
entero, y las que faltan suelen ser precisamente las que atrapan errores de verdad y no de estilo.

El criterio practico, para no repetir el debate cada seis meses: **listar los complementos que el
proyecto tiene activados y comprobar uno a uno si biome los cubre.** Si los cubre, se migra y se
gana tiempo en cada ejecucion. Si falta uno solo que importe, mantener los dos es peor que
mantener eslint. Y la asimetria manda: quitar reglas es gratis, descubrir en produccion el fallo que
la regla que se perdio habria atrapado, no.

Ojo: la configuracion plana de la version 9 rompio `.eslintrc`, asi que un complemento que no se
haya actualizado no arranca — y varios del ecosistema largo llevan tiempo sin hacerlo. `--fix`
reescribe el fichero y unas pocas reglas pueden cambiar el comportamiento al arreglar; sin el arbol
limpio en git no hay revision posible. Y sin `--cache` es lento de verdad en un repositorio grande,
que es justo el sitio donde se deja de correr.
