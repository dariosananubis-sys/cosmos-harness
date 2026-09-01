# Embebidos — hardware y firmware

Barrido GitHub para COSMOS. Nicho: microcontroladores (ESP32, Arduino, Raspberry Pi Pico, STM32),
firmware y sistemas de tiempo real, sensores y actuadores, protocolos de dispositivo (I2C, SPI,
UART, MQTT, BLE, LoRa), consumo y energía, actualización remota, y depuración por hardware.

Método: cupo de WebSearch agotado (dado). API de GitHub autenticada — `/repos/{owner}/{repo}` como
vía principal (rate limit "core", 5000/h, sin fricción) tras topar repetidamente con el límite de
30/min de `/search/repositories`. Fecha: 2026-09-01. Estrellas, licencia y fecha del último push tal
cual las devolvió la API en ese momento — nada de esto se ha instalado ni conectado a hardware real
en esta sesión.

**Nota de filtro propia de este nicho**: dos barreras separadas, no una. El **coste** (tarjeta,
licencia, suscripción) es una; **necesitar hardware físico** para que la herramienta sirva de algo
es otra, y se marca aparte en cada entrada que aplique — comprar una sonda de depuración de 5€ no es
lo mismo que el filtro de "coste cero" del resto de COSMOS, pero es una barrera real que hay que
decir.

---

## De primera

Máximo 10. Framework de fabricante + entorno multiplataforma + RTOS (los dos que empatan de verdad,
con motivo) + lenguaje de prototipado + el patrón dominante de integración con Home Assistant +
broker MQTT + depuración por hardware + protocolo de radio de largo alcance.

