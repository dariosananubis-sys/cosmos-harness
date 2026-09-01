---
cosmos: pueblo
nombre: esphome
padre: embebidos
resumen: Un YAML se convierte en firmware que se anuncia solo en el concentrador domestico.
---

https://github.com/esphome/esphome - GPL-3.0 segun el `LICENSE` del repo (la API de GitHub la
devuelve como `NOASSERTION`, sin verificar por que) - 11.623 estrellas - ultimo push 2026-09-01
(comprobado por API de GitHub el 2026-09-01).

```bash
pipx install esphome
```

```yaml
# sensor.yaml
esphome:
  name: sensor-salon
esp32:
  board: esp32dev
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
api:
ota:
  - platform: esphome
sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      name: "Temperatura salon"
```

```bash
esphome run sensor.yaml        # compila, graba por USB y abre los logs
esphome upload sensor.yaml     # a partir de la segunda vez, por radio
```

Gana a escribir el firmware a mano con `esp-idf` en su hueco concreto: el cliente MQTT, la
reconexion de WiFi, el anuncio del dispositivo y la actualizacion por radio ya vienen resueltos, y
son justo las cuatro cosas que se escriben mal. `home-assistant/core` (90,2k estrellas) no es el
rival sino la otra mitad: aquel es el concentrador, este es el aparato.

Y lo que no hace bien: en cuanto el aparato necesita logica que no esta en un componente ya escrito,
el YAML se queda corto y hay que bajar a `esp-idf` o a un `lambda` en C++ incrustado — que es peor
sitio para depurar que un proyecto en C de verdad.

Necesita hardware fisico. `esphome config sensor.yaml` valida el YAML sin placa, pero eso solo dice
que el fichero esta bien escrito.

Ojo con el secreto: `!secret` lee de un `secrets.yaml` que NO se commitea. Las credenciales de la red
del cliente nunca van en el fichero del dispositivo.
