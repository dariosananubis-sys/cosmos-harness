---
cosmos: pueblo
nombre: acceso-remoto
padre: infraestructura/servidores
resumen: Vigila y vuelve a levantar el acceso remoto de la maquina, porque la que se queda sin el no puede pedir ayuda.
---

`cosecha/acceso-remoto-watchdog.sh` — comprueba cada pocos minutos consola remota, pantalla
compartida y red privada, y los reactiva si se han caido.

No es lo mismo que `uptime-kuma`, y por eso entran los dos: aquel mira desde fuera y avisa, este
repara desde dentro. Si lo que se cae es justo el canal por el que entrarias a arreglarlo, el aviso
llega y no sirve de nada.

Trae documentado el enredo que cuesta una tarde: una red privada con consola propia puede quedarse
con el puerto de la consola del sistema, de modo que el servicio figura como levantado y aun asi no
se puede entrar por el camino de siempre.
