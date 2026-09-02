---
cosmos: pueblo
nombre: mimalloc
padre: rendimiento
resumen: Reservador de memoria de sustitucion directa: se enlaza o se precarga y se nota, sin tocar el codigo.
---

https://github.com/microsoft/mimalloc · MIT · 13.342★ · push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install mimalloc

# 1. medir ANTES, sin tocar el programa
hyperfine --warmup 3 './mi-programa datos.txt'

# 2. precargar el reservador y volver a medir  (macOS)
hyperfine --warmup 3 \
  'DYLD_INSERT_LIBRARIES=/opt/homebrew/lib/libmimalloc.dylib ./mi-programa datos.txt'
# en Linux:  LD_PRELOAD=/usr/lib/libmimalloc.so ./mi-programa datos.txt

# o enlazado, sin variables de entorno:
clang prog.c -o prog -lmimalloc
```

Es de las pocas mejoras de rendimiento que **no exige entender el programa**: se cambia el reservador
y se mide con `hyperfine` antes y después. Gana a `jemalloc`, la alternativa clásica del hueco, por
facilidad de adopción en un proyecto nuevo (una biblioteca, sin ajustes obligatorios) y por soporte
nativo de la arquitectura de los portátiles actuales, donde `jemalloc` fue durante años terreno
incómodo.

Ojo, y es lo que evita anunciar una mejora que no existe: **si el programa no reserva memoria en el
camino caliente, no cambia nada**. Como toda optimización, entra después de medir, no antes. Además,
`mimalloc` cambia el consumo de memoria residente: puede ir más rápido y ocupar más RAM, así que la
medición tiene que mirar las dos cosas. Y `DYLD_INSERT_LIBRARIES` **no funciona** contra binarios
firmados y protegidos del sistema en macOS: si el programa es del sistema, la precarga se ignora en
silencio y la comparación sale plana sin que nada avise.
