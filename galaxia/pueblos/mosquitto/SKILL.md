---
cosmos: pueblo
nombre: mosquitto
padre: embebidos
resumen: Servidor de mensajeria ligero para dispositivos: cabe en una placa pequena y no pide agrupacion.
---

https://github.com/eclipse-mosquitto/mosquitto · licencia dual EPL-2.0 / EDL-1.0 (la API de GitHub la devuelve como `NOASSERTION` precisamente por ser dual) · 11.172★ · último push 2026-08-27 (comprobado por API de GitHub el 2026-09-01).

```bash
brew install mosquitto
```

```bash
# 1. arrancar el broker con una config minima y autenticada
cat > mosquitto.conf <<'EOF'
listener 1883 127.0.0.1
allow_anonymous false
password_file passwd
EOF
mosquitto_passwd -c passwd usuario-de-ejemplo     # pide la clave por teclado
mosquitto -c mosquitto.conf -v &

# 2. suscribirse y publicar
mosquitto_sub -h 127.0.0.1 -u usuario-de-ejemplo -P '<clave>' -t 'casa/#' &
mosquitto_pub -h 127.0.0.1 -u usuario-de-ejemplo -P '<clave>' -t 'casa/salon/temp' -m '21.4'
```

Gana a `emqx/emqx` (16,7k estrellas) para el caso normal de agencia: sin dependencias externas,
arranca en un contenedor de decenas de megas o en una Raspberry Pi. EMQX solo compensa con miles de
dispositivos concurrentes y agrupacion real, y ademas hay que leerse su `LICENSE` antes de
desplegarlo a un cliente porque ha llevado piezas fuera del Apache puro.

Y lo que no hace bien — el falso verde de este pueblo: el paquete trae `allow_anonymous` en el
ejemplo de muchos tutoriales, y un broker anonimo escuchando en `0.0.0.0` es un aparato abierto a
Internet. Si `listener` no lleva IP, escucha en todas las interfaces. Sin TLS, usuario y clave
viajan en claro. Para produccion: `listener 8883`, `cafile`/`certfile`/`keyfile`, y nunca
`allow_anonymous true`.

`esphome` resuelve el lado del aparato; alguien tiene que atender el otro extremo, y ese es este.
