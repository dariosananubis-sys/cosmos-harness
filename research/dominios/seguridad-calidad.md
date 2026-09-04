# Seguridad y calidad — barrido GitHub para COSMOS

Dominio completo: **SAST, secretos, revisión de código, accesibilidad, RGPD/privacidad y
calidad/refactorización** (barrido de 2026-09-01, este documento) + **dependencias/SCA, cadena de
suministro y testing** (rescatado de un barrido anterior interrumpido, integrado tal cual, sin
reescribir ni degradar — ver nota al final de cada bloque).

Método: cupo de `WebSearch` de la sesión agotado (200/200). Todo verificado en vivo contra
`api.github.com` con token autenticado (`security find-internet-password -s github.com -w`, nunca
impreso ni escrito a fichero) — límite 5.000 peticiones/hora. Para README se usó
`raw.githubusercontent.com/<owner>/<repo>/<rama>/README.md` (o el endpoint `contents/` cuando el
fichero tiene mayúsculas atípicas, caso Presidio: `README.MD`). Estrellas, fecha de último `push` y
licencia son el dato duro; el resto (mecanismo, límite de gratuidad) sale de leer el propio README
o `LICENSE`, nunca de memoria.

---

## De primera

### SAST / análisis estático de seguridad

| Recurso | Estrellas | Último push | Por qué gana |
|---|---:|---|---|
| `semgrep/semgrep` | 16.459 | 2026-09-01 | Pattern-matching semántico real (no regex) sobre 30+ lenguajes, con reglas legibles como el propio código. LGPL-2.1, CLI gratis. **Límite exacto, confirmado en su propio README**: la Community Edition "will miss many true positives as it can only analyze code within the boundaries of a single function or file" — el análisis cross-file/cross-función (taint interprocedural) exige Semgrep AppSec Platform (Pro), de pago. Es la misma frontera que ya usa la skill instalada `static-analysis-semgrep` (detecta Pro si está disponible). |
| `github/codeql` | 10.036 | 2026-09-01 | El único de esta tabla con **taint tracking interprocedural real** (dataflow entre funciones y ficheros), motor de GitHub Advanced Security. MIT el repo de queries. **Trampa de coste verificada en el propio README**: "If you'd like to use the CodeQL CLI to analyze closed-source code, you will need a separate commercial license." Gratis para repos públicos vía GitHub Actions (code scanning); para analizar en local código propietario de cliente (el caso de <la agencia>) hace falta licencia comercial — no vale asumirlo gratis sin comprobar el contrato de cada organización. |
| `PyCQA/bandit` (8.249★, push 2026-08-29) + `securego/gosec` (8.937★, push 2026-08-31) | — | — | Escáneres oficiales por lenguaje, ambos con mecanismo real más allá del regex: bandit recorre el AST de Python; gosec combina reglas sobre el AST/SSA de Go **con taint analysis propio** (rastrea el dato desde input de usuario hasta función peligrosa — SQLi, command injection, SSRF, deserialización insegura). Apache-2.0 los dos, sin capa de pago. Ruido bajo porque son específicos de un solo lenguaje, no generalistas. |
| `Bearer/bearer` | 2.739 | 2026-08-31 | SAST con **análisis de flujo de datos**, no solo patrones: rastrea sensibilidad (PII/PHI) igual que rastrea una inyección SQL. Cubre OWASP Top 10 + CWE Top 25 nativamente en Go/Java/JS/TS/PHP/Python/Ruby. Bisagra real hacia RGPD (ver más abajo). CLI gratis; cross-file avanzado en más lenguajes y Bearer Pro son de pago (vía Cycode). |

### Detección de secretos

