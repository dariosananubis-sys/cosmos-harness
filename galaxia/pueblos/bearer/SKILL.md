---
cosmos: pueblo
nombre: bearer
padre: ciberseguridad/analisis/vulnerabilidades
resumen: Sigue el flujo de datos y dice por donde viaja lo sensible, no solo donde se declara.
---

https://github.com/Bearer/bearer · Elastic License 2.0 (leído en su `LICENSE.txt`; la API de GitHub la reporta como `NOASSERTION`) · 2.739★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install bearer/tap/bearer
```

```bash
# informe de seguridad sobre el árbol actual
bearer scan .

# el informe que sirve para RGPD: qué datos personales hay y a dónde salen
bearer scan . --report dataflow --format json --output flujo-de-datos.json

# solo lo grave, para una tubería que deba fallar
bearer scan . --severity critical,high --exit-code 1
```

Entra junto a `semgrep` porque responde otra pregunta: no qué patrón aparece, sino **a dónde acaba
llegando un dato personal** — a qué base, a qué API de terceros. Gana a `data-privacy-stack/presidio`
(10.701★) en este hueco porque Presidio detecta datos personales dentro de un texto ya producido, y
esto los rastrea dentro del **código** que los mueve. Sirve a la vez al nicho y al agua de custodia.

Ojo, y es lo que más pesa: **la licencia no es libre**. Elastic License 2.0 permite usarlo, leerlo y
modificarlo, pero prohíbe ofrecerlo como servicio gestionado a terceros y prohíbe saltarse sus
limitaciones por clave. Para auditar código propio o de un cliente no estorba; para empotrarlo en un
producto que se vende, hay que leerla antes. Además, el análisis entre ficheros avanzado y varios
lenguajes están en la capa de pago (Bearer Pro, vía Cycode): el CLI gratuito **no lo dice al
terminar**, así que un informe verde puede ser un informe corto.
