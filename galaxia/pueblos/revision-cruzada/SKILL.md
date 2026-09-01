---
cosmos: pueblo
nombre: revision-cruzada
padre: agentes-ia/evaluacion
resumen: Tres familias de modelos revisan el mismo cambio a la vez; el codigo de salida sale del acuerdo, no de una opinion.
---

`cosecha/multi-review.py` — manda el mismo cambio a tres familias de modelos distintas en paralelo y
sintetiza un veredicto. Lo que lo hace util no es la revision, que cualquiera hace: es que **el
desacuerdo es la senal**. Sale con cero si las tres coinciden en que se puede integrar, con uno si
discrepan y con dos si alguna encuentra algo critico, asi que se puede colgar de un enganche y
parar de verdad.

Familias distintas y no tres pasadas del mismo modelo, porque un modelo se equivoca de forma
consistente consigo mismo: repetirlo confirma el error en vez de encontrarlo.

Corre sobre modelos de capa gratuita, sin tarjeta. Los identificadores concretos que trae escritos
envejecen rapido y hay que actualizarlos; lo que no envejece es la regla de elegir tres proveedores
que no compartan entrenamiento.
