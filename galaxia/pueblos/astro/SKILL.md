---
cosmos: pueblo
nombre: astro
padre: web/construccion-de-sitios
resumen: Genera HTML estatico por defecto y solo envia JS a los componentes que de verdad lo necesitan.
---

https://github.com/withastro/astro · MIT · 62.252★ · último push 2026-09-03 (comprobado 2026-09-03, `.../commits/HEAD.atom`)

```bash
npm create astro@latest mi-sitio
cd mi-sitio && npm run dev      # http://localhost:4321
```

```astro
---
// src/pages/index.astro — corre en build, no llega al navegador
const productos = await fetch("https://api.example.com/productos").then(r => r.json());
---
<html lang="es">
  <body>
    <h1>Catalogo</h1>
    {productos.map((p) => <article>{p.nombre}</article>)}
    <!-- solo este componente carga su JS, y solo cuando es visible -->
    <script src="/carrito.js" client:visible></script>
  </body>
</html>
```

Frente a `wordpress`+Elementor, que domina el país (7 de 7 sitios de cliente): gana cuando el
sitio es **contenido que no cambia por visita** — landing, catálogo estático, documentación,
blog — y lo que importa es la puntuación de rendimiento, no que el cliente edite el contenido
él mismo desde un panel visual. Su "hidratación parcial" (`client:visible`, `client:idle`) manda
cero JavaScript de framework hasta que un componente concreto lo necesita, al revés que un SPA que
carga el framework entero para pintar una página estática. Pierde frente a WordPress+Elementor en
el caso que domina este país: un cliente que edita su propio contenido sin tocar código.

Ojo: escribir en `.astro` con islas de React/Vue/Svelte mezcladas es cómodo hasta que hay que
depurar el límite entre lo que corre en build y lo que corre en el navegador — un error ahí no
avisa igual que un error de runtime normal. Y sin plugin del framework de turno, los componentes
de isla no hidratan: el fallo típico es olvidar `client:*` y preguntarse por qué el botón no hace
nada.
