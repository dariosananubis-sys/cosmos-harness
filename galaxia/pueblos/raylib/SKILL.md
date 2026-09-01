---
cosmos: pueblo
nombre: raylib
padre: juegos
resumen: Biblioteca en C minima, sin motor ni editor: arranca en segundos y sirve para aprender o para hacer herramientas.
---

https://github.com/raysan5/raylib - Zlib - 34.547 estrellas - ultimo push 2026-08-29 (comprobado por
API de GitHub el 2026-09-01).

```bash
brew install raylib
```

```c
// juego.c
#include "raylib.h"

int main(void) {
    InitWindow(800, 450, "ejemplo");
    SetTargetFPS(60);
    Vector2 pos = { 400, 225 };
    while (!WindowShouldClose()) {
        if (IsKeyDown(KEY_RIGHT)) pos.x += 2.0f;
        if (IsKeyDown(KEY_LEFT))  pos.x -= 2.0f;
        BeginDrawing();
            ClearBackground(RAYWHITE);
            DrawCircleV(pos, 20, MAROON);
        EndDrawing();
    }
    CloseWindow();
    return 0;
}
```

```bash
cc juego.c -o juego $(pkg-config --libs --cflags raylib) && ./juego
```

Es el escalon de abajo de `godot` y `bevy`: no hay editor, ni escena, ni sistema de activos. Hay una
ventana, un bucle y funciones de dibujo — y compila y arranca en segundos, que es lo que lo hace la
unica de las tres comoda en una maquina de 8 GB con memoria justa. Se elige para entender como
funciona un juego por dentro o para construir una herramienta propia sin cargar con un motor entero.

Y lo que no hace bien: todo lo que un motor hace por ti. No hay gestion de escenas, ni serializacion
de estado, ni interfaz de usuario mas alla de lo minimo, ni exportacion a moviles resuelta, ni
sistema de fisicas. En cuanto el proyecto pide escenas, animacion y publicar en varias plataformas,
se sube a `godot` y se acepta el peso.

La licencia Zlib permite uso comercial cerrado sin atribucion obligatoria en el binario — mas
permisiva que la GPL de otras alternativas del hueco.

Encaja con `miniaudio` para el sonido y con `tiled` para los mapas, y ninguno de los tres arrastra
un subsistema entero.
