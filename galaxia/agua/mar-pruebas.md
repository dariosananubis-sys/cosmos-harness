---
cosmos: mar
nombre: pruebas
moja: ["**/test/**", "**/tests/**", "**/*_test.*", "**/*.test.*", "**/*.spec.*", "**/conftest.py"]
resumen: Un test afirma lo medido, no lo deseado. Cobertura alta no demuestra que haya una sola asercion.
---

Se mide primero y se escribe la asercion despues: el test afirma lo medido, no lo deseado.

La unica forma objetiva de separar un test real de uno decorativo es la mutacion: se altera el
codigo a proposito y se mira si alguien se entera. Un mutante que sobrevive es una rama que nadie
comprobaba. Cuesta ordenes de magnitud mas que la suite, asi que se apunta a un modulo y se corre
de madrugada, nunca en cada commit.

El caso que rompe casi nunca se escribe a mano: se busca mutando la entrada y viendo que caminos
nuevos aparecen. Si nadie ha intentado romperlo con datos que nadie escribiria, no esta probado.

El fallo intermitente se graba, no se razona: una ejecucion repetible bit a bit convierte una
condicion de carrera en algo depurable. En sistemas distribuidos la prueba seria inyecta el fallo
real -particion, reloj desviado, proceso muerto- y comprueba la historia observada.

Un test cuyo disparador no es el que usa produccion pasa sin probar nada. Para extremo a extremo,
navegador real con traza, nunca una simulacion.

Se dobla el borde mas externo que resuelva el caso: cada capa de mas es un contrato que toca
sostener a mano. Si hay que teclear una estructura de mas de tres claves para contentar a un doble,
se doblo demasiado adentro.

Las herramientas de mutacion de cada lenguaje estan en `rendimiento/calidad`.
