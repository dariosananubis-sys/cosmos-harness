---
cosmos: pueblo
nombre: wireshark
padre: ciberseguridad/analisis/forense
resumen: Analizador de trafico de red de referencia; tshark es su linea de comandos para capturas.
---

https://github.com/wireshark/wireshark · GPL-2.0 · 9.815★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
brew install wireshark
```

```bash
# captura por linea de comandos con tshark (mismo motor de disección que wireshark)
tshark -i en0 -w captura.pcap -a duration:60

# leer un pcap ya capturado y filtrar solo trafico HTTP
tshark -r captura.pcap -Y http
```

Es la herramienta de facto para inspeccionar tráfico de red capturado: más de 3.000 disectores de
protocolo, capaz de reconstruir sesiones TCP y extraer objetos transferidos (ficheros, credenciales
en claro) de un `.pcap`. `tshark` es su cara de terminal — mismo motor, sin interfaz gráfica —, la
forma de usarlo en un servidor remoto o dentro de un script de automatización forense.

Gana a `tcpdump` en profundidad de análisis: aquel captura igual de bien (usan el mismo `libpcap`
por debajo) pero no diseca el protocolo ni reconstruye nada — es la herramienta correcta para dejar
grabando un servidor de producción por su bajo coste, y luego se abre el `.pcap` resultante con
`wireshark`/`tshark` para el análisis de verdad. Frente a `zeek`, que no captura para mirar a mano
sino que analiza el tráfico en vivo y saca registros estructurados (conexiones, DNS, HTTP) pensados
para alimentar un SIEM, `wireshark` gana en la inspección manual profunda de un incidente concreto;
`zeek` gana en vigilancia continua de una red entera.

Ojo: capturar tráfico de una red que no es tuya, o interceptar comunicaciones ajenas, requiere
autorización explícita — en la mayoría de jurisdicciones es delito sin ella. El tráfico cifrado
(TLS) no se descifra solo con capturarlo: hace falta la clave de sesión (`SSLKEYLOGFILE`) o el
propio wireshark solo ve metadatos. Un pcap grande (varios GB) consume mucha RAM al abrirlo con
la interfaz gráfica; para capturas largas, filtra en el propio `tshark` o trabaja en flujo.
