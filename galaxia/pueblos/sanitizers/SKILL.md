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
# memoria: desbordamiento, uso despues de liberar, fuga
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
