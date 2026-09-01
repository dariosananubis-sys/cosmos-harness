---
cosmos: pueblo
nombre: lm-evaluation-harness
padre: modelos-locales
resumen: Evalua contra los mismos bancos de pruebas publicados, para poder comparar con lo que otros publican.
---

Es el motor que hay detras de la tabla publica de resultados que todo el mundo cita, asi que es el
unico camino para que un numero propio signifique algo fuera de casa.

Corre entero en local contra el modelo servido, sin pagar un modelo juez, que es lo que separa esto de
las herramientas de evaluacion por criterio subjetivo. `mlflow` registra que paso en cada corrida;
este dice si el modelo es mejor o peor que otro en la misma prueba.
