---
cosmos: pueblo
nombre: a11y-auditoria-wcag
padre: web/calidad-de-sitio
resumen: Guiones de navegador para foco, reflow y tamano de objetivo: la mitad que ningun motor detecta.
---

https://github.com/masuP9/a11y-specialist-skills · MIT · 56★ · último push 2026-06-13 (comprobado 2026-09-01)

```bash
npx skills add masuP9/a11y-specialist-skills          # las 4 skills
npm install -D @a11y-skills/audit                     # el paquete con los guiones de navegador
```

Lo que trae y ningún motor de reglas da: guiones de Playwright dedicados a **foco visible, reflow,
espaciado de texto y tamaño del objetivo táctil** —la mitad de la norma que no se automatiza con
reglas estáticas— más la metodología WAIC de auditoría formal en cuatro fases (automatizada,
interactiva, manual, calidad de contenido).

Gana a `Community-Access/accessibility-agents` (403★, siete veces más estrellas) en profundidad de
mecanismo: aquella es en su mayor parte prosa alrededor del mismo motor de reglas
—`dequelabs/axe-core`— envuelta en 79 agentes. Aquí hay un paquete npm que se ejecuta. Es el pueblo
hermano de `axe-core`: aquel encuentra el 57 % automatizable, esto ataca el resto.

Ojo, dos cosas: **último push 2026-06-13**, casi tres meses sin actividad — el más parado de los cuatro
de este nicho, vigilar antes de apoyar en él un compromiso con cliente. Y ninguna de las cuatro fases
sustituye la comprobación con lector de pantalla y teclado real: la fase «manual» es una lista de qué
mirar, no una medición. Declarar WCAG AA con esto solo es un falso verde.
