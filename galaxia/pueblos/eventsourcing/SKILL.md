---
cosmos: pueblo
nombre: eventsourcing
padre: trading/codigo-de-bot
resumen: Registro que solo crece: el estado se reconstruye repitiendo lo ocurrido, no se guarda digerido.
---

https://github.com/pyeventsourcing/eventsourcing · BSD-3-Clause · 1.684★ · último push 2026-08-23 (comprobado 2026-09-01)

```bash
pip install eventsourcing
```

```python
from eventsourcing.domain import Aggregate, event

class Posicion(Aggregate):
    @event("Abierta")
    def __init__(self, simbolo, cantidad):
        self.simbolo, self.cantidad = simbolo, cantidad
    @event("Ejecutada")                     # cada hecho se registra, no se sobrescribe
    def aplicar_ejecucion(self, cantidad):
        self.cantidad += cantidad

# arrancar el bot = repetir los hechos guardados; el estado sale igual siempre
```

Si lo que se persiste es la posición actual, un corte a media escritura la deja mintiendo y no hay
forma de saber desde cuándo. Si lo que se persiste es cada **hecho** —orden enviada, ejecución
recibida, cancelación confirmada—, arrancar es repetir, el resultado es el mismo siempre y la
auditoría queda hecha de paso. Aporta almacén de eventos, reconstrucción por agregado, instantáneas
para no repetir un año entero y control de concurrencia optimista.

Ojo, cuándo **no** hace falta: con un bot pequeño, una tabla en SQLite que solo añade filas cumple lo
mismo con menos piezas — meter esto ahí es sobreingeniería. Entra cuando hay que versionar los
hechos, reconstruir a una fecha o justificar un saldo ante alguien. Y el registro que solo crece
**crece de verdad**: sin política de instantáneas, reconstruir un agregado de un año son miles de
eventos releídos en cada arranque.
