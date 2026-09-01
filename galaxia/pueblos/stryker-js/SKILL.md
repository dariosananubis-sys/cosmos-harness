---
cosmos: pueblo
nombre: stryker-js
padre: rendimiento/calidad
resumen: Mutacion en JavaScript y TypeScript, con modo incremental y un complemento por cada ejecutor de pruebas.
---

https://github.com/stryker-mutator/stryker-js · Apache-2.0 · 3.068★ · push 2026-08-31 (comprobado 2026-09-01, v10.0.0)

```bash
npm i -D @stryker-mutator/core
npx stryker init                 # pregunta el ejecutor e instala su complemento

npx stryker run
npx stryker run --incremental    # reutiliza el informe anterior: solo lo que cambio
npx stryker run --concurrency 4 --mutate "src/precios/**/*.ts"
```

Hace lo mismo que su equivalente de Python —alterar el codigo y ver quien se entera— sobre el
ecosistema de JavaScript y TypeScript, y es ahi donde esta su valor: hay complemento oficial para
`vitest`, `jest`, `mocha`, `karma`, `jasmine` y `tap`, mas el comprobador de tipos de TypeScript, asi
que se enchufa a la suite que el proyecto ya tiene en vez de imponer una. El modo `--incremental`
guarda el resultado y en la siguiente vuelta solo reejecuta lo tocado, que es lo que hace viable
ponerlo en una rama y no solo en una ejecucion nocturna.

Contra `c8` o `istanbul` no hay debate posible, y es el argumento entero de este pueblo: un fichero de
pruebas del que se borren todos los `expect` conserva el **100% de cobertura** y baja a **0% de
mutacion**. Solo una de las dos cifras esta midiendo lo que a uno le importa.

Ojo: sigue costando ordenes de magnitud mas que correr la suite una vez, asi que su sitio por defecto
es la ejecucion programada y no el gancho de cada commit. **Sin complemento para el ejecutor no
arranca**, y ahi se acaba la evaluacion: un proyecto sobre un ejecutor minoritario —`bun`, por
ejemplo, que solo tiene complemento de la comunidad— es un caso a comprobar antes de prometer nada. El
estado que guarda `--incremental` **se queda obsoleto en silencio** si cambia la configuracion o la
version, y entonces informa de un resultado que ya no corresponde al codigo: ante una cifra
sospechosa, borrar el estado y correr entero. En TypeScript, los mutantes que no compilan solo se
descartan como tales si esta instalado `@stryker-mutator/typescript-checker`; sin el, ensucian el
resultado. Y hay mutantes equivalentes que nunca se van a matar: **el 100% no es el objetivo**, el
objetivo es que ningun superviviente sea una sorpresa.
