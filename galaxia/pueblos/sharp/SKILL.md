---
cosmos: pueblo
nombre: sharp
padre: web/imagenes
resumen: Redimensiona y recomprime a formatos modernos en milisegundos por imagen.
---

https://github.com/lovell/sharp · Apache-2.0 · 32.624★ · último push 2026-08-30 (comprobado 2026-09-01)

```bash
npm install sharp
node -e "const s=require('sharp');s('entrada.jpg').resize({width:1600,withoutEnlargement:true}).webp({quality:80}).toFile('salida.webp').then(i=>console.log(i))"
```

Sobre `libvips`, la biblioteca de imagen más rápida que existe: redimensiona y recomprime a formatos
modernos en milisegundos por imagen. Es la pieza que convierte una carpeta de fotos de cámara en algo
que carga en un móvil, y la que hace que esa conversión quepa en un guion de despliegue en vez de en
una tarde.

Gana a `GoogleChromeLabs/squoosh` (25.772★) porque aquel es una aplicación web para tratar imágenes de
una en una — no se automatiza. Y gana a `imagemin/imagemin` (5.722★) por viveza: aquel lleva **sin push
desde 2025-03-07**, año y medio, y además necesita un compresor distinto por formato, mientras esto los
cubre todos con una API.

Ojo, dos cosas que muerden: `resize({width: N})` **amplía** una imagen más pequeña que `N` si no se
pone `withoutEnlargement: true`, y ampliar una foto de catálogo se ve. Y `sharp` trae binarios
compilados por plataforma: un `npm install` hecho en macOS y desplegado a un servidor Linux sin
reinstalar falla en tiempo de ejecución, no al instalar.
