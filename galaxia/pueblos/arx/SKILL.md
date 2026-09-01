---
cosmos: pueblo
nombre: arx
padre: cumplimiento/datos-personales
resumen: Anonimiza con k-anonimato y mide el riesgo de reidentificacion que queda.
---

https://github.com/arx-deidentifier/arx · Apache-2.0 · 734★ · push 2025-10-01 (comprobado 2026-09-01)

```bash
# aplicacion Java de escritorio: descargar el ejecutable de la version publicada
open https://github.com/arx-deidentifier/arx/releases     # arx-x.y.z.jar / instalador por sistema
java -jar arx-*.jar

# o como biblioteca, desde Maven
# <dependency><groupId>org.deidentifier</groupId>
#   <artifactId>libarx</artifactId><version><VERSION></version></dependency>
```

Frontera con `presidio`, y son dos requisitos distintos que no se sustituyen: aquel **encuentra y
sustituye lo que se ve** (un DNI, un nombre, una matrícula); este **demuestra que lo que queda no
permite volver a identificar a nadie**. Un conjunto de datos sin nombres pero con código postal,
fecha de nacimiento y sexo reidentifica a la mayoría de la población — eso es lo que mide aquí el
k-anonimato, la l-diversidad y la t-cercanía, junto al riesgo de reidentificación que sobrevive a la
transformación.

**Norma que cubre**: es la herramienta para argumentar el considerando 26 del RGPD (Reglamento UE
2016/679), que es el que define cuándo un dato deja de ser personal —territorio Unión Europea— y el
criterio de «medios razonablemente utilizables» del dictamen 05/2014 del antiguo Grupo del artículo
29. En España, complementa pero no sustituye lo que exige la LOPDGDD (Ley Orgánica 3/2018).

**Lo que NO comprueba**: no dice si el tratamiento tiene base legítima, ni si hay que hacer
evaluación de impacto, ni lleva registro de actividades. Un dato anonimizado con métricas impecables
sigue siendo ilegal si se obtuvo sin base jurídica. Y el resultado depende por completo de las
jerarquías de generalización que escriba la persona: mal definidas, dan una k alta y una
anonimización falsa.

Ojo de vida: **el último empujón es de octubre de 2025**, casi un año antes de esta comprobación, y
734 estrellas. Sigue siendo la única del barrido en su hueco con base científica publicada, pero es
el pueblo más frágil de este nicho — revisar antes de construir producto encima.
