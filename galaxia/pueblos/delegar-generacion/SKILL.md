---
cosmos: pueblo
nombre: delegar-generacion
padre: agentes-ia/construccion
resumen: Un modelo redacta el encargo y otro teclea el fichero; el prompt se ve antes de correr y la cuota agotada reintenta.
---

`cosecha/codex-delegate.sh` — separa decidir que construir de teclear el codigo: el modelo que
razona redacta un encargo autocontenido y una consola generadora escribe el fichero. El encargo
queda a la vista antes de ejecutarse, que es la diferencia entre delegar y perder el control: si el
prompt esta mal, se ve ahi y no en el resultado.

`cosecha/codex-handler.sh` — la llamada real: fija el modo de escritura en el espacio de trabajo,
resuelve la ruta absoluta de salida, detecta por el texto del error que lo que fallo fue la cuota y
no el codigo, y reintenta en vez de abortar. Esa distincion es la que evita repetir un trabajo largo
entero por un limite temporal.

Se usa cuando el encargo pasa de unas decenas de lineas. Por debajo de eso, delegar cuesta mas que
escribirlo.
