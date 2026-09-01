---
cosmos: pueblo
nombre: samply
padre: rendimiento/velocidad/perfilado
resumen: Perfilador de muestreo nativo que no instrumenta nada y abre el resultado en el navegador.
---

https://github.com/mstange/samply · Apache-2.0 · 4.401★ · push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install samply        # o: cargo install --locked samply

samply record ./mi-binario --argumentos     # abre el resultado en el navegador al terminar
samply record --pid <PID>                   # engancharse a un proceso nativo ya en marcha
samply record --save-only -o perfil.json.gz ./mi-binario
```

Perfilador de muestreo nativo que **no instrumenta nada** y abre el resultado en la interfaz del
perfilador de Firefox: línea de tiempo, pila invertida, gráfico de llama y filtrado por hilo, sin
instalar una aplicación de escritorio. Gana a los perfiladores de máquina virtual de Java (como
`async-profiler`) y a `perf` en esta casa por lo pragmático: corre en este Mac y con este procesador
sin instalar nada más, mientras que `perf` es solo Linux y `Instruments` obliga a abrir Xcode entero.

Frontera con `py-spy`: para un proceso de **Python** ya corriendo en producción, el que se engancha
por identificador de proceso es aquel, que entra como pueblo propio.

Ojo: sin **símbolos de depuración** el perfil sale lleno de direcciones y no vale para nada — compilar
con `debug = true` en el perfil de release antes de medir. Y es un proyecto de una persona con 4.401
estrellas: es el pueblo con menos respaldo del nicho, y en Linux hay días en que `perf` ve cosas que
él no. Para medir de verdad en producción Linux, `perf` sigue siendo la referencia.
