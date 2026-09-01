---
cosmos: pueblo
nombre: serpbear
padre: visibilidad
resumen: Sigue la posicion de cada palabra clave dia a dia en tu propio servidor y avisa de las caidas.
---

https://github.com/towfiqi/serpbear · MIT · 2.064★ · push 2026-05-14 (comprobado 2026-09-01)

```bash
docker run -d --name serpbear -p 3000:3000 \
  -e USER=<usuario> -e PASSWORD=<clave> \
  -e SECRET=<CADENA_ALEATORIA> -e APIKEY=<CADENA_ALEATORIA> \
  -e NEXT_PUBLIC_APP_URL=http://localhost:3000 \
  -v "$PWD/serpbear-data:/app/data" towfiqi/serpbear:latest

# anadir dominio y palabras clave por API
curl -s -X POST http://localhost:3000/api/domains \
  -H "Authorization: <APIKEY>" -H "Content-Type: application/json" \
  -d '{"domain":"ejemplo.test"}'
```

Único hueco del nicho que ninguna otra pieza cubre: **la serie temporal de posiciones**, día a día,
por palabra clave y por dispositivo, con aviso cuando una cae. Autoalojado y sin cuenta de terceros,
frente a Ahrefs o Semrush, que es donde se va el presupuesto de una agencia pequeña.

Descartado el servidor de herramientas para la consola de búsqueda del buscador: es de terceros y
custodiaría el acceso delegado a la propiedad del cliente, que es exactamente lo que el agua de
custodia no permite dar a la ligera. Queda como hueco declarado.

Ojo, y es lo que hay que saber antes de prometérselo a nadie: **el rastreo de posiciones lo hace un
proveedor externo** (scrapingrobot, serply, spaceserp o similar), que tiene su propia capa gratuita
limitada y su plan de pago. Sin proveedor configurado, el panel se instala y **no mide nada**. Ese
alta no se contrata sin orden explícita. Y la posición que devuelve un raspador es una foto sin
personalización ni ubicación: sirve para ver la tendencia, no para discutir un número exacto con un
cliente.

Ojo de vida: último empujón el 2026-05-14, casi cuatro meses antes de esta comprobación, con 2.064
estrellas. Estable, pero es el pueblo con el ritmo más lento del nicho — vigilar si los proveedores
de rastreo cambian su API.
