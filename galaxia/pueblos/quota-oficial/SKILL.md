---
cosmos: pueblo
nombre: quota-oficial
padre: agentes-ia/coste
resumen: Pregunta la cuota que queda al servicio en vez de adivinarla, y senala el pico dentro de la ventana.
---

`cosecha/quota-oficial.py` — consulta el consumo real de la suscripcion contra su propio recurso de
uso, resolviendo cual es la configuracion activa a partir del proceso vivo y leyendo la credencial
del llavero del sistema, con reintento creciente.

`cosecha/quota-peak.py` — sobre los registros locales, dice en que momento de la ventana se gasto el
pico. Sirve para atribuir el gasto a una tarea concreta, que es lo que el numero total no dice.

Sin esto, cualquier herramienta de control de cuota tiene dos opciones: estimar, o leer la interfaz
por raspado. La primera se equivoca justo cuando importa y la segunda se rompe al primer cambio de
diseno.
