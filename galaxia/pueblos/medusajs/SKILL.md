---
cosmos: pueblo
nombre: medusajs
padre: web/comercio-electronico
resumen: Motor de comercio headless en Node; carrito, pedidos y precios por API, sin frontend impuesto.
---

https://github.com/medusajs/medusa · MIT (Enterprise aparte) · 36.115★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
npx create-medusa-app@latest mi-tienda
```

```ts
// src/api/store/productos-destacados/route.ts — endpoint propio sobre el motor
import type { MedusaRequest, MedusaResponse } from "@medusajs/framework/http";

export async function GET(req: MedusaRequest, res: MedusaResponse) {
  const query = req.scope.resolve("query");
  const { data: productos } = await query.graph({
    entity: "product",
    fields: ["id", "title", "thumbnail"],
    filters: { tags: { value: "destacado" } },
  });
  res.json({ productos });
}
```

```bash
npx medusa develop      # backend en :9000, admin en :9000/app
```

Gana a `saleor/saleor` (el otro comercio headless en Python/GraphQL) cuando el equipo ya vive en
Node/TypeScript y quiere módulos propios (precios, promociones, cumplimiento) sin salir del mismo
lenguaje que el frontend. Frente a WooCommerce, que es el motor de comercio de este país en el
99% de los casos de cliente: gana cuando el catálogo lo consume una app o frontend a medida por
API; pierde en el caso normal de este taller, una tienda sobre WordPress que el cliente administra
desde el panel que ya conoce.

Ojo: "headless" significa que no trae front de tienda — construirlo (el Next.js Starter incluido
en el propio proyecto) es trabajo aparte, no viene con checkout listo para producción sin
personalizar. Y el nombre del pueblo es `medusajs`, no `medusa`: ese nombre ya lo usa
`crytic/medusa` (el fuzzer de contratos) en este mismo jardín.
