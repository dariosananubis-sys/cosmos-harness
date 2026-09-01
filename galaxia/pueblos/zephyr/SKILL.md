---
cosmos: pueblo
nombre: zephyr
padre: embebidos
resumen: Tiempo real con cientos de placas soportadas, arbol de dispositivo y arranque firmado.
---

https://github.com/zephyrproject-rtos/zephyr - Apache-2.0 - 16.370 estrellas - ultimo push
2026-09-01 (comprobado por API de GitHub el 2026-09-01). Proyecto de la Linux Foundation.

```bash
brew install cmake ninja gperf python3 ccache qemu dtc libmagic
pipx install west
west init ~/zephyrproject && cd ~/zephyrproject && west update
west zephyr-export
pip install -r zephyr/scripts/requirements.txt
west sdk install
```

```bash
cd ~/zephyrproject/zephyr
west build -p always -b esp32_devkitc/esp32/procpu samples/basic/blinky
west flash
west build -p always -b qemu_x86 samples/hello_world && west build -t run   # sin placa
```

Empata de verdad con `FreeRTOS/FreeRTOS` (7.749 estrellas, MIT) y la frontera esta escrita en los
dos pueblos: proyecto nuevo que quiere pilas incluidas — arbol de dispositivo, controladores, BLE,
USB, sistema de ficheros, arranque firmado con MCUboot — aqui; base de codigo ya existente o nucleo
lo mas pequeno posible, alli.

Y lo que no hace bien: la curva. El arbol de dispositivo y `Kconfig` son dos lenguajes de
configuracion mas que aprender antes de encender un LED, y un `west update` se trae del orden de
varios gigas de modulos. En un Mac de 8 GB compila, pero la primera puesta a punto es de tarde
entera, no de rato.

Ventaja real sobre el resto del nicho: `qemu_x86` y `native_sim` permiten ejecutar de verdad sin
placa, asi que el falso verde de "compila pero no se ha probado" se puede cerrar en parte antes de
tener hardware.
