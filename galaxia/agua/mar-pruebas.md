---
cosmos: mar
nombre: pruebas
moja: ["**/test/**", "**/tests/**", "**/*_test.*", "**/*.test.*", "**/*.spec.*", "**/conftest.py"]
resumen: Un test afirma lo medido, no lo deseado. Cobertura alta no demuestra que haya una sola asercion.
---

Se mide primero y se escribe la asercion despues: el test afirma lo medido, no lo deseado.

La unica forma objetiva de separar un test real de uno decorativo es la mutacion: se altera el
codigo a proposito y se mira si alguien se entera. Un mutante que sobrevive es una rama que nadie
estaba comprobando. Cuesta ordenes de magnitud mas que correr la suite, asi que se apunta a un
modulo y se ejecuta de madrugada, nunca en cada commit. Para extremo a extremo, navegador real con
traza, nunca una simulacion del navegador.

**El caso que rompe casi nunca se escribe a mano.** Se busca mutando la entrada y observando que
caminos nuevos se destapan; el nicho de ciberseguridad tiene el motor, y aqui vale la idea: si nadie
ha intentado romperlo con datos que nadie escribiria, no esta probado.

**El fallo intermitente se graba, no se razona.** Una ejecucion grabada y repetible bit a bit
convierte la condicion de carrera en algo que se puede depurar; el nicho de sistemas tiene la
herramienta. Y cuando el sistema es distribuido, la prueba seria inyecta el fallo real —particion de
red, reloj desincronizado, proceso muerto— y comprueba linealizabilidad sobre la historia observada,
que es como se encontraron los fallos de consistencia de media docena de bases de datos conocidas.

Un test cuyo disparador no es el que usa produccion pasa sin probar nada.

Que motor de mutacion corresponde a cada lenguaje esta en `rendimiento/calidad`, junto al resto de
herramientas que aplican estas politicas.

Se dobla el borde mas externo que resuelva el caso: cada capa de mas es un contrato que toca
sostener a mano. Si hay que teclear una estructura de mas de tres claves para contentar a un doble,
se doblo demasiado adentro; doblando solo el origen de los datos, el codigo real arma el objeto
valido sin ayuda.

El interprete se nombra entero: coger el del sistema en vez del entorno del proyecto convirtio
518 pruebas en verde en 194 con 39 caidas por dependencias que no estaban.
