---
cosmos: pueblo
nombre: bevy
padre: juegos/motores
resumen: Motor sin editor: todo en codigo y con entidad-componente-sistema de fabrica.
---

https://github.com/bevyengine/bevy · Apache-2.0 (dual con MIT, a eleccion) · 47.989★ · último push 2026-09-01 (comprobado por API de GitHub el 2026-09-01).

```bash
brew install rust
cargo new mi-juego && cd mi-juego
cargo add bevy
```

```rust
use bevy::prelude::*;

#[derive(Component)]
struct Velocidad(Vec2);

fn mover(tiempo: Res<Time>, mut q: Query<(&mut Transform, &Velocidad)>) {
    for (mut t, v) in &mut q {
        t.translation += v.0.extend(0.0) * tiempo.delta_secs();
    }
}

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_systems(Update, mover)
        .run();
}
```

No compite con `godot`, lo complementa: aqui no hay editor visual ni arbol de escena, todo es codigo
y el modelo entidad-componente-sistema viene de fabrica. Se elige cuando el equipo ya piensa en Rust
o cuando lo que se construye es una herramienta o un motor propio encima, no un juego con un editor
rapido.

Y lo que no hace bien, dicho sin adornos:

- **La primera compilacion son minutos y aprieta el enlazado.** El enlazado de un `cargo build` de
  un proyecto Bevy limpio puede acaparar varios GB de RAM libres durante ese paso. Se mitiga con
  `cargo add bevy --features dynamic_linking` en desarrollo, pero es la barrera real de este pueblo.
  `raylib` arranca en segundos y se cita para ese caso.
- **Rompe la API en cada version menor.** Es un proyecto pre-1.0 con guia de migracion por version:
  un tutorial de hace seis meses no compila hoy. Fijar la version exacta en `Cargo.toml`.
- **No hay editor.** Colocar entidades a mano en codigo es lento para un juego con contenido; los
  mapas se dibujan en `tiled` y se importan.

Coste cero real: Apache-2.0/MIT, sin regalias ni umbral de ingresos, a diferencia de Unity y Unreal.
