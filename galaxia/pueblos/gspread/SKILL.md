---
cosmos: pueblo
nombre: gspread
padre: analitica/hojas-de-calculo
resumen: Lee y escribe hojas de calculo en la nube por su API oficial, como si fueran una tabla mas.
---

Via oficial, no scraping. Es la fuente real de muchos datos de trabajo aqui.

Descartado el servidor de herramientas para hojas de calculo de escritorio: resuelve el formato de
oficina, pero un servidor de herramientas cuesta contexto en cada sesion y aqui la fuente esta en la
nube. Queda anotado para cuando el fichero llegue por correo.

De la cosecha propia hay tres clientes del mismo proveedor que no entran: `cosecha/gsheet_sa.py` y
`cosecha/gsheets.py` —el mismo trabajo por cuenta de servicio y por autorizacion de usuario, con
menos mantenimiento detras que este—, y `cosecha/gdoc-read.py`, que lee un documento de texto a
plano: caso demasiado estrecho para ocupar linea de catalogo.
