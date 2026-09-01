---
cosmos: pueblo
nombre: platformio
padre: embebidos
resumen: Un solo comando compila para cuarenta plataformas y resuelve librerias por proyecto.
---

https://github.com/platformio/platformio-core - Apache-2.0 - 9.431 estrellas - ultimo push
2026-08-28 (comprobado por API de GitHub el 2026-09-01).

```bash
pipx install platformio
```

```ini
; platformio.ini
[env:esp32dev]
platform  = espressif32
board     = esp32dev
framework = espidf
monitor_speed = 115200
lib_deps  = knolleary/PubSubClient@^2.8
```

```bash
pio project init --board esp32dev
pio run                 # compila
pio run -t upload       # graba
pio device monitor      # consola serie
```

Gana a instalar a mano la cadena de compilacion de cada fabricante (`esp-idf` por un lado,
`raspberrypi/pico-sdk` por otro, STM32Cube por otro): un solo comando cubre mas de cuarenta
plataformas y las librerias se fijan por proyecto en `platformio.ini`, no en una carpeta global
compartida. En un Mac de 8 GB, cada IDE nativo aparte es lo que revienta el disco.

Y lo que no hace bien: por debajo sigue llamando al framework del fabricante, asi que cuando el
error es de verdad — una particion mal calculada, un `sdkconfig` que no aplica — la capa de en medio
estorba y hay que ir a leer la documentacion de `esp-idf` igualmente. Ademas cada `platform` que
anadas se descarga entera a `~/.platformio`: cuatro plataformas ya son varios gigas.

Necesita hardware fisico para `upload` y `monitor`. `pio run` a secas compila y no prueba nada.
