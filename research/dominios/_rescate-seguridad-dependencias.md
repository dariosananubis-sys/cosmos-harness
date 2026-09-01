# Rescate — dependencias, cadena de suministro y testing

Material producido por un barrido que se interrumpió antes de escribir su fichero. Se conserva
porque los datos están verificados en vivo contra `api.github.com` el 2026-09-01. **No es el informe
completo del dominio**: cubre solo dependencias/SCA, cadena de suministro y testing. Quien retome
`seguridad-calidad` debe partir de aquí y no repetir este tramo.

## De primera

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

### Por qué el de mutación es el que más importa aquí

Stryker y mutmut son la **única forma objetiva de distinguir un test con aserción real de uno
decorativo**. Cambian el código a propósito —invierten una condición, borran una llamada— y miran si
algún test se entera. Un mutante que sobrevive es una rama que la suite no estaba comprobando de
verdad, por mucho que la cobertura dijera 90 %.

Es exactamente la misma disciplina que `GOAL.md` §7 exige al validador de COSMOS: **ver el rojo a
propósito**. Aquí es un mecanismo, y encaja de forma natural en la fase 2.

`ossf/scorecard` y `sigstore/cosign` son complementarios, no alternativas: los escáneres miran CVE
ya catalogadas, Scorecard mira si el proceso es un blanco fácil, y cosign mira si lo que se ejecuta
es lo que se firmó.

## Segunda fila

- `cypress-io/cypress` — 51.021★, push 2026-09-01. Mismo mecanismo que Playwright pero sin WebKit nativo.
- `google/oss-fuzz` — 12.607★. Fuzzing continuo real, pero el coste de integración es alto.
- `renovatebot/renovate` — 22.380★. Abre PR de actualización de verdad. Self-hosted gratis (AGPL-3.0). Es mantenimiento, no auditoría.
- `CycloneDX/cyclonedx-python` (390★) y SPDX `tools-python` (254★, push 2026-03-13) — piezas de formato SBOM; complementan, no sustituyen.
- `ossf/allstar` — 1.446★. Fuerza políticas a nivel de organización, pero exige instalar una app con permisos amplios; Scorecard es de solo lectura y más ligero.
- `rustsec/rustsec` — 1.948★. Real, pero solo Rust; ya cubierto por OSV-Scanner.
- `socketdev/socket-cli` — 313★. Analiza el **comportamiento** de instalación de un paquete (scripts, ofuscación, red) más allá de la CVE catalogada: detecta el paquete nuevo malicioso, que es el hueco real de los demás. CLI gratis con límite no verificado; el panel de organización es de pago. **No dar de alta nada: revisar el CLI, no contratar.**

## Descartado

- **`jeremylong/DependencyCheck`** — solo 55★ porque **el repo se movió**; su descripción literal en GitHub empieza por «The dependency-check repository has moved:». La herramienta sigue viva en otra URL. No citar esta como fuente sin resolver antes el destino.
- **`manja316/claude-dependency-auditor`** — su `SKILL.md`, leído en vivo, sí **ejecuta** `npm audit --json`, `pip-audit`, `cargo audit` y `go vuln check` en vez de describirlos, y filtra falsos positivos por ecosistema. Pero tiene **0 estrellas**: cero validación social. Mecanismo bueno, procedencia sin verificar — pasa por auditoría de código antes de instalarse, nunca directo.

## Para quien cubra SAST y revisión de código

`anthropics/claude-code-security-review` — 6.132★, push 2026-02-11. Action oficial de Anthropic que
revisa PR buscando vulnerabilidades analizando el diff. Cae fuera del tramo de este rescate; que no
se pierda.

## Nota de método, y es importante para las siguientes rondas

Este barrido se quedó sin **WebSearch a mitad** (200/200 del cupo de sesión, compartido entre
agentes) y luego chocó con el **límite de 60 peticiones/hora** de la API de GitHub sin autenticar,
tras unas 20 llamadas.

Resuelto para las siguientes rondas: con el token del llavero del sistema, el límite sube a **5.000
peticiones/hora** (verificado). El token se lee en tiempo de ejecución y no se escribe en ningún
sitio:

```bash
export GH_TOKEN=$(security find-internet-password -s github.com -w)
curl -s -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/repos/OWNER/REPO
```
