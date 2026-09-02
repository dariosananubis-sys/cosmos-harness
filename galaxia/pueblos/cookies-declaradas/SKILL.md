---
cosmos: pueblo
nombre: cookies-declaradas
padre: cumplimiento
resumen: Mide que terceros carga la web de verdad y declara eso y solo eso, en lugar de la lista heredada de la plantilla.
---

`scripts/cookies_catalogo.py`, `legales-bloque-cookies.py`, `legales-bloque-rest.py`,
`legales-cookies-complianz.py` y `legales-purga-servicios-complianz.py` — herramientas propias, no
hay repositorio público. Las rutas SON la referencia.

```bash
# 1. medir y escribir el bloque declarativo (con acceso al servidor)
python3 scripts/legales-bloque-cookies.py <slug> --ver
python3 scripts/legales-bloque-cookies.py <slug> --terceros "Google Analytics" --aplicar

# 1-bis. el mismo texto sin SSH, solo por la API del gestor
python3 scripts/legales-bloque-rest.py <dominio> --terceros "Google Analytics" \
  --tabla "_ga,_ga_XXXXXXX" --aplicar
#     credenciales en ~/.wp-sites/rest.json: {"<dominio>": {"base","user","app"}}

# 2. rellenar finalidad, caducidad y titularidad de cada cookie
python3 scripts/legales-cookies-complianz.py <slug> --ver
python3 scripts/legales-cookies-complianz.py <slug> --aplicar

# 3. quitar los servicios que la web NO carga
python3 scripts/legales-purga-servicios-complianz.py <slug> \
  --mantener "WordPress,Complianz,Elementor,Google Analytics" --purgar-servicios --aplicar
```

La diferencia con el asistente de `Complianz` —y con `CookieYes`, `Cookiebot` o `Iubenda`, que son
los rivales reales de este hueco— es esa: **aquí la lista sale de medir el HTML, no de marcar
casillas ni de heredar el catálogo del plugin**. Estos guiones no sustituyen a Complianz: lo
corrigen, porque el plugin publica su ficha por cookie pero nunca escribe la frase «propias o de
terceros» y arrastra servicios de su catálogo que la web no carga. `cookies_catalogo.py` trae más de sesenta patrones de cookies
de gestor, tienda, maquetador, analítica y redes con su clasificación legal escrita en castellano; el
resto los escribe de forma repetible entre marcadores, así que pasarlo dos veces no duplica nada.

**Norma que cubre**: artículo **22.2 de la LSSI-CE (Ley 34/2002)** en su redacción vigente, los
artículos 6 y 7 del **RGPD** para el consentimiento, y —donde está el rechazo real— la **Guía de uso
de cookies de la AEPD**, cuya versión adaptada a las directrices del CEPD rige desde enero de 2023.
Territorio: **España**. Fecha de la comprobación de esta ficha: 2026-09-01; la guía de la AEPD se
revisa, así que antes de usarla como argumento ante el organismo, mirar la edición vigente.

**Lo que NO comprueba**: no valida el banner ni el rechazo en igualdad de condiciones, no mira si se
cargan terceros antes del consentimiento (eso es medición en vivo, con el navegador), y no toca el
registro de consentimientos. Que la política sea correcta no significa que la web lo sea.

Ojo: **sobre-declarar es el fallo más común y no es inofensivo**. Describe un tratamiento de datos
que no existe y delata que nadie miró la web; por eso existe el paso 3. Y todos los guiones son
idempotentes solo mientras se respeten los marcadores HTML: editar el bloque a mano desde el panel
rompe la reescritura y deja dos bloques.
