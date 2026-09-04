---
cosmos: pueblo
nombre: firecrawl
padre: extraccion/fuentes-web
resumen: Convierte un sitio entero en markdown listo para un modelo, con render de JavaScript incluido.
---

https://github.com/firecrawl/firecrawl · AGPL-3.0 · 175.900★ · último push 2026-09-03 (comprobado
2026-09-03). Código abierto y autoalojable; también existe como servicio de pago en firecrawl.dev
— aquí solo se documenta la vía autoalojada, sin cuenta ni tarjeta.

```bash
git clone https://github.com/firecrawl/firecrawl.git && cd firecrawl
cp .env.example .env      # USE_DB_AUTHENTICATION=false para la primera prueba, sin auth
docker compose up -d      # API + workers + Playwright + Redis + cola, todo local
```

```bash
curl -s -X POST http://localhost:3002/v1/scrape \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://SITIO-DEL-ALCANCE.example", "formats": ["markdown"]}'

curl -s -X POST http://localhost:3002/v1/crawl \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://SITIO-DEL-ALCANCE.example", "limit": 50}'
```

Frente a `trafilatura`, que **no ejecuta JavaScript** y devuelve `None` explícito en una página que
pinta el contenido en el cliente, aquí el motor incluye Playwright por dentro precisamente para ese
caso — a cambio de arrastrar un servicio con Redis y cola de trabajos, no una librería que se importa
y ya. Frente a `scrapy`/`crawlee`, que dan el control fino del rastreo (spiders, cola propia,
middlewares), aquí la salida ya viene troceada en markdown limpio pensado para entrar directo en el
contexto de un modelo — el trabajo está hecho, no la librería para hacerlo.

Gana a montar `playwright` + `trafilatura` a mano para el caso de "quiero el contenido de un sitio
entero en markdown, ya" — `/v1/crawl` descubre y sigue los enlaces del sitio con un solo endpoint. Se
pierde control fino frente a `scrapy` cuando el rastreo necesita reglas propias por sección o
paginación compleja.

Ojo, y es el aviso serio: la versión autoalojada por Docker Compose **no es un binario suelto** — trae
API, workers, Playwright, Redis, RabbitMQ y una base de datos Postgres propia (NuQ). En una máquina
justa de memoria, ese conjunto de servicios permanentes pesa igual que `windmill` o `fossology`: no
se levanta para una consulta puntual, se apaga cuando no se usa. Y la licencia es **AGPL-3.0 con
copyleft de red**: para uso interno o de agencia no estorba, pero ofrecerlo como servicio a terceros
sin publicar los cambios sí exige revisarla. El servicio de pago del mismo fabricante (`firecrawl.dev`,
con clave de API y facturación) es un producto aparte que no se contrata sin orden explícita — todo
lo de arriba corre en local a coste cero.
