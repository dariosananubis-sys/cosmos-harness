---
cosmos: pueblo
nombre: sqlmap
padre: ciberseguridad/ofensiva/explotacion
resumen: Detecta e inyecta SQL solo, identifica el motor y escala a la base entera.
---

https://github.com/sqlmapproject/sqlmap · GPL-2.0 (leído en `LICENSE`; la API de GitHub la reporta como `NOASSERTION`) · 38.336★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install sqlmap
```

```bash
# un solo objetivo del alcance; enumerar, sin volcar de más
sqlmap -u "https://OBJETIVO-DEL-ALCANCE/item?id=1" --batch --dbs

# confirmada la inyección, solo la estructura de una tabla
sqlmap -u "https://OBJETIVO-DEL-ALCANCE/item?id=1" --batch \
  -D nombre_bd -T usuarios --columns
```

No tiene rival cercano en su hueco concreto y lleva veinte años vivo: detecta la técnica de inyección
(booleana, por tiempo, por error, UNION, apilada), identifica el motor y, cuando el motor lo permite,
escala hasta shell del sistema. Frente al escaneo genérico de `zaproxy`, esto es el especialista que
se lanza cuando ya hay un parámetro sospechoso.

Ojo: se lanza contra **un objetivo del alcance** y con volcado limitado. `--dump-all` sobre una base
de producción es exfiltración de datos personales — sacar la base entera casi nunca hace falta para
demostrar la vulnerabilidad, y en un encargo con datos de terceros puede ser ilegal aunque el pentest
esté autorizado. Y sus opciones de toma del sistema operativo (`--os-shell`, `--os-pwn`) escriben en
el objetivo: fuera del alcance explícito, no se tocan.
