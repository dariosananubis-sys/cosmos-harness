---
cosmos: mar
nombre: pruebas
moja: ["**/test/**", "**/tests/**", "**/*_test.*", "**/*.test.*", "**/*.spec.*", "**/conftest.py"]
resumen: Un test afirma lo medido, no lo deseado. Cobertura alta no demuestra que haya una sola asercion.
---

Se mide primero y se escribe la asercion despues. Una comprobacion que nunca ha dado rojo no se
distingue de una rota.

La unica forma objetiva de separar un test real de uno decorativo es la mutacion: se altera el
codigo a proposito y se mira si alguien se entera. `stryker-js` en JavaScript y TypeScript, `mutmut`
en Python. Un mutante que sobrevive es una rama que nadie estaba comprobando. Para extremo a extremo,
navegador real con traza, nunca una simulacion del navegador.

**El caso que rompe casi nunca se escribe a mano.** Se busca mutando la entrada y observando que
caminos nuevos se destapan; el nicho de ciberseguridad tiene el motor, y aqui vale la idea: si nadie
ha intentado romperlo con datos que nadie escribiria, no esta probado.

**El fallo intermitente se graba, no se razona.** Una ejecucion grabada y repetible bit a bit
convierte la condicion de carrera en algo que se puede depurar; el nicho de sistemas tiene la
herramienta. Y cuando el sistema es distribuido, la prueba seria inyecta el fallo real —particion de
red, reloj desincronizado, proceso muerto— y comprueba linealizabilidad sobre la historia observada,
que es como se encontraron los fallos de consistencia de media docena de bases de datos conocidas.

Un test cuyo disparador no es el que usa produccion pasa sin probar nada.
