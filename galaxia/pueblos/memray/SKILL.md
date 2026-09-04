---
cosmos: pueblo
nombre: memray
padre: rendimiento/perfilado
resumen: Perfilador de memoria de Python; dice que linea reservo cada byte, incluida memoria nativa.
---

https://github.com/bloomberg/memray · Apache-2.0 · 15.212★ · último push 2026-09-01 (comprobado 2026-09-03)

```bash
pip install memray
```

```bash
# perfila la ejecucion completa de un script y guarda el registro binario
memray run -o perfil.bin RUTA/AL/PROYECTO/script.py

# grafico de llama de memoria, navegable en el navegador
memray flamegraph perfil.bin

# engancharse a un proceso Python ya en marcha, sin reiniciarlo
memray attach --pid <PID>
```

Este oficio prometía «memoria» en su resumen y no traía ni un solo perfilador de memoria: todo lo
instalado (`py-spy`, `samply`) mide CPU y tiempo, no bytes reservados. `memray` rastrea cada
`malloc`/`free` de un proceso Python, incluida la memoria reservada por extensiones en C
(numpy, pandas, PyTorch) que un perfilador puro de Python no ve, y construye un árbol de
asignaciones por línea de código con su grafo de llamadas. Gana a `tracemalloc` (de la stdlib) en
que ve la memoria nativa además de la de objetos Python, y en que su reporte (`flamegraph`,
`table`) es mucho más navegable que una lista plana de líneas.

Ojo: el overhead de rastrear cada asignación es real — puede ralentizar el programa perfilado
notablemente, así que no es para dejarlo puesto en producción de forma permanente, sino para una
sesión de diagnóstico acotada. En macOS necesita compilar extensiones nativas (Xcode Command Line
Tools) la primera vez. Y como todo perfilador de memoria: un pico que ya se liberó antes del
volcado final no aparece si no se capturó con `--follow-fork` o en el momento exacto del pico.
