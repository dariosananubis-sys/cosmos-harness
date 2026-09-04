---
cosmos: pueblo
nombre: payload
padre: web/construccion-de-sitios
resumen: CMS headless que es tambien tu backend Next.js; colecciones tipadas, admin panel y API REST/GraphQL.
---

https://github.com/payloadcms/payload · MIT · 44.552★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
npx create-payload-app@latest mi-cms
```

```ts
// src/collections/Productos.ts
import type { CollectionConfig } from "payload";

export const Productos: CollectionConfig = {
  slug: "productos",
  fields: [
    { name: "nombre", type: "text", required: true },
    { name: "precio", type: "number", required: true },
    { name: "imagen", type: "upload", relationTo: "media" },
  ],
};
```

```bash
npm run dev      # admin en /admin, API en /api/productos, GraphQL en /api/graphql
```

Gana a `strapi` (el CMS headless más nombrado) en que no es un servicio aparte: es una app Next.js
normal, así que el frontend y el backend viven en el mismo repo y el mismo despliegue, sin
sincronizar dos proyectos. Frente a WordPress+Elementor, que domina el país: gana cuando el
contenido lo consume una app propia por API (tienda con frontend a medida, app móvil) en vez de
servir el HTML final directamente; pierde cuando el cliente quiere editar visualmente su propia
maquetación, que es Elementor.

Ojo: es Next.js entero por debajo, así que hospedarlo pide un entorno Node con build, no un
hosting compartido de PHP como WordPress — el coste y la complejidad de despliegue son mayores
para un sitio simple. Y las migraciones de esquema entre versiones mayores de Payload (3.x) han
movido campos de configuración; fijar versión y leer el CHANGELOG antes de actualizar en
producción.
