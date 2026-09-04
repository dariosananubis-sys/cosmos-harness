---
cosmos: pueblo
nombre: pa11y
padre: cumplimiento/web-legal
resumen: Barrido de accesibilidad por lote contra una lista de URL, con umbral de fallo para la tuberia y evidencia.
---

https://github.com/pa11y/pa11y · LGPL-3.0 · 4.501★ · último push 2026-08-28 (comprobado 2026-09-03)

```bash
npm install -g pa11y pa11y-ci
```

```json
// .pa11yci — lista de URL y umbral, el fichero que hace esto reproducible
{
  "defaults": { "standard": "WCAG2AA", "runners": ["axe", "htmlcs"] },
  "urls": [
    "https://SITIO-DEL-CLIENTE.example/",
    "https://SITIO-DEL-CLIENTE.example/contacto"
  ]
}
```

```bash
pa11y https://SITIO-DEL-CLIENTE.example/ --reporter cli
pa11y-ci --json > evidencia-a11y.json     # codigo de salida != 0 si hay errores: para la tuberia
```

Puede usar `axe-core` **por dentro** como uno de sus dos motores (`runners: ["axe", "htmlcs"]`, junto
al histórico HTML_CodeSniffer) — no compite con él, lo envuelve. La diferencia de nicho es la que
importa: `axe-core` (en `web/calidad-de-sitio`) es el motor que se enchufa a mano en Playwright
dentro de una suite de calidad; `pa11y` es la capa de **cumplimiento** ya montada — lista de URL en
un fichero versionado, umbral de fallo declarado y un informe por lote pensado para adjuntarse como
evidencia legal (Kit Digital, auditoría de accesibilidad exigida por normativa), sin escribir una
línea de Playwright.

Gana a montar el mismo barrido a mano sobre `axe-core` en que ya trae el listado de URL, el
umbral y el informe hechos; se pierde granularidad de depuración interactiva, que es donde sigue
ganando `axe-core` con su interfaz de navegador.

Ojo: usando solo `htmlcs` (el motor por defecto si no se declara `runners`) se pierde toda la
cobertura extra de `axe-core` — declarar los dos runners explícitamente, no fiarse del valor por
defecto. Y el aviso de siempre en esta norma: cero errores de `pa11y-ci` es la mitad automatizable de
la norma revisada, no una certificación de accesibilidad — lo manual (foco, lector de pantalla, orden
de lectura) sigue siendo `a11y-auditoria-wcag`.
