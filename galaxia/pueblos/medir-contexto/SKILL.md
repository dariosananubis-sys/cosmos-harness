---
cosmos: pueblo
nombre: medir-contexto
padre: agentes-ia/coste
resumen: Bascula de contexto: deduplica por peticion sobre las transcripciones y dice que parte fue crear cache.
---

`cosecha/medir-contexto-claude.py` — mide el coste real de una sesion leyendo sus transcripciones,
deduplicando por identificador de peticion y separando lo que fue crear cache de lo que fue salida.
Es el numero que decide donde recortar: medido asi, la mayor parte del gasto de una ventana suele ser
material nuevo entrando, no razonamiento.

`cosecha/barrido-transcripts.py` — busca patrones en esas mismas transcripciones. Se usa para lo otro
que no se ve: comprobar si una regla se leyo, si un fichero entro dos veces o si algo se escapo.

Complementa al medidor de este propio arbol: aquel mide lo que un catalogo cuesta antes de empezar,
este mide lo que una sesion gasto de verdad.
