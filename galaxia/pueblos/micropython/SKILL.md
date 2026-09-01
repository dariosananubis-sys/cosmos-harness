---
cosmos: pueblo
nombre: micropython
padre: embebidos
resumen: Consola interactiva dentro del microcontrolador: se prueba un sensor sin recompilar ni volver a grabar.
---

https://github.com/micropython/micropython - MIT segun su `LICENSE` (la API de GitHub la devuelve
como `NOASSERTION` por variacion de cabeceras entre ficheros; revisar antes de redistribuir) -
22.034 estrellas - ultimo push 2026-08-31 (comprobado por API de GitHub el 2026-09-01).

```bash
brew install python3
pipx install esptool
pipx install mpremote
# firmware oficial de la placa: https://micropython.org/download/
esptool.py --port /dev/cu.usbserial-0001 erase_flash
esptool.py --port /dev/cu.usbserial-0001 write_flash -z 0x1000 ESP32_GENERIC-20260101.bin
```

```bash
mpremote connect /dev/cu.usbserial-0001 repl
>>> from machine import Pin
>>> Pin(2, Pin.OUT).value(1)      # responde en el acto, sin recompilar
```

```bash
mpremote connect /dev/cu.usbserial-0001 cp main.py :main.py   # copiar y arrancar solo
```

Gana a `adafruit/circuitpython` (4,5k estrellas, MIT) fuera del catalogo de placas de Adafruit: aquel
es una bifurcacion orientada a ensenanza con mejor soporte "enchufar y listo" de los sensores de esa
marca, pero MicroPython corre en mas chips (ESP32, RP2040, STM32, nRF) y trae hilos, `asyncio` y
soporte de red mas completo. Frente a `esp-idf` la diferencia no es de calidad sino de bucle de
trabajo: alli probar una linea son minutos de compilar y grabar; aqui se escribe en la consola.

Y lo que no hace bien: el interprete se come del orden de 100 KB de RAM antes de ejecutar nada, no
hay control fino del consumo y el arranque es mas lento. Para el prototipo va; cuando importan la
memoria, la bateria o el tiempo de arranque, se baja a compilado. Correr los dos en fases distintas
del mismo proyecto es lo normal, no una contradiccion.

Necesita hardware fisico. Hay compilaciones para Unix que corren en el Mac, pero sin `machine`,
que es la mitad del sentido de esto.
