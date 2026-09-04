---
cosmos: mar
nombre: pruebas
moja: ["**/test/**", "**/tests/**", "**/*_test.*", "**/*.test.*", "**/*.spec.*", "**/conftest.py"]
resumen: Un test afirma lo medido, no lo deseado. Cobertura alta no demuestra que haya una sola asercion.
---

Se mide primero y se escribe la asercion despues: el test afirma lo medido, no lo deseado.

Solo la mutacion separa con objetividad el test real del decorativo: se rompe el codigo a proposito
y se mira quien se entera; el mutante vivo es una rama que nadie comprobaba.
Cuesta ordenes de magnitud mas que la suite: un modulo cada vez y de madrugada, nunca en cada
commit. Los motores por lenguaje estan en `refactorizacion/mutacion`.

El caso que rompe no se escribe a mano: se muta la entrada y se miran los caminos nuevos; sin
datos que nadie escribiria, no esta probado.

El fallo intermitente se graba, no se razona: repetible bit a bit, la condicion de carrera se
vuelve depurable. En distribuido se inyecta el fallo real -particion, reloj desviado, proceso
muerto- y se comprueba la historia observada.

Un disparador que no es el de produccion pasa sin probar nada; el extremo a extremo, en
navegador real con traza, nunca simulado.

Se dobla el borde mas externo que resuelva el caso: cada capa de mas es un contrato sostenido a
mano; mas de tres claves para contentar a un doble es doblar demasiado adentro.

Generar la entrada que rompe: `hypothesis` (`cosmos abrir hypothesis`), aunque viva en `trading`.
