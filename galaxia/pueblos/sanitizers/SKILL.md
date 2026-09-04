---
cosmos: pueblo
nombre: sanitizers
padre: rendimiento/depuracion
resumen: Detectan en ejecucion el desbordamiento, el uso despues de liberar y la carrera que ningun test ve.
---

https://github.com/google/sanitizers · Apache-2.0 con excepciones LLVM · 12.461★ · push 2026-05-19 (comprobado 2026-09-01)

Ese repositorio es la **documentación y el seguimiento de fallos**; la implementación viaja dentro del
compilador, en `compiler-rt` de https://github.com/llvm/llvm-project (40.038★, push 2026-09-01,
comprobado 2026-09-01). Por eso no hay nada que instalar: se activan con una bandera.

```bash
# memoria: desbordamiento, uso despues de liberar, fuga (la fuga NO, en macOS: ver abajo)
clang -fsanitize=address -fno-omit-frame-pointer -g -O1 prog.c -o prog && ./prog

# concurrencia: carrera de datos entre hilos
clang -fsanitize=thread -g -O1 prog.c -o prog && ./prog

# comportamiento indefinido, y que aborte en el primer hallazgo
clang -fsanitize=undefined -fno-sanitize-recover=all -g prog.c -o prog && ./prog

# en Rust, sobre nightly:
RUSTFLAGS="-Zsanitizer=address" cargo +nightly test --target x86_64-unknown-linux-gnu
```

No tienen competidor real: son la implementación de referencia y están integrados en los dos
compiladores mayores (Clang y GCC), así que el coste de adopción es una bandera en el fichero de
compilación. `valgrind` cubre parte de lo mismo sin recompilar, pero es entre diez y cincuenta veces
más lento y no detecta carreras de datos con la fiabilidad de `-fsanitize=thread`.

Ojo, y son tres avisos que deciden si el resultado vale: **no se combinan** —dirección e hilos son
incompatibles en la misma compilación, hay que pasar la suite dos veces—; **encarecen la ejecución**
(el doble o el triple de tiempo, y varias veces la memoria), así que van en una tarea aparte de la
tubería, no en cada compilación de desarrollo; y **solo ven lo que el código ejecuta**. Una suite con
poca cobertura pasa en verde con los mismos fallos dentro: verde aquí no es «no hay errores de
memoria», es «no los hubo en estos caminos».

Y el falso verde que hay que conocer, **medido en macOS arm64 con Apple clang 21** (2026-09-01): de las
tres cosas que promete el desinfectante de direcciones, **la fuga es la que calla en macOS**. El
programa que pierde memoria sale con 0 y sin una línea; forzar el detector lo confiesa; y pedirlo
suelto ni siquiera compila.

```bash
printf '#include <stdlib.h>\nint main(void){char*p=malloc(1234);p[0]=1;return 0;}\n' > fuga.c

clang -fsanitize=address -g -O1 fuga.c -o fuga && ./fuga; echo "EXIT=$?"
#   EXIT=0                    <- ni una palabra sobre los 1234 bytes perdidos

ASAN_OPTIONS=detect_leaks=1 ./fuga
#   ==NNNNN==AddressSanitizer: detect_leaks is not supported on this platform.   (aborta, 134)

clang -fsanitize=leak -g fuga.c -o fuga
#   clang: error: unsupported option '-fsanitize=leak' for target 'arm64-apple-darwin23.2.0'
```

Consecuencia práctica: en un portátil de esta familia, «pasé la suite con `-fsanitize=address` y no
hay fugas» es una frase vacía — no es que no las haya, es que nadie las buscó. Las fugas se cazan en
Linux (contenedor o máquina virtual), o con `leaks` de macOS contra el proceso vivo. Lo que sí
funciona aquí, comprobado con una carrera de dos hilos sobre la misma variable, es
`-fsanitize=thread`: la reporta en la primera ejecución, con el fichero y la línea.