| Recurso | Estrellas | Último push | Por qué gana |
|---|---:|---|---|
| `trufflesecurity/trufflehog` | 27.645 | 2026-09-01 | Único de los tres con **verificación real**: para cada secreto detectado, intenta autenticarse contra el proveedor (AWS, Stripe, GitHub…) y confirma si sigue vivo. Clasifica 800+ tipos. Esto es lo que baja el ruido de verdad — un hallazgo "verificado" no es una opinión de regex, es una llamada de red que confirma o descarta. AGPL-3.0, CLI gratis; hay producto Enterprise de monitorización continua (Slack/Jira/Confluence…), de pago, aparte. |
| `gitleaks/gitleaks` | 29.046 | 2026-08-26 | El más adoptado (badge "protected by gitleaks" en miles de repos), detección por regex + entropía sobre historial git completo, MIT. **Aviso literal en su propio README, verificado 2026-09-01**: *"Gitleaks is feature complete. I'm not merging new features into Gitleaks. Future releases will be security patches only. I'm shifting my focus to Betterleaks."* — sigue siendo sólido hoy, pero su desarrollo activo se ha movido a otro repo (ver `betterleaks/betterleaks` en Humo). |

### Revisión de código automatizada

| Recurso | Estrellas | Último push | Por qué gana / coste |
|---|---:|---|---|
| `anthropics/claude-code-security-review` | 6.132 | 2026-02-11 | GitHub Action oficial de Anthropic: analiza el **diff de cada PR con Claude** (Opus por defecto), no patrones — detecta lógica de negocio insegura que el pattern-matching no ve (auth bypass, IDOR, lógica de permisos), y tiene una segunda pasada de filtrado de falsos positivos con el propio modelo. Arquitectura legible en `claudecode/` (`github_action_audit.py`, `findings_filter.py`). **💰 No es gratis**: el input `claude-api-key` exige clave de la API de Anthropic (facturación por uso), no la cubre una suscripción de Claude Code — cae dentro de "nunca pagar sin orden" del arnés. El propio README avisa además: "not hardened against prompt injection […] only be used to review trusted PRs". |

### Accesibilidad (con ángulo EN 301 549)

| Recurso | Estrellas | Último push | Por qué gana |
|---|---:|---|---|
| `dequelabs/axe-core` | 7.461 | 2026-08-31 | El motor de verdad detrás de casi todo lo demás (incluida la auditoría de accesibilidad de Lighthouse). Dato honesto y verificado en su README: **"find on average 57% of WCAG issues automatically"**, y devuelve resultados como `incomplete` cuando no puede estar seguro — no fuerza pass/fail donde no lo sabe (la señal trivalente que exige `revisor-adversarial.md`). MPL-2.0, gratis, sin capa de pago. |
| `pa11y/pa11y` | 4.493 | 2026-08-28 | CLI/Node para CI que envuelve axe-core (o HTML_CodeSniffer). No aporta motor propio, aporta el enchufe fácil a pipeline — por eso va segunda fila, no primera. |
| `GoogleChrome/lighthouse-ci` | 7.063 | 2026-03-27 (5+ meses sin push, único candidato de esta lista con signo de posible abandono) | Automatiza Lighthouse (accesibilidad + rendimiento + SEO) commit a commit y guarda histórico para ver regresiones. Útil para tendencia, no para hallazgo puntual. |

**EN 301 549** (norma europea que exige la Ley/EAA 2025 y que subyace a WCAG 2.1/2.2 AA): no
apareció ningún escáner de primera fila que mapee hallazgos directamente a sus cláusulas — ver
"Lo que falta".

### RGPD y privacidad de datos

