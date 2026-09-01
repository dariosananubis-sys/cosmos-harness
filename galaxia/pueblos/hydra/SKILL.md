---
cosmos: pueblo
nombre: hydra
padre: cientifico
resumen: Compone la configuracion del experimento y deja registrada la de cada corrida, sobreescribible desde la consola.
---

Es la pieza que hace que un experimento se pueda repetir: cada ejecucion guarda su configuracion
completa, y cualquier parametro se cambia desde la linea de comandos sin tocar el codigo.

Complementa a `mlflow`, que registra el resultado, y a `dvc`, que versiona el dato: este fija la
entrada. Sin el, la pregunta "con que semilla y que parametros salio esto" se responde de memoria, que
es como no responderla.
