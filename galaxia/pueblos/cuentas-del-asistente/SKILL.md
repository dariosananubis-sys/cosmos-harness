---
cosmos: pueblo
nombre: cuentas-del-asistente
padre: agentes-ia/coste
resumen: Varias cuentas del mismo asistente vivas a la vez: cual gasta la cuota, que ninguna caduque, y matar las zombis.
---

`cosecha/claude-cuenta.sh` — arranca el asistente con un directorio de configuracion aislado por
cuenta, asi que todas las ventanas gastan la cuota de la elegida y las demas se quedan iniciadas en
reposo, a coste cero. No toca el llavero compartido, que es por donde dos ventanas rotando el mismo
token acaban revocando la sesion. Un alias mal escrito corta con error en vez de abrir en silencio
otra cuenta, que es justo lo que existe para evitar.

`cosecha/mantener-sesiones-claude.sh` — una cuenta que nadie usa pierde la sesion en unos dias
porque su credencial de refresco caduca. La renueva con la inferencia mas barata que existe (modelo
pequeno, sin herramientas, sin proyecto, sin persistencia) y solo cada varios dias. Se niega a tocar
dos alias que resulten ser la misma cuenta: dos sitios rotando la misma credencial es exactamente el
incidente que este guion intenta evitar.

`cosecha/reap-claude-orphans.sh` — mata las sesiones cuyo proceso padre ya murio y los servidores de
herramientas que dejaron colgando. Solo toca lo que quedo colgando del proceso inicial, asi que la
sesion viva nunca entra en el barrido. En una maquina con poca memoria esos restos llenan el
intercambio y provocan mas caidas, que dejan mas restos.

Distinto de preguntar por la cuota: aquello dice cuanta queda, esto decide de quien sale y evita que
la cuenta parada haya que reactivarla a mano el dia que hace falta.
