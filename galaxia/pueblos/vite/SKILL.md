---
cosmos: pueblo
nombre: vite
padre: web/construccion-de-sitios
resumen: Servidor de desarrollo con arranque instantaneo via ESM nativo; sustituyo a webpack como estandar.
---

https://github.com/vitejs/vite · MIT · 82.661★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
npm create vite@latest mi-app -- --template react-ts
cd mi-app && npm install && npm run dev
```

```ts
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { port: 5173 },
  build: { target: "es2022" },
});
```

Gana a `webpack` en velocidad de arranque: sirve los módulos ES nativos del navegador sin
empaquetar nada en desarrollo, así que un proyecto grande arranca en milisegundos donde webpack
tarda segundos en construir el grafo de dependencias completo. Es además la base bajo la que corren
hoy `astro`, SvelteKit y buena parte de la nueva generación de frameworks — no es solo una
herramienta, es la capa de bajo nivel que todos comparten. Frontera con `astro`: aquel es el
framework de sitio completo (routing, contenido, SSR); esto es el motor de build y dev server que
`astro` usa por debajo.

Ojo: rapidísimo en desarrollo (ESM sin empaquetar) y empaquetado con `rollup` para producción son
**dos rutas de ejecución distintas** — un bug que solo aparece en `npm run build` y no en `npm run
dev` es la sorpresa más repetida, casi siempre por código que asume una variable de entorno o un
`import.meta` que se resuelve distinto en cada modo.
