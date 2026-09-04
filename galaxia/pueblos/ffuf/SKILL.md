---
cosmos: pueblo
nombre: ffuf
padre: ciberseguridad/ofensiva/reconocimiento
resumen: Fuzzer HTTP rapido en Go para directorios, parametros, vhosts y subdominios.
---

https://github.com/ffuf/ffuf · MIT · 16.629★ · último push 2026-08-20 (comprobado 2026-09-03)

```bash
brew install ffuf
```

```bash
# descubrimiento de directorios/ficheros sobre un objetivo del alcance
# actua solo dentro de un alcance con autorizacion explicita por escrito
ffuf -u https://OBJETIVO-DEL-ALCANCE/FUZZ -w wordlist.txt -mc 200,301,302

# fuzzing de virtual hosts por cabecera Host
ffuf -u https://OBJETIVO-DEL-ALCANCE/ -H "Host: FUZZ.objetivo-del-alcance" -w subdominios.txt -fs 0
```

Gana a `gobuster` en velocidad y flexibilidad: su motor en Go concurrente satura el objetivo
mucho antes, y el marcador `FUZZ` funciona en cualquier parte de la petición (URL, cabecera,
cuerpo, cookie), no solo al final de la ruta — así sirve igual para directorios, parámetros
GET/POST, subdominios y vhosts con la misma herramienta. Frontera con `subfinder`: aquí se fuerza
por diccionario contra un objetivo ya conocido, allí se descubren subdominios por fuentes
pasivas sin tocar el objetivo.

Ojo: a concurrencia alta (`-t`) puede tumbar un servicio frágil o disparar el WAF — bajar `-t` y
usar `-rate` en producción de cliente. Un wordlist genérico da muchos falsos negativos en rutas
poco comunes: la calidad del hallazgo depende del wordlist, no solo de la herramienta. Filtra
siempre por tamaño/código (`-fs`, `-mc`) o el ruido de páginas 200 genéricas ahoga el resultado.
