---
cosmos: pueblo
nombre: jscpd
padre: rendimiento/calidad
resumen: Encuentra bloques copiados con el mismo umbral en 224 formatos, asi que mide un monorepo entero de una vez.
---

https://github.com/kucherenko/jscpd · MIT · 6.092★ · push 2026-08-31 (comprobado 2026-09-01, v5.1.1)

```bash
brew install jscpd            # o: npm i -g jscpd@5   (v5 es un binario Rust, no necesita Node)

jscpd ./src

jscpd ./src --min-tokens 70 --reporters console,html \
  --ignore "**/node_modules/**,**/dist/**,**/*.min.*,**/migrations/**" \
  --threshold 5             # sale con codigo 1 si la duplicacion pasa del 5%
```

Tokeniza y busca coincidencias por huella (Rabin-Karp), asi que encuentra el bloque copiado aunque le
hayan cambiado los nombres de las variables y el espaciado. Su ventaja frente a `PMD CPD`, el otro
detector serio, es la **cobertura de formatos**: 224, con deteccion entre formatos distintos y un solo
informe, de modo que en un repositorio con backend en Python, frontend en TypeScript y guiones en Bash
sale un unico numero comparable en vez de tres herramientas con tres criterios.

Es lo que hace medible la parte de «no duplicar» del criterio de codigo: convierte una opinion sobre
el diseno en un porcentaje que se pone en integracion continua con `--threshold` y se ve subir o bajar
entre versiones.

Ojo: es **tokenizacion, no semantica**. Dos funciones que hacen exactamente lo mismo escritas de forma
distinta salen limpias, asi que un informe en verde no significa que no haya duplicacion — significa
que no hay copias literales. Al reves tambien falla: con `--min-tokens` bajo denuncia importaciones,
cabeceras de licencia, andamiaje repetido de pruebas y sobre todo **ficheros generados**, que son
duplicacion legitima; sin una lista de exclusiones cuidada el informe trae cientos de hallazgos falsos
y se deja de mirar a la semana. Se empieza por encima del valor por defecto (50 fichas) y se baja solo
si el ruido lo permite. Y hay **dos motores conviviendo**: la version 4 en TypeScript y la 5 reescrita
en Rust; comparten opciones y fichero de configuracion, pero la 5 no trae el almacen LevelDB ni la API
programable de Node, asi que un guion que dependa de eso necesita `jscpd@4` explicitamente.
