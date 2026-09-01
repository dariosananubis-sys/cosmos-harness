---
cosmos: pueblo
nombre: search-console
padre: visibilidad
resumen: Da de alta y verifica el sitio en el buscador, envia el mapa y pregunta por que una URL no esta indexada.
---

`cosecha/gsc-search-console.py` y `cosecha/gsc-service-account-token.js` — herramientas propias, no
hay repositorio público. Las rutas SON la referencia. APIs oficiales:
https://developers.google.com/webmaster-tools/v1 y https://developers.google.com/site-verification/v1

```bash
export GSC_SERVICE_ACCOUNT_JSON=~/.secrets/<cuenta-servicio>.json

python3 cosecha/gsc-search-console.py add-property https://ejemplo.test/
python3 cosecha/gsc-search-console.py get-token   https://ejemplo.test/   # devuelve el <meta ...>
python3 cosecha/gsc-search-console.py verify      https://ejemplo.test/   # tras inyectar el meta
python3 cosecha/gsc-search-console.py submit-sitemap https://ejemplo.test/ https://ejemplo.test/sitemap_index.xml
python3 cosecha/gsc-search-console.py inspect-url    https://ejemplo.test/ https://ejemplo.test/contacto/

# el mismo testigo, sin arrastrar la biblioteca oficial de autenticacion:
node --input-type=module -e "
import { serviceAccountAccessToken } from './cosecha/gsc-service-account-token.js';
import { readFileSync } from 'node:fs';
const sa = JSON.parse(readFileSync(process.env.GSC_SERVICE_ACCOUNT_JSON, 'utf8'));
console.log((await serviceAccountAccessToken(sa)).slice(0, 12) + '...');"
```

Se prefiere al servidor de herramientas público que expone la misma consola con decenas de
herramientas de análisis por dos motivos. El primero es de alcance: aquí hace falta el trozo
accionable —dar de alta, verificar, enviar el mapa, preguntar por qué una URL no está indexada— y ese
trozo no necesita ni instalación ni intermediario. El segundo es de custodia, y pesa más: **ese
servidor es de terceros y custodiaría el acceso delegado a la propiedad del cliente**. Si lo que se
busca es análisis de consultas y canibalización, ese servidor es mejor herramienta que esto.

`gsc-service-account-token.js` acuña el testigo firmando el vale RS256 a mano; sirve para cualquier
API del mismo proveedor cambiando el ámbito, así que también vale para la de analítica. Los dos
comparten `cosecha/log.py`, que da el formato de registro común a esta familia de envoltorios de
API; no es una herramienta, es su dependencia.

Es la **única pieza de este nicho que le habla al buscador**; el resto mide el sitio desde fuera.

Ojo: `inspect-url` tiene **cuota diaria por propiedad** y se agota rápido en un lote grande —los
errores de cuota no dicen que sea cuota, dicen 403—. Y la cuenta de servicio tiene que estar añadida
como usuario de la propiedad en Search Console: crear la cuenta y habilitar las dos APIs no basta, y
el error tampoco lo explica. Ese es el paso que se olvida.
