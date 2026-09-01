---
cosmos: pueblo
nombre: lighthouse
padre: web/calidad-de-sitio
resumen: Motor canonico que audita una URL y devuelve informe con las metricas de experiencia de carga.
---

https://github.com/GoogleChrome/lighthouse · Apache-2.0 · 30.718★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
npm install -g lighthouse
lighthouse https://example.com --output json --output-path /tmp/informe.json --only-categories=performance
python3 -c "import json;d=json.load(open('/tmp/informe.json'));print(d['categories']['performance']['score'])"
```

Referencia oficial y gratuita, corre en local y **no manda datos a ningún sitio**. Es el motor que hay
debajo de casi todo lo demás del nicho, incluida su propia parte de accesibilidad (que es `axe-core`).

Gana a `addyosmani/web-quality-skills` (2.730★), la colección que lo envuelve: aquella aporta listas de
causas y arreglos por framework, que es exactamente el tipo de consejo que un modelo bueno ya trae. El
motor sí aporta; la envoltura no. También queda fuera `cosecha/pagespeed-accessibility.py`, envoltura
del servicio alojado: ese servicio **es este mismo motor corriendo en casa ajena**, con cuota y sin
control de versión. Se usa esto en local; aquello solo cuando hace falta la medición de campo del
buscador.

Ojo: una sola pasada de Lighthouse **no es una medición**, es una muestra — el ruido entre ejecuciones
en la misma máquina supera muchas veces la diferencia que se está intentando probar. Hay que correr
varias y quedarse con la mediana, y comparar siempre contra la misma red y el mismo perfil de CPU. Y
audita la URL que se le da: para el sitio entero está `unlighthouse`.
