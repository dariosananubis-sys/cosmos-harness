# Pueblos lote 3 — de prosa a herramienta usable: 7 nichos, 56 pueblos

Fecha: 2026-09-01 · Árbol: `galaxia/` · Nichos: `automatizacion` (11), `infraestructura` (9),
`documentos` (9), `rendimiento` (8), `visibilidad` (7), `saas` (6), `cumplimiento` (6).
Continuación de [`pueblos-lote1.md`](pueblos-lote1.md): mismo contrato, mismo estilo.

Contrato aplicado, el de `spec/PUEBLO.md`: cada cuerpo trae ahora (1) URL literal del repositorio
con licencia, estrellas y último push **con fecha de comprobación**; (2) comando de instalación en
bloque de código; (3) ejemplo mínimo copiable y pegable; (4) por qué este y no el rival,
**nombrándolo**; (5) lo que NO hace bien — el aviso que evita el falso verde.

El `resumen` del frontmatter **no se tocó en ninguno**: los 56 ya cabían en 120 caracteres y
distinguían de su vecino (el más largo era `node-red`, 117). `cosmos`, `nombre` y `padre`,
intactos.

## 1. Cuántos y dónde

**56 pueblos reescritos, el 100 % de los asignados.** Ninguno fuera de mis nichos: el aplicador
lee el `padre` de cada frontmatter y rechaza lo que no empiece por uno de los siete.

- **`automatizacion` (11)**: twenty, docuseal, openproject, aviso-por-chat, celery, correo-smtp,
  hammerspoon, n8n, node-red, rpaframework, windmill.
- **`infraestructura` (9)**: restic, caddy, gitea, ntfy, uptime-kuma, victoriametrics,
  acceso-remoto, contenedor-efimero, sops.
- **`documentos` (9)**: markitdown, pandoc, openapi-generator, d2, diagrams, mermaid, weasyprint,
  context7, mkdocs-material.
- **`rendimiento` (8)**: tokio, rr, sanitizers, bpftrace, hyperfine, py-spy, samply, mimalloc.
- **`visibilidad` (7)**: advertools, bing-webmaster, claude-seo-ai, geo-optimizer, matomo,
  search-console, serpbear.
- **`saas` (6)**: gobl, casdoor, lago, panel-auth-cookie, stripe-agent-toolkit,
  validadores-frontera.
- **`cumplimiento` (6)**: arx, presidio, fossology, ort, cookies-declaradas, paginas-legales.

De esos 56, **10 son herramientas propias** que apuntan a `cosecha/` y no tienen repositorio
público: aviso-por-chat, correo-smtp, acceso-remoto, contenedor-efimero, panel-auth-cookie,
validadores-frontera, cookies-declaradas, paginas-legales, bing-webmaster y search-console. En
ellos la «URL» es la ruta del fichero, el comando de uso salió de **leer el propio guion** (su
docstring de uso, su `argparse`, sus `export`), y el cuerpo explica **por qué se prefiere a la
alternativa pública**, que es lo que justifica que existan.

## 2. Verificación en vivo de los 46 de GitHub

Cupo de `WebSearch` agotado, así que todo se comprobó con la **API de GitHub autenticada** el
2026-09-01 (token del llavero, nunca escrito a fichero ni impreso). Estrellas, `pushed_at` y
licencia SPDX de cada repositorio, más:

- **Homebrew**: `formulae.brew.sh/api` — 12 fórmulas y 1 cask confirmados existentes
  (pandoc, d2, caddy, restic, sops, hyperfine, ntfy, mimalloc, samply, openapi-generator,
  victoriametrics, graphviz; cask hammerspoon).
- **PyPI**: 10 paquetes confirmados (stripe-agent-toolkit, advertools, presidio-analyzer,
  presidio-anonymizer, markitdown, weasyprint, mkdocs-material, diagrams, py-spy, rpaframework,
  geo-optimizer-skill, celery).
- **npm**: 6 paquetes confirmados (@stripe/agent-toolkit, @mermaid-js/mermaid-cli, node-red, n8n,
  windmill-cli, @upstash/context7-mcp).
- **Docker Hub**: 6 imágenes y sus etiquetas confirmadas con HTTP 200 (gitea/gitea:latest,
  matomo:latest, louislam/uptime-kuma:2, victoriametrics/victoria-metrics:latest,
  towfiqi/serpbear:latest, casbin/casdoor-all-in-one:latest, openproject/openproject:16).
- **READMEs y `pyproject.toml`** leídos en crudo por la API para no inventar órdenes: ort, gobl,
  geo-optimizer-skill (CLI real: `geo`, no `geo-optimizer`), claude-seo-ai, lago, casdoor,
  windmill, docuseal, markitdown, fossology, stripe.

### Redirecciones y datos que NO eran los que decía la ficha anterior