| Recurso | Estrellas | Último push | Por qué gana |
|---|---:|---|---|
| `Bearer/bearer` | 2.739 | 2026-08-31 | (mismo repo que en SAST, entra aquí por mecanismo distinto) Su análisis de flujo de datos clasifica qué variables llevan PII/PHI y por dónde viajan en el código (bases de datos, APIs de terceros como OpenAI o Sentry). El propio README dice para qué sirve el informe que genera: **"Privacy Impact Assessment (PIA), Data Protection Impact Assessment (DPIA), Records of Processing Activities (RoPA) input for GDPR compliance reporting"** — es la única herramienta de este barrido que produce un artefacto RGPD real desde código, no una plantilla de política. |
| `data-privacy-stack/presidio` (antes `microsoft/presidio`) | 10.701 | 2026-08-31 | Motor de detección/anonimización de PII en **datos** (texto, imágenes), no en código: reconocedores por NER + regex + checksum, en varios idiomas, con anonimización real (no solo detección). MIT. Complementa a Bearer: Bearer dice "por dónde viaja el PII en tu código", Presidio dice "aquí hay un DNI en este texto, lo redacto". Nota de procedencia: el repo se transfirió de la organización `microsoft` a `data-privacy-stack` — su propio README lo anuncia ("Presidio is moving to a new home"), sigue MIT y activo, pero cualquier cita futura debe usar la URL nueva. |

### Calidad y refactorización

| Recurso | Estrellas | Último push | Por qué gana |
|---|---:|---|---|
| `astral-sh/ruff` | 49.418 | 2026-09-01 | El linter/formateador Python de facto ya: AST real (no regex), 900+ reglas con reimplementación nativa de plugins populares (flake8-bugbear, isort, y reglas al estilo bandit), 10-100x más rápido que Flake8. MIT, gratis, sin capa de pago — sustituye 4-5 herramientas Python sueltas. |
| `eslint/eslint` | 27.495 | 2026-09-01 | El estándar JS/TS, AST real vía `espree`/`@typescript-eslint`. MIT, gratis. |
| `golangci/golangci-lint` | 19.342 | 2026-08-30 | Meta-linter Go: orquesta 100+ linters reales (incluye `gosec`) en un solo paso, con caché. GPL-3.0, gratis. |
| `kucherenko/jscpd` | 6.091 | 2026-08-31 | Detección de duplicación por **tokenización real** (no diff de texto) sobre 223 formatos — mide de verdad, no cuenta líneas parecidas. MIT. Su propia descripción se declara ya "AI-ready with token-efficient reporter, skill and MCP server", pensado para que un agente lo use sin volcarle el repo entero. |

Comparado con el resto del dominio, calidad es donde el filtro "mecanismo, no prosa" es más fácil
de aplicar: un linter o un detector de duplicados o se ejecuta y escupe `fichero:línea`, o no sirve.
Los cuatro de arriba lo hacen; ningún candidato "de primera" aquí es checklist.

---

### Dependencias, cadena de suministro y testing (rescate 2026-09-01, íntegro)

> Bloque conservado tal cual del barrido anterior — mismos datos, mismas estrellas, misma fecha de
> verificación. No se ha tocado una línea.

| Recurso | Estrellas | Último push | Mecanismo |
|---|---:|---|---|
| `google/osv-scanner` | 10.948 | 2026-09-01 | Parsea lockfiles de ~20 ecosistemas contra la base OSV.dev. Offline con base cacheada. Ruido bajo (base deduplicada). Apache-2.0 |
| `aquasecurity/trivy` | 37.725 | 2026-08-28 | SCA + secretos + configuración de IaC + SBOM, sobre imágenes, ficheros y repos. Base cacheada offline. El CLI cubre el caso entero sin tarjeta |
| `anchore/syft` + `anchore/grype` | 9.492 / 12.814 | 2026-08-31 | Syft genera SBOM real leyendo el árbol instalado; Grype lo audita contra su base. Apache-2.0 |
| `pypa/pip-audit` | 1.359 | 2026-08-31 | Oficial de la PyPA. Audita entornos y `requirements.txt`, con `--fix` |
| `ossf/scorecard` | 5.662 | 2026-08-31 | No busca CVE: mide la higiene del repo (protección de rama, anclaje por SHA en CI, permisos de token). Score por check con evidencia |
| `sigstore/cosign` | 6.274 | 2026-08-31 | Firma sin claves (OIDC) y verifica artefactos, con transparencia pública. Criptografía real, no heurística |
| `microsoft/playwright` | 95.461 | 2026-08-31 | End-to-end con navegador real y trazas. O carga la página o falla con evidencia |
| `stryker-mutator/stryker-js` | 3.067 | 2026-08-31 | Mutación real: altera el código, reejecuta la suite y reporta los mutantes que sobreviven |
| `boxed/mutmut` | 1.412 | 2026-08-17 | El equivalente en Python, mismo mecanismo |

