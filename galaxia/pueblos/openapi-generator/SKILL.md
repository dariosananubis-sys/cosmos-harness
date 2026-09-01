---
cosmos: pueblo
nombre: openapi-generator
padre: documentos
resumen: Del mismo esquema salen documentacion, cliente y esqueleto: no pueden divergir.
---

https://github.com/OpenAPITools/openapi-generator · Apache-2.0 · 26.711★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install openapi-generator      # o: docker run --rm -v "$PWD:/local" openapitools/openapi-generator-cli

openapi-generator validate -i openapi.yaml
openapi-generator generate -i openapi.yaml -g typescript-fetch -o clientes/ts
openapi-generator generate -i openapi.yaml -g html2 -o docs/api
openapi-generator list                # los ~100 generadores disponibles
```

Es el criterio central del nicho aplicado de forma literal: **del mismo esquema salen documentación,
cliente y esqueleto de servidor**, así que no pueden divergir — no hay una segunda copia que
actualizar y quedarse vieja. Gana a `swagger-codegen`, del que es la bifurcación mantenida por la
comunidad: mismo origen, mucho más ritmo y muchos más generadores. Y gana a escribir el cliente a
mano por lo obvio, que es que el cliente a mano se queda atrás en el primer cambio de campo.

Ojo: la calidad **varía muchísimo entre generadores**. Los populares (TypeScript, Java, Go, Python)
están cuidados; los de la cola larga generan código que compila y poco más. Antes de meter uno en la
tubería, generar una vez y **leer la salida** — no se adopta un generador por estar en la lista. Y
regenerar pisa lo que haya en el directorio de destino: la personalización va en plantillas
(`-t plantillas/`) o en `.openapi-generator-ignore`, nunca editando el código generado.
