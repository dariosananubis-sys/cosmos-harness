---
cosmos: pueblo
nombre: unlighthouse
padre: web/calidad-de-sitio
resumen: Pasa esa auditoria al sitio entero de un comando y guarda historico para ver regresiones.
---

https://github.com/harlan-zw/unlighthouse · MIT · 4.794★ · último push 2026-08-14 (comprobado 2026-09-01)

```bash
npx unlighthouse --site https://example.com
npx unlighthouse-ci --site https://example.com --budget 75 --build-static
```

Orquesta el motor anterior sobre **todas las URL descubiertas** y produce un panel comparable entre
ejecuciones. Es la diferencia entre auditar la portada y auditar el sitio: casi todos los problemas de
rendimiento de una web de cliente viven en las fichas y en el archivo, no en la home, que es la única
que se mira.

Gana a `GoogleChrome/lighthouse-ci` (7.063★), el orquestador equivalente del propio ecosistema, por
viveza: aquel lleva sin commits desde **2026-03-27**, más de cinco meses, mientras este está activo. Y
`unlighthouse-ci` cubre lo mismo que aquel resolvía —presupuesto por categoría y salida estática para
la integración continua— con un solo comando.

Ojo: descubre por rastreo, así que **lo que no esté enlazado no se audita** y la cifra de «páginas
revisadas» parece completa igualmente; conviene contrastarla con el sitemap. Y lanza muchas instancias
de Chrome en paralelo: en una máquina de 8 GB hay que bajar la concurrencia o el propio equipo
distorsiona la medición que se está tomando.
