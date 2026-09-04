---
cosmos: pueblo
nombre: tailwindcss
padre: web/construccion-de-sitios
resumen: Clases utilitarias en el propio HTML; el CSS final solo lleva lo que de verdad se uso.
---

https://github.com/tailwindlabs/tailwindcss · MIT · 97.431★ · último push 2026-08-31 (comprobado 2026-09-03)

```bash
npm install tailwindcss @tailwindcss/vite
```

```html
<!-- index.html -->
<link href="/src/estilos.css" rel="stylesheet">
<button class="rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700">
  Guardar
</button>
```

```css
/* src/estilos.css */
@import "tailwindcss";
```

Gana a escribir CSS a mano o con Bootstrap en velocidad de iteración: el diseño se ve y se cambia
sin saltar de fichero, y el motor solo genera en el CSS final las clases que de verdad aparecen en
el código — un proyecto grande no arrastra reglas muertas. Frontera con Elementor, que domina el
país: aquel es visual para quien no escribe código; esto es para quien sí escribe HTML/JSX y quiere
el mismo resultado sin salir de la plantilla.

Ojo: el HTML se llena de clases largas y repetidas — sin extraer a un componente (`<Boton>` en
vez de repetir la cadena de clases seis veces), el marcado se vuelve difícil de leer a simple
vista, aunque el CSS final sea pequeño. Y la v4 cambió la configuración de `tailwind.config.js` a
directivas `@theme` dentro del propio CSS: un tutorial o snippet de la v3 no se copia y pega tal
cual.
