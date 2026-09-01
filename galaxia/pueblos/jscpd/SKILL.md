---
cosmos: pueblo
nombre: jscpd
padre: rendimiento/calidad
resumen: Encuentra bloques copiados con el mismo umbral en unos 150 formatos, asi que compara un monorepo entero.
---

https://github.com/kucherenko/jscpd · MIT · 6.092★ · push 2026-08-31 (comprobado 2026-09-01, v5.1.1)

```bash
npx jscpd .                                   # no hace falta instalarlo

npx jscpd --min-tokens 70 --reporters console,html \
  --ignore "**/node_modules/**,**/dist/**,**/*.min.*,**/migrations/**" \
  --threshold 5 src/                          # sale con codigo 1 si pasa del 5% duplicado
```

Tokeniza y busca coincidencias por huella (Rabin-Karp), asi que ve el bloque copiado aunque le hayan
cambiado los nombres de las variables y el espaciado. Su ventaja frente a `PMD CPD`, que es el otro
detector serio, es la **cobertura de formatos**: alrededor de ciento cincuenta, con el mismo umbral y
un solo informe, de modo que en un repositorio con backend en Python, frontend en TypeScript y
guiones en Bash sale un unico numero comparable en vez de tres herramientas con tres criterios.

Es la medida que hace accionable la parte de «no duplicar» del criterio de codigo: convierte una
opinion sobre el diseno en un porcentaje que se puede poner en integracion continua con `--threshold`
y ver subir o bajar entre versiones.

Ojo: es **tokenizacion, no semantica**. Dos funciones que hacen exactamente lo mismo escritas de
forma distinta salen limpias, asi que un informe en verde no significa que no haya duplicacion —
significa que no hay copias literales. Al reves tambien falla: con `--min-tokens` bajo denuncia
importaciones, cabeceras de licencia, andamiaje repetido de pruebas y sobre todo **ficheros
generados**, que son duplicacion legitima; sin una lista de exclusiones cuidada el informe trae
cientos de hallazgos falsos y se deja de mirar a la semana. Se empieza alto (70 fichas o mas) y se
baja solo si el ruido lo permite.
