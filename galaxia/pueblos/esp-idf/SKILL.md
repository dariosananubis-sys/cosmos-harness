---
cosmos: pueblo
nombre: esp-idf
padre: embebidos/firmware
resumen: Framework del fabricante para el microcontrolador mas usado, con radio y bluetooth.
---

https://github.com/espressif/esp-idf · Apache-2.0 · 18.916★ · último push 2026-08-31 (comprobado 2026-09-01)
(comprobado por API de GitHub el 2026-09-01).

```bash
brew install cmake ninja dfu-util python3
git clone --recursive https://github.com/espressif/esp-idf.git ~/esp/esp-idf
~/esp/esp-idf/install.sh esp32
```

```bash
. ~/esp/esp-idf/export.sh          # cada terminal nueva
idf.py create-project hola && cd hola
idf.py set-target esp32
idf.py build
idf.py -p /dev/cu.usbserial-0001 flash monitor
```

Gana a `espressif/arduino-esp32` (17,3k estrellas, LGPL-2.1), que es el otro camino al mismo chip:
aquel expone la API de Arduino y esconde el sistema operativo; este da acceso directo al FreeRTOS de
abajo, a la particion de flash, al arranque seguro y al ahorro de energia. Cuando el firmware pasa
de encender un LED a dormir en microamperios y actualizarse por radio, se acaba aqui de todos modos.

Necesita hardware fisico. Sin una placa ESP32 conectada (clones desde unos 3 euros) esto solo
compila: `flash` y `monitor` fallan, y un `build` verde no dice absolutamente nada sobre si el
firmware funciona. Es el falso verde clasico del nicho.

Aviso de maquina: `install.sh` se baja la cadena de compilacion completa y deja del orden de varios
gigas en `~/.espressif`. En un Mac de 8 GB cabe, pero no es una instalacion que se hace por curiosidad.
