---
cosmos: pueblo
nombre: toxiproxy
padre: trading/bots/codigo-de-bot
resumen: Corta la red a proposito entre el bot y el mercado: latencia, timeout y conexion caida.
---

https://github.com/Shopify/toxiproxy · MIT · 12.294★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install toxiproxy
brew services start toxiproxy      # el servidor; el bot apunta al proxy, no al mercado
```

```bash
# poner el proxy en medio: el bot se conecta a localhost:6000 en vez de al mercado
toxiproxy-cli create mercado -l 127.0.0.1:6000 -u api.mercado-ejemplo:443

# el fallo se enciende desde el propio test
toxiproxy-cli toxic add mercado -t latency -a latency=1000    # +1000 ms
toxiproxy-cli toxic add mercado -t timeout -a timeout=0       # acepta y no responde
toxiproxy-cli toxic remove mercado -n latency_downstream      # y se apaga
```

La pregunta que ningún manual contesta —qué pasa si la conexión cae justo después de mandar la orden
y antes de recibir la confirmación— solo se contesta provocándola. Se pone en medio como
intermediario y el fallo se enciende y apaga desde el test: mil milisegundos de retardo, cortar a
mitad de respuesta, aceptar y no contestar. Es la única forma de comprobar de verdad la idempotencia
del envío y el arranque con posición abierta, en vez de confiar en que el código de reconexión hace
lo que dice.

Se ejecuta como proceso aparte y se maneja por su interfaz, así que sirve igual para un bot en
Python que en cualquier otro lenguaje. Ojo, la frontera declarada: roza el mar `pruebas`, que ya
nombra la idea de inyectar el fallo real; entra como pueblo porque aquí el modo de fallo es de
**dinero**, no de consistencia. Y prueba el canal de red, no la lógica de mercado: un `timeout` no
simula un rechazo del mercado ni una ejecución parcial — eso se prueba con el mercado simulado.
