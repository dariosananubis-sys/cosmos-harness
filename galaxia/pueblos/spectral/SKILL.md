---
cosmos: pueblo
nombre: spectral
padre: saas/contrato
resumen: Comprueba el contrato de la API contra reglas propias, no solo que el fichero este bien formado.
---

https://github.com/stoplightio/spectral · Apache-2.0 · 3.195★ · último push 2026-09-01 (comprobado por
API de GitHub el 2026-09-01)

```bash
npm install -g @stoplight/spectral-cli
```

```yaml
# .spectral.yaml — el conjunto oficial, mas las reglas de la casa
extends: ["spectral:oas"]
rules:
  operacion-con-resumen:
    description: Toda operacion necesita un summary legible
    given: $.paths[*][get,post,put,patch,delete]
    severity: error
    then: { field: summary, function: truthy }

  respuesta-de-error-declarada:
    description: Un POST que puede fallar declara el 4xx, no solo el 200
    given: $.paths[*].post.responses
    severity: error
    then: { field: "400", function: truthy }

  sin-rutas-en-plural-mixto:
    given: $.paths
    severity: warn
    then: { function: casing, functionOptions: { type: kebab } }
```

```bash
spectral lint openapi.yaml                       # sale distinto de cero si hay errores
spectral lint openapi.yaml --format junit -o resultados.xml     # para la tuberia
```

La diferencia con un validador de esquema es la que importa: aquel dice si el fichero **es** un
OpenAPI válido; esto dice si es un OpenAPI **que sirve**. Una especificación perfectamente válida
puede no declarar ningún error, no describir la paginación y llamar `getUserData` a una cosa y
`user_info` a la siguiente — y todo eso se descubre cuando el cliente ya integró.

Gana a llevar la revisión de API en una lista de comprobación de la revisión de código, que es lo que
se hace de verdad: aquello depende de que alguien se acuerde, y esto es un comando con código de
salida. Y gana a las reglas incrustadas en un servicio alojado porque el conjunto vive en el repo,
versionado, y se discute en una PR como cualquier otra decisión.

Frontera con `openapi-generator`, que ya vive en el nicho de documentos: aquel **genera cliente y
servidor** a partir del contrato; esto decide si el contrato merece que se genere nada a partir de él.
El orden correcto es este primero.

Y lo que no hace bien:

- **No prueba la API, solo el documento.** Una especificación impecable puede describir un servicio que
  devuelve otra cosa: eso lo caza un contrato ejecutado contra el servicio real, no un analizador.
- **El conjunto de reglas por defecto es tibio a propósito.** `spectral:oas` avisa de lo evidente; el
  valor está en las reglas propias, y escribirlas con `given` en JSONPath tiene su curva.
- **Con severidad `warn` no rompe la tubería** y acaba siendo ruido que nadie mira. Una regla o es
  `error` y bloquea, o sobra.
- El fabricante fue absorbido y el ritmo del proyecto depende de eso: sigue con empujones diarios a
  fecha de esta comprobación, pero conviene mirarlo cada trimestre. La alternativa viva si algún día se
  para es `daveshanley/vacuum` (MIT · 1.122★ · push 2026-08-26, comprobado el 2026-09-01), que lee
  estos mismos conjuntos de reglas.
