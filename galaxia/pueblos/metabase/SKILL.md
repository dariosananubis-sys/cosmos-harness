---
cosmos: pueblo
nombre: metabase
padre: analitica/cuadros-de-mando
resumen: Plataforma de BI con servidor: cualquiera hace su consulta sin escribir SQL, sobre datos ya cargados.
---

https://github.com/metabase/metabase · AGPL-3.0 fuera de enterprise/, comercial dentro · 49.068★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
docker run -d -p 3000:3000 --name metabase metabase/metabase
```

```sql
-- Metabase la genera desde su editor visual; esto es lo que ejecuta por debajo
SELECT categoria, date_trunc('month', fecha) AS mes, sum(importe) AS total
FROM ventas
GROUP BY 1, 2
ORDER BY 2 DESC;
```

Gana a `streamlit` y a `rill` cuando quien necesita el dato **no escribe código**: alguien de
ventas o dirección abre el navegador, arrastra columnas en el "question builder" y saca su propio
corte sin pedirle nada a nadie, y el resultado se guarda como panel compartido con permisos por
usuario. Pierde frente a los dos cuando el presupuesto de memoria del proceso anfitrión está
ajustado: es un servidor JVM permanente con su propia base de metadatos, mientras que `streamlit`
no añade proceso propio y `rill` es un solo binario con DuckDB dentro.

Ojo, dos cosas: la licencia es **doble** — AGPL-3.0 fuera del directorio `enterprise/`, comercial
dentro (SSO, permisos avanzados, white labeling quedan tras el muro de pago) — así que "Metabase
es gratis" es cierto solo para la edición Open Source. Y el peso es real, no un rumor: **corre
sobre JVM** con su propio proceso de arranque y su base de datos de aplicación (H2 por defecto,
Postgres recomendado en producción) — con la memoria del anfitrión ya repartida entre otros
procesos, ese servidor permanente es el primero en notarse.
