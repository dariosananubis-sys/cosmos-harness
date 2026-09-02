---
cosmos: pueblo
nombre: rpaframework
padre: automatizacion/escritorio
resumen: Automatiza aplicaciones de escritorio y ficheros de oficina como codigo versionado, no como aplicacion aparte.
---

https://github.com/robocorp/rpaframework · Apache-2.0 · 1.555★ · push 2026-08-29 (comprobado 2026-09-01)

```bash
pip install rpaframework

python - <<'PY'
from RPA.Excel.Files import Files
libro = Files()
libro.open_workbook("entrada.xlsx")
print(libro.read_worksheet(header=True)[:3])
libro.close_workbook()
PY
```

Gana a las suites de arrastrar y soltar de este terreno (UiPath, Power Automate Desktop, Automation
Anywhere), que son de pago o exigen desplegar su propia aplicación: aquí el proceso es un fichero
que entra en el repositorio, se revisa en una pull request y corre en integración continua. Trae
librerías para hoja de cálculo, PDF, correo, navegador y ventanas del sistema, así que cubre el
trabajo repetitivo de un programa que no tiene API y solo se deja llevar por su interfaz.

Ojo, dos avisos que deciden si vale o no: la automatización por interfaz es **frágil por
naturaleza** —un cambio de versión del programa mueve un botón y el guion falla—, así que se elige
solo cuando de verdad no hay API. Y el proyecto tiene 1.555 estrellas: es el menos respaldado de
este nicho, con la mayor parte del ecosistema empujando hacia la plataforma de pago de la misma
empresa. Antes de construir encima, comprobar que la librería concreta que se va a usar sigue viva.

A las tres de la mañana: no hay planificador ni reintento propios. Corre como un guion; lo que da
reintentos es ponerlo detrás de `celery` o como tarea de `windmill`, y lo que da diagnóstico es
guardar una captura de pantalla en el manejador de error — sin ella, un fallo de interfaz es
irreproducible.
