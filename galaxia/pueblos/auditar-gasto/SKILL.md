---
cosmos: pueblo
nombre: auditar-gasto
padre: agentes-ia/coste
resumen: Busca en la configuracion las fugas conocidas: reglas sin filtro de ruta y servidores conectados sin usarse.
---

`cosecha/auditar-gasto.py` — revisa la configuracion del arnes contra una lista de fugas ya
diagnosticadas y sale con codigo de error si aparece una nueva, asi que se puede colgar de un
enganche o de la integracion continua.

Es el complemento estatico de `medir-contexto`: aquel dice cuanto se gasto, este dice por que se
gastara otra vez manana. La leccion que lo justifica es que el detector no falla casi nunca; lo que
falla es que nadie lo ejecuta, y por eso aqui devuelve codigo de salida en vez de un informe bonito.
