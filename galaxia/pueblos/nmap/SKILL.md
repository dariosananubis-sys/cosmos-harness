---
cosmos: pueblo
nombre: nmap
padre: ciberseguridad/ofensiva/reconocimiento
resumen: El escaner de puertos y huella de servicio de referencia; motor de red bajo nuclei/httpx.
---

https://github.com/nmap/nmap · NPSL (Nmap Public Source License) · 13.512★ · último push 2026-09-02 (comprobado 2026-09-03)

```bash
brew install nmap
```

```bash
# escaneo autorizado sobre el alcance del cliente, con deteccion de version de servicio
# actua solo dentro de un alcance con autorizacion explicita por escrito
nmap -sV 198.51.100.0/24

# top 1000 puertos + deteccion de SO, guardando en los 3 formatos
nmap -sV -O -oA informe-alcance 198.51.100.0/24
```

Es la capa que falta debajo de `nuclei` y `httpx`: esos hablan HTTP contra un objetivo ya
identificado, `nmap` es el que descubre qué puertos y servicios hay antes de eso — TCP/UDP,
huella de sistema operativo y de versión de servicio, con motor de scripts (NSE) para más de
600 comprobaciones. Sin él, un pentest de red no tiene con qué empezar: es el estándar de facto
desde hace 25 años y lo asumen la mayoría de guías y certificaciones ofensivas.

Gana a `masscan`/`rustscan` en profundidad, no en velocidad: aquellos barren los 65535 puertos de
rangos enteros en segundos porque no hacen casi nada más, `nmap` es varios órdenes de magnitud más
lento en el mismo barrido pero es el único de los tres con huella de servicio, detección de SO y
motor de scripts NSE. El patrón habitual es encadenarlos: `masscan`/`rustscan` para descubrir puertos
abiertos rápido en una red grande, `nmap -sV` después solo sobre esos puertos para identificar qué
corre en ellos.

Ojo: **alcance autorizado siempre** — escanear una red que no es tuya ni tienes permiso escrito
para auditar es, en la mayoría de jurisdicciones, un delito. `-sV` es más lento y más ruidoso
que un escaneo SYN plano (`-sS`): en un firewall con IDS puede disparar alertas o bloqueos. Un
puerto filtrado no es lo mismo que cerrado, y `nmap` no distingue siempre uno de otro sin
`-sA`. Contra redes grandes, limita con `--top-ports` o `-p` en vez de escanear los 65535 puertos.
