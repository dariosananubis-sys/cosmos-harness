---
cosmos: pueblo
nombre: context7
padre: documentos/referencia
resumen: Trae la documentacion vigente de una biblioteca en vez de fiarse de lo que el modelo recuerda.
---

https://github.com/upstash/context7 · MIT · 61.477★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp
claude mcp list                       # comprobar que conecta
# y para quitarlo cuando la sesion no lo necesita:
claude mcp remove context7
```

Uso, dos pasos, desde el propio agente: `resolve-library-id` con el nombre de la biblioteca
(`"next.js"`) devuelve su identificador (`/vercel/next.js`), y `query-docs` con ese identificador
trae la documentación vigente del tema que se pregunte.

Resuelve el fallo más caro al programar contra una biblioteca: **el patrón obsoleto que el modelo
aprendió hace dos versiones**. Se consulta antes de escribir, no después de que falle. Gana a
buscar en la web porque devuelve el fragmento de la documentación oficial de la versión, no un
artículo de blog de hace tres años que sale primero en el buscador.

Ojo, y es una decisión de presupuesto, no de calidad: como todo servidor de herramientas, **cuesta
contexto en cada sesión** por el mero hecho de estar conectado. Se deja conectado solo mientras se
usa. Ya está disponible en esta casa. Y la cobertura depende de que la biblioteca esté indexada:
para una interna o muy nueva no hay nada que traer, y ahí el resultado vacío se confunde con «no
existe esa API».
