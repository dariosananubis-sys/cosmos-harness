---
cosmos: pueblo
nombre: godot
padre: juegos
resumen: Motor 2D y 3D con editor visual, gratis sin regalias ni umbral de ingresos.
---

https://github.com/godotengine/godot · MIT · 116.475★ · último push 2026-08-31 (comprobado por API de GitHub el 2026-09-01).

```bash
brew install --cask godot
```

```gdscript
# jugador.gd — nodo CharacterBody2D
extends CharacterBody2D

const VELOCIDAD := 300.0

func _physics_process(delta: float) -> void:
    var direccion := Input.get_axis("ui_left", "ui_right")
    velocity.x = direccion * VELOCIDAD
    velocity.y += 980.0 * delta
    move_and_slide()
```

```bash
godot --path . --headless --export-release "Web" build/index.html   # exportar sin abrir el editor
godot --path . --headless --quit                                     # importar assets en tuberia
```

Es el motor por defecto salvo que el proyecto pida escribirlo todo en codigo (`bevy`) o correr en el
navegador sin instalar nada (`phaser`). Gana a Unity y a Unreal —los dos motores comerciales del
sector, que se nombran porque la decision se toma aqui— por dinero, y con el numero delante: Unreal cobra
**un 5 % de regalias sobre lo que el titulo ingrese por encima del primer millon de dolares**
(texto del propio Epic, leido el 2026-09-01); Unity cobra por licencia segun ingresos y ya cambio su
modelo de cobro con efecto retroactivo una vez. Godot es MIT: cero regalias, cero cuota, cero cuenta.

Ese millon es el umbral que decide, y decide en los dos sentidos: **por debajo, Unreal tambien sale
gratis**, asi que quien elija Godot por precio para un proyecto que no va a facturar un millon se
esta contando un cuento — ahi la comparacion honesta es por herramientas, no por dinero. Por encima,
cada 100.000 dolares de ingreso son 5.000 que no se pagan, y para entonces cambiar de motor cuesta
el proyecto entero. Por eso la decision es al elegir, no al publicar.

Y lo que no hace bien: el 3D pesado. Para un juego 3D con exigencias graficas altas, Unreal sigue
estando por delante en herramientas y en iluminacion, y hay que decirlo. El 2D de Godot, en cambio,
es de los mejores que hay.

Aviso de maquina: el editor abre en un Mac de 8 GB sin problema, pero la exportacion a web y a movil
requiere descargar las plantillas de exportacion (varios cientos de megas por version, y hay que
bajarlas otra vez en cada actualizacion del motor).
