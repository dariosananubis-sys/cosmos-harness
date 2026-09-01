---
cosmos: pueblo
nombre: windmill
padre: automatizacion
resumen: Convierte un guion en webhook, flujo e interfaz sin dibujar nodos: el automatismo es codigo.
---

https://github.com/windmill-labs/windmill · Apache-2.0 y AGPL-3.0 según directorio, con módulos propietarios · 17.752★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
curl -fsSL https://raw.githubusercontent.com/windmill-labs/windmill/main/docker-compose.yml -o docker-compose.yml
curl -fsSL https://raw.githubusercontent.com/windmill-labs/windmill/main/.env -o .env
docker compose up -d                  # panel en http://localhost:8000

npm install -g windmill-cli
wmill workspace add <espacio> <espacio> http://localhost:8000/
wmill sync push                       # los guiones del repositorio suben versionados
```

Gana a `n8n` cuando el automatismo ya es código: aquí un guion de Python, TypeScript, Go o Bash se
convierte solo en webhook, en paso de flujo, en tarea programada y en formulario, conservando tipos
y pruebas. Dibujar con nodos lo que ya está escrito es un paso atrás — y revisar un diff de nodos en
JSON es peor que revisar un diff de código.

A las tres de la mañana: reintentos por paso con espera constante o exponencial, tiempo límite por
trabajo, y **manejador de error a nivel de flujo**; los trabajos fallidos quedan en la vista de
Runs con su entrada exacta, que es la cola muerta desde la que se relanza. Además tiene concurrencia
limitada por ruta, que es lo que evita que el reintento de las tres de la mañana tumbe la API a la
que llama.

Ojo: la licencia es mixta por directorio (Apache-2.0, AGPL-3.0 y una edición empresarial cerrada).
Antes de empotrar nada en un producto de cliente, mirar bajo qué fichero de licencia cae el
directorio que se toca. Y el modo de un solo contenedor lleva PostgreSQL dentro: para producción,
base de datos aparte y `wmill sync` contra un repositorio, no ediciones en el panel.
