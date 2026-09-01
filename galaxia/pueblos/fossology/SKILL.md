---
cosmos: pueblo
nombre: fossology
padre: cumplimiento/licencias
resumen: El mismo cumplimiento con base de datos e interfaz para la revision humana del abogado.
---

https://github.com/fossology/fossology · GPL-2.0 · 1.024★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
docker run -d --name fossology -p 8081:80 fossology/fossology
# http://localhost:8081/repo — usuario fossy, contrasena fossy (CAMBIARLA en el primer acceso)

# o con base de datos aparte, que es lo sensato para un expediente que se guarda anos
curl -fsSL https://raw.githubusercontent.com/fossology/fossology/master/docker-compose.yml \
  -o docker-compose.yml && docker compose up -d
```

Empata de verdad con `ort` y por eso entran los dos, con la frontera escrita: **consola dentro de la
tubería allí, expediente revisable a mano aquí**. Este tiene base de datos, interfaz y flujo de
revisión con decisiones firmadas por persona, que es lo que un abogado necesita para dar por buena
una licencia dudosa — y lo que ninguna herramienta de línea de comandos produce. Gana a `scancode`
(el escáner suelto que usa por dentro medio ecosistema) precisamente por eso: `scancode` escupe
hallazgos, este guarda quién decidió qué y cuándo.

**Norma que cubre**: no es una norma legal sino cumplimiento contractual de licencias de software
libre. Emite en formato **SPDX** (2.3 y superiores) y su flujo está alineado con **OpenChain
ISO/IEC 5230**, que es el estándar que piden los clientes grandes al subcontratar. Territorio:
ninguno en concreto; la licencia obliga igual en todas partes.

**Lo que NO comprueba**: patentes, marcas, exportación de criptografía ni cláusulas de contrato
propias del cliente. Y no detecta código copiado sin cabecera de licencia: si nadie escribió la
licencia en el fichero, aquí sale como desconocido, no como infracción.

Ojo: la imagen de un solo contenedor lleva PostgreSQL dentro y **viene con credenciales por defecto
publicadas**. Vale para probar; para un expediente que se conserva años, base de datos aparte,
contraseña cambiada y el servicio nunca expuesto a internet.
