# Juegos — videojuegos

Barrido GitHub para COSMOS. Nicho `juegos` (#9 de 20, `UNIVERSO.md`): motores, bucle de juego y
física, gestión de activos, herramientas de edición, audio, publicación multiplataforma, y
generación procedimental. Su propio código vive dentro (país `codigo-de-motor`), no en una capa
aparte.

Método: API de GitHub autenticada sobre las 10 consultas del encargo (godot, bevy, raylib, game
engine rust, game development tools, pixel art tools, tilemap editor, game audio library, entity
component system, procedural generation) + lookups directos para completar huecos (Tiled, LDtk,
Capacitor de audio, TIC-80 vs PICO-8, ECS alternativos). Estrellas/licencia/`pushed_at` en vivo,
2026-09-01. Las listas «awesome» (awesome-godot, awesome-game-engine-dev…) se usaron solo para
descubrir candidatos, no entran como recurso.

**Aviso de coste**: Unity y Unreal quedan fuera de la lista a propósito — no son gratis de verdad
(Unity cobra Pro/Enterprise por encima de umbrales de ingresos y tuvo el intento de "runtime fee" en
2023; Unreal cobra 5% de royalty por encima de 1M$ de ingresos brutos) y además son mucho más
pesados de instalar/correr que cualquier cosa de esta lista. Aseprite (editor de pixel art de
referencia) tampoco entra "de primera" por lo mismo: los binarios cuestan ~20$, aunque el código es
público y se puede compilar uno mismo gratis — se cita en segunda fila con esa matización, y
LibreSprite (fork 100% libre) ocupa su hueco en el top 10.

**Aviso de máquina (Mac 8 GB)**: el editor de Godot es ligero (unos cientos de MB) y va bien; la
**primera compilación de un proyecto Bevy** en Rust puede tardar varios minutos y usar bastante
RAM/CPU en el enlazado — normal, no es un fallo. Blender (mencionado como pieza de arte 3D, fuera de
esta lista porque no es específico de un motor) y motores de mundos fotorrealistas como Infinigen
**no encajan cómodos en 8 GB** — se marca explícitamente donde aparece.

---

## De primera

Máximo 10. Uno por hueco: motor con editor, motor code-first, motor web, arte pixel, mapas, ECS,
consola fantasía, audio, ruido procedimental.

1. **[Godot](https://github.com/godotengine/godot)** — 116.5k★, MIT, muy activo (push de hoy).
   **Por qué gana**: el único motor 2D/3D completo con editor visual que es gratis sin condiciones
   (sin royalties, sin fee por ingresos, sin cuenta) — exporta a escritorio, móvil y web desde el
   mismo proyecto. Es el motor por defecto salvo que el proyecto pida específicamente code-first
   (Bevy) o navegador puro sin instalar nada (Phaser).

2. **[Bevy](https://github.com/bevyengine/bevy)** — 48.0k★, Apache-2.0, muy activo (push de hoy).
   **Por qué gana su propio hueco (no compite con Godot, lo complementa)**: motor Rust "data-driven"
   sin editor visual — todo en código, ECS de fábrica, pensado para quien quiere control total o
   está construyendo herramientas/motor propio encima. Elegir Bevy cuando el equipo ya piensa en
   Rust o el proyecto necesita rendimiento/arquitectura ECS más que un editor rápido.

3. **[raylib](https://github.com/raysan5/raylib)** — 34.5k★, Zlib, activo. **Por qué gana**:
   biblioteca C mínima (no motor, no editor) para aprender programación de juegos desde cero o
   construir herramientas propias sin cargar con un motor entero — la opción más ligera de las tres
   para un Mac de 8 GB, arranca en segundos.

4. **[Phaser](https://github.com/phaserjs/phaser)** — 40.2k★, MIT, activo. **Por qué gana su hueco**:
   motor 2D para navegador (Canvas/WebGL) — el juego corre con abrir un HTML, sin instalar nada en
   el cliente ni exportar builds nativos. Encaja con el perfil de agencia web: minijuegos embebidos
   en una página, sin la fricción de tiendas de apps.

5. **[LibreSprite](https://github.com/LibreSprite/LibreSprite)** — 8.3k★, GPL-2.0, activo (push
   jun-2026). **Por qué gana frente a Aseprite**: fork del último commit GPLv2 de Aseprite,
   binarios precompilados **gratis de verdad** (Aseprite cobra ~20$ por los suyos aunque el código
   sea público). Editor de sprites/animación con las mismas bases que el estándar de facto del
   sector.

6. **[Tiled](https://github.com/mapeditor/tiled)** — 12.9k★, licencia NOASSERTION en metadata de
   GitHub (el proyecto documenta doble licencia BSD/GPL en su propio repo — **sin verificar en vivo
   hoy**, revisar `LICENSE.txt`), activo. **Por qué gana**: editor de mapas/tilesets universal — el
   formato `.tmx` lo importan casi todos los motores (Godot, Bevy vía `bevy_ecs_tiled`, Phaser,
   raylib) por plugin oficial o comunitario. LDtk (4.2k★, MIT) es la alternativa más moderna y
   ligera, se cita en segunda fila para cuando no hace falta esa compatibilidad universal.

7. **[EnTT](https://github.com/skypjack/entt)** — 13.1k★, MIT, activo. **Por qué gana frente a
   flecs**: la librería ECS en C++ moderna con más adopción y mejor rendimiento medido por
   benchmarks propios del proyecto — se usa dentro de motores comerciales reales (Minecraft
   incluido). flecs (8.6k★, foco en C con bindings multi-lenguaje) queda en segunda fila para cuando
   el ECS tiene que exponerse fuera de C++.

8. **[TIC-80](https://github.com/nesbox/TIC-80)** — 6.1k★, MIT, activo. **Por qué gana frente a
   PICO-8**: consola de fantasía (editor+runtime+build-in todo en una ventana, estética retro
   deliberada) **100% libre y gratis**, mientras que PICO-8 —la referencia del género— cuesta ~15$ y
   es cerrado. Satisface el filtro de coste cero sin perder la propuesta de valor (prototipar juegos
   pequeños rápido, con límites creativos a propósito).

9. **[miniaudio](https://github.com/mackron/miniaudio)** — 7.2k★, dominio público/MIT a elección
   (licencia dual, sin dependencias), muy activo. **Por qué gana frente a SoLoud**: un único fichero
   C, cero dependencias, reproducción y captura de audio multiplataforma — más activo que SoLoud
   (2.2k★, sin push desde ago-2024). Encaja directo en un proyecto raylib o Bevy sin traer un motor
   de audio completo.

10. **[noise-rs](https://github.com/Razaekel/noise-rs)** — 1.1k★, Apache-2.0. **Por qué gana**:
    biblioteca de ruido procedimental (Perlin, Simplex, Worley…) en Rust, ligera y sin más
    dependencias que hacer un `cargo add` — encaja con Bevy y con cualquier generador de terreno
    casero. Se prefiere sobre Infinigen (más potente pero exige Blender + GPU para render
    fotorrealista, no cabe cómodo en 8 GB de RAM — ver segunda fila).

---

## Segunda fila

- **[flecs](https://github.com/SanderMertens/flecs)** — 8.6k★. ECS en C puro con bindings a
  C++/otros lenguajes; preferible a EnTT cuando el ECS debe exponerse fuera de C++ (p. ej. un motor
  con scripting).
- **[Aseprite](https://github.com/aseprite/aseprite)** — 39.1k★, código público pero binarios de
  pago (~20$); el estándar real del sector si el presupuesto lo permite o se compila uno mismo.
- **[LDtk](https://github.com/deepnight/ldtk)** — 4.2k★, MIT. Editor de niveles moderno, más
  ligero y con mejor UX que Tiled; menos integraciones de terceros que Tiled.
- **[Pixelorama](https://github.com/Orama-Interactive/Pixelorama)** — 10.2k★, MIT, hecho en Godot.
  Alternativa GUI a LibreSprite, multiplataforma incluyendo versión web.
- **[GDevelop](https://github.com/4ian/GDevelop)** — 26.1k★. Motor 2D/3D **sin código** (eventos
  visuales); la opción cuando quien construye el juego no programa.
- **[libgdx](https://github.com/libgdx/libgdx)** — 25.4k★, Apache-2.0. Framework Java/Kotlin
  multiplataforma, maduro pero pesa más (JVM) que raylib/Bevy para un equipo pequeño.
- **[PixiJS](https://github.com/pixijs/pixijs)** — 48.1k★, MIT. Renderer WebGL puro, más bajo nivel
  que Phaser — usar cuando Phaser sobra y solo hace falta dibujar rápido en canvas.
- **[Excalibur](https://github.com/excaliburjs/Excalibur)** / **[Kaplay](https://github.com/kaplayjs/kaplay)** —
  2.3k★ / 1.8k★, motores web en TypeScript más pequeños que Phaser, para juegos simples con menos
  boilerplate.
- **[Defold](https://github.com/defold/defold)** — 6.3k★. Motor 2D en Lua, "completamente gratis"
  según el propio proyecto, ligero; alternativa cuando Lua es el lenguaje preferido del equipo.
- **[LÖVE](https://github.com/love2d/love)** — 8.7k★. Framework 2D minimalista en Lua, arranque
  instantáneo, ideal para prototipos y jams en máquinas modestas.
- **[kira](https://github.com/tesselode/kira)** — 1.1k★, Apache-2.0. Audio expresivo pensado para
  Bevy (mezcla, efectos, timing preciso) cuando miniaudio se queda corto.
- **[Infinigen](https://github.com/princeton-vl/infinigen)** — 7.2k★, BSD-3-Clause. Generación
  procedimental de mundos fotorrealistas — potente pero **exige Blender + GPU**, no cabe cómodo en
  8 GB de RAM; anotado aquí para no perderlo de vista si algún día se usa otra máquina.
- **[SoLoud](https://github.com/jarikomppa/soloud)** — 2.2k★. API C++ más simple que miniaudio,
  menos activo (sin push desde ago-2024) — sigue siendo válido para proyectos pequeños.

## Humo

- **[Dialogic](https://github.com/dialogic-godot/dialogic)** — sistema de diálogos/novela visual
  para Godot, listo para usar.
- **[Avian](https://github.com/avianphysics/avian)** — física 2D/3D para Bevy basada en ECS.
- **[bevy_ecs_tiled](https://github.com/adrien-bon/bevy_ecs_tiled)** — importa mapas Tiled en Bevy.
- **[godot-tiled-importer](https://github.com/vnen/godot-tiled-importer)** — lo mismo para Godot.
- **[RetroArch/libretro](https://github.com/libretro/RetroArch)** — frontend multiplataforma de
  emuladores, útil para probar cómo corre un juego en distinto hardware/input.
- **[jsfxr](https://github.com/chr15m/jsfxr)** / **[bfxr](https://github.com/increpare/bfxr)** —
  generadores instantáneos de efectos de sonido retro (estilo chiptune), cero curva de aprendizaje.
- **[Cocos Engine](https://github.com/cocos/cocos-engine)** — motor 2D/3D libre con tirón fuerte en
  el mercado móvil chino; alternativa a Godot si el target principal es Android en ese mercado.
- **[godot-demo-projects](https://github.com/godotengine/godot-demo-projects)** — proyectos
  oficiales de ejemplo, punto de partida rápido para aprender el editor.

---

## Mapeo a COSMOS

```
sistema-solar  juegos
├── continente  motores
│   ├── pais  motores-con-editor       provincias: Godot · GDevelop (sin código) · Defold · Cocos
│   ├── pais  motores-web              provincias: Phaser · PixiJS · Excalibur · Kaplay
│   ├── pais  motores-code-first       provincias: Bevy · raylib · LÖVE · libgdx
│   └── pais  codigo-de-motor          ← su propio código vive aquí
│              provincias: ECS (EnTT, flecs) · física (Avian) · bucle de juego
├── continente  activos-y-edicion
│   ├── pais  arte-pixel               provincias: LibreSprite · Pixelorama · (Aseprite, de pago)
│   ├── pais  mapas-y-niveles          provincias: Tiled · LDtk
│   └── pais  dialogo-y-narrativa      provincias: Dialogic
├── continente  audio
│   └── pais  motores-de-audio         provincias: miniaudio · SoLoud · kira · efectos retro (jsfxr, bfxr)
├── continente  generacion-procedimental
│   └── pais  ruido-y-terreno          provincias: noise-rs · (Infinigen, pesado — no cabe en 8GB)
└── continente  publicacion-multiplataforma
    └── pais  consolas-fantasia-y-testing   provincias: TIC-80 · RetroArch/libretro
```

Los mares del universo (`criterio`, `pruebas`, `resistencia`, `accesibilidad`, `custodia`) mojan
este nicho igual que a los otros 19 — sin invocación manual.

## Lo que falta

- **Ninguna herramienta de esta lista se ha probado en vivo hoy** (regla 5 del filtro) — es un
  barrido de metadata GitHub, no una prueba de campo. Antes de adoptar una para un proyecto real,
  abrir el editor/`cargo run`/`cargo build --example` correspondiente.
- **No hay ganador claro de "test automation for games"** buscando la frase literal — el hueco de
  testing automatizado específico de videojuegos (más allá de compilar y correr a mano) sigue
  abierto; lo más cercano encontrado fue RetroArch como frontend multiplataforma, que no es un
  framework de test.
- **Unity y Unreal se descartan a propósito** (ver aviso de coste arriba) — si algún proyecto de
  cliente ya viene en Unity/Unreal, ese trabajo cae fuera de este catálogo "coste cero" y hay que
  tratarlo aparte.
- **Blender** (modelado/animación 3D) no entra en esta lista porque no es específico de un motor de
  juegos — es una pieza transversal de la cadena de activos 3D que probablemente merece su propio
  hueco en el nicho `medios`, no aquí.
