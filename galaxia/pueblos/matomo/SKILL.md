---
cosmos: pueblo
nombre: matomo
padre: visibilidad
resumen: Analitica en servidor propio: embudos y mapas de calor sin ceder un dato a un tercero.
---

https://github.com/matomo-org/matomo · GPL-3.0 · 21.828★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
cat > docker-compose.yml <<'YML'
services:
  db:
    image: mariadb:11
    environment:
      MARIADB_ROOT_PASSWORD: <CLAVE_ROOT>
      MARIADB_DATABASE: matomo
    volumes: [db:/var/lib/mysql]
  matomo:
    image: matomo:latest
    ports: ["8080:80"]
    volumes: [matomo:/var/www/html]
    depends_on: [db]
volumes: { db: {}, matomo: {} }
YML
docker compose up -d          # asistente de instalacion en http://localhost:8080

# comprobar por API que entran visitas (el testigo sale de Administracion > API)
curl -s "http://localhost:8080/index.php?module=API&method=VisitsSummary.get\
&idSite=1&period=day&date=today&format=json&token_auth=<TESTIGO_API>"
```

Cierra la mitad del hueco que la tanda anterior dejó declarado por custodia: **medir el tráfico real
sin entregar el acceso delegado de la propiedad del cliente a un servidor ajeno**. Gana a `Plausible`
y a `Umami`, los otros dos autoalojados, cuando hace falta lo que ellos deliberadamente no tienen:
embudos, mapas de calor, grabación de sesión y segmentación. Si solo hacen falta visitas y páginas
vistas, `Plausible` es más ligero y más honesto de mantener.

La otra mitad —el rendimiento **dentro del buscador**— sigue sin pueblo por el mismo motivo de
custodia; lo accionable de ahí lo cubre `search-console`.

Ojo: sin configurar el archivado por `cron`, Matomo procesa los informes durante la petición del
navegador y el panel se arrastra en cuanto hay tráfico. Es el fallo de rendimiento clásico y se
arregla con una tarea programada de `core:archive`. Y su modo de consentimiento **no es automático**:
para no necesitar banner hay que activar la anonimización de IP y desactivar cookies explícitamente
en la configuración; instalarlo tal cual no lo hace conforme por sí solo.
