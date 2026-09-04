---
cosmos: pueblo
nombre: promptfoo
padre: agentes-ia/evaluacion
resumen: Matriz declarativa de prompts x modelos con codigo de salida; incluye red teaming automatizado.
---

https://github.com/promptfoo/promptfoo · MIT · 24.774★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
npm install -g promptfoo
```

```yaml
# promptfooconfig.yaml
prompts:
  - "Resume en una frase: {{texto}}"
providers:
  - anthropic:claude-sonnet-4-5
  - openai:gpt-5
tests:
  - vars:
      texto: "El servidor cayo por falta de memoria durante el despliegue."
    assert:
      - type: contains
        value: "memoria"
      - type: llm-rubric
        value: "el resumen no inventa datos que no estan en el texto"
```

```bash
promptfoo eval          # matriz completa, HTML con diffs lado a lado
promptfoo redteam run   # ataques automatizados: inyeccion, jailbreak, fuga de datos
echo $?                 # != 0 si algun assert o ataque paso: engancha en CI
```

Gana a `deepeval` cuando la pregunta es **comparar** — el mismo prompt contra varios modelos o
varias versiones de un prompt, en una tabla que se ve de un vistazo — y cuando hace falta
**red teaming** de serie: ataques de inyección y jailbreak generados y puntuados sin escribir cada
caso a mano. Pierde frente a él cuando la evaluación necesita vivir dentro de la lógica Python del
agente, caso a caso, como parte de la misma suite de tests.

Ojo: `llm-rubric` es, otra vez, un LLM juzgando a otro LLM — coste y varianza que hay que medir, no
asumir. Y `redteam run` manda de verdad los prompts de ataque al proveedor configurado: contra un
endpoint de producción con límite de gasto, eso es tráfico y coste real, no una simulación local.
