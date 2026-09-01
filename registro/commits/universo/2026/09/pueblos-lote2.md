# Lote 2 — de prosa a herramienta: 47 pueblos reescritos

Fecha: 2026-09-01 · Árbol: `galaxia/` · Nichos: `agentes-ia` (20), `web` (15), `extraccion` (7),
`modelos-locales` (5). Contrato aplicado: [`spec/PUEBLO.md`](../../../../../spec/PUEBLO.md).

**Estado fijado** (el árbol muta mientras se escribe, hay tres agentes más en paralelo): base
`0b82242`, árbol sin commitear, **157 ficheros sucios** al cerrar. La configuración cambió *durante*
el trabajo: otro agente borró `galaxia.toml`, movió su contenido a `cosmos.toml` y creó
`ejemplo.toml` — los comandos de verificación de abajo son los que valen **después** de ese cambio.

## Lo que se hizo

**47 de 47 reescritos.** Se conservó el frontmatter íntegro (`cosmos`, `nombre`, `padre`, `resumen`)
y se sustituyó el cuerpo entero. Ningún `resumen` hubo que tocarlo: los 47 ya cumplían los 120
caracteres y distinguían de su vecino.

Cada cuerpo trae ahora las cinco cosas del contrato:

1. **URL literal** con licencia, estrellas y último push, **con la fecha de comprobación**
   (`comprobado 2026-09-01`).
2. **Comando de instalación** en bloque de código.
3. **Ejemplo mínimo copiable**, con marcadores explícitos (`<slug>`, `example.com`) y cero valores
   reales.
4. **Por qué este y no el rival**, con el rival nombrado y su cifra.
5. **Lo que no hace bien** — el aviso que evita el falso verde.

Medida antes / después sobre estos 47:

| | antes | después |
|---|---|---|
| url `http(s)` o ruta de fichero | 0/47 | **47/47** |
| bloque de código | 0/47 | **47/47** |
| comando de instalación / de uso | 0/47 | **47/47** |
| rival nombrado con cifra | parcial, sin cifras | **47/47** |
| apartado de avisos («ojo») | 0/47 | **47/47** |

## Verificación de datos: 49 repositorios en vivo

Cupo de `WebSearch` agotado, así que **todo** salió de `api.github.com` autenticada
(`repos/OWNER/REPO`), más `raw.githubusercontent.com` para los comandos de instalación y los
ejemplos de uso, el 2026-09-01. El token nunca se escribió a fichero ni se imprimió.

Se verificaron los 33 repositorios que son pueblo **y además los 16 rivales que se nombran**, porque
una comparación sin cifra del rival no informa (regla 4 del contrato). Hallazgos que cambiaron el
texto:

- **`sentence-transformers` se ha movido de organización**: ya no es `UKPLab/sentence-transformers`
  sino `huggingface/sentence-transformers` (19.055★, Apache-2.0). La ruta vieja redirige, pero
  confunde a quien audite la procedencia. Queda dicho en el pueblo.
- **`openclaw/openclaw` y `WordPress/agent-skills` y `woocommerce/agent-skills` devuelven
  `NOASSERTION`**: tienen fichero `LICENSE` pero GitHub no les asigna SPDX. Escrito como «licencia
  sin SPDX» y con el aviso de leer el fichero antes de redistribuir, en vez de inventar el
  identificador.
- **Rivales muertos o parados, con su fecha**, que es lo que hace defendible la elección:
  `dedupeio/dedupe` (2025-07-29), `imagemin/imagemin` (2025-03-07),
  `microsoft/autogen` (2026-04-15), `GoogleChrome/lighthouse-ci` (2026-03-27),
  `Automattic/wordpress-agent-skills` (2026-03-17), `Shopify/liquid-skills` (2026-03-18),
  `antlr/antlr4` (2026-02-16), `jina-ai/reader` (2026-05-22).
- **`elementor-mcp` no tenía URL ninguna**: se identificó el plugin real (EMCP Tools) leyendo la
  cabecera de `cosecha/wp-mcp-sync.py` (`emcp-tools-server`) y confirmándolo contra el README:
  https://github.com/msrbuilds/elementor-mcp · GPL-2.0 · 661★ · 2026-08-30 · PHP 8.1+ · **200+
  herramientas MCP**.

