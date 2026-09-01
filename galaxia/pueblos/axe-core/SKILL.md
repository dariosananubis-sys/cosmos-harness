---
cosmos: pueblo
nombre: axe-core
padre: web/calidad-de-sitio
resumen: Motor de reglas que encuentra automaticamente cerca de la mitad de los fallos de la norma.
---

https://github.com/dequelabs/axe-core · MPL-2.0 · 7.462★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
npx @axe-core/cli https://example.com --tags wcag2a,wcag2aa
npm install --save-dev axe-core @axe-core/playwright
```

```javascript
import { AxeBuilder } from '@axe-core/playwright';
const resultados = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
console.log(resultados.violations.length, resultados.incomplete.length);
```

El dato honesto lo publica el propio proyecto: encuentra en promedio el **57 %** de los problemas de la
norma. Por eso entra el motor y no las colecciones de agentes que lo envuelven — todas ellas llaman a
esto por debajo, así que instalar el envoltorio es pagar dos veces por el mismo hallazgo.

Gana a `pa11y/pa11y` (4.493★) en licencia y en integración: MPL-2.0 frente a LGPL-3.0, y el mismo motor
enchufado a Playwright con tres líneas. `dequelabs/axe-core-npm` (720★) no aporta motor, solo el
enchufe de línea de comandos; se usa con `npx` y no se instala.

Ojo, y es el falso verde más caro de la accesibilidad: **cero violaciones no es una web accesible**, es
el 57 % revisado. El otro 43 % —foco, reflow, orden de lectura, texto alternativo con sentido— no lo
ve ninguna máquina y va en el pueblo hermano `a11y-auditoria-wcag`. Y `results.incomplete` es la lista
que casi todo el mundo ignora: son comprobaciones que axe **no pudo decidir**, no comprobaciones
pasadas.
