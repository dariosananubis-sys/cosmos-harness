---
cosmos: pueblo
nombre: eventsourcing
padre: trading/codigo-de-bot
resumen: Registro que solo crece: el estado se reconstruye repitiendo lo ocurrido, no se guarda digerido.
---

Si lo que se persiste es la posicion actual, un corte a media escritura la deja mintiendo y no hay
forma de saber desde cuando. Si lo que se persiste es cada hecho —orden enviada, ejecucion recibida,
cancelacion confirmada—, arrancar es repetir, el resultado es el mismo siempre y la auditoria queda
hecha de paso.

Aporta almacen de eventos, reconstruccion por agregado, instantaneas para no repetir un ano entero y
control de concurrencia optimista.

Cuando NO hace falta: con un bot pequeno, una tabla que solo anade filas en SQLite cumple lo mismo
con menos piezas. Esto entra cuando hay que versionar los hechos, reconstruir a una fecha o justificar
un saldo ante alguien.