## Herramientas propias (`cosecha/`): 22 pueblos

Ahí la «URL» es la ruta del fichero y lo que importa es el comando de uso **real**, leído del propio
guion (docstring o bloque de uso), no supuesto. Los 22 apuntan a ficheros que existen hoy en
`cosecha/` — comprobado uno a uno. En cada uno se responde además la pregunta que justifica que
exista: por qué se prefiere a la alternativa pública (`codex exec` a pelo, `jq`, `screencapture` a
secas, el buscador de un registrador, `ssh <host> wp …`, el panel de WooCommerce, `/cost`…).

## Cosas que se corrigieron por el camino

- **`captura-recortada` describía mal una de sus dos herramientas.** Decía que
  `cosecha/foto-cuadrar.py` «recorta a la región exacta antes de meter la imagen en contexto». El
  docstring real del guion dice otra cosa: *«Re-encuadra una foto de producto a lienzo cuadrado sin
  costura visible»*. Es una herramienta de fotografía de producto, no de capturas. Se sacó del
  pueblo, se puso en su lugar el `screencapture -R` nativo (más barato y sin dependencias) y se dejó
  el aviso de no confundirlos. **`foto-cuadrar.py` queda sin pueblo**: su sitio natural es
  `web/imagenes`, junto a `sharp` y `rembg` — no se creó porque crear pueblos no entra en este
  encargo.
- **El error de `agentes-ia/coste` estaba en `research/HERRAMIENTAS-PROPIAS.md`**, que describe
  `foto-cuadrar.py` igual de mal («Recorta/encuadra capturas de pantalla a una región exacta»). No se
  tocó: está fuera del alcance de este lote. Queda anotado aquí para el que lo arregle.

## Avisos por nicho, según pedía el encargo

**`modelos-locales` (Mac de 8 GB).** Los 5 dicen si caben y con qué cuantización, en números:

| Pueblo | ¿Cabe en 8 GB? |
|---|---|
| `lancedb` | Sí, con holgura — y es **la razón de que gane**: no mantiene el índice en RAM |
| `sentence-transformers` | `all-MiniLM-L6-v2` (22M, ~90 MB) trivial · `BGE-M3` (~2,2 GB) cabe pero se lleva ¼ de la máquina |
| `mlx-lm` | ~3B en 4-bit con soltura · 7-8B en 4-bit (~4-4,5 GB) al límite · **>13B cuantizado no entra** |
| `ollama` | 7B `Q4_K_M` ≈ 4-4,5 GB, margen justo · 13B Q4 ≈ 7-8 GB, no recomendable con el sistema abierto |
| `lm-evaluation-harness` | El arnés es ligero; el coste es el modelo evaluado — mismas reglas |

**`agentes-ia`, servidores MCP y su coste de contexto.** Ninguno de los 20 es un servidor MCP (el más
cercano, `mcp-call`, es un *cliente* de un solo tiro, y ese es justo su argumento). Donde el número
manda se cita medido: `microsoft/playwright-mcp` = **71 herramientas permanentes**, que es la
justificación numérica de preferir `agent-browser` (**cero herramientas permanentes**, se invoca por
consola). En `web`, `elementor-mcp` sí es un servidor MCP y lleva el aviso más gordo del lote:
**200+ herramientas que se pagan en cada sesión mientras esté conectado**.

## Los que ya no merecían estar (no se han borrado)

1. **`web-fidelidad-elementor` — el guion no vive en este árbol.** Referencia una skill del arnés
   (`.claude/skills/web-fidelidad-elementor/SKILL.md`), no un fichero de `cosecha/` ni un repositorio
   público. `cosmos compilar` exporta el directorio del pueblo, así que en una máquina sin ese arnés
   el pueblo **promete algo que no entrega** — exactamente lo que prohíbe la última línea de
   `spec/PUEBLO.md`. Además el nombre **colisiona** con la skill real del arnés en `.claude/skills/`.
   Se ha reescrito con el aviso de procedencia en cabecera y con comandos de medición que sí se
   ejecutan (`agent-browser` + `scrollWidth`/`offsetParent`), pero la decisión de fondo —bajar el
   guion a `cosecha/` o retirar el pueblo— no es de este encargo.
