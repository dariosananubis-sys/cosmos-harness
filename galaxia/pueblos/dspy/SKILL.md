---
cosmos: pueblo
nombre: dspy
padre: agentes-ia/construccion
resumen: Programa el flujo en modulos y deja que un optimizador reescriba los prompts contra metricas.
---

https://github.com/stanfordnlp/dspy · MIT · 37.744★ · último push 2026-08-31 (comprobado 2026-09-03)

```bash
pip install dspy
```

```python
import dspy

lm = dspy.LM("anthropic/claude-sonnet-4-5")
dspy.configure(lm=lm)

class ResumenFirma(dspy.Signature):
    """Resume un texto en una frase sin inventar datos."""
    texto: str = dspy.InputField()
    resumen: str = dspy.OutputField()

resumidor = dspy.Predict(ResumenFirma)
print(resumidor(texto="El servidor cayo por falta de memoria durante el despliegue.").resumen)

# un optimizador reescribe el prompt interno contra un set de ejemplos y una metrica
optimizado = dspy.MIPROv2(metric=lambda ej, pred: ej.resumen in pred.resumen).compile(
    resumidor, trainset=[]
)
```

Gana a escribir el prompt a mano en cualquiera de los pueblos vecinos cuando hay **un conjunto de
ejemplos y una métrica objetiva**: en vez de iterar el texto del prompt a ojo, un optimizador
(`MIPROv2`, `BootstrapFewShot`) prueba variantes y se queda con la que mejor puntúa. Pierde frente
a `pydantic-ai` o `claude-agent-sdk` para un agente simple de una sola llamada, donde no hay
conjunto de entrenamiento que optimizar y el vocabulario de `Signature`/`Module` es coste sin
beneficio.

Ojo: optimizar cuesta — `MIPROv2` sobre un modelo de pago prueba decenas de variantes de prompt
contra el trainset entero, y eso son llamadas reales que se pagan una vez por optimización, no
por uso. Y el prompt final que genera es opaco: lo que corre en producción no es el texto que
escribió una persona, así que depurar un fallo pide inspeccionar el prompt compilado, no el
código Python.
