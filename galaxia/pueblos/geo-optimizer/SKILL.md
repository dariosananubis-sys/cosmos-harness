---
cosmos: pueblo
nombre: geo-optimizer
padre: visibilidad
resumen: Comprueba si los buscadores con IA pueden leerte y citarte, y si sus rastreadores tienen paso.
---

https://github.com/Auriti-Labs/geo-optimizer-skill · MIT · 749★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
pip install geo-optimizer-skill        # o sin instalar: uvx --from geo-optimizer-skill geo ...

geo audit --url https://ejemplo.test
geo audit --sitemap https://ejemplo.test/sitemap.xml --max-urls 25
geo llms --base-url https://ejemplo.test --output ./public/llms.txt
geo schema --type faq --url https://ejemplo.test
geo diff --before https://ejemplo.test/pagina-vieja --after https://ejemplo.test/pagina-nueva

# y como servidor de herramientas del agente:
pip install 'geo-optimizer-skill[mcp]' && claude mcp add geo-optimizer -- geo-mcp
```

Especialista dedicado al eje de respuesta generativa: extractabilidad del texto, densidad de hechos,
bloques de respuesta, fichero de permisos para modelos (`llms.txt`) y **acceso real de los rastreadores
de IA**. Frontera con `claude-seo-ai`: allí el eje clásico de indexación y marcado, aquí el de ser
citado por un modelo. No compiten, se suman.

Ojo de coste, y es una regla dura de esta casa: **la verificación de menciones reales (`geo
citations`, `geo snapshots`) llama a modelos de pago por uso**. No se usa. Todo lo del bloque de
arriba funciona sin clave y sin gasto; en cuanto una orden pida un proveedor, se para y se pregunta.

Ojo de fondo: lo que mide es **si te pueden leer y citar**, que es una hipótesis razonable, no una
señal confirmada por ningún buscador con IA. No hay documentación oficial que diga que un `llms.txt`
mejora la citación; es una convención emergente. Se usa como higiene, no como promesa — y desde luego
no se le vende a un cliente como posicionamiento garantizado.