2. **`a11y-auditoria-wcag` — el más parado de su nicho.** `masuP9/a11y-specialist-skills`: **56★ y
   último push 2026-06-13**, casi tres meses. Entra por mecanismo (paquete npm con guiones de
   Playwright reales) frente a un rival con 403★ que es sobre todo prosa, y esa sigue siendo la
   decisión correcta hoy — pero es el candidato número uno a caerse en la próxima revisión, y no hay
   sustituto vivo detectado. Anotado en el cuerpo del pueblo.
3. **`woocommerce-skills` — 9 estrellas y dos skills documentadas.** Se sostiene solo por ser la
   **única** fuente que documenta el contenedor de servicios y la Store API post-HPOS. Si aparece
   cobertura equivalente en la documentación oficial, deja de tener motivo. Anotado en el cuerpo.

Ninguno se borró: son avisos, no ejecuciones.

## Salida de la verificación

Los comandos del encargo usaban `--config galaxia.toml`, que **ya no existe** (otro agente lo movió a
`cosmos.toml` durante la tarea). Con el fichero ausente, `validar` cae a un presupuesto por defecto y
escupe **201 falsos `E19`** («vista plana desincronizada») que no son del contenido: son el choque de
dos árboles por el mismo `destino`, el bug de spec que el propio `galaxia.toml` documentaba en su
cabecera. Los comandos buenos hoy son sin `--config`:

```
$ python3 -m cosmos validar galaxia
COSMOS  rojo  2 errores

E17  agua/oceano-verificar.md
     solapamiento 45.5% entre mar/pruebas y oceano/verificar
E17  estrellas/web.md
     solapamiento 100.0% entre mar/accesibilidad y estrella/web
```

```
$ python3 -m cosmos medir galaxia
COSMOS  medir

  Entrada base .... 1.128 tokens
  Peor nicho ...... 1.771 tokens   (ciberseguridad, 26 pueblos)
  Agua condicional  817 tokens     (5 aguas por paths:, fuera de la entrada)
  Peor con agua ... 2.588 tokens
  Universo ........ 62.681 tokens
  Descarga ........ 97,2 %
  Presupuesto ..... 4.000     OK, quedan 1.412 tokens en el peor caso con agua
```

**Bajo presupuesto: sí** — 2.588 de 4.000 en el peor caso con agua, 1.412 de margen. Y confirma lo
que decía el contrato: los cuerpos escritos aquí engordaron el universo (60.983 → 62.681 tokens,
descarga 97,1 % → 97,2 %) **sin mover ni un token la entrada**, porque solo el `resumen` entra en el
catálogo.

**Verde: no del todo, y no por este lote.** Quedan 2 errores `E17` de solapamiento, los dos **fuera
del boundary de este encargo** (`agua/oceano-verificar.md` y `estrellas/web.md`; aquí solo se escribe
en pueblos de los cuatro nichos y en `registro/`). El de `estrellas/web.md` es del dominio web y es un
**100 % de solapamiento** con `mar/accesibilidad` —la misma frase literal en dos nodos co-cargables—,
así que se arregla dejándola en uno y referenciándola desde el otro. No se tocó: no es mío.

## Lo que no se pudo verificar

- **`explodinggradients/ragas`** devolvió `404` en la API: el repositorio ha cambiado de ruta o se ha
  retirado. Se eliminó de la comparación de `lm-evaluation-harness`, donde el barrido original lo
  citaba; en su lugar se nombra `promptfoo/promptfoo` (24.722★), sí verificado. **No se escribió el
  dato sin comprobar.**
- **El «57 % de los fallos de la norma» de `axe-core`** es una cifra que publica Deque, no una
  medición propia: va atribuida explícitamente («el dato honesto lo publica el propio proyecto»), no
  como hecho verificado aquí.
- **Nada de esto se instaló ni se ejecutó.** Los comandos de instalación y los ejemplos salen del
  README oficial de cada proyecto o del docstring del propio guion de `cosecha/`, leídos en vivo hoy;
  no se corrió ninguno. Es el mismo límite que ya declaraban los barridos de `research/`.
- **Las cifras de estrellas** son las que devuelve la API el 2026-09-01 y se toman tal cual: varias
  superan las 100k, muy por encima de ciclos anteriores, y sin herramienta de auditoría de estrellas
  no se puede descartar inflación.
