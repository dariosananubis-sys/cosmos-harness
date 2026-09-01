---
cosmos: pueblo
nombre: twenty
padre: automatizacion/clientes
resumen: Relacion con clientes autoalojada con API REST y de grafo para engancharla a lo demas.
---

https://github.com/twentyhq/twenty · AGPL-3.0 con ficheros comerciales marcados · 55.982★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
git clone --depth 1 https://github.com/twentyhq/twenty && cd twenty
docker compose up -d                    # panel en http://localhost:3000

# leer contactos por la API REST (el token sale de Ajustes > API y webhooks)
curl -s "http://localhost:3000/rest/people?limit=5" \
  -H "Authorization: Bearer <TOKEN_API>"
```

Gana a `EspoCRM` y a `SuiteCRM`, los otros dos autoalojables del hueco, en dos cosas: expone la
misma base por REST y por GraphQL (así que se engancha a un flujo de `n8n` sin plugin), y marca en
el propio árbol de ficheros cuáles son de la edición de pago — se sabe dónde está el límite sin leer
letra pequeña ni descubrirlo al desplegar.

Ojo: no factura. Cierra la venta y ahí acaba; la factura es `gobl` y el cobro recurrente es `lago`.
Y la licencia es AGPL con excepciones comerciales: si se ofrece la instancia a un tercero como
servicio, hay que revisar qué ficheros del árbol quedan fuera de la AGPL antes de tocar código.
