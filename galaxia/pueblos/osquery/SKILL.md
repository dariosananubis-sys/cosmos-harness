---
cosmos: pueblo
nombre: osquery
padre: ciberseguridad/defensiva/deteccion
resumen: Convierte el sistema operativo en una base SQL consultable: procesos, red, usuarios, ficheros.
---

https://github.com/osquery/osquery · Apache-2.0 o GPL-2.0 (a elegir) · 23.537★ · último push 2026-08-25 (comprobado 2026-09-03)

```bash
brew install osquery
```

```bash
# pegado tal cual en una terminal: entra a osqueryi, corre las dos consultas y sale
osqueryi <<'SQL'
SELECT pid, name, cmdline FROM processes WHERE on_disk = 0;   -- procesos sin binario en disco
SELECT * FROM listening_ports WHERE port = 4444;               -- quien escucha en ese puerto
SQL
```

```bash
# la misma consulta sin entrar a la consola, para un guion o un cron
osqueryi --json "SELECT pid, name, cmdline FROM processes WHERE on_disk = 0;"
```

Ocupa el hueco de detección que no cubre ninguna herramienta ofensiva de este nicho: expone
procesos, conexiones de red, usuarios, paquetes instalados, claves de arranque y cientos de tablas
más como si fueran filas SQL, así que una consulta detecta en segundos lo que a mano llevaría
recorrer varios comandos del sistema por host. Con `osqueryd` corre en segundo plano y programa
esas consultas (`scheduled queries`) para vigilancia continua en flota, con los resultados
exportables a un SIEM.

Gana a `auditd` (el registro de auditoría nativo del kernel Linux) en que el mismo lenguaje SQL
consulta estado vivo del sistema entero —red, paquetes, usuarios— y no solo el registro de eventos
que `auditd` decide grabar según sus reglas; pierde en que `auditd` es más ligero y ya viene en el
kernel, sin agente aparte que desplegar. Frente a una plataforma de detección completa como
`wazuh` o `velociraptor` —que además correlacionan, alertan y responden—, `osquery` es la pieza de
**consulta**: varias de esas plataformas lo usan por dentro como motor de recolección.

Ojo: es un **agente que hay que desplegar en cada máquina** — no analiza nada de forma remota ni
pasiva, así que sin agente instalado no hay visibilidad. Una consulta mal escrita en una tabla que
recorre todo el disco (`file` sin `WHERE` acotado) puede ser lenta y pesada en un host con muchos
ficheros. No es un IDS: detecta lo que le preguntas explícitamente, no genera alertas por sí solo
sin configurar reglas y un sistema que las evalúe (rsyslog, un SIEM, o `osquery`'s propio decorador).
