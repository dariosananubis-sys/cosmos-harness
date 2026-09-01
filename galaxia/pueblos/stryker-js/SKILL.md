---
cosmos: pueblo
nombre: stryker-js
padre: rendimiento/calidad
resumen: Mutacion en JavaScript y TypeScript; usa la cobertura por test para reejecutar solo lo que toca el mutante.
---

https://github.com/stryker-mutator/stryker-js · Apache-2.0 · 3.068★ · push 2026-08-31 (comprobado 2026-09-01, v10.0.0)

```bash
npm i -D @stryker-mutator/core
npx stryker init                 # elige el ejecutor: vitest, jest, mocha, karma...

npx stryker run
npx stryker run --incremental    # reutiliza el informe anterior, solo lo cambiado
npx stryker run --concurrency 4 --mutate "src/precios/**/*.ts"
```

Hace lo mismo que su equivalente de Python —alterar el codigo y ver quien se entera— con una
diferencia de ingenieria que se nota: mide **que pruebas cubren cada linea** antes de empezar y,
para cada mutante, vuelve a ejecutar solo esas. Sumado a los procesos en paralelo y al modo
incremental, baja de horas a decenas de minutos en un proyecto normal. Sigue siendo mucho mas caro
que correr la suite una vez, asi que su sitio tambien es la ejecucion programada, no el gancho de
cada commit.

Contra `c8` o `istanbul` no hay debate posible, y es el argumento entero de este pueblo: un fichero
de pruebas del que se borren todos los `expect` conserva el **100% de cobertura** y baja a **0% de
mutacion**. Una de las dos cifras esta midiendo lo que a uno le importa.

Ojo: **necesita un complemento para el ejecutor** que use el proyecto; con un ejecutor sin
complemento no arranca, y ahi se acaba la evaluacion. El modo incremental guarda un fichero de
estado que **se queda obsoleto en silencio** si cambia la configuracion o la version, y entonces
informa de un resultado que ya no corresponde al codigo: ante una cifra sospechosa, borrar el estado
y correr entero. Los mutantes que producen un error de tipos se descartan por diseno, asi que el
porcentaje de TypeScript no es comparable con el del mismo codigo en JavaScript. Y, igual que en
Python, hay mutantes equivalentes que nunca se van a matar: **el 100% no es el objetivo**, el
objetivo es que ningun superviviente sea una sorpresa.
