---
cosmos: pueblo
nombre: crawlee
padre: extraccion/fuentes-web
resumen: Cola de peticiones, rotacion de proxy y pool de navegador ya montados; scrapy lo cita como alternativa cuando falta eso.
---

https://github.com/apify/crawlee · Apache-2.0 · 25.629★ · último push 2026-09-03 (comprobado 2026-09-03).
Node ≥ 16. Hay puerto en Python, `apify/crawlee-python`, repositorio aparte.

```bash
npm install crawlee playwright
```

```javascript
import { PlaywrightCrawler, Dataset } from 'crawlee';

const rastreador = new PlaywrightCrawler({
    async requestHandler({ request, page, enqueueLinks, log }) {
        const titulo = await page.title();
        log.info(`${request.url}: ${titulo}`);
        await Dataset.pushData({ url: request.url, titulo });
        await enqueueLinks();              // sigue enlaces, respetando la cola y el mismo dominio
    },
    maxRequestsPerCrawl: 100,
});

await rastreador.run(['https://SITIO-DEL-ALCANCE.example']);
```

Ya estaba citado sin pueblo propio en la ficha de `scrapy` de este mismo país: «`apify/crawlee-python`
es la alternativa razonable si se quiere el pool de sesiones y el almacenamiento ya montados». Este
pueblo nombra ese hueco con su propio repositorio (el original en JS/TS, más estrellas y más viejo
que el puerto en Python citado allí). Frente a `scrapy`, la cola de peticiones, la rotación de proxy,
el pool de navegador (Playwright o Puppeteer) y el almacenamiento en disco ya vienen integrados de
fábrica, así que un rastreo con JavaScript pesado necesita menos piezas sueltas que montar.

Frente a `playwright` a secas, aporta justo lo que a este le falta para rastrear un sitio entero: cola
de URLs, deduplicación, reintentos y `enqueueLinks()` en vez de escribir ese bucle a mano. Frente a
`firecrawl`, la frontera es dónde corre: aquí todo vive en el propio proceso Node sin servicio
externo; `firecrawl` es una API (autoalojable, pero con más piezas) pensada para devolver markdown
listo para un modelo, no una librería para tejer la lógica de rastreo propia.

Ojo: el pool de navegador (`PlaywrightCrawler`) tiene el mismo coste de memoria que `playwright`
suelto — cada pestaña abierta es un proceso de Chromium, y `maxConcurrency` sin acotar en una máquina
justa de RAM se come todo lo demás. Y `enqueueLinks()` sin filtro de dominio sigue cualquier enlace
que encuentre: sin `strategy: 'same-domain'` o una lista de patrones, un rastreo puede salirse del
sitio que se quería cubrir y no parar nunca.