| Lo que se creía | Lo que es, comprobado 2026-09-01 |
|---|---|
| `stripe/agent-toolkit` | **Renombrado a `stripe/ai`** (1.784★, MIT, push 2026-08-30). Los paquetes conservan el nombre viejo. |
| `microsoft/presidio` | **Movido a `data-privacy-stack/presidio`** (10.702★, MIT, push 2026-08-31). Redirect vivo; la cita nueva usa la URL nueva. |
| `google/sanitizers` como implementación | Ese repo es **documentación y seguimiento de fallos** (12.461★, push 2026-05-19). La implementación vive en `compiler-rt` de `llvm/llvm-project` (40.038★, push 2026-09-01). Ambos citados en la ficha. |
| `go install .../gobl/cmd/gobl` | El módulo del CLI es **`gobl.dev`**, no `gobl`. |
| Licencias «Other» de GitHub | Leído el `LICENSE` real: twenty = AGPL-3.0 con ficheros comerciales · celery = BSD-3-Clause · n8n = **Sustainable Use License** (fair-code, no OSI) · windmill = Apache-2.0 + AGPL-3.0 por directorio + módulos propietarios · rr = MIT (Mozilla) · sanitizers = Apache-2.0 con excepciones LLVM. |

## 3. Lo que NO se pudo verificar, y por qué

1. **Los calendarios de la normativa española de facturación** (`gobl`). Verifactu (RD 1007/2023 +
   Orden HAC/1177/2024) y la factura entre empresas de la Ley 18/2022 se han aplazado varias veces.
   **Cupo de `WebSearch` agotado**, así que las fechas de obligatoriedad **no se comprobaron en
   vivo**. La ficha cita las normas, marca explícitamente que el calendario está sin verificar, y
   manda confirmarlo en el BOE o en la sede de la AEAT antes de prometer una fecha a un cliente.
   Lo mismo con la edición vigente de la Guía de cookies de la AEPD en `cookies-declaradas`.
2. **Ninguna herramienta se ejecutó de verdad.** El encargo no lo pedía y no había entorno para
   hacerlo (Linux para `rr`, `bpftrace`, `sanitizers`; Docker para nueve pueblos; cuentas de API
   para `bing-webmaster`, `search-console`, `serpbear`). Lo verificado es que **la URL, el paquete,
   la fórmula, la imagen y la etiqueta existen**, y que las órdenes salen de la documentación
   oficial o del propio código. No es «probado»; es «no inventado». Los pueblos NO afirman haberse
   ejecutado.
3. **Nada de pago se dio de alta.** `serpbear` necesita un proveedor de rastreo externo,
   `geo-optimizer` cobra por uso en `geo citations` / `geo snapshots`, `stripe` cobra comisión por
   transacción y `mkdocs-material` tiene edición Insiders de pago. Los cuatro quedan **anotados con
   el importe o el modelo de cobro y sin contratar**, según la regla dura del arnés.

## 4. Avisos propios de cada nicho, aplicados

- **`cumplimiento`** — cada ficha dice **qué norma, versión y territorio** cubre y qué NO comprueba:
  `arx` → considerando 26 del RGPD (UE) y dictamen 05/2014; no valida base jurídica ni EIPD.
  `presidio` → ninguna norma, solo ayuda al art. 5.1.c del RGPD; su reconocedor de DNI español no
  valida la letra. `fossology` y `ort` → SPDX 2.3 / CycloneDX y OpenChain ISO/IEC 5230; no ven
  patentes, marcas ni código copiado sin cabecera. `cookies-declaradas` → art. 22.2 LSSI-CE (Ley
  34/2002) + arts. 6 y 7 RGPD + Guía de cookies de la AEPD, España; no valida el banner ni la carga
  previa al consentimiento. `paginas-legales` → art. 10 LSSI-CE, España; no cubre la política de
  privacidad de los arts. 13-14 del RGPD.
- **`infraestructura`** — el cuerpo prioriza la copia **verificable**. `restic` encabeza el nicho
  con `check --read-data-subset` y `restore` a un directorio temporal en la misma tanda de órdenes,
  y con el aviso de que `check` a secas **pasa en verde con datos corruptos**. Se marcan además tres
  bases SQLite/PostgreSQL que **se corrompen si se copian en caliente** (uptime-kuma, openproject,
  gitea).
- **`automatizacion`** — cada pueblo dice qué pasa a las tres de la mañana. `celery`: `acks_late`
  exige idempotencia y **no trae cola muerta de serie** con Redis. `n8n`: reintento por nodo +
  Error Workflow, y **sin Error Workflow el fallo nocturno no avisa a nadie**. `windmill`:
  reintentos por paso, límite de tiempo y concurrencia por ruta. `node-red`: no hay reintento por
  nodo, se construye con `catch`. `correo-smtp` y `rpaframework`: **no reintentan ni encolan**,
  van detrás de `celery`. `aviso-por-chat`: nunca lanza excepción a propósito, así que un fallo de
  envío es silencioso salvo que se lea su `{ok, sent, errors}`.
- **`saas`/facturación** — fecha citada en todo (2026-09-01) y calendario marcado como no
  verificado. `lago` lleva el aviso de que **sin `transaction_id` único, un reintento de red
  duplica el consumo y el cliente recibe una factura inflada**.

## 5. Los que ya no merecían estar (no borrados, señalados)

Ninguno se ha borrado. Cuatro llevan ahora en el cuerpo un «ojo de vida» explícito:

| Pueblo | Señal | Qué dice la ficha |
|---|---|---|
| **`arx`** (`cumplimiento/datos-personales`) | 734★ · último push **2025-10-01**, once meses antes | El más frágil del lote. Sigue siendo el único del barrido en su hueco con base científica publicada, pero se marca como pueblo a revisar antes de construir producto encima. |
| **`claude-seo-ai`** (`visibilidad`) | **47★** · push 2026-06-01 | Entra por estar en producción en esta casa, **no por respaldo de comunidad**. Su reemplazo evaluado ya está nombrado en la propia ficha (`AgriciDaniel/claude-seo`). |
| **`serpbear`** (`visibilidad`) | 2.064★ · push 2026-05-14 | Estable pero el ritmo más lento del nicho, y **no mide nada sin un proveedor de rastreo externo** que hay que contratar. |
| **`hammerspoon`** (`automatizacion`) | 16.029★ · push **2026-07-08** | Mantenido pero sin desarrollo diario; solo macOS y con un paso manual de permisos que no se puede provisionar. |

Menciones menores del mismo tipo, ya escritas en su cuerpo: `advertools` (1.450★, push 2026-06-30),
`hyperfine` (push 2026-04-30, maduro y estable), `samply` (4.401★, proyecto de una persona),
`rpaframework` (1.555★, el menos respaldado de su nicho) y los tres conversores de `gobl`
(`gobl.facturae` 7★, `gobl.verifactu` 15★, `gobl.es.ticketbai` 7★ — estrellas de un dígito para algo
que emite facturas legales).

## 6. Salida de `validar` y `medir`

**Ojo con la configuración**: durante esta tanda otro agente **borró `galaxia.toml`** y dejó
`cosmos.toml` apuntando al árbol real (ver [`fix-gate.md`](fix-gate.md)). Invocar
`--config galaxia.toml` ahora cae a los valores por defecto y produce **201 falsos E19** («vista
plana desincronizada» contra `.claude/skills`, que no es el destino de este árbol). La invocación
correcta es la de abajo.

```
$ python3 -m cosmos validar galaxia --config cosmos.toml
COSMOS  verde  0 errores

$ python3 -m cosmos medir galaxia --config cosmos.toml
COSMOS  medir

  Entrada base .... 1.128 tokens
  Peor nicho ...... 1.771 tokens   (ciberseguridad, 26 pueblos)
  Agua condicional  813 tokens     (5 aguas por paths:, fuera de la entrada)
  Peor con agua ... 2.584 tokens
  Universo ........ 85.429 tokens
  Descarga ........ 97,9 %
  Presupuesto ..... 4.000     OK, quedan 1.416 tokens en el peor caso con agua
```

**Verde y bajo presupuesto**, con 1.416 tokens de margen en el peor caso con agua.

El cuerpo de los pueblos no entra en el catálogo, así que las 56 fichas largas **no mueven la
entrada**: el «peor nicho» sigue siendo `ciberseguridad` con 1.771 tokens, exactamente igual que
antes de esta tanda. Lo que sube es `Universo` (22.103 → 85.429), que es material bajo demanda, y
con él la descarga (92,0 % → 97,9 %).

### Un rojo intermedio que NO era mío, y cómo se resolvió

Durante esta tanda la galaxia pasó por **rojo con 2 errores E17** —solapamiento entre
`galaxia/agua/mar-pruebas.md` ↔ `galaxia/agua/oceano-verificar.md` y
`galaxia/agua/mar-accesibilidad.md` ↔ `galaxia/estrellas/web.md`—. Comprobado con
`git diff --stat HEAD` en el momento: **cero cambios en esos cuatro ficheros, idénticos a HEAD**.
Aparecieron al endurecer otro agente `cosmos/validar.py` (`PALABRAS_VACIAS_E17` pasó de 37 palabras
a solo las gramaticales), lo que destapó dos solapamientos preexistentes. Estaban **fuera de mi
boundary**, así que no se tocaron: los cerró su dueño mientras se escribía este parte
(`galaxia/agua/mar-pruebas.md` y `galaxia/estrellas/web.md`, −3/+2 líneas). Queda anotado por si
vuelve.

Mis 56 pueblos pasan el contrato de `spec/PUEBLO.md` **medido a máquina, no a ojo**:

- **56/56** traen URL `http(s)` o ruta de `cosecha/` en la primera línea del cuerpo.
- **56/56** traen bloque de código con instalación y uso.
- **46/46** de los que son de GitHub traen licencia + estrellas + `pushed_at` + `comprobado 2026-09-01`.
- **56/56** nombran al menos una alternativa concreta en el cuerpo (medido buscando en cada cuerpo
  nombres propios de herramientas distintos del propio pueblo, no una frase hecha).
- **56/56** traen apartado de avisos (`Ojo:` o «lo que NO comprueba»).

Frente al punto de partida —0/189 con URL, 0/189 con bloque de código, 0/189 con comando de
instalación— este lote deja 56 fichas que sí nombran lo que hay que ejecutar. Lo que **no** afirman
es haberse ejecutado: eso sigue en 0/56 y está dicho en el apartado 3.
