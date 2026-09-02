---
cosmos: pueblo
nombre: presidio
padre: cumplimiento/datos-personales
resumen: Detecta y sustituye datos personales en textos e imagenes antes de que salgan de casa.
---

https://github.com/data-privacy-stack/presidio · MIT · 10.702★ · push 2026-08-31 (comprobado 2026-09-01)

El repositorio **se movió** de `microsoft/presidio` a `data-privacy-stack/presidio`; el redirect
sigue vivo pero cualquier cita nueva usa la URL de arriba.

```bash
pip install presidio-analyzer presidio-anonymizer
python -m spacy download es_core_news_lg

python - <<'PY'
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

texto = "Contacta con Ana en ana@ejemplo.test o en el 600 000 000."
res = AnalyzerEngine().analyze(text=texto, language="es")
print(AnonymizerEngine().anonymize(text=texto, analyzer_results=res).text)
PY
```

Reconocedores por entidades, expresiones regulares y sumas de control, en varios idiomas, con
anonimización real (sustituir, cifrar, enmascarar, sintetizar) y no solo detección. Gana a
`piiscan`, `presidio-cli` y `presidio-rs` —las herramientas menores del mismo barrido— por
cobertura de idiomas y por ser el único con anonimizador propio; y su frontera con `bearer` es
clara: `bearer` dice **por dónde viaja** el dato personal en tu código, este dice **aquí hay un DNI
en este texto y lo tacho**.

Se pasa antes de exportar un conjunto de datos, de enseñarlo en un informe o de dárselo a un modelo.
Es la pieza ejecutable del agua de custodia para el caso de los datos.

**Norma que cubre**: ninguna, y conviene decirlo así. Es una herramienta técnica que ayuda a
cumplir el principio de minimización del RGPD (art. 5.1.c, Unión Europea), no un certificador. **Lo
que NO comprueba**: no mide riesgo de reidentificación de lo que queda —eso es `arx`—, no lleva
registro de tratamientos y no valida bases jurídicas.

Ojo: los reconocedores en español son bastante peores que en inglés, y el de DNI/NIE español no
valida la letra de control por defecto — hay que añadir un reconocedor propio o pasar el resultado
por `scripts/nif-cif-validator.js`. Un falso negativo aquí es un dato personal que sale de casa, así
que la salida se revisa por muestreo antes de fiarse; nunca se declara «anonimizado» por haberlo
ejecutado.
