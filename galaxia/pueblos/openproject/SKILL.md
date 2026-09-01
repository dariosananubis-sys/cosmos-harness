---
cosmos: pueblo
nombre: openproject
padre: automatizacion/proyectos
resumen: Proyectos, hitos y horas imputadas con API completa y sin partes de pago.
---

https://github.com/opf/openproject · GPL-3.0 · 15.986★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
docker run -d --name openproject -p 8080:80 \
  -e OPENPROJECT_SECRET_KEY_BASE=<CADENA_ALEATORIA_64_HEX> \
  -v "$PWD/op-pgdata:/var/openproject/pgdata" \
  -v "$PWD/op-assets:/var/openproject/assets" \
  openproject/openproject:16

# listar tareas por la API v3 (usuario literal 'apikey', contraseña = la clave)
curl -s -u apikey:<CLAVE_API> "http://localhost:8080/api/v3/work_packages?pageSize=5"
```

Gana a `Redmine` (del que desciende) por API v3 coherente y partes de horas de serie, y a `Taiga`
por tener presupuesto e imputación de horas sin edición de pago. Es la única del barrido cuyo núcleo
está entero bajo licencia libre: los planes de pago añaden módulos, no desbloquean lo básico.

Frontera con el de al lado: en `twenty` vive el cliente antes de vender, aquí el trabajo después de
vender.

Ojo: el contenedor único mete PostgreSQL dentro. Vale para una instalación pequeña, pero la copia de
seguridad hay que hacerla del volumen `op-pgdata` con `pg_dump` desde dentro — copiar el directorio
en caliente da una base corrupta. Para algo serio, base de datos aparte.
