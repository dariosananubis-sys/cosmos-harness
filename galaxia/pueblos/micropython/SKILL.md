---
cosmos: pueblo
nombre: micropython
padre: embebidos
resumen: Consola interactiva dentro del microcontrolador: se prueba un sensor sin recompilar ni volver a grabar.
---

Cambia el bucle de trabajo del firmware. Con `esp-idf` o `zephyr`, probar una linea son varios
minutos de compilar y grabar; aqui se escribe en la consola por el cable y responde.

Se usa para explorar el aparato nuevo y para el prototipo, y se baja a compilado cuando importan la
memoria, el consumo o el arranque. Correr los dos en el mismo proyecto en fases distintas es lo
normal, no una contradiccion.