**Por qué el de mutación es el que más importa aquí.** Stryker y mutmut son la única forma objetiva
de distinguir un test con aserción real de uno decorativo. Cambian el código a propósito —invierten
una condición, borran una llamada— y miran si algún test se entera. Un mutante que sobrevive es una
rama que la suite no estaba comprobando de verdad, por mucho que la cobertura dijera 90%. Es
exactamente la misma disciplina que `GOAL.md` §7 exige al validador de COSMOS: ver el rojo a
propósito. `ossf/scorecard` y `sigstore/cosign` son complementarios, no alternativas: los
escáneres miran CVE ya catalogadas, Scorecard mira si el proceso es un blanco fácil, y cosign mira
si lo que se ejecuta es lo que se firmó.

---

## Segunda fila

**De este barrido:**

- `Yelp/detect-secrets` — 4.630★, push 2026-04-02. Complementa a gitleaks/trufflehog con otro
  modelo: no escanea todo el histórico, crea una **línea base** (`.secrets.baseline`) y solo alerta
  de secretos *nuevos* — pensado para bloquear en pre-commit sin tener que limpiar primero todo el
  repo. Apache-2.0. Sin verificación en vivo (a diferencia de trufflehog): más falsos positivos si
  se usa como único escáner.
- `terryyin/lizard` — 2.477★, push 2026-08-29. Complejidad ciclomática + NLOC multi-lenguaje sin
  necesitar compilar; mecanismo real (parsing ligero), útil como gate de CI cuando `ruff`/`eslint`
  no cubren el lenguaje.
- `pmd/pmd` — 5.479★, push 2026-09-01. Analizador multi-lenguaje con su propio detector de copia-pega
  (CPD) integrado; punto fuerte en Java/Apex, más débil que jscpd en cobertura de formatos.
- `SonarSource/sonarqube` — 10.944★, push 2026-08-28. Combina quality gate + duplicación +
  complejidad + algo de seguridad en un solo panel self-hosted (Community Edition, LGPL-3.0). **No
  verificado en vivo el límite exacto de la Community Edition** (qué lenguajes/funciones caen en
  Developer/Enterprise de pago) — antes de recomendarlo a un cliente, comprobar el límite actual en
  su propia documentación de precios, no asumirlo de memoria.

**Del rescate (tal cual):**

- `cypress-io/cypress` — 51.021★, push 2026-09-01. Mismo mecanismo que Playwright pero sin WebKit nativo.
- `google/oss-fuzz` — 12.607★. Fuzzing continuo real, pero el coste de integración es alto.
- `renovatebot/renovate` — 22.380★. Abre PR de actualización de verdad. Self-hosted gratis (AGPL-3.0). Es mantenimiento, no auditoría.
- `CycloneDX/cyclonedx-python` (390★) y SPDX `tools-python` (254★, push 2026-03-13) — piezas de formato SBOM; complementan, no sustituyen.
- `ossf/allstar` — 1.446★. Fuerza políticas a nivel de organización, pero exige instalar una app con permisos amplios; Scorecard es de solo lectura y más ligero.
- `rustsec/rustsec` — 1.948★. Real, pero solo Rust; ya cubierto por OSV-Scanner.
- `socketdev/socket-cli` — 313★. Analiza el comportamiento de instalación de un paquete (scripts, ofuscación, red) más allá de la CVE catalogada: detecta el paquete nuevo malicioso, que es el hueco real de los demás. CLI gratis con límite no verificado; el panel de organización es de pago. No dar de alta nada: revisar el CLI, no contratar.

