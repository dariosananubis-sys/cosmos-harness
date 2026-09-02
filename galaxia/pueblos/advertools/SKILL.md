---
cosmos: pueblo
nombre: advertools
padre: visibilidad/auditoria
resumen: Biblioteca que rastrea, lee mapas del sitio y ficheros de robots y devuelve tablas para analizar.
---

https://github.com/eliasdabbas/advertools · MIT · 1.450★ · push 2026-06-30 (comprobado 2026-09-01)

```bash
pip install advertools

python - <<'PY'
import advertools as adv, pandas as pd

# 1. leer el mapa del sitio como tabla
mapa = adv.sitemap_to_df("https://ejemplo.test/sitemap.xml")
print(mapa[["loc", "lastmod"]].head())

# 2. leer robots.txt como tabla
print(adv.robotstxt_to_df("https://ejemplo.test/robots.txt"))

# 3. rastrear, con freno para no tumbar la web del cliente
adv.crawl("https://ejemplo.test", "salida.jl", follow_links=True,
          custom_settings={"CLOSESPIDER_PAGECOUNT": 50, "DOWNLOAD_DELAY": 1})
d = pd.read_json("salida.jl", lines=True)
print(d[["url", "title", "status", "h1"]].head())
PY
```

Siete años de desarrollo y mecanismo real: **cada función devuelve una tabla**, así que se compone
con el motor analítico (`pandas`) en vez de exigir su propio formato de informe. Eso es lo que la
separa de Screaming Frog y de los rastreadores con interfaz: aquí el resultado entra en un cuaderno,
se cruza con los datos de `search-console` y se filtra como cualquier otra tabla.

Descartado el rastreador con interfaz web que sustituye a la herramienta de escritorio de pago: hace
lo mismo que este más el orquestador, y su propio informe avisa de que circulan varias copias con
nombres casi idénticos.

Ojo: `crawl` es Scrapy por debajo y **arranca sin freno si no se le pone**. Contra la web de un
cliente, siempre con `DOWNLOAD_DELAY` y `CLOSESPIDER_PAGECOUNT`, o se convierte en una prueba de carga
no pedida. No renderiza JavaScript: un sitio que pinta el contenido en el navegador sale casi vacío y
sin error — falso verde. Y su ritmo bajó (último empujón junio de 2026, 1.450 estrellas): funciona,
pero no se le supone una corrección rápida.
