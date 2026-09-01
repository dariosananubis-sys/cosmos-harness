---
cosmos: pueblo
nombre: probe-rs
padre: embebidos
resumen: Graba y depura por sonda desde el mismo comando de compilacion, con mensajes de error legibles.
---

https://github.com/probe-rs/probe-rs - Apache-2.0 - 2.924 estrellas - ultimo push 2026-09-01
(comprobado por API de GitHub el 2026-09-01).

```bash
brew install probe-rs/probe-rs/probe-rs
# o, con Rust ya instalado:  cargo install probe-rs-tools --locked
```

```bash
probe-rs list                                  # ve la sonda conectada
probe-rs info --chip STM32F411CEUx
probe-rs run --chip STM32F411CEUx target/thumbv7em-none-eabihf/debug/mi-firmware
```

```toml
# .cargo/config.toml — para que 'cargo run' grabe y ejecute directamente
[target.thumbv7em-none-eabihf]
runner = "probe-rs run --chip STM32F411CEUx"
```

Gana a `openocd-org/openocd` (2,3k estrellas, GPL-2.0) en el flujo diario: alli hay que levantar un
servidor por un lado y conectar GDB por otro, y cuando falla el mensaje es un volcado de protocolo;
aqui es un comando y los errores dicen que pasa. Para chips raros, OpenOCD sigue cubriendo mas
objetivos, y ahi no hay discusion.

Necesita hardware fisico: una sonda SWD/JTAG. Es la barrera mas concreta de este pueblo — un ST-Link
clonico cuesta unos 5 euros y muchas placas de desarrollo (Nucleo, Discovery, Pico como CMSIS-DAP)
ya la traen integrada, pero sin ella no se ejecuta ni un comando util.

Y lo que no hace bien: la lista de chips soportados no es la de OpenOCD. Antes de prometer soporte,
`probe-rs chip list | grep <familia>` — descubrir que el chip del cliente no esta despues de montar
el proyecto es la forma cara de enterarse.
