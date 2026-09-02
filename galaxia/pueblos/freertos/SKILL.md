---
cosmos: pueblo
nombre: freertos
padre: embebidos/firmware
resumen: El nucleo mas pequeno y mas desplegado: planificador, colas y semaforos, y nada mas alrededor.
---

https://github.com/FreeRTOS/FreeRTOS · MIT · 7.749★ · último push 2026-08-26 (comprobado por API de GitHub el 2026-09-01). El nucleo suelto, sin las demos, esta en https://github.com/FreeRTOS/FreeRTOS-Kernel.

```bash
git clone --recurse-submodules https://github.com/FreeRTOS/FreeRTOS-Kernel.git
```

```c
/* Dos tareas y una cola: el "hola mundo" real del planificador. */
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

static QueueHandle_t cola;

static void productor(void *arg) {
    uint32_t n = 0;
    for (;;) { xQueueSend(cola, &n, portMAX_DELAY); n++; vTaskDelay(pdMS_TO_TICKS(500)); }
}
static void consumidor(void *arg) {
    uint32_t n;
    for (;;) { xQueueReceive(cola, &n, portMAX_DELAY); /* usar n */ }
}
void app_main(void) {
    cola = xQueueCreate(8, sizeof(uint32_t));
    xTaskCreate(productor,  "prod", 2048, NULL, 5, NULL);
    xTaskCreate(consumidor, "cons", 2048, NULL, 5, NULL);
    vTaskStartScheduler();   /* en ESP-IDF ya esta arrancado: no se llama */
}
```

Empata a proposito con `zephyrproject-rtos/zephyr` (16.370 estrellas, Apache-2.0), y la frontera es
esta: aqui cuando hace falta el nucleo minimo, cuando la placa apenas tiene RAM o cuando ya existe
codigo escrito sobre el; alli cuando el proyecto es nuevo y quiere de fabrica cientos de placas,
controladores, red, sistema de ficheros y arranque firmado. Este es un planificador con colas y
semaforos; aquel es un sistema operativo con su ecosistema. Elegir Zephyr por costumbre en una placa
diminuta se paga en memoria.

Y lo que no hace bien: no trae pila de red, ni controladores, ni sistema de ficheros, ni gestor de
paquetes. Todo eso lo pone el framework del fabricante — en un ESP32, `esp-idf` ya lleva FreeRTOS
dentro y arranca el planificador por ti, asi que llamar a `vTaskStartScheduler()` alli cuelga.

Necesita hardware fisico para servir de algo: un puerto simulado en Mac (`POSIX`) sirve para
entender la API, no para medir tiempos reales.