---

## Descartado

**Del rescate (tal cual):**

- **`jeremylong/DependencyCheck`** — solo 55★ porque el repo se movió; su descripción literal en GitHub empieza por «The dependency-check repository has moved:». La herramienta sigue viva en otra URL. No citar esta como fuente sin resolver antes el destino.
- **`manja316/claude-dependency-auditor`** — su `SKILL.md`, leído en vivo, sí ejecuta `npm audit --json`, `pip-audit`, `cargo audit` y `go vuln check` en vez de describirlos, y filtra falsos positivos por ecosistema. Pero tiene 0 estrellas: cero validación social. Mecanismo bueno, procedencia sin verificar — pasa por auditoría de código antes de instalarse, nunca directo.

**De este barrido:**

- Búsquedas directas de "PII detection scanner" y "GDPR data discovery" en GitHub Search API no
  devolvieron nada con validación social real (el más alto, `armenak/DataDefender`, se queda en
  161★; el resto son proyectos de portfolio o hackathon, 0-5★, sin actividad sostenida). No se listan
  porque ninguno pasó el filtro de "mecanismo, no prosa" con evidencia suficiente — `Bearer` y
  `Presidio` (arriba) cubren el hueco real con mucha más solidez.
- `rubik/radon` — 2.014★ pero **sin push desde 2024-10-20** (casi dos años). Buen mecanismo
  (métricas de complejidad Python reales) pero probable abandono; usar `lizard` en su lugar salvo que
  se confirme actividad reciente antes de adoptarlo.

---

## Humo

- `betterleaks/betterleaks` — 1.819★, push 2026-08-31. El proyecto al que el propio autor de
  gitleaks está moviendo su foco (ver aviso citado arriba). Demasiado nuevo para primera fila, pero
  a vigilar de cara a la siguiente ronda del dominio.
- `biomejs/biome` — 25.693★. Formateador+linter JS/TS en Rust, alternativa "todo en uno" a
  ESLint+Prettier; no se profundizó porque ESLint ya cubre el mecanismo y tiene más ecosistema de reglas de seguridad (`typescript-eslint`, 16.374★, incluido).
- `holmdigital/a11y-hd` — 9★, push 2026-08-31. Mapea fallos WCAG a EN 301 549 y legislación nacional
  en 17 jurisdicciones — la idea correcta para el ángulo legal europeo, pero sin tracción todavía.
- `BIK-BITV/BIK-Web-Test` — 96★. Procedimiento de test alemán (WCAG 2.1 + EN 301 549 + BITV 2.0);
  más metodología institucional que herramienta reusable directa.
- `Bearer/bearer` tiene además "Bearer Pro by Cycode" (de pago) para cross-file avanzado en
  C#/Kotlin/Elixir/VB.Net/Rust/Swift — mencionado ya en la tabla de primera, no una entrada nueva.

---

## Mapeo a COSMOS

Sigue la convención ya fijada en `infraestructura-devops.md` y en `TAXONOMIA.md` (que da
"seguridad" y "QA" como ejemplo textual de **continente**):

