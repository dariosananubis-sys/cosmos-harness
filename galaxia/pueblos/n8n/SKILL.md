---
cosmos: pueblo
nombre: n8n
padre: automatizacion/flujos
resumen: Encadena cuatrocientas integraciones con nodos, con flujo de error y reintento por nodo.
---

https://github.com/n8n-io/n8n · Sustainable Use License (fair-code, no OSI) · 203.014★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
docker run -d --name n8n -p 5678:5678 \
  -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
# panel en http://localhost:5678

# crear un flujo por API (la clave sale de Ajustes > API)
curl -s -X POST http://localhost:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: <CLAVE_API>" -H "Content-Type: application/json" \
  -d '{"name":"aviso","nodes":[],"connections":{},"settings":{}}'
```

Gana a `Activepieces` y a `Huginn`, los otros dos del hueco, por comunidad y documentación: el caso
raro de las tres de la mañana ya lo escribió alguien, y eso es lo que de verdad se paga en una
herramienta de integración. Frente a `windmill`, la frontera es el formato: allí el automatismo es
código versionado, aquí es un grafo que se arrastra.

A las tres de la mañana: cada nodo tiene **Retry On Fail** (`maxTries`, `waitBetweenTries`), y el
flujo admite un **Error Workflow** global que se dispara con el error y el payload. Las ejecuciones
fallidas quedan guardadas con sus datos en Executions — esa es la cola muerta, y desde ahí se
reintenta a mano.

Ojo: sin Error Workflow configurado, un fallo nocturno **no avisa a nadie**; solo se ve entrando al
panel. Y la licencia no es libre estándar: es de uso sostenible —gratis para uso propio y
modificable, prohibido revenderlo como servicio alojado que compita—. Para lo que hace la casa no
estorba, pero condiciona ofrecerlo a un cliente como plataforma.
