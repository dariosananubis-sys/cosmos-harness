---
cosmos: pueblo
nombre: lago
padre: saas
resumen: Medicion de consumo y facturacion por uso, autoalojada, para cobrar por lo que se gasta de verdad.
---

https://github.com/getlago/lago · AGPL-3.0 · 10.451★ · push 2026-08-31 (comprobado 2026-09-01)

```bash
git clone --depth 1 https://github.com/getlago/lago.git && cd lago
docker compose up -d                 # panel en http://localhost:80

# registrar consumo: un evento por uso real
curl -s -X POST http://localhost:3000/api/v1/events \
  -H "Authorization: Bearer <CLAVE_API>" -H "Content-Type: application/json" \
  -d '{"event":{"transaction_id":"<UUID_UNICO>","external_subscription_id":"<SUB>",
       "code":"llamadas_api","properties":{"unidades":120}}}'
```

Software real y autoalojable, no una guía. Resuelve la parte que la pasarela **no** hace: contar
eventos de uso, agregarlos por periodo con su ventana y su prorrateo, y convertirlos en línea de
factura. `stripe-agent-toolkit` cobra lo que le digas; esto decide **cuánto** hay que cobrar. Gana a
`Killbill`, el otro autoalojado maduro del hueco, por API moderna y coste de arranque: aquel es un
servidor Java con plugins y una curva mucho más larga.

Entra porque el modelo de producto vendible **sin medición de consumo se queda en tarifa plana**, y
la tarifa plana es la que se come el margen cuando un cliente consume diez veces más que el resto.

Ojo: `transaction_id` es la clave de idempotencia. **Sin un identificador único y estable por evento,
un reintento de red duplica el consumo y el cliente recibe una factura inflada** — es el fallo caro
de este pueblo. Y la licencia es AGPL: alojarlo como servicio para terceros obliga a publicar las
modificaciones. Emite líneas de factura, no la factura legal: eso lo hace `gobl`.
