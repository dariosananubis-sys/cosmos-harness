---
cosmos: pueblo
nombre: medir-contexto
padre: agentes-ia/coste
resumen: Lo que saben las transcripciones: cuanto costo la sesion, que entro de mas y que comandos se ejecutaron.
---

`cosecha/medir-contexto-claude.py` — mide el coste real de una sesion leyendo sus transcripciones,
deduplicando por identificador de peticion y separando lo que fue crear cache de lo que fue salida.
Es el numero que decide donde recortar: medido asi, la mayor parte del gasto de una ventana suele ser
material nuevo entrando, no razonamiento.

`cosecha/barrido-transcripts.py` — busca patrones en esas mismas transcripciones. Se usa para lo otro
que no se ve: comprobar si una regla se leyo, si un fichero entro dos veces o si algo se escapo.

`cosecha/cc-history.sh` — la tercera lectura de la misma fuente: los comandos de consola que se
ejecutaron de verdad, de un proyecto o de todos en orden cronologico. Es el rastro con el que se
audita a posteriori lo que se toco fuera del repositorio —un despliegue, un borrado— cuando el
resumen de la sesion ya no lo cuenta. Corre a demanda, sin instalacion ni credenciales.

Complementa al medidor de este propio arbol: aquel mide lo que un catalogo cuesta antes de empezar,
este mide lo que una sesion gasto de verdad.
