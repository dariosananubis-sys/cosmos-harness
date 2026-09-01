---
cosmos: pueblo
nombre: blacklight
padre: cumplimiento
resumen: Carga la pagina de verdad y mide que rastreadores saltan antes de que nadie acepte nada.
---

https://github.com/the-markup/blacklight-collector · GPL-3.0 · 240★ · último push 2026-08-27
(comprobado por API de GitHub el 2026-09-01). Es el motor del inspector de privacidad publicado por
The Markup.

```bash
npm install @themarkup/blacklight-collector       # arrastra un navegador sin interfaz
```

```js
// medir.mjs
import { collect } from '@themarkup/blacklight-collector';

const r = await collect('https://<DOMINIO_A_MEDIR>/', {
  outDir: './salida', headless: true, numPages: 3, defaultTimeout: 30000,
});
console.log(JSON.stringify(r.reports, null, 2));
// third_party_trackers, cookies, canvas_fingerprinters, session_recorders,
// key_logging, fb_pixel_events, ga_third_party_cookies
```

```bash
node medir.mjs > informe.json
```

Cubre exactamente el hueco que `cookies-declaradas` deja escrito: aquel mide el HTML servido y escribe
la declaración legal, pero **no ve lo que se carga en el navegador antes del consentimiento**. Eso es
medición en vivo, y es donde está la sanción: no en que la política esté mal redactada, sino en que la
analítica y el píxel de la red social se disparen mientras el aviso todavía está en pantalla.

Gana a mirar la pestaña de red a mano, que es lo que se hace de verdad, en dos cosas: reconoce a los
terceros contra listas de bloqueo publicadas en vez de a ojo, y detecta **comportamientos**, no solo
peticiones — huella digital por lienzo, grabación de sesión y captura de pulsaciones aparecen en el
informe con su fichero de origen. Y frente a `lighthouse` y `unlighthouse`, que ya viven en el nicho de
web: aquellos miden calidad y rendimiento del sitio; esto mide privacidad, y es otro informe.

**Norma que cubre**: artículo **22.2 de la LSSI-CE (Ley 34/2002)** —el consentimiento previo para
almacenar o recuperar información en el equipo del usuario— y la **Guía de uso de cookies de la AEPD**
en su edición adaptada a las directrices del CEPD, vigente desde enero de 2023; junto a los artículos 6
y 7 del **RGPD** para el consentimiento. Territorio: **España**, con el mismo fondo en toda la Unión.
Fecha de esta comprobación: 2026-09-01; la guía de la AEPD se revisa, y antes de usarla como argumento
ante el organismo hay que mirar la edición vigente.

**Lo que NO comprueba**: no valida el banner —ni que rechazar sea tan fácil como aceptar, que es el
motivo de rechazo más común—, no lee el registro de consentimientos, no escribe ningún texto legal y no
dice si el tratamiento tiene base jurídica. Da hechos medidos, no un dictamen.

Ojo, y es lo que más pesa aquí: **240 estrellas y un solo laboratorio detrás**. Es el único del barrido
que mide esto y por eso entra, pero es el pueblo más frágil de su nicho — revisar cada trimestre. Y dos
límites técnicos que hacen falso el verde: mide **una carga sin interacción**, así que un rastreador que
solo salta al pulsar un botón no aparece; y las listas de terceros envejecen, de modo que un dominio
nuevo puede pasar sin identificar. Ausencia de hallazgos no es prueba de cumplimiento.
