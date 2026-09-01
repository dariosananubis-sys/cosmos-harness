---
cosmos: pueblo
nombre: node-red
padre: automatizacion
resumen: Flujos por nodos para hardware y protocolo: puerto serie, mensajeria de dispositivo y miles de nodos de la comunidad.
---

https://github.com/node-red/node-red · Apache-2.0 · 23.604★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
docker run -d --name nodered -p 1880:1880 \
  -v node_red_data:/data nodered/node-red:latest-22
# panel en http://localhost:1880

# inyectar un flujo por la API de administracion (mqtt -> depuracion)
curl -s -X POST http://localhost:1880/flow -H "Content-Type: application/json" -d '{
  "label": "humedad",
  "nodes": [
    {"id":"b1","type":"mqtt-broker","broker":"localhost","port":"1883"},
    {"id":"n1","type":"mqtt in","topic":"planta/humedad","broker":"b1","x":140,"y":80,"wires":[["n2"]]},
    {"id":"n2","type":"debug","name":"ver","x":340,"y":80,"wires":[]}
  ]}'
```

Gana el hueco que `n8n` y `windmill` no cubren igual de bien: hablar con aparatos. Su catálogo de
nodos de comunidad es de protocolos y dispositivos —puerto serie, Modbus, MQTT, CAN, GPIO—, no de
servicios web con API. La frontera con los vecinos: `n8n` cuando el flujo une servicios en la nube,
`windmill` cuando el automatismo es código versionado, y este cuando al otro lado hay una placa, un
sensor o un bus. Es la pareja natural del nicho de embebidos, que lo nombra sin duplicarlo.

A las tres de la mañana: no hay reintento por nodo como en `n8n`. Lo que hay es el nodo `catch`, que
recoge el error de los nodos que se le indiquen, y `status`, que ve el estado de la conexión; el
reintento se construye con `delay` en modo limitador y una realimentación. Es más trabajo, pero
queda explícito en el flujo.

Ojo: el estado vive en el fichero `flows.json` del volumen, y **editar en el panel mientras alguien
despliega por API pisa cambios sin avisar**. Si el flujo importa, se versiona el `flows.json` y se
despliega desde el repositorio, no desde el navegador.
