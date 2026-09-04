---
cosmos: pueblo
nombre: scalene
padre: rendimiento/perfilado
resumen: Perfila CPU, GPU y memoria a la vez y separa el tiempo propio del de librerias nativas.
---

https://github.com/plasma-umass/scalene · Apache-2.0 · 13.496★ · último push 2026-08-27 (comprobado 2026-09-03)

```bash
pip install scalene
```

```bash
# perfila CPU + memoria + GPU (si hay) de un script, con reporte HTML interactivo
scalene RUTA/AL/PROYECTO/script.py

# solo un rango del codigo, marcado con comentarios @profile en las funciones de interes
scalene --profile-only script.py
```

Frontera con `py-spy` y `memray`: donde `py-spy` mide CPU de un proceso ya en marcha desde fuera y
`memray` mide solo memoria en profundidad, `scalene` da los tres a la vez (CPU, GPU, memoria) en
una sola pasada por línea, y lo hace **distinguiendo tiempo en código Python del tiempo en código
nativo** (C, numpy) automáticamente — sin esa distinción, una línea que llama a una función de
numpy parece cara cuando el cuello real puede estar en cómo se la llama, no en la llamada en sí.
Gana a `cProfile` en que su overhead es muy inferior al usar muestreo en vez de instrumentar cada
llamada, y añade GPU (uso de NVIDIA vía `nvidia-smi`) que ningún otro perfilador de este país mide.

Ojo: el desglose GPU solo funciona con GPU NVIDIA — en Apple Silicon esa parte del reporte queda
vacía. Es de muestreo como `py-spy`, así que funciones muy cortas y muy frecuentes pueden
subestimarse. Y el reporte HTML interactivo, aunque muy legible, es más pesado de generar que un
`.svg` de llama plano: para una sesión rápida de "¿qué línea gasta más?", puede bastar con la
salida de terminal (`--cli`) sin abrir el navegador.
