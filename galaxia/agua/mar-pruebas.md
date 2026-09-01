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
