---
cosmos: pueblo
nombre: cookies-declaradas
padre: cumplimiento
resumen: Mide que terceros carga la web de verdad y declara eso y solo eso, en lugar de la lista heredada de la plantilla.
---

`cosecha/cookies_catalogo.py` — catalogo de mas de sesenta patrones de cookies de gestor, tienda,
maquetador, analitica y redes, con su clasificacion legal escrita en castellano.

`cosecha/legales-bloque-cookies.py` y `cosecha/legales-bloque-rest.py` — miden los servicios de
terceros que aparecen de verdad en el HTML y escriben el bloque declarativo de forma repetible: el
primero con acceso al servidor, el segundo solo por API para sitios donde no lo hay.

`cosecha/legales-cookies-complianz.py` — rellena la ficha de cada cookie: finalidad, caducidad y
titularidad.

`cosecha/legales-purga-servicios-complianz.py` — quita los servicios que no se cargan. Sobre-declarar
es el fallo mas comun y no es inofensivo: describe un tratamiento de datos que no existe y delata que
nadie miro la web.

La diferencia con cualquier asistente del gestor de consentimiento es esa: aqui la lista sale de
medir el HTML, no de marcar casillas.
