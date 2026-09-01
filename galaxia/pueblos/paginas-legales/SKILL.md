---
cosmos: pueblo
nombre: paginas-legales
padre: cumplimiento
resumen: Crea y audita el aviso legal y la politica de cookies de una web publicada, y cambia su texto sin romperla.
---

`cosecha/legales-crear-paginas.py`, `legales-lssi.py` y `legales-texto.py` — herramientas propias, no
hay repositorio público. Las rutas SON la referencia.

```bash
# 1. auditar lo publicado (sin tocar nada). Sale 0 si pasa, 1 si falla algo
python3 cosecha/legales-lssi.py https://<dominio-cliente>/ --razon-social "Ejemplo S.L." \
  --json informe.json

# 2. crear el aviso legal y la politica si no existen (sin --aplicar solo ensena que haria)
python3 cosecha/legales-crear-paginas.py <slug> \
  --titular "Nombre Apellidos" --nif <NIF> \
  --domicilio "Calle Ejemplo, 1, 00000 Ciudad" --email contacto@ejemplo.test --aplicar

# 3. corregir un dato mal escrito, sustitucion literal e idempotente
python3 cosecha/legales-texto.py <slug> --pagina aviso-legal \
  --buscar "Identificador fiscal: ES <NIF>" --sustituir "NIF: <NIF>" --aplicar
```

Se prefiere a los generadores públicos de textos legales por lo que hacen los otros dos guiones: un
generador te da un texto y ahí acaba. **`legales-lssi.py` audita lo que hay publicado contra lo que
la ley pide**, que es la parte que nadie repite pasado el primer mes, y devuelve código de salida —así
que entra en un gate automático. Y `legales-texto.py` corrige un dato en una página ya maquetada, del
editor clásico o del maquetador, sin rehacerla.

Es el otro extremo del nicho respecto a `presidio` y `arx`: aquellos protegen el dato personal por
dentro; esto es lo que la web tiene que **decir por fuera**, y es lo que mira quien inspecciona.

**Norma que cubre**: artículo **10 de la LSSI-CE (Ley 34/2002)** —denominación social completa,
domicilio, NIF/CIF y medio de contacto directo, de forma permanente, directa y gratuita— más los
requisitos de contenido de la política de cookies que exige la **Guía de cookies de la AEPD**
(tipo, finalidad, propias o de terceros, plazo de conservación). Territorio: **España**. Los dos
motivos de rechazo que originaron estos guiones son textuales de una revisión de Kit Digital de
2026-08-26.

**Lo que NO comprueba**: política de privacidad del RGPD (arts. 13 y 14), condiciones de
contratación de comercio electrónico, ni accesibilidad. Un aviso legal impecable con una política de
privacidad ausente sigue incumpliendo.

Ojo: **los datos no se inventan**. Salen del briefing, de las hojas del cliente o de lo que la propia
web ya publica; un NIF equivocado en un aviso legal es peor que no tener aviso legal. Y sin
`--aplicar` todo va en seco: ese es el modo con el que se empieza siempre.
