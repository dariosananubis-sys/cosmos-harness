---
cosmos: pueblo
nombre: codeql
padre: ciberseguridad/analisis/vulnerabilidades
resumen: Analisis de flujo de datos entre funciones y ficheros; gratis en repos publicos de GitHub.
---

https://github.com/github/codeql · MIT (queries y librerias QL) · 10.045★ · último push 2026-09-03 (comprobado 2026-09-03, `.../commits/HEAD.atom`)

```bash
brew install codeql
```

```bash
# crear la base de datos de un proyecto y correr el paquete de seguridad estandar
codeql database create basedatos-CODIGO --language=python --source-root RUTA/AL/PROYECTO
codeql database analyze basedatos-CODIGO codeql/python-queries --format=sarif-latest --output=resultados.sarif
```

Gana a `semgrep` en profundidad: `codeql` sigue el dato interprocedimental — de un parámetro de
entrada a través de varias funciones y ficheros hasta el `sink` peligroso (taint tracking real),
mientras que `semgrep` casa patrones sintácticos rápidos dentro de un ámbito más local. La
frontera es velocidad contra alcance: `semgrep` corre en segundos y sirve como gate de CI en cada
commit; `codeql` tarda minutos en construir la base de datos y encaja mejor en un análisis
programado o pre-release. En GitHub, además, es **gratis para repositorios públicos** vía code
scanning — para repos privados hace falta GitHub Advanced Security, que sí es de pago.

Ojo: la base de datos hay que reconstruirla si el código cambia mucho — no es incremental de
verdad entre commits muy distintos. Los `queries` que trae por defecto cubren los patrones
conocidos de cada lenguaje: un patrón de vulnerabilidad muy específico del dominio necesita una
query custom en QL, que tiene su propia curva de aprendizaje. Un hallazgo de flujo de datos exige
revisión manual antes de reportarlo — puede haber saneamiento intermedio que la query no reconoce.
