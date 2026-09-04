---
cosmos: pueblo
nombre: katana
padre: visibilidad/auditoria
resumen: Rastreador en Go que tambien lee JavaScript para sacar endpoints; advertools no renderiza y este si, en modo headless.
---

https://github.com/projectdiscovery/katana · MIT · 17.379★ · último push 2026-08-31 (comprobado
2026-09-03). De ProjectDiscovery, mismo equipo que `nuclei`.

```bash
brew install katana
```

```bash
katana -u https://SITIO-DEL-ALCANCE.example -d 3 -o urls.txt        # profundidad 3, a fichero

# modo headless: sigue enlaces que solo aparecen tras ejecutar JavaScript
katana -u https://SITIO-DEL-ALCANCE.example -headless -jc -o urls-js.txt

# solo lo que cuelga de rutas concretas, con limite de ritmo
katana -u https://SITIO-DEL-ALCANCE.example -mrs 500 -rl 50
```

El falso verde que `advertools` declara en su propia ficha —«no renderiza JavaScript: un sitio que
pinta el contenido en el navegador sale casi vacío y sin error»— es exactamente lo que resuelve
`katana` con `-headless`: levanta un navegador de verdad para descubrir rutas que solo existen tras
ejecutar el JavaScript de la página, además de parsear el JavaScript estático en busca de endpoints
de API embebidos (`-jc`, «JavaScript crawling»). Escrito en Go, así que un rastreo de miles de URL es
más rápido y con menos memoria que el equivalente sobre Scrapy.

Frontera con `advertools`: aquel devuelve **tablas** listas para `pandas` (título, H1, estado, todo
en una fila) pensadas para análisis SEO; `katana` devuelve una **lista de URLs y endpoints**, más
cerca de mapear la superficie de un sitio (qué existe) que de auditar su contenido (cómo está cada
página). Se usan en cascada: `katana` para descubrir, `advertools` para analizar lo
descubierto.

Ojo: el modo `-headless` necesita un navegador Chromium instalado y consume bastante más memoria y
CPU que el rastreo simple — en una máquina justa de recursos, reservarlo para cuando el rastreo sin
JavaScript salga sospechosamente corto. Y como todo rastreador activo, `-rl` (límite de ritmo) no es
opcional contra la web de un cliente: sin él, un catálogo grande puede generar suficiente tráfico
como para parecer una prueba de carga no pedida. El alcance autorizado se verifica antes de cada
rastreo, igual que con `nuclei`.
