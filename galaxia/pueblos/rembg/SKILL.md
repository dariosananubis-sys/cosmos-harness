---
cosmos: pueblo
nombre: rembg
padre: web/imagenes
resumen: Quita el fondo de cientos de fotos de una pasada y deja el recorte con transparencia.
---

https://github.com/danielgatis/rembg · MIT · 24.566★ · último push 2026-08-18 (comprobado 2026-09-01)

```bash
pip install "rembg[cpu,cli]"
rembg i entrada.jpg salida.png                 # una
rembg p ./fotos-originales ./fotos-recortadas  # el lote entero
```

El único maduro de su hueco con licencia permisiva. Se ejecuta por lotes y deja el recorte con
transparencia, listo para la ficha de producto.

Gana a `nadermx/backgroundremover` (8.028★) en licencia y en adopción, y sobre todo en el modo por
lotes: `rembg p` recorre un directorio entero con un comando, que es como llega el trabajo real —
doscientas fotos de un catálogo, no una.

Ojo, el flujo que evita rehacerlo todo: **revisar una muestra antes de lanzar el lote**. El modelo se
come el pelo, los flecos y los objetos semitransparentes sin avisar y sin fallar — devuelve un PNG
perfectamente válido con el producto mutilado, así que el error no aparece hasta que alguien mira las
fotos en la tienda. Y la primera ejecución **descarga el modelo de la red** a la caché del usuario: en
una máquina sin salida falla ahí, no en el recorte.
