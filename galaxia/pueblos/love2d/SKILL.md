---
cosmos: pueblo
nombre: love2d
padre: juegos/motores
resumen: Motor 2D en Lua con tres funciones de ciclo de vida; el juego entero cabe en un zip renombrado a .love.
---

https://github.com/love2d/love · Zlib · 8.672★ · último push 2026-08-26 (comprobado 2026-09-03)

```bash
brew install --cask love
```

```lua
-- main.lua — el juego entero puede vivir en un solo fichero
function love.load()
    x, y = 400, 225
end

function love.update(dt)
    if love.keyboard.isDown("right") then x = x + 200 * dt end
    if love.keyboard.isDown("left")  then x = x - 200 * dt end
end

function love.draw()
    love.graphics.circle("fill", x, y, 20)
end
```

```bash
love .                          # ejecuta la carpeta con main.lua directamente
zip -9 -r mi-juego.love .       # empaqueta: renombrar el zip a .love ES el ejecutable multiplataforma
```

Ocupa un escalón distinto al de sus dos vecinos del país: frente a `raylib` (biblioteca en C, sin
bucle ni empaquetado resueltos), aquí `love.load`/`love.update`/`love.draw` ya son el ciclo de vida
completo del juego, con física (Box2D embebido), audio y física de partículas de fábrica. Frente a
`godot`, la diferencia es la ausencia deliberada de editor visual: no hay escena que arrastrar, todo
es Lua — lo que lo hace más rápido de aprender para quien ya sabe programar y peor para trabajo
visual (partículas, animación de huesos) que en `godot` se hace a golpe de ratón.

Gana a escribir el mismo juego 2D directamente sobre `SDL` en que el bucle, la carga de recursos y el
empaquetado multiplataforma (`.love` corre igual en Windows, macOS y Linux con el mismo binario) ya
están resueltos; se pierde el control de bajo nivel que sí tiene `raylib`.

Ojo: Lua no comprueba tipos ni goles de compilación — un error de nombre en una variable no se ve
hasta que esa línea se ejecuta en tiempo real, a mitad de partida. Y `love2d` no tiene sistema de
escenas ni editor: para un proyecto que crece más allá de un puñado de pantallas, organizar el
estado a mano se convierte rápido en el mismo problema que resuelve un motor con editor —momento en
el que conviene revisar si el proyecto no debería estar en `godot`.
