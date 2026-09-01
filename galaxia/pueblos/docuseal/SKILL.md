---
cosmos: pueblo
nombre: docuseal
padre: automatizacion/firma
resumen: Firma multiple sobre plantillas de PDF con API propia, en casa y sin cuota por documento.
---

https://github.com/docusealco/docuseal · AGPL-3.0 · 18.411★ · push 2026-08-31 (comprobado 2026-09-01)

```bash
docker run --name docuseal -p 3000:3000 -v "$PWD/docuseal:/data" docuseal/docuseal

# enviar una plantilla a firmar (el token sale de Ajustes > API)
curl -s -X POST http://localhost:3000/api/submissions \
  -H "X-Auth-Token: <TOKEN_API>" -H "Content-Type: application/json" \
  -d '{"template_id":1,"send_email":true,
       "submitters":[{"role":"Firmante","email":"persona@ejemplo.test"}]}'
```

Gana a `OpenSign`, el otro autoalojado del hueco, por API documentada, clientes oficiales en varios
lenguajes y plantillas construidas desde un PDF u ofimática existente en vez de rehechas a mano.
Frente a DocuSign o Signaturit, lo que se ahorra es la cuota por documento, que es donde se va el
dinero cuando la firma es rutina y no excepción.

Ojo: aquí sale firma **simple o avanzada** según cómo se configure (evidencia de IP, sello de
tiempo, trazabilidad). La **cualificada** del eIDAS (Reglamento UE 910/2014, art. 3.12) exige un
prestador cualificado y un dispositivo de creación — eso es un tercero de pago y se para aquí a
preguntar. Y la licencia es AGPL: alojarlo para un cliente como servicio obliga a publicar las
modificaciones.
