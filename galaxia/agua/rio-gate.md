---
cosmos: rio
nombre: gate
moja: []
invoca: python3 -m puente.gate
resumen: Verifica lo que se va a commitear, no lo que hay suelto en disco.
---

Es lo que corre en cada commit local una vez instalado el enganche. La diferencia importa:
comprobar el arbol de trabajo aprueba cambios que no entran en el commit y rechaza otros que si.

`--sin-pruebas` deja fuera las suites cuando solo interesa la estructura.
