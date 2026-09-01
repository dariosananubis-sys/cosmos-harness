# Conocimiento — documentación, formación e investigación

Barrido GitHub para COSMOS, nicho 20 (`conocimiento`). Cubre: generación de documentación desde el
código, sitios de documentación, diagramas como código, documentación de API desde el esquema,
material de formación, gestión de conocimiento/notas enlazadas, y verificación de fuentes.

**Método**: API de GitHub autenticada (`search/repositories` + `repos/{owner}/{repo}`), cupo de
WebSearch agotado. Fecha del barrido: 2026-09-01. Toda cifra fue confirmada en vivo esa fecha
(estrellas, licencia, `archived`, `pushed_at`); lo que no, va marcado `NO VERIFICADO`.

**Criterio propio del encargo**: prioridad a lo que **se genera desde la fuente** (docs desde el
código, diagramas desde texto) sobre lo que se escribe a mano — lo escrito a mano se desincroniza,
lo generado no puede.

---

## De primera

1. **[squidfunk/mkdocs-material](https://github.com/squidfunk/mkdocs-material)** — 27.4k★, MIT,
   `pushed_at` 2026-08-30. **Por qué gana**: es el combo generador+tema de facto para documentación
   técnica desde Markdown — versionado (`mike`), búsqueda instantánea, i18n, modo oscuro y decenas de
   extensiones (admonitions, tabs, diagramas) sin escribir HTML. Motor de plugins de Python maduro y
   el estándar que otros temas (`sphinx-material`, `zensical`) imitan explícitamente.

2. **[facebook/docusaurus](https://github.com/facebook/docusaurus)** — 66.1k★, MIT, `pushed_at`
   2026-08-31. **Por qué gana su hueco**: cuando la documentación necesita componentes React
   interactivos (MDX) además de páginas estáticas, o versionado multi-release de un producto grande —
   terreno donde MkDocs se queda corto. Mantenido por Meta, con el ecosistema de plugins más grande
   del hueco React-based.

3. **[rust-lang/mdBook](https://github.com/rust-lang/mdBook)** — 22.1k★, MPL-2.0, `pushed_at` de
   hoy. **Por qué gana**: la vía más ligera para convertir una carpeta de Markdown en un "libro" web
   navegable — sin Node.js, un solo binario Rust. Gana cuando el requisito es simplicidad radical
   (documentación técnica larga y lineal, tipo manual), no un sitio con features de producto.

4. **[mermaid-js/mermaid](https://github.com/mermaid-js/mermaid)** — 90.0k★, MIT, `pushed_at` de
   hoy. **Por qué gana**: diagramas desde texto embebido directamente en Markdown — soportado
   nativamente por GitHub, GitLab, Obsidian y por los propios Artifacts de Claude (sin librería que
   cargar). Es la opción por defecto cuando el diagrama vive junto al texto que lo explica.

5. **[d2lang/d2](https://github.com/d2lang/d2)** — 25.1k★, MPL-2.0, `pushed_at` 2026-08-31. **Por
   qué gana su hueco**: cuando el diagrama es de arquitectura compleja con muchos nodos, D2 tiene
   auto-layout notablemente mejor que Mermaid y una sintaxis más legible a mano. Empatan de verdad
   con Mermaid en objetivo — se usa Mermaid si el diagrama vive dentro de Markdown/chat, D2 si es un
   diagrama de arquitectura autónomo que hay que mantener a largo plazo.

6. **[mingrammer/diagrams](https://github.com/mingrammer/diagrams)** — 42.6k★, MIT, `pushed_at`
   2026-08-16. **Por qué gana**: único de su hueco con **iconos oficiales** de AWS/GCP/Azure/K8s —
   dibuja diagramas de arquitectura cloud como código Python, exportando PNG/SVG. Ni Mermaid ni D2
   tienen ese catálogo de iconos; se elige `diagrams` específicamente para infraestructura cloud.

7. **[OpenAPITools/openapi-generator](https://github.com/OpenAPITools/openapi-generator)** — 26.7k★,
   Apache-2.0, `pushed_at` de hoy. **Por qué gana**: genera documentación **y** clientes SDK **y**
   stubs de servidor desde un único esquema OpenAPI — es la pieza que hace que "documentación de API"
   y "código de API" nunca diverjan, el criterio central de este nicho aplicado de forma literal.

8. **[requarks/wiki](https://github.com/requarks/wiki)** (Wiki.js) — 28.8k★, AGPL-3.0, `pushed_at`
   2026-08-30. **Por qué gana**: wiki de equipo autohospedada más completa y activa — edición
   colaborativa en tiempo real, control de acceso granular, y puede respaldar el contenido en Git
   (Markdown versionado, no una base de datos opaca).

9. **[TriliumNext/Trilium](https://github.com/TriliumNext/Trilium)** — 37.7k★, AGPL-3.0,
   `pushed_at` de hoy. **Por qué gana su hueco**: para "notas enlazadas" personales (el ángulo
   Zettelkasten/segundo cerebro) frente a Wiki.js orientado a equipo — árbol de notas jerárquico con
   enlaces cruzados, cifrado por nota, y motor de scripting propio. Continuación activa de
   TriliumNext tras el parón del proyecto original.

10. **[structurizr/structurizr](https://github.com/structurizr/structurizr)** — 369★, Apache-2.0,
    `pushed_at` 2026-06-29. **Por qué gana**: herramienta oficial del propio creador del modelo C4
    (Simon Brown) — "modelos como código" que generan diagramas de arquitectura de software en
    varios niveles de zoom desde una única fuente de verdad DSL, evitando el diagrama de arquitectura
    que nadie actualiza tras el primer sprint.

---

## Segunda fila

- **[BookStackApp/BookStack](https://github.com/BookStackApp/BookStack)** — 19.0k★, MIT, `pushed_at`
  de hoy (gestionado ahora en Codeberg, el repo de GitHub es espejo). Wiki jerárquica
  libros/capítulos/páginas, muy pulida para manuales internos; alternativa a Wiki.js cuando se
  prioriza estructura tipo libro sobre edición colaborativa en vivo.
- **[outline/outline](https://github.com/outline/outline)** — 40.4k★, `NOASSERTION` — **ojo**: es
  código fuente disponible bajo licencia tipo BSL, no OSI puro; el auto-hospedaje para uso interno
  suele estar permitido pero no revenderlo como servicio. Verificar la licencia exacta antes de
  adoptarlo si hay dudas de uso comercial.
- **[Redocly/redocly-cli](https://github.com/Redocly/redocly-cli)** — 1.5k★, MIT. Linter/validador
  de OpenAPI + generador de documentación bonita — complementa a `openapi-generator` en la parte de
  validar el esquema antes de generar nada desde él.
- **[yuzutech/kroki](https://github.com/yuzutech/kroki)** — 4.3k★, MIT. Servidor único que renderiza
  Mermaid, D2, PlantUML, Graphviz y ~20 lenguajes de diagrama más desde una sola API — útil cuando un
  proyecto mezcla varios DSL de diagramas y no se quiere instalar un renderer por cada uno.
- **[vuejs/vitepress](https://github.com/vuejs/vitepress)** — 18.3k★, MIT. Generador de sitios
  estáticos Vite+Vue, más rápido de compilar que Docusaurus para documentación de proyectos del
  ecosistema Vue.
- **[TypeStrong/typedoc](https://github.com/TypeStrong/typedoc)** (8.5k★) y
  **[jsdoc/jsdoc](https://github.com/jsdoc/jsdoc)** (15.5k★) — generadores de documentación de API
  desde comentarios/tipos del propio código fuente TypeScript/JavaScript.
- **[sphinx-doc/sphinx](https://github.com/sphinx-doc/sphinx)** — 8.0k★, el generador clásico de
  Python (usado por la propia documentación de Python), ganador cuando el proyecto ya es Python y
  necesita `autodoc` (documentación extraída de docstrings).
- **[terraform-docs/terraform-docs](https://github.com/terraform-docs/terraform-docs)** — 4.8k★,
  MIT. Genera documentación de módulos Terraform desde el propio `.tf` — mismo principio "desde la
  fuente" aplicado a infraestructura como código.

## Humo

- **[docsifyjs/docsify](https://github.com/docsifyjs/docsify)** (31.5k★) — genera el sitio de docs
  en el navegador en tiempo de carga, sin build; útil para documentación muy pequeña sin pipeline CI.
- **[zensical/zensical](https://github.com/zensical/zensical)** (5.6k★) — generador de sitio
  estático nuevo del mismo equipo de Material for MkDocs, más joven.
- **[soulspace-org/overarch](https://github.com/soulspace-org/overarch)** (298★) — modelo de datos
  para arquitectura de software con generación C4/UML vía PlantUML, alternativa Clojure a Structurizr.
- **[d2lang/d2-obsidian](https://github.com/d2lang/d2-obsidian)** (311★) — plugin oficial de D2 para
  Obsidian (relevante porque `notes/` de este mismo workspace es una vault Obsidian).
- **[qiobn/zotero-research-assistant](https://github.com/qiobn/zotero-research-assistant)** (12★) —
  MCP para Zotero con búsqueda semántica y expansión de red de citas; muy joven.

## Verificación de fuentes — hueco débil, con transparencia

Los únicos hallazgos directos de "citation verification" son proyectos de investigación muy
recientes y con pocas estrellas: **kirinccchang/citereview** (19★, detección de autoridades
alucinadas en escritura legal) y **rpatrik96/hallmark** (12★, benchmark de alucinación de citas en
papers ML, 2.525 entradas). Ninguno tiene la madurez para "de primera"; se documentan aquí porque son
lo único que existe hoy en GitHub que **mide** alucinación de citas en vez de solo advertir sobre
ella — vigilar en 3 meses.

---

## Mapeo a COSMOS

```
sistema-solar  conocimiento
├── continente  generacion-desde-la-fuente
│   ├── pais  sitios-de-documentacion   mkdocs-material · docusaurus · mdbook · vitepress
│   └── pais  api-desde-esquema         openapi-generator · redocly-cli · sphinx · typedoc · jsdoc
├── continente  diagramas-como-codigo
│   ├── pais  texto-a-diagrama          mermaid · d2 · kroki
│   └── pais  arquitectura-como-codigo  diagrams (mingrammer) · structurizr · overarch
├── continente  conocimiento-y-notas
│   ├── pais  wikis-de-equipo           wiki.js · bookstack · outline (licencia a revisar)
│   └── pais  notas-enlazadas           trilium
├── continente  verificacion-de-fuentes   ← inmaduro, sin ganador todavía
│   └── pais  deteccion-de-alucinacion  citereview · hallmark
└── continente  codigo-conocimiento     ← el código propio del nicho
       provincias: plugins/temas a medida sobre mkdocs-material o docusaurus, generadores
       propios de diagramas desde datos de COSMOS (p. ej. el árbol de nichos de este mismo
       documento como D2/Mermaid), extractores de docstrings o de esquema propios cuando el
       generador estándar no cubre un formato del cliente
```

## Lo que falta

- **Verificación de fuentes** es el hueco más débil de los tres nichos barridos hoy: nada maduro,
  vivo y self-hosted que verifique una cita contra la fuente real (no solo detecte alucinación en
  un benchmark). Si aparece algo con tracción real, revisar.
- **Material de formación generado desde código** (turn a codebase into a course/tutorial
  automáticamente): no apareció ningún proyecto de este tipo con tracción en las consultas hechas;
  posible hueco genuino o consulta insuficiente — revisar con términos más específicos si se vuelve
  prioritario.
- La licencia de `outline/outline` necesita lectura explícita del fichero `LICENSE` antes de
  adoptarlo (GitHub no detectó SPDX estándar) — no se ha verificado en este barrido si el
  autohospedaje interno sin reventa está permitido sin restricción.
