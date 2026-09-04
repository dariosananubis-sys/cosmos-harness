---
cosmos: pueblo
nombre: httpx
padre: ciberseguridad/ofensiva/reconocimiento
resumen: Sondeo HTTP masivo (vivo, titulo, tecnologia, codigo) sobre listas de hosts de subfinder.
---

https://github.com/projectdiscovery/httpx · MIT · 10.347★ · último push 2026-09-01 (comprobado 2026-09-03)

```bash
brew install httpx
```

```bash
# comprobar cuales de una lista de hosts del alcance sirven HTTP, con titulo y tecnologia detectada
subfinder -d objetivo-del-alcance.example -silent | httpx -title -tech-detect -status-code

# sondeo directo de un rango, guardando solo lo que responde 200
httpx -l objetivos-del-alcance.txt -mc 200 -o vivos.txt
```

Es el enlace entre `subfinder` (que entrega nombres) y `nuclei` (que necesita objetivos vivos
para escanear): sin él, una lista de miles de subdominios se escanea entera aunque la mayoría no
sirvan HTTP, desperdiciando tiempo y ruido. Gana a un bucle de `curl` en que resuelve en paralelo
miles de hosts, sigue redirecciones, detecta tecnología (CMS, servidor, framework) y saca
capturas de pantalla opcionales, todo en una sola pasada.

Ojo: un host que no responde no significa que esté caído — puede estar filtrando por
`User-Agent`, por IP de origen, o solo aceptar HTTPS con SNI concreto. La detección de tecnología
(`-tech-detect`) es por huella (cabeceras, cookies, rutas conocidas) y da falsos negativos con
stacks poco comunes o mal configurados a propósito. A concurrencia alta contra un solo dominio
puede leerse como un escaneo agresivo por el WAF del cliente.

Ojo de nombre: `pip install httpx` NO instala esto — instala `encode/httpx`, el cliente HTTP async de
Python, otra herramienta. Este `httpx` se instala con `brew install httpx` o
`go install github.com/projectdiscovery/httpx/cmd/httpx@latest`.
