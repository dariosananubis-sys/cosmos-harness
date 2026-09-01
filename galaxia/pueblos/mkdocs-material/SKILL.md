---
cosmos: pueblo
nombre: mkdocs-material
padre: documentos/sitios
resumen: Documentacion navegable desde Markdown con busqueda, versiones e idiomas sin HTML.
---

https://github.com/squidfunk/mkdocs-material · MIT · 27.358★ · push 2026-08-30 (comprobado 2026-09-01)

```bash
pip install mkdocs-material

mkdocs new .
cat > mkdocs.yml <<'YML'
site_name: Documentacion
theme:
  name: material
  features: [navigation.tabs, search.suggest, content.code.copy]
plugins: [search]
YML

mkdocs serve            # http://127.0.0.1:8000 con recarga en caliente
mkdocs build            # HTML estatico en site/
```

Documentación navegable desde Markdown, con buscador que funciona sin servicio externo, versiones e
idiomas. Descartados `docusaurus` —mismo hueco, pero arrastra un proyecto de Node entero y componentes
interactivos que aquí no hacen falta— y `mdbook`, que produce un libro de un solo binario pero tiene
un ecosistema de extensiones mucho más pobre. Este gana por extensiones maduras y coste de arranque
bajo: dos ficheros y ya hay sitio.

Ojo: parte de lo llamativo (el modo tarjetas sociales, el aviso de cookies integrado, el buscador
alojado, algunos bloques) vive en la **edición Insiders**, que es de pago por patrocinio. La
documentación oficial mezcla las dos ediciones y marca las de pago con un icono fácil de pasar por
alto: antes de prometer una función, comprobar que no lleva la marca. Todo lo listado arriba es de la
edición libre.
