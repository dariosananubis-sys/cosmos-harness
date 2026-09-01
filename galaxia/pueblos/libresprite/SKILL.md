---
cosmos: pueblo
nombre: libresprite
padre: juegos
resumen: Editor de sprites y animacion con binarios gratis de verdad, no solo el codigo.
---

https://github.com/LibreSprite/LibreSprite - GPL-2.0 - 8.323 estrellas - ultimo push 2026-06-15
(comprobado por API de GitHub el 2026-09-01). Dos meses y medio sin movimiento: vivo, pero de ritmo
lento.

```bash
brew install --cask libresprite
```

```bash
# guion en Lua para procesos por lotes: exportar cada capa a un PNG
# (Archivo > Scripts en la interfaz, o el guion en ~/.config/libresprite/scripts/)
```

```lua
local sprite = app.activeSprite
for i, capa in ipairs(sprite.layers) do
  capa.isVisible = false
end
for i, capa in ipairs(sprite.layers) do
  capa.isVisible = true
  app.command.SaveFileCopyAs{ filename = "export/" .. capa.name .. ".png" }
  capa.isVisible = false
end
```

Gana a `aseprite/aseprite` —el estandar de facto del sector, que es su origen— en lo unico que
decide en este catalogo: Aseprite publica su codigo pero cobra unos 20 dolares por los binarios
compilados; este es la bifurcacion libre del ultimo commit con licencia GPLv2 y sus binarios son
gratis de verdad. Mismas bases: capas, animacion por fotogramas, paletas indexadas, exportacion a
hoja de sprites.

Y lo que no hace bien, dicho claro: **se quedo en el Aseprite de 2016**. Todo lo que Aseprite ha
anadido desde entonces —etiquetas de animacion mejoradas, la API de guiones moderna, mallas de
deformacion, mejoras de rendimiento— no esta aqui. Si el trabajo es de produccion diaria de arte
pixel, los 20 dolares de Aseprite se amortizan el primer dia y hay que decirlo; este pueblo existe
porque el criterio de coste cero de este catalogo es duro, no porque sea mejor herramienta.

Ritmo lento: dos meses y medio sin push. Es un pueblo a revisar cada trimestre, no uno sobre el que
construir una tuberia critica.
