---
cosmos: pueblo
nombre: blender
padre: juegos/activos
resumen: Modelado, animacion y render 3D con API de Python completa; se automatiza sin abrir ventana.
---

https://github.com/blender/blender · GPL (leído en `COPYING`, que remite a `doc/license/GPL-license.txt`
— texto de la versión 2) · 19.964★ · último push 2026-09-03 (comprobado 2026-09-03). Este es el
repositorio espejo en GitHub; el desarrollo real vive en `projects.blender.org`, y es el que cita la
web oficial — la URL de arriba sigue siendo válida para clonar y para citar estrellas de comunidad.

```bash
brew install --cask blender
```

```bash
# render por lote sin abrir interfaz, para un pipeline de assets de juego
blender -b escena.blend -o //render_ -f 1                      # un solo fotograma
blender -b escena.blend --python exportar.py -- --formato gltf # guion propio con argumentos tras --
```

```python
# exportar.py — se ejecuta dentro de Blender con --python; bpy solo existe en ese proceso
import bpy, sys
args = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.export_scene.gltf(filepath="/RUTA/AL/PROYECTO/modelo.glb", export_format="GLB")
```

Es el pueblo que faltaba en este país para la **creación** de activos 3D: `tiled` mapea niveles en
2D, `libresprite` dibuja arte de píxel y `miniaudio` reproduce el sonido ya grabado, pero ninguno
modela, anima ni renderiza en 3D. Gana a `Godot`/`Bevy` (los motores del país vecino) en que no es un
motor de juego — es donde se **produce** el modelo, la textura o la animación que luego importa el
motor, con exportadores nativos a glTF, FBX y USD.

Frente a herramientas de pago del mismo hueco (Maya, 3ds Studio Max, Cinema 4D), gana por ser libre y
por tener una **API de Python completa** (`bpy`) que convierte cualquier tarea repetitiva —convertir
cien modelos a un formato, generar variantes de una textura, hornear una colisión— en un guion que
corre en `--background` sin abrir ventana, apto para una tubería de integración continua.

Ojo: es una aplicación pesada — la interfaz completa y sus dependencias ocupan varios gigas de disco
y, al renderizar con el motor Cycles, puede tirar de GPU si está configurado para ello; con `-b` y sin
motor de trazado de rayos activado no supone ese coste. Y la superficie de `bpy` cambia entre
versiones mayores (2.8 rompió casi toda la API de guiones anteriores): un guion escrito para una
versión no se garantiza que corra en otra sin revisar las notas de migración.
