---
cosmos: pueblo
nombre: tiled
padre: juegos
resumen: Editor de mapas y conjuntos de baldosas cuyo formato importan casi todos los motores por complemento.
---

https://github.com/mapeditor/tiled - GPL-2.0 segun el `COPYING` del repositorio para el editor, con
la biblioteca `libtiled` bajo BSD-2-Clause (la API de GitHub devuelve `NOASSERTION` por ser doble;
leer el fichero antes de redistribuir) - 12.860 estrellas - ultimo push 2026-08-27 (comprobado por
API de GitHub el 2026-09-01).

```bash
brew install --cask tiled
```

```bash
tiled --export-map mapa.tmx mapa.json      # a JSON, que es lo que leen los motores
tiled --export-tileset baldosas.tsx baldosas.json
```

```gdscript
# Godot, con el complemento de importacion de TMX
var mapa := load("res://mapas/mapa.tmx")
```

```js
// Phaser, con el JSON exportado arriba
this.load.tilemapTiledJSON('mapa', 'assets/mapa.json')
```

Es la pieza que falta entre el arte y el motor: los mapas se dibujan una vez y los leen `godot`,
`bevy` (por `bevy_ecs_tiled`) y `phaser` por complemento oficial o de la comunidad. Gana a
`deepnight/ldtk` (4,2k estrellas, MIT), que es mas moderno, mas ligero y de interfaz mas agradable,
precisamente por esa compatibilidad: cuando todavia no esta decidido el motor, el formato que todos
entienden vale mas que la interfaz mas bonita. Si el motor ya esta decidido y tiene importador de
LDtk, la comparacion se da la vuelta.

Y lo que no hace bien: es un editor de escritorio, no una biblioteca. No hay API para generar mapas
por programa mas alla de escribir el XML a mano, y la exportacion por linea de comandos requiere que
la aplicacion este instalada. Para mapas generados proceduralmente esto no sirve.

Ojo con la licencia antes de redistribuir: el editor es GPL-2.0. Eso no afecta a los mapas que
produces —el formato `.tmx` es tuyo— pero si al hecho de empaquetar el editor dentro de un producto
cerrado.
