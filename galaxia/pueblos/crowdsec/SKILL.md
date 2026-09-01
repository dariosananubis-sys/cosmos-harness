---
cosmos: pueblo
nombre: crowdsec
padre: ciberseguridad/defensiva/deteccion
resumen: Bloquea por comportamiento y comparte las firmas entre instalaciones, no solo por IP.
---

https://github.com/crowdsecurity/crowdsec · MIT · 14.704★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
# no hay fórmula de Homebrew: se instala en el servidor que se defiende
curl -s https://install.crowdsec.net | sudo sh
sudo apt install crowdsec crowdsec-firewall-bouncer-iptables
```

```bash
# qué escenarios y qué analizadores están cargados
sudo cscli hub list

# añadir la colección de un servicio concreto y recargar
sudo cscli collections install crowdsecurity/nginx
sudo systemctl reload crowdsec

# qué ha decidido: alertas vistas y bloqueos vigentes
sudo cscli alerts list
sudo cscli decisions list

# levantar un bloqueo puesto por error
sudo cscli decisions delete --ip 203.0.113.10
```

Sustituye al bloqueador clásico por intentos fallidos (`fail2ban`) añadiendo dos cosas: decide por
**escenario de comportamiento** en vez de por conteo de líneas, y comparte las firmas entre
instalaciones, así que una dirección que ya atacó a otro llega bloqueada. Frontera con la vigilancia
de infraestructura (`infraestructura/uptime-kuma`): allí se comprueba que el servicio responde, aquí
quién está llamando y con qué intención.

Ojo: el motor detecta, pero **quien bloquea es el «bouncer»** — instalar solo `crowdsec` deja un
sistema que observa y no corta, y el panel se ve igual de lleno. Segundo aviso: la inteligencia
compartida implica **enviar señales de tus alertas** a su servicio central; es opcional y se puede
correr en local, pero es una decisión de datos que se declara antes de ponerlo en un servidor de
cliente. Y un escenario mal afinado bloquea a un usuario legítimo: probar en `--simulation` primero.
