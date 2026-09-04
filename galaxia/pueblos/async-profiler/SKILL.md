---
cosmos: pueblo
nombre: async-profiler
padre: rendimiento/perfilado
resumen: Perfilador de bajo overhead para la JVM; CPU, alocaciones y locks sin cambiar el codigo.
---

https://github.com/async-profiler/async-profiler · Apache-2.0 · 9.131★ · último push 2026-09-02 (comprobado 2026-09-03)

```bash
brew install async-profiler
```

```bash
# grafico de llama de CPU de una JVM ya en marcha, 30 segundos
asprof -d 30 -f perfil.html <PID>

# perfil de alocaciones de memoria en vez de CPU
asprof -e alloc -d 30 -f perfil-memoria.html <PID>
```

Es el equivalente de `py-spy` para el mundo JVM: se engancha a un proceso Java/Kotlin/Scala **ya
en marcha en producción**, sin instrumentar el código ni reiniciar el servicio, usando eventos
del propio sistema operativo y de la JVM (`perf_events` en Linux, `AsyncGetCallTrace`) en vez del
muestreo por interrupción de `hprof`/JVisualVM, que sufre el «problema de la línea de seguridad»
(safepoint bias): esas herramientas solo muestrean en puntos donde la JVM ya se detiene, así que
ven un perfil sesgado. Gana a JFR (Java Flight Recorder) integrado en overhead cuando se necesita
perfilar alocaciones o locks con más detalle sin activar todo el aparato de JFR.

Ojo: en Linux con contenedores, `perf_events` puede necesitar capacidades extra (`--cap-add
SYS_ADMIN` o ejecutar con privilegio) que un entorno gestionado (algunos PaaS) no concede — sin
eso, cae a un modo de menor precisión. Es específico de la JVM: no perfila código nativo llamado
vía JNI más allá del punto de entrada, igual que `py-spy` con extensiones en C de Python.