```
sistema-solar  Software / Ingeniería
└─ planeta     Ingeniería y Producto
   └─ continente  Seguridad y Calidad de Software
      └─ país         SEGURIDAD Y CALIDAD DE CÓDIGO   ← este dominio
         ├─ provincia  SAST y análisis estático
         │   ├─ ciudad  Generalistas multi-lenguaje   → pueblos: Semgrep, CodeQL
         │   ├─ ciudad  Nativos por lenguaje           → pueblos: Bandit (Python), gosec (Go)
         │   └─ ciudad  SAST con flujo de datos        → pueblo: Bearer
         ├─ provincia  Detección de secretos
         │   └─ ciudad  Escaneo de repos               → pueblos: Gitleaks, TruffleHog, detect-secrets
         ├─ provincia  Revisión de código con IA
         │   └─ pueblo  claude-code-security-review (💰 API de pago)
         ├─ provincia  Dependencias y cadena de suministro (rescate)
         │   ├─ ciudad  SCA / vulnerabilidades         → pueblos: OSV-Scanner, Trivy, Grype+Syft, pip-audit
         │   └─ ciudad  Higiene de repo y firma         → pueblos: Scorecard, cosign
         ├─ provincia  Testing (rescate)
         │   ├─ ciudad  End-to-end                     → pueblo: Playwright
         │   └─ ciudad  Mutación                        → pueblos: Stryker, mutmut
         ├─ provincia  Accesibilidad
         │   ├─ ciudad  Motor de reglas                 → pueblo: axe-core
         │   └─ ciudad  Integración CI                  → pueblos: pa11y, lighthouse-ci
         ├─ provincia  RGPD y privacidad
         │   ├─ ciudad  PII en código (flujo)            → pueblo: Bearer
         │   └─ ciudad  PII en datos (detección/anonimizado) → pueblo: Presidio
         └─ provincia  Calidad y refactorización
             ├─ ciudad  Linters nativos por lenguaje    → pueblos: Ruff, ESLint, golangci-lint
             └─ ciudad  Duplicación y complejidad        → pueblos: jscpd, lizard, PMD/CPD
```

---

## Lo que falta

1. **Mapeo automático a EN 301 549**: ningún escáner de primera fila traduce sus hallazgos WCAG
   directamente a las cláusulas de la norma europea (la que exige la EAA 2025). Los dos candidatos
   encontrados (`holmdigital/a11y-hd`, `BIK-BITV/BIK-Web-Test`) son de tracción baja o metodología
   institucional no reusable tal cual. Hoy esto se resuelve a mano: correr axe-core/pa11y y mapear el
   resultado WCAG → EN 301 549 por tabla de equivalencia (existe, es pública, pero no está
   automatizada en ninguna herramienta seria).
2. **Auditoría RGPD de extremo a extremo** (consentimiento, cookies, base legal, retención, DSAR):
   Bearer y Presidio cubren el lado técnico (dónde está el PII y cómo se anonimiza) pero ninguno
   audita el cumplimiento legal/procesal completo — eso sigue siendo trabajo humano o de una
   plataforma comercial de compliance, fuera del alcance "gratis y con mecanismo" de este barrido.
3. **Límite exacto de la capa gratuita de SonarQube Community Edition** no verificado en vivo
   (qué lenguajes y qué funciones — branch analysis, PR decoration — caen en Developer/Enterprise de
   pago): antes de recomendarlo a un cliente, comprobar contra `sonarsource.com` en el momento, no
   contra este documento.
4. **`gosec`/`bandit` no tienen equivalente propio verificado aquí** para PHP o Ruby con taint
   analysis real (Semgrep CE los cubre, pero solo con alcance de una función/fichero, según su propio
   aviso de límite arriba) — si un cliente concreto corre esos stacks, revisar de nuevo antes de
   asumir que Semgrep basta.
5. **`radon`** (métricas de complejidad Python) lleva casi dos años sin `push` — confirmar que sigue
   vivo antes de instalarlo; se recomienda `lizard` mientras tanto.

---

## Nota de método (heredada del rescate, sigue vigente)

Este dominio, en su primera pasada, se quedó sin `WebSearch` a mitad (200/200 del cupo de sesión,
compartido entre agentes) y luego chocó con el límite de 60 peticiones/hora de la API de GitHub sin
autenticar. Con el token del llavero del sistema el límite sube a 5.000 peticiones/hora (verificado,
y así se hizo todo este barrido completo sin volver a tocar `WebSearch`):

```bash
export GH_TOKEN=$(security find-internet-password -s github.com -w)
curl -s -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/repos/OWNER/REPO
```
