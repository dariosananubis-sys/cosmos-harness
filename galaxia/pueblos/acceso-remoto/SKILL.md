---
cosmos: pueblo
nombre: acceso-remoto
padre: infraestructura/servidores
resumen: Vigila y vuelve a levantar el acceso remoto de la maquina, porque la que se queda sin el no puede pedir ayuda.
---

`scripts/acceso-remoto-watchdog.sh` — herramienta propia, no hay repositorio público. La ruta ES la
referencia.

```bash
sudo install -m 755 scripts/acceso-remoto-watchdog.sh /usr/local/sbin/
sudo /usr/local/sbin/acceso-remoto-watchdog.sh          # una pasada, a mano
sudo tail -f /var/log/acceso-remoto-watchdog.log

# cada 5 minutos, como demonio del sistema
sudo launchctl bootstrap system /Library/LaunchDaemons/<tu-etiqueta>.acceso-remoto-watchdog.plist
```

Comprueba consola remota, pantalla compartida y red privada, y **los reactiva** si se han caído:
una actualización del sistema, un cambio en Compartir o un reinicio de energía los apagan sin avisar.

No es lo mismo que `uptime-kuma`, y por eso entran los dos: aquel mira desde fuera y avisa, este
repara desde dentro. Si lo que se cae es justo el canal por el que entrarías a arreglarlo, el aviso
llega y no sirve de nada. Y se prefiere a un `cron` con `systemctl restart` porque comprueba el
puerto de verdad (`nc -z` contra 127.0.0.1) antes de tocar nada, en lugar de reiniciar servicios
sanos cada cinco minutos.

Ojo, y es el enredo que cuesta una tarde: **una red privada con consola propia puede quedarse con el
puerto de la consola del sistema**. El servicio figura como levantado, el guion lo ve vivo, y aun así
no se puede entrar por el camino de siempre. Si el acceso falla con el vigilante en verde, mirar qué
proceso tiene el puerto 22 antes de mirar el servicio.

Y el aviso de siempre: esto reactiva el acceso, no lo protege. Un demonio que vuelve a abrir la
consola remota cada cinco minutos es también un demonio que impide cerrarla — desactivarlo antes de
retirar una máquina.
