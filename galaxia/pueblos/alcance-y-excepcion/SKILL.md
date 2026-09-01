---
cosmos: pueblo
nombre: alcance-y-excepcion
padre: agentes-ia
resumen: Declara que se puede tocar y bloquea el resto; el permiso extra se pide con motivo y caduca solo.
---

`cosecha/alcance.py` — declara que proyectos estan autorizados en la tarea actual y deniega la
escritura fuera de ahi. Es el radio de dano convertido en guardarrail, en vez de en una frase del
encargo que nadie vuelve a leer.

`cosecha/excepcion-codigo.py` — la valvula: un pase con motivo escrito y caducidad de un dia para
saltarse un bloqueo concreto. Sin caducidad, toda excepcion se vuelve permanente el mismo dia que se
concede.

Las dos piezas juntas son el patron: la puerta esta cerrada por defecto, abrirla deja rastro, y se
vuelve a cerrar sola sin que nadie tenga que acordarse.
