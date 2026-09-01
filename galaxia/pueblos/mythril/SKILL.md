---
cosmos: pueblo
nombre: mythril
padre: blockchain
resumen: Ejecucion simbolica sobre el codigo maquina: sirve cuando del contrato ajeno solo hay lo que esta desplegado.
---

`slither` y `echidna` necesitan el codigo fuente. Este trabaja sobre el bytecode, que es lo unico que
hay al auditar un contrato de terceros ya en produccion, que es la mitad de los encargos reales.

No sustituye a los otros dos: se ejecuta despues, sobre lo desplegado, para comprobar que lo que corre
es lo que se leyo. Cuando no hay fuente, es lo unico que queda.
