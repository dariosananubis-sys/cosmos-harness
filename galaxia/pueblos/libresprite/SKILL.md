---
cosmos: pueblo
nombre: libresprite
padre: juegos
resumen: Editor de sprites y animacion con binarios gratis de verdad, no solo el codigo.
---

https://github.com/LibreSprite/LibreSprite - GPL-2.0 - 8.323 estrellas - ultimo push 2026-06-15
(comprobado por API de GitHub el 2026-09-01). **El push enganya y hay que mirar las versiones, no los
commits**: la ultima estable es la **v1.1, de 2023-12-03**, y la v1.2 (2025-03-02) sigue marcada como
prelanzamiento. Casi dos anos sin binario estable, con el codigo moviendose.

**No hay formula ni cask en Homebrew**, aunque medio internet lo repita:
`brew install --cask libresprite` responde `Error: Cask 'libresprite' is unavailable: No Cask with
this name exists.` (comprobado el 2026-09-01). Se baja el binario de la pagina de versiones, y el
paso del final no es opcional: el `.app` viene con **firma ad hoc**, no notarizada
(`codesign -dv` -> `Signature=adhoc`), asi que Gatekeeper lo bloquea sin decir por que.

```bash
curl -L -o libresprite.dmg \
  https://github.com/LibreSprite/LibreSprite/releases/download/v1.2/libresprite-development-macos-arm64.dmg
hdiutil attach -nobrowse libresprite.dmg          # monta en /Volumes/LibreSprite
cp -R /Volumes/LibreSprite/libresprite.app /Applications/
hdiutil detach /Volumes/LibreSprite
xattr -dr com.apple.quarantine /Applications/libresprite.app
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

Ritmo a vigilar, y la senal buena no es el push: son las **versiones**. Un proyecto que commitea y no
publica estable en veintiun meses es uno del que se baja un prelanzamiento y se cruza los dedos. Se
revisa cada trimestre mirando `/releases`, no `/commits`, y no se construye encima una tuberia
critica.
