---
cosmos: pueblo
nombre: alcance-y-excepcion
padre: agentes-ia
resumen: Declara que se puede tocar y bloquea el resto; el permiso extra se pide con motivo y caduca solo.
origen: propio
---

`scripts/alcance.py` y `scripts/excepcion-codigo.py` — herramientas propias, no de GitHub. Escriben en
`progress/gates/`, que va gitignorado.

```bash
python3 scripts/alcance.py proyecto-a --tarea "footer de proyecto-a"
python3 scripts/alcance.py proyecto-a proyecto-b        # varias de una vez
python3 scripts/alcance.py --ver                        # qué hay declarado
python3 scripts/excepcion-codigo.py <slug> "Quitar el bloque heredado" \
  --nativo-descartado "ninguno: esto es para BORRAR codigo, no para anadirlo"
python3 scripts/alcance.py --quitar                     # al terminar
```

Las dos piezas son el patrón entero: la puerta está cerrada por defecto, abrirla deja rastro, y se
cierra sola sin que nadie tenga que acordarse. `alcance.py` convierte el radio de daño en guardarraíl
en vez de en una frase del encargo que nadie relee — nació de un caso real en el que el encargo
hablaba de UNA web y el arreglo acabó aplicado a dieciocho, tres de ellas sin punto de restauración.
`excepcion-codigo.py` es la válvula, con motivo escrito obligatorio y caducidad de 24 h: sin
caducidad, toda excepción se vuelve permanente el mismo día que se concede.

Gana a una regla escrita en el prompt en lo único que importa: el bloqueo lo aplica un enganche que
**deniega**, no pregunta. Una instrucción se olvida a la vez que se olvida el alcance.

Ojo, dos cosas: **sin fichero de alcance no se bloquea nada** — quien no lo declara trabaja como
siempre, así que esto no protege a quien no lo usa. Y el pase de excepción **no hace pasar el gate**:
el código sigue contando como falla; quitarla es otra decisión, que autoriza una persona.
