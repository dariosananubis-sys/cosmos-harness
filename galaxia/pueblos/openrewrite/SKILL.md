---
cosmos: pueblo
nombre: openrewrite
padre: refactorizacion/transformacion
resumen: Migra un proyecto JVM entero con recetas que conocen los tipos y respetan formato y comentarios.
---

https://github.com/openrewrite/rewrite · Apache-2.0 · 3.688★ · push 2026-09-01 (comprobado 2026-09-01, v8.91.4)

```bash
# Maven, sin tocar el pom: se activa la receta desde la linea de ordenes
mvn -U org.openrewrite.maven:rewrite-maven-plugin:dryRun \
  -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-migrate-java:RELEASE \
  -Drewrite.activeRecipes=org.openrewrite.java.migrate.UpgradeToJava21
# el informe queda en target/rewrite/rewrite.patch; para aplicarlo:
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-migrate-java:RELEASE \
  -Drewrite.activeRecipes=org.openrewrite.java.migrate.UpgradeToJava21

# Gradle, con el plugin declarado en build.gradle
./gradlew rewriteDryRun
./gradlew rewriteRun
```

Es la unica pieza de este continente que **sabe de tipos**. Construye un arbol semantico sin
perdidas —con el classpath resuelto—, asi que una receta puede decir «cambia esta llamada solo
cuando el receptor es de verdad `java.util.List`», distinguirlo de otra clase que se llama igual, y
devolver el fichero con su formato original, sus comentarios y hasta sus espacios en blanco intactos.
Eso es lo que ninguna herramienta de patron sintactico puede prometer, y es la diferencia entre una
migracion de version que se revisa en una tarde y una que produce un diff imposible de leer.

**El coste de entrada es real y conviene decirlo antes de empezar**: no trabaja sobre texto, asi que
necesita que el proyecto **compile** y que sus dependencias se resuelvan enteras. Un repositorio que
no construye no se puede migrar con esto. La primera ejecucion descarga el arbol de dependencias
completo y, en un proyecto grande, tarda minutos y pide memoria de sobra (`MAVEN_OPTS=-Xmx4g` es
habitual); y escribir una receta propia no declarativa significa escribir un modulo Java con su
propio ciclo de compilacion. Para un cambio de una tarde no compensa; para subir de version un
monorepo de doscientos modulos, no hay alternativa seria.

Ojo: el catalogo maduro es **de la maquina virtual de Java**. Hay recetas para otros lenguajes, pero
mucho menos rodadas, y ahi el coste de entrada deja de compensar. `RELEASE` como version del
artefacto trae la ultima receta publicada, lo que hace la ejecucion **no reproducible** entre dos
dias distintos: para integracion continua se fija la version exacta. Y `dryRun` antes que `run`
siempre: el parche se lee, el arbol reescrito ya no.