1. **[esp-idf](https://github.com/espressif/esp-idf)** (Espressif) — 18.9k★, Apache-2.0, push
   2026-08-31. **Por qué gana**: framework oficial del fabricante para el microcontrolador más usado
   por hobbyistas y small-business (ESP32/ESP32-S/ESP32-C), con WiFi+BLE integrados de fábrica —
   nadie escribe firmware ESP32 serio sin pasar por aquí, directamente o a través de PlatformIO.
   **Necesita hardware**: una placa ESP32 (clones desde ~3€) para que sirva de algo más allá de
   compilar.

2. **[PlatformIO Core](https://github.com/platformio/platformio-core)** — 9.4k★, Apache-2.0, push
   2026-08-28. **Por qué gana**: un único CLI que unifica el build de ESP-IDF, Arduino, Zephyr,
   STM32Cube y más de 40 plataformas más, con gestión de librerías y dependencias por proyecto (como
   `npm`/`cargo` pero para firmware). Evita instalar una toolchain distinta por cada fabricante —
   crítico en un Mac de 8 GB donde cada IDE nativo pesa aparte.

3. **[Zephyr RTOS](https://github.com/zephyrproject-rtos/zephyr)** — 16.4k★, Apache-2.0, push
   2026-09-01. **Empata a propósito con FreeRTOS (siguiente entrada)**: Zephyr gana cuando el
   proyecto es nuevo y quiere soporte de fábrica para cientos de placas/drivers/protocolos (BLE,
   USB, filesystems, arranque seguro con MCUboot integrado) bajo un solo build system (CMake +
   devicetree). Proyecto CNCF, gobernanza abierta real.

4. **[FreeRTOS](https://github.com/FreeRTOS/FreeRTOS)** — 7.7k★, MIT, push 2026-08-26. **Gana sobre
   Zephyr** cuando lo que hace falta es el kernel más pequeño y probado del sector (scheduler +
   colas + semáforos, sin más), o cuando el proyecto ya tiene una base de código FreeRTOS existente
   — es el RTOS más desplegado del mundo por volumen de unidades, mantenido oficialmente por AWS.

5. **[MicroPython](https://github.com/micropython/micropython)** — 22k★, licencia MIT (GitHub la
   muestra como NOASSERTION por variación de cabeceras entre ficheros; verificar `LICENSE` antes de
   redistribuir). **Por qué gana**: REPL interactivo sobre serie en el propio microcontrolador —
   prototipar un sensor nuevo sin recompilar y reflashear cada vez. Corre en ESP32, RP2040 (Pico),
   STM32 y más.

6. **[ESPHome](https://github.com/esphome/esphome)** — 11.6k★, licencia NOASSERTION (GPL-3.0 según
   su repo; verificar). **Por qué gana** el hueco "home assistant integration": convierte un YAML
   declarativo en firmware completo para ESP32/ESP8266/RP2040/BK72xx con auto-descubrimiento nativo
   en Home Assistant — evita escribir a mano el cliente MQTT + la lógica de reconexión + el OTA que
   ESPHome ya trae resuelto.

7. **[Home Assistant Core](https://github.com/home-assistant/core)** — 90.2k★, Apache-2.0, push
   2026-09-01. **No es un duplicado de ESPHome**: ESPHome es el lado del *dispositivo*, Home
   Assistant es el lado del *hub* que los orquesta a todos (incluyendo dispositivos que no son
   ESPHome — Zigbee, Z-Wave, cámaras...). El patrón dominante de integración doméstica es "ESPHome +
   HA Core" como pareja, no uno sin el otro.

8. **[Eclipse Mosquitto](https://github.com/eclipse-mosquitto/mosquitto)** — 11.2k★, licencia dual
   EPL-2.0/EDL-1.0 (GitHub la muestra NOASSERTION por ser dual). **Por qué gana** sobre EMQX
   (16.7k★, segunda fila) para el caso típico de agencia: broker MQTT self-hosted mínimo, sin
   dependencias externas, corre cómodo en un Raspberry Pi o un contenedor de 20 MB — EMQX solo
   compensa con miles de dispositivos concurrentes y clustering real.

9. **[probe-rs](https://github.com/probe-rs/probe-rs)** — 2.9k★, Apache-2.0, push 2026-09-01. **Por
   qué gana** sobre OpenOCD (segunda fila) para el flujo de depuración por hardware: se integra
   directo en `cargo run`/`cargo embed` sin el baile OpenOCD+GDB por separado, con mensajes de error
   legibles. **Necesita hardware**: una sonda SWD/JTAG (ST-Link, J-Link, o un Pico como CMSIS-DAP —
   clones desde ~5€, algunas placas de dev ya traen la sonda integrada).

10. **[RadioLib](https://github.com/jgromes/RadioLib)** — 2.6k★, MIT, push 2026-08-22. **Por qué
    gana** sobre arduino-lmic (segunda fila, solo LoRaWAN-MAC): una sola librería cubre LoRa, LoRaWAN
    y varios chips de radio más (RFM69, SX126x, nRF24, CC1101) — cuando el proyecto empieza sin
    saber si acabará en LoRa puro o LoRaWAN, RadioLib no obliga a decidir de antemano.

---

## Segunda fila

- **[embedded-hal](https://github.com/rust-embedded/embedded-hal)** — 2.6k★, Apache-2.0/MIT dual.
  El conjunto de traits estándar de Rust para I2C/SPI/UART/GPIO — no es una herramienta en sí, es el
  contrato que hace que un driver de sensor escrito una vez funcione en cualquier chip compatible.
  Junto a **[esp-hal](https://github.com/esp-rs/esp-hal)** (2.1k★, Apache-2.0, la implementación
  concreta para ESP32) y probe-rs (de primera) forman el stack "embebido en Rust" que pedía el brief.
- **[pico-sdk](https://github.com/raspberrypi/pico-sdk)** — 4.9k★, BSD-3-Clause. El SDK oficial en
  C/C++ para el RP2040/RP2350 (Raspberry Pi Pico) — el framework de fabricante que faltaba en la
  lista de primera por no repetir tres frameworks de fabricante en el top 10.
  **[pico-sdk-tools](https://github.com/raspberrypi/pico-sdk-tools)** (94★) trae el toolchain
  empaquetado aparte.
- **[MCUboot](https://github.com/mcu-tools/mcuboot)** — 2.1k★, Apache-2.0, push 2026-08-31.
  Bootloader seguro para microcontroladores de 32 bits, el estándar de facto para OTA con firma
  criptográfica — usado por Zephyr de fábrica. **Ojo con la URL**: existe un mirror en
  `zephyrproject-rtos/mcuboot` con solo 43★, el repo real y activo es `mcu-tools/mcuboot`.
- **[Mender](https://github.com/mendersoftware/mender)** — 1.2k★, cliente Apache-2.0. **Coste**: el
  cliente y el servidor open-source son gratis; la gestión de flotas (Mender.io hosted / Enterprise)
  tiene tiers de pago — válido para un dispositivo o una prueba, hay que verificar el límite antes de
  prometerlo para una flota de cliente.
- **[NimBLE-Arduino](https://github.com/h2zero/NimBLE-Arduino)** — 1.1k★, Apache-2.0. Pila BLE
  ligera (bajo consumo de RAM/flash frente al BLE stack por defecto de Arduino-ESP32) empaquetada
  para el IDE de Arduino.
- **[arduino-lmic](https://github.com/mcci-catena/arduino-lmic)** — 683★, MIT. LoRaWAN-MAC puro
  para Arduino; más estrecho que RadioLib pero con más rodaje específico en despliegues LoRaWAN
  clásicos.
- **[CircuitPython](https://github.com/adafruit/circuitpython)** — 4.5k★, licencia MIT
  (NOASSERTION en GitHub). Fork de MicroPython de Adafruit orientado a enseñanza y a su propio
  catálogo de placas — mejor soporte de sensores "plug and play" de Adafruit que MicroPython vanilla.
- **[arduino-esp32](https://github.com/espressif/arduino-esp32)** — 17.3k★, LGPL-2.1. El "core" de
  Arduino para ESP32 mantenido por el propio Espressif — para quien prefiere la API de Arduino sobre
  ESP-IDF puro.
- **[Arduino IDE 2.x](https://github.com/arduino/arduino-ide)** — 3.2k★, AGPL-3.0, push
  2026-07-27. El IDE oficial actual; el repo legado `arduino/Arduino` (14.6k★, IDE 1.x) lleva sin
  push desde 2025-10 — está superseded, no se recomienda para proyecto nuevo.
- **[EMQX](https://github.com/emqx/emqx)** — 16.7k★, licencia NOASSERTION en GitHub. Broker MQTT que
  escala a millones de conexiones con clustering nativo; **verificar el fichero LICENSE real antes
  de desplegar en producción de cliente** — EMQX ha tenido piezas bajo licencias distintas al Apache
  puro del broker base en versiones recientes.
- **[Paho MQTT](https://github.com/eclipse-paho)** (paho.mqtt.python 2.4k★, paho.mqtt.c 2.4k★) —
  clientes MQTT de referencia de la Eclipse Foundation, multi-lenguaje; la opción "aburrida y
  correcta" cuando la librería del framework no alcanza.
- **[PubSubClient](https://github.com/knolleary/pubsubclient)** — 4k★, MIT. Cliente MQTT clásico
  para Arduino, minúsculo en RAM/flash — el que usa medio internet de tutoriales ESP8266/ESP32.
- **[Zigbee2MQTT](https://github.com/Koenkk/zigbee2mqtt)** — 15.6k★, GPL-3.0. Puente Zigbee↔MQTT sin
  el bridge propietario del fabricante — el protocolo de dispositivo que falta si un cliente ya
  tiene sensores Zigbee en vez de WiFi/BLE.
- **[Node-RED](https://github.com/node-red/node-red)** — 23.6k★, Apache-2.0. **Frontera declarada**:
  encaja aquí solo para el caso concreto de orquestar/pintar dashboards de dispositivos IoT; como
  herramienta de automatización de flujo general pertenece al nicho `automatizacion` (#17), no a
  éste.
- **[OpenOCD](https://github.com/openocd-org/openocd)** — 2.3k★, licencia NOASSERTION (GPL-2.0
  histórico). El puente JTAG/SWD estándar de facto, más verboso que probe-rs pero con soporte de
  chips que probe-rs aún no cubre. **Necesita hardware**: una sonda de depuración física.
- **[stlink](https://github.com/stlink-org/stlink)** — 5.2k★, BSD-3-Clause. Toolset open-source
  específico para programar/depurar STM32 vía ST-Link. **Necesita hardware**: un ST-Link (clones
  desde ~2€, muchas placas Nucleo/Discovery ya lo traen integrado).
- **[python-can](https://github.com/hardbyte/python-can)** — 1.6k★, LGPL-3.0. Librería CAN bus para
  Python sobre SocketCAN y adaptadores USB-CAN. **Necesita hardware**: una interfaz CAN física (o
  SocketCAN en Linux) para ser algo más que una librería sin bus que hablar.
- **[can-utils](https://github.com/linux-can/can-utils)** — 2.9k★, sin licencia declarada en GitHub
  (NOLIC — verificar antes de redistribuir). Utilidades de línea de comandos para SocketCAN
  (`candump`, `cansend`) — el complemento de terminal a python-can. **Necesita hardware** igual.
- **[PulseView](https://github.com/sigrokproject/pulseview)** (782★) + **[libsigrok](https://github.com/sigrokproject/libsigrok)**
  (434★), ambos GPL-3.0, mirrors de solo lectura de sigrok.org, cadencia lenta (~10 meses sin push en
  el mirror, aunque el proyecto real sigue activo en su propio git). Software de analizador lógico
  que habla con decenas de clones baratos de Saleae. **Necesita hardware**: un analizador lógico USB
  (clones desde ~10€) — sin él, esto no hace nada.
- **[WiringPi](https://github.com/WiringPi/WiringPi)** — 3.3k★, LGPL-3.0. **Frontera declarada**:
  GPIO para la Raspberry Pi como ordenador Linux completo, no para el Pico (que es el micro que pidió
  Darío). Se menciona por si un cliente tiene una Pi normal, no un Pico, haciendo el mismo trabajo.

## Humo

- **[trezor-firmware](https://github.com/trezor/trezor-firmware)** (1.8k★) — firmware real de un
  hardware wallet; útil como referencia de diseño embebido con foco en seguridad, no como
  herramienta de propósito general.
- **[platform-espressif32](https://github.com/platformio/platform-espressif32)** (1.2k★) — la
  definición de plataforma ESP32 dentro del ecosistema PlatformIO, no un proyecto standalone.
- **[hardkernel/wiringpi](https://github.com/hardkernel/wiringpi)** (64★) — mirror del WiringPi
  original de Gordon Henderson (archivado por su autor); el fork activo es `WiringPi/WiringPi`.
- **[platformio-vscode-ide](https://github.com/platformio/platformio-vscode-ide)** (1.4k★, sin push
  desde 2025-01) — la extensión de VSCode de PlatformIO; cadencia de push más lenta que el core, sin
  ser señal de abandono del proyecto en conjunto.

## Mapeo a COSMOS

```
sistema-solar  embebidos
├── continente  microcontroladores-y-entornos-de-desarrollo
│   ├── pais  frameworks-oficiales-de-fabricante
│   │          provincias: ESP32 · Raspberry-Pi-Pico · STM32
│   │          pueblos: esp-idf, pico-sdk + pico-sdk-tools, (STM32Cube — no verificado en vivo)
│   ├── pais  entornos-multiplataforma
│   │          provincias: build-unificado · IDE
│   │          pueblos: PlatformIO Core, PlatformIO IDE (VSCode), Arduino IDE 2.x, arduino-esp32
│   └── pais  codigo-embebido-en-rust           ← el código propio de este nicho
│              provincias: HAL-como-contrato · HAL-por-chip · depuracion-integrada
│              pueblos: embedded-hal, esp-hal, probe-rs
├── continente  firmware-y-sistemas-de-tiempo-real
│   ├── pais  RTOS
│   │          provincias: ecosistema-CNCF-amplio · kernel-minimo-probado
│   │          pueblos: Zephyr RTOS, FreeRTOS
│   ├── pais  interpretes-embebidos
│   │          provincias: prototipado-rapido · educativo
│   │          pueblos: MicroPython, CircuitPython
│   └── pais  arranque-seguro-y-actualizacion-remota
│              provincias: bootloader-firmado · gestion-de-flota
│              pueblos: MCUboot, Mender (cliente OSS, flota de pago)
├── continente  sensores-actuadores-y-protocolos-de-dispositivo
│   ├── pais  radio-de-corto-y-largo-alcance
│   │          provincias: LoRa/LoRaWAN · Bluetooth-Low-Energy · Zigbee
│   │          pueblos: RadioLib, arduino-lmic, NimBLE-Arduino, Zigbee2MQTT
│   ├── pais  bus-de-campo
│   │          provincias: I2C/SPI/UART-via-HAL · CAN
│   │          pueblos: embedded-hal (I2C/SPI/UART), python-can, can-utils
│   └── pais  mensajeria-IoT
│              provincias: broker · cliente · puente-de-protocolo
│              pueblos: Eclipse Mosquitto, EMQX, Paho MQTT, PubSubClient
├── continente  hogar-y-orquestacion-de-dispositivos
│   └── pais  integracion-con-home-assistant
│              provincias: firmware-declarativo-del-dispositivo · hub-central
│              pueblos: ESPHome, Home Assistant Core, (Node-RED — frontera con `automatizacion`)
└── continente  depuracion-por-hardware-y-analisis-de-senal
    ├── pais  sondas-de-depuracion
    │          provincias: SWD/JTAG-moderno · SWD/JTAG-clasico · programador-especifico-STM32
    │          pueblos: probe-rs, OpenOCD, stlink   (los tres necesitan sonda física)
    └── pais  analizadores-logicos-y-de-bus
               provincias: captura-de-senal-digital
               pueblos: PulseView + libsigrok        (necesitan analizador lógico físico)
```

Frontera declarada: Home Assistant Core (90.2k★) es software puro sin nada de hardware propio —
entra porque ESPHome+HA Core es el patrón real de integración doméstica, no porque el nicho
`embebidos` deba tragarse todo lo que HA integra. Node-RED entra solo por su uso como dashboard de
dispositivos IoT; como motor de automatización general pertenece al nicho `automatizacion` (#17).
WiringPi entra en Humo/segunda fila con frontera explícita: es GPIO para una Raspberry Pi completa
(Linux), no para el Raspberry Pi Pico (microcontrolador) que pidió el brief.

## Lo que falta

- **Nada de esto se ha conectado a hardware real.** Todo el barrido es metadatos de GitHub
  (estrellas, licencia, fecha de push) — el filtro "perfecto" de COSMOS exige "se ha usado una vez
  en un caso real" antes de quedarse fijo en el catálogo; eso está pendiente para cada pueblo aquí.
- **STM32Cube** (el framework oficial de ST) no se verificó en vivo — ST no lo distribuye como un
  repo GitHub único y central de la misma forma que Espressif con esp-idf; queda mencionado de
  pasada, sin marcar como recurso confirmado.
- **Licencias mostradas como NOASSERTION por GitHub** (MicroPython, ESPHome, Mosquitto, EMQX, Paho,
  Mender, OpenOCD, CircuitPython, can-utils sin licencia) — antes de comprometerse con un cliente,
  leer el fichero LICENSE real de cada repo. EMQX y Mender en particular tienen historial de piezas
  de pago (fleet management/enterprise) fuera del núcleo gratuito — declarado en su ficha, no
  verificado línea a línea del contrato de licencia.
- **Servidor de red LoRaWAN (tipo ChirpStack) no se investigó.** RadioLib/arduino-lmic cubren el
  nodo/dispositivo; si un cliente necesita gateway + servidor de red LoRaWAN completo, falta ese
  ángulo entero.
- **CAN bus con cobertura mínima** (python-can + can-utils) — no se exploró un stack con GUI tipo
  SavvyCAN para diagnóstico visual, ni herramientas específicas de automoción (J1939, OBD-II).
- **El endpoint `/search` de GitHub golpeó el rate-limit de 30/min repetidamente**, igual que en
  `sistemas.md` el mismo día — se resolvió con `/repos/{owner}/{repo}` directo, que no tuvo el
  problema pero exige saber de antemano qué repo buscar (más conocimiento previo, menos
  descubrimiento por búsqueda libre).
- Sin datos de clientes, IPs ni credenciales en este fichero.
