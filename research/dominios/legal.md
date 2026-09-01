# Legal — cumplimiento y propiedad

Barrido GitHub para COSMOS, nicho 19 (`legal`). Cubre: RGPD con herramienta real, licencias de
software y su compatibilidad, contratos (generación/análisis), propiedad intelectual, accesibilidad
legal europea (EN 301 549), y retención/borrado de datos.

**Método**: API de GitHub autenticada (`search/repositories` + `repos/{owner}/{repo}`), cupo de
WebSearch agotado. Se resolvió un redirect (`microsoft/presidio` → `data-privacy-stack/presidio`,
confirmado vía `Location` header) antes de dar por bueno el hallazgo. Fecha del barrido: 2026-09-01.
Toda cifra fue confirmada en vivo esa fecha; lo que no, va marcado `NO VERIFICADO`.

**Criterio propio del encargo**: este nicho está lleno de plantilla disfrazada de herramienta. Solo
entra lo que **analiza, detecta o valida de verdad** contra datos reales — un generador de textos de
política **queda fuera aunque tenga miles de estrellas** (caso descartado explícitamente más abajo).

---

## De primera

1. **[oss-review-toolkit/ort](https://github.com/oss-review-toolkit/ort)** — 2.1k★, Apache-2.0,
   `pushed_at` 2026-08-31. **Por qué gana**: suite completa que automatiza el cumplimiento de
   licencias de software de punta a punta — analiza dependencias, evalúa contra políticas
   configurables, genera SBOM y notice files. Es el que de verdad **ejecuta** un pipeline de
   compliance, no una checklist; adoptado por proyectos de la Eclipse Foundation.

2. **[fossology/fossology](https://github.com/fossology/fossology)** — 1.0k★, GPL-2.0, `pushed_at`
   de hoy. **Por qué gana su hueco**: el toolkit de compliance de licencias más veterano y completo
   (escaneo de licencia, copyright y control de exportación), con base de datos y UI web para
   flujo de trabajo de auditoría legal — proyecto de la Linux Foundation, sigue con commits activos.
   Gana frente a ORT cuando hace falta el flujo de auditoría humana con UI, no solo el CLI de CI.

3. **[owasp-dep-scan/dep-scan](https://github.com/owasp-dep-scan/dep-scan)** — 1.3k★, MIT,
   `pushed_at` 2026-08-16. **Por qué gana**: escáner OWASP que cruza vulnerabilidades conocidas
   **con** límites de licencia de las dependencias en un solo informe — cubre repos locales e
   imágenes de contenedor. Útil cuando el riesgo legal (licencia) y el de seguridad se quieren en la
   misma pasada de CI.

4. **[anchore/syft](https://github.com/anchore/syft)** — 9.5k★, Apache-2.0, `pushed_at` 2026-08-31.
   **Por qué gana**: generador de SBOM (Software Bill of Materials) de referencia — CLI que produce
   CycloneDX/SPDX desde imágenes o filesystem. El SBOM es la evidencia que de verdad se pide en
   auditorías de propiedad intelectual y en la CRA europea; sin un SBOM real, "cumplimiento de
   licencias" es una promesa, no un dato.

5. **[dequelabs/axe-core](https://github.com/dequelabs/axe-core)** — 7.5k★, MPL-2.0, `pushed_at`
   2026-08-31. **Por qué gana**: es el motor de accesibilidad automatizada que usan casi todas las
   demás herramientas del hueco (Lighthouse, extensiones de navegador, integraciones Cypress/
   Playwright/Selenium listadas más abajo). EN 301 549 remite a WCAG 2.1 AA como base técnica —
   correr axe-core es la forma real de medir esa parte del cumplimiento, no de "creer" que se cumple.

6. **[pa11y/pa11y](https://github.com/pa11y/pa11y)** — 4.5k★, LGPL-3.0, `pushed_at` 2026-08-28.
   **Por qué gana su hueco**: complementa a axe-core con un runner pensado para CI/CD
   (`pa11y-ci`) y un dashboard programado (`pa11y-dashboard`) para vigilar accesibilidad de muchas
   URLs en el tiempo — el ángulo "auditoría continua" que axe-core solo (como librería) no da.

7. **[data-privacy-stack/presidio](https://github.com/data-privacy-stack/presidio)** — 10.7k★,
   `pushed_at` 2026-08-31 (repo movido desde `microsoft/presidio`, redirect confirmado en vivo).
   **Por qué gana**: el framework de detección y anonimización de PII de referencia — analizador NER
   configurable + motor de anonimización (redacción, hash, cifrado, sustitución) sobre texto
   estructurado y no estructurado. Es la base sobre la que están construidas media docena de
   herramientas menores encontradas en este barrido (`piiscan`, `presidio-cli`, `presidio-rs`…).

8. **[arx-deidentifier/arx](https://github.com/arx-deidentifier/arx)** — 734★, Apache-2.0,
   `pushed_at` 2025-10-01. **Por qué gana**: no es un simple sustituidor de texto — implementa
   técnicas reales de anonimización estadística (k-anonimato, l-diversidad) con análisis de riesgo de
   reidentificación y de pérdida de utilidad de los datos. Es el candidato serio cuando el requisito
   RGPD es "datos anonimizados de forma demostrable", no solo "sin nombres visibles".

9. **[sam247/openredaction](https://github.com/sam247/openredaction)** — 103★, MIT, `pushed_at`
   2026-08-31. **Por qué gana su hueco**: detección y redacción de PII en JS/TypeScript **100%
   local**, sin llamada a ningún servicio externo — encaja con el requisito de coste cero y sin fuga
   de datos a terceros que Presidio (Python/contenedor más pesado) no siempre resuelve tan ligero.

10. **[IBM/ai-privacy-toolkit](https://github.com/IBM/ai-privacy-toolkit)** — 113★, MIT, `pushed_at`
    2025-09-17. **Por qué gana**: aplica técnicas reales de privacidad (anonimización + evaluación de
    riesgo de inferencia de pertenencia) específicamente a modelos de IA — el ángulo "RGPD para
    datos usados en entrenar/consultar un modelo", que ninguno de los anteriores cubre.

---

## Segunda fila

- **[fsfe/reuse-tool](https://github.com/fsfe/reuse-tool)** — 583★, herramienta oficial de la FSFE
  para el estándar REUSE (cabeceras de licencia + SPDX por fichero) — valida de verdad, no solo
  documenta. `pushed_at` 2026-08-22.
- **[anchore/grype](https://github.com/anchore/grype)** — 12.8k★, Apache-2.0. Escáner de
  vulnerabilidades compañero de syft — mismo pipeline de evidencia, ángulo seguridad en vez de
  licencia.
- **[sbom-tool/sbom-tools](https://github.com/sbom-tool/sbom-tools)** — 239★, MIT, `pushed_at`
  2026-08-31. Diff semántico de SBOM/CBOM/AI-BOM + scoring de calidad y validación de compliance
  contra CycloneDX/SPDX — útil cuando el SBOM ya existe y hay que auditar su evolución.
- **[Privado-Inc/privado](https://github.com/Privado-Inc/privado)** — 654★, LGPL-3.0. Escaneo
  estático que detecta flujos de datos personales en el código — más orientado a "dónde vive el dato
  personal en mi app" que Presidio (que opera sobre texto/documentos ya extraídos).
- **[onebeyond/license-checker](https://github.com/onebeyond/license-checker)** y
  **[pilosus/pip-license-checker](https://github.com/pilosus/pip-license-checker)** — puertas de CI
  específicas de ecosistema (npm / Python) que rechazan licencias no permitidas; más estrechas que
  ORT/FOSSology pero triviales de integrar cuando solo hace falta un ecosistema.
- **[smithoss/gonymizer](https://github.com/smithoss/gonymizer)** — 161★, Apache-2.0, `pushed_at`
  2026-05-04. Anonimiza volcados de PostgreSQL reales — el caso concreto "quiero un dump de
  producción sin datos personales para QA".
- **[holmdigital/a11y-hd](https://github.com/holmdigital/a11y-hd)** — 9★, MIT, `pushed_at`
  2026-08-31. Mapea fallos WCAG a EN 301 549 y ley nacional en 17 jurisdicciones — muy específico y
  muy joven (9★), a vigilar; hoy no sustituye a axe-core+pa11y, los complementa con el mapeo legal.
- **[68publishers/consent-management-platform](https://github.com/68publishers/consent-management-platform)**
  — 65★, `NOASSERTION`. Widget de consentimiento de cookies autohospedado con lógica real de opt-in/
  opt-out y almacenamiento de consentimiento — no es una plantilla de texto, gestiona estado.

## Humo

- **[CISOfy/lynis](https://github.com/CISOfy/lynis)** (16.3k★) — auditoría de sistema que también
  cubre HIPAA/ISO27001/PCI DSS; más de seguridad que de legal puro.
- **[americanexpress/earlybird](https://github.com/americanexpress/earlybird)** (773★) — escáner de
  secretos y PII en repos de código.
- **[vanctran/ra11y](https://github.com/vanctran/ra11y)** (2★) — escáner de accesibilidad
  multi-estándar sin dependencias en runtime; muy nuevo.
- **[Quantco/conda-deny](https://github.com/Quantco/conda-deny)** (32★) — compliance de licencias
  para entornos conda.
- **[nixys/nxs-data-anonymizer](https://github.com/nixys/nxs-data-anonymizer)** (293★) — anonimiza
  dumps de Postgres/MySQL, alternativa a gonymizer.

## Descartado explícitamente (aplicando el filtro del encargo)

- **`nisrulz/app-privacy-policy-generator`** (4.7k★) y el resto de generadores de política de
  privacidad/T&C encontrados (`Tempest-Solutions-Company`, `zuri-training/*`…): producen texto
  legal, no analizan ni validan nada. Fuera por definición del encargo, con independencia de sus
  estrellas.

---

## Mapeo a COSMOS

```
sistema-solar  legal
├── continente  licencias-y-propiedad
│   ├── pais  auditoria-de-dependencias   ort · fossology · owasp-dep-scan
│   └── pais  evidencia-sbom              syft · grype · sbom-tools · reuse-tool
├── continente  datos-personales
│   ├── pais  deteccion-pii               presidio · openredaction · earlybird
│   └── pais  anonimizacion               arx · ai-privacy-toolkit · gonymizer · nxs-data-anonymizer
├── continente  accesibilidad-legal
│   └── pais  auditoria-wcag-en301549     axe-core · pa11y · a11y-hd (mapeo legal)
├── continente  contratos-y-consentimiento
│   └── pais  gestion-de-consentimiento   consent-management-platform (68publishers)
└── continente  codigo-legal            ← el código propio del nicho
       provincias: reglas de política de licencias para ORT/dep-scan escritas a medida,
       scripts de anonimización de dumps de cliente antes de QA, reglas custom de detección
       PII sobre datos de negocio propios (no genéricas)
```

## Lo que falta

- **Análisis de contratos**: todo lo encontrado son proyectos académicos o de portfolio (<25★,
  varios sin mantenimiento desde 2019-2023). No hay un ganador real, vivo y self-hosted para
  "analiza este contrato y saca riesgos" — el hueco está vacío de verdad, no es que se haya
  descartado algo.
- **Retención de datos**: mismo problema — lo que aparece es o bien scripts de partición/purga de
  una base de datos concreta (MySQL) o analizadores de políticas de privacidad ya escritas (no
  gestores de retención). Sin candidato de primera.
- **Gestión de consentimiento tipo OneTrust self-hosted**: nada maduro y activo; el hallazgo mejor
  (68publishers) es un widget, no una plataforma completa con registro de auditoría y DSR
  (Data Subject Access Request).
- Revisar en 3 meses si `a11y-hd` gana tracción — si crece, sube a "de primera" como el mapeo
  EN 301 549 que hoy falta.
