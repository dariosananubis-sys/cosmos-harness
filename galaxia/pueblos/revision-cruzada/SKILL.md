---
cosmos: pueblo
nombre: revision-cruzada
padre: agentes-ia/evaluacion
resumen: Tres familias de modelos revisan el mismo cambio a la vez; el codigo de salida sale del acuerdo, no de una opinion.
---

`scripts/multi-review.py` — herramienta propia, no de GitHub. Habla con tres familias de modelos por
OpenRouter, en su capa gratuita.

```bash
export OPENROUTER_API_KEY="<clave-de-capa-gratuita>"
python3 scripts/multi-review.py                       # revisa `git diff HEAD`
python3 scripts/multi-review.py --last-commit
python3 scripts/multi-review.py --diff-file parche.diff --context "refactor de autenticacion"
echo $?    # 0 acuerdo -> integrable | 1 discrepancia | 2 crítico | 3 error de configuración
```

Lo útil no es la revisión, que cualquiera hace: es que **el desacuerdo es la señal**. Al devolver un
código de salida por consenso se puede colgar de un enganche y parar de verdad, en vez de producir
otro informe que nadie lee.

Familias distintas y no tres pasadas del mismo modelo, porque un modelo se equivoca de forma
consistente consigo mismo: repetirlo confirma el error en vez de encontrarlo. Es lo mismo que exige la
regla del revisor adversarial de esta casa — encadenar revisores con ángulos distintos, nunca clonar
uno.

Ojo: los identificadores de modelo que trae escritos **envejecen en semanas** y una capa gratuita que
desaparece se ve igual que un fallo de red (sale 3, no 1). Lo que no envejece es la regla: tres
proveedores que no compartan entrenamiento. Y si la clave no está puesta, sale 3 — un 3 nunca es un
visto bueno.
