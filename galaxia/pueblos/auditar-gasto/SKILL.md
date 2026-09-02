---
cosmos: pueblo
nombre: auditar-gasto
padre: agentes-ia/coste
resumen: Busca en la configuracion las fugas conocidas: reglas sin filtro de ruta y servidores conectados sin usarse.
---

`scripts/auditar-gasto.py` — herramienta propia, no de GitHub. Solo lectura salvo con `--arreglar`.

```bash
python3 scripts/auditar-gasto.py              # audita; sale 1 si hay fuga, 0 si limpio
python3 scripts/auditar-gasto.py --arreglar   # vuelve a apagar los plugins de la lista
```

Revisa la configuración del arnés contra fugas ya diagnosticadas: enganches de `UserPromptSubmit`,
rules cargadas siempre (`paths:` ausente o mal puesto cuando deberían ser perezosas), el catálogo de
skills/agentes/comandos que el CLI inyecta en el system prompt —incluido el de los plugins
habilitados—, duplicación literal entre `CLAUDE.md` y las rules, y ficheros de memoria huérfanos.

Es el complemento estático de `medir-contexto`: aquel dice cuánto se gastó, este dice por qué se
volverá a gastar mañana. Gana a un informe bonito porque **devuelve código de salida**: se cuelga de
un enganche o de la integración continua y para de verdad. El detector casi nunca falla; lo que falla
es que nadie lo ejecuta.

Ojo: viene con las tres listas (`GLOBALES_OK`, `PLUGINS_DESCARTADOS`, `PLUGINS_APAGADOS`) y el
`PRESUPUESTO_CATALOGO` **vacíos a propósito**. Sin rellenarlos con el histórico del repo propio, sale
verde sin haber mirado nada — falso verde de manual.
