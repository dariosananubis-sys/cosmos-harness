---
cosmos: pueblo
nombre: lm-evaluation-harness
padre: modelos-locales
resumen: Evalua contra los mismos bancos de pruebas publicados, para poder comparar con lo que otros publican.
---

https://github.com/EleutherAI/lm-evaluation-harness · MIT · 13.854★ · último push 2026-09-01
(comprobado 2026-09-01)

```bash
pip install lm-eval
lm_eval --model hf --model_args pretrained=<id-del-modelo> \
  --tasks hellaswag --limit 50 --output_path /tmp/eval
lm_eval --model local-completions --model_args base_url=http://localhost:11434/v1 --tasks arc_easy
```

Es el motor real que hay detrás de la tabla pública de resultados que todo el mundo cita, así que es
**el único camino para que un número propio signifique algo fuera de casa**: mismos prompts, mismas
tareas, comparable con lo que publica cualquiera.

**Memoria**: el propio arnés de evaluación es ligero; el coste es el modelo evaluado más el conjunto de
datos, así que valen las mismas reglas que servirlo (4-bit, ≤7B). El `--limit` no es un atajo, es lo
que hace la evaluación viable aquí — con la salvedad de abajo.

Gana a `promptfoo/promptfoo` (24.722★) y a las herramientas de evaluación por criterio subjetivo en lo
que importa para esta casa: corre **entero en local** contra el modelo servido, sin pagar un modelo
juez. Y su frontera con `mlflow` es limpia: aquel registra qué pasó en cada corrida, este dice si el
modelo es mejor o peor que otro en la misma prueba.

Ojo: un resultado con `--limit` **no es comparable** con las cifras publicadas, que corren la tarea
completa; publicarlo como si lo fuera es el falso verde de este pueblo. Y las tareas se descargan de
la red en la primera ejecución.
