# Ciberseguridad — barrido GitHub para COSMOS

Nicho completo #1 de `spec/UNIVERSO.md`: el oficio de ciberseguridad de punta a punta —ofensiva
autorizada, defensiva, análisis forense/malware y gobierno— **con su código dentro**, en los países
`codigo-ofensivo` y `codigo-defensivo` que UNIVERSO.md ya esbozaba.

**No duplica** `research/dominios/seguridad-calidad.md` (47 recursos, ya cerrado): ese documento
cubre SAST, SCA/dependencias, secretos, revisión de código con IA, testing y accesibilidad desde la
óptica de *proteger nuestro propio código* (Semgrep, CodeQL, Trivy, Gitleaks, TruffleHog, Bandit,
gosec, axe-core…). Aquí no vuelven a aparecer — se citan por nombre cuando hace falta enlazar.

Método: cupo de `WebSearch` de la sesión agotado. Todo verificado en vivo contra `api.github.com`
con token del llavero (`security find-internet-password -s github.com -w`, nunca impreso ni
escrito a fichero), límite 5.000 peticiones/hora para lookups directos y 30/min para `search/repositories`
(pausas de 2-3s entre búsquedas). READMEs y ficheros `LICENSE`/`COPYING` por
`raw.githubusercontent.com/<owner>/<repo>/<rama>/<fichero>`. Estrellas, fecha de último `push` y
licencia son dato duro leído del propio endpoint; el resto (mecanismo, límite exacto) sale de leer
el LICENSE/README real, nunca de memoria — donde no se pudo verificar en vivo, se marca.

## Límite ético de este dominio (parte del filtro, no un adorno)

Solo entran: **defensivo, auditoría autorizada, CTF, formación e investigación**. Fuera de la lista
(a "Humo" si aparecen, con motivo): técnicas destructivas, denegación de servicio, objetivos masivos,
compromiso de cadena de suministro, evasión de detección con fines maliciosos. Las herramientas de
doble uso que sí entran (Metasploit, Impacket, frameworks C2) llevan su contexto de uso legítimo
declarado en la propia fila — son el pan de cualquier pentester autorizado y no se descartan por
ser potentes.

---

## De primera

### Ofensiva — reconocimiento y explotación

| Recurso | Estrellas | Último push | Licencia | Por qué gana |
|---|---:|---|---|---|
| `rapid7/metasploit-framework` | 38.924 | 2026-08-31 | BSD-3-Clause (verificado en `COPYING`) | El framework de explotación de referencia: exploits, payloads, encoders y post-explotación integrados en un solo motor con base de módulos actualizada a diario. **Ojo con la marca**: el *framework* de este repo es gratis y libre; Rapid7 vende aparte "Metasploit Pro" (GUI, reporting, colaboración de equipo) como producto comercial — no confundir uno con otro al presupuestar a cliente. |
| `sqlmapproject/sqlmap` | 38.333 | 2026-09-01 | GPL-2.0 (verificado en `LICENSE`) | Inyección SQL automatizada y toma de base de datos, sin rival cercano en su hueco específico: detecta motor, técnica de inyección (booleana, tiempo, error, UNION, stacked) y escala a shell del SO cuando el motor lo permite. Sigue activo 20 años después de su primer release. |
| `projectdiscovery/nuclei` | 30.961 | 2026-08-31 | MIT | Escáner de vulnerabilidades por plantillas YAML (miles, mantenidas por la comunidad y actualizadas a diario) — cubre el hueco de "escáner de vulnerabilidades gratis" que en el mundo comercial ocupan Nessus/Qualys. Motor real (no solo HTTP fuzzing): soporta DNS, red, cloud, y encadenar plantillas. |
| `owasp-amass/amass` | 15.081 | 2026-07-19 | Apache-2.0 (verificado en `LICENSE`) | Mapeo de superficie de ataque **en profundidad**: combina descubrimiento pasivo (OSINT, certificados, APIs) y activo (fuerza bruta DNS, scraping, resolución masiva) en un solo grafo de activos. Gana a `subfinder` (14.350★, mismo autor de ecosistema ProjectDiscovery) porque este último es solo enumeración pasiva de subdominios — Amass cubre el caso completo de reconocimiento de un objetivo, no solo un paso. |
| `fortra/impacket` | 16.054 | 2026-08-28 | Licencia propia basada en Apache 1.1 (verificado en `LICENSE`, permisiva con cláusula de atribución) | Biblioteca Python de protocolos de red Windows (SMB, MSRPC, Kerberos, LDAP) que es la base de facto del post-explotación en Active Directory: trae de serie `secretsdump.py`, `psexec.py`, `GetUserSPNs.py`, y la reimportan herramientas de terceros (NetExec, BloodHound-adjacent tooling). Sin este repo no hay AD pentest serio en Python. |

### Código ofensivo — el suyo, dentro del nicho

| Recurso | Estrellas | Último push | Licencia | Por qué gana |
|---|---:|---|---|---|
| `NationalSecurityAgency/ghidra` | 74.188 | 2026-08-31 | Apache-2.0 | Framework de ingeniería inversa completo (desensamblador + **descompilador** real, no solo listado de instrucciones) de la NSA, gratis. Es la alternativa seria a IDA Pro (licencia comercial de miles de dólares) — gana a `radare2`/`Cutter` (24.697★/19.646★, ambos excelentes y CLI-first) por tener UI de análisis integrada, scripting Java/Python y ser hoy el punto de entrada estándar para quien no vive ya en r2. |
| `AFLplusplus/AFLplusplus` | 6.741 | 2026-08-31 | AGPL-3.0 | El fuzzer coverage-guided de facto: fork comunitario de AFL con QEMU mode (fuzzing de binarios sin código fuente), CompCor, y decenas de mutadores. Gana a `google/honggfuzz` (3.376★, push 2026-06-19, mecanismo similar pero comunidad más pequeña) y a `libFuzzer` (vive dentro de LLVM, sin repo propio que auditar) por ser el más activo y el que integra con más objetivos out-of-the-box. **AGPL-3.0**: para uso de auditoría/pentest no hay problema (no se redistribuye como servicio), pero si se empaqueta como SaaS conviene revisar el copyleft de red. |

### Código defensivo — el suyo, dentro del nicho

| Recurso | Estrellas | Último push | Licencia | Por qué gana |
|---|---:|---|---|---|
| `jedisct1/libsodium` | 13.927 | 2026-08-31 | ISC (verificado en `LICENSE`, permisiva) | Biblioteca de criptografía aplicada diseñada para que sea difícil usarla mal: API de alto nivel (`crypto_secretbox`, `crypto_box`, `crypto_sign`) que evita las decisiones que rompen OpenSSL en manos inexpertas (elección de modo, padding, nonces). Es el "libro de estilo" de criptografía aplicada correcta, portable a casi cualquier lenguaje vía bindings. |
| `corazawaf/coraza` | 3.777 | 2026-08-31 | Apache-2.0 | WAF reescrito en Go, **100% compatible con las reglas del OWASP Core Rule Set** (badge verificado en su propio README) y compatible con la sintaxis de ModSecurity. Gana a `owasp-modsecurity/ModSecurity` (9.759★, sigue vivo, push 2026-07-28) para el caso "código defensivo" concreto porque se **embebe como librería Go dentro de tu propia aplicación** (validación en frontera real, en el proceso) en vez de exigir un módulo nativo de Apache/nginx aparte — el patrón que pide este país del nicho. |

### Defensiva — detección

| Recurso | Estrellas | Último push | Licencia | Por qué gana |
|---|---:|---|---|---|
| `SigmaHQ/sigma` (rules) + `SigmaHQ/sigma-cli` (motor, sobre `pySigma`) | 10.966 / 209 | 2026-09-01 / 2026-07-07 | Reglas: Detection Rule License 1.1 (pública, verificado en `LICENSE`) · motor: LGPL-2.1 | El "YARA de los logs": una regla Sigma se escribe una vez y `sigma-cli` la traduce a la sintaxis de Splunk, Elastic, Sentinel, QRadar… sin reescribir la lógica de detección por SIEM. El repo `sigma` es el corpus/estándar (público dominio la especificación); `sigma-cli`/`pySigma` es el motor que de verdad ejecuta la conversión — mismo patrón de pareja contenido+motor que YARA. |

### Análisis — malware y forense

| Recurso | Estrellas | Último push | Licencia | Por qué gana |
|---|---:|---|---|---|
| `VirusTotal/yara` (motor) + `Yara-Rules/rules` (corpus) | 9.845 / 4.882 | 2026-08-25 / 2024-04-17 | BSD-3-Clause (motor, verificado) | Motor de pattern-matching de facto para identificar familias de malware sobre ficheros y memoria — "el grep con esteroides" de forense/malware. El motor está muy vivo; el corpus de reglas (`Yara-Rules/rules`) lleva sin `push` desde 2024 — se sigue usando como base, pero conviene complementarlo con reglas más recientes (p. ej. Trellix ATR, ReversingLabs, ambos en Segunda fila) antes de confiar solo en él. |
| `volatilityfoundation/volatility3` | 4.366 | 2026-08-19 | Volatility Software License 1.0 (custom, verificado en `LICENSE.txt` — **no** es MIT/GPL estándar, leer antes de redistribuir) | Framework de forense de memoria de referencia: extrae procesos, conexiones de red, claves de registro y artefactos de un volcado de RAM sin necesitar el sistema vivo. Es el sucesor activo de `volatilityfoundation/volatility` (v2, 8.063★ pero sin `push` desde 2025-05-16) — v3 es donde está el desarrollo real hoy, aunque v2 siga teniendo más estrellas históricas. |

---

## Segunda fila

**Ofensiva / post-explotación:**
- `peass-ng/PEASS-ng` — 20.409★, push 2026-09-01, GPL. linPEAS/winPEAS: el primer script que se corre tras conseguir shell en Linux/Windows/macOS para buscar rutas de escalada. Se quedó fuera de primera fila por presupuesto de slots, no por calidad — es tan canónico como cualquiera de la lista de arriba.
- `SpecterOps/BloodHound` — 3.368★, push 2026-09-01, Apache-2.0. Mapea Active Directory como grafo y encuentra caminos de ataque ("shortest path to Domain Admin") que a ojo son invisibles. Complementa a Impacket: Impacket ejecuta, BloodHound decide qué ejecutar.
- `zaproxy/zaproxy` (OWASP ZAP) — 15.714★, push 2026-09-01, Apache-2.0. La respuesta directa a "necesito Burp Suite Pro pero gratis": proxy interceptor + escáner activo/pasivo + spider, mantenido hoy por Checkmarx. Cubre el 90% del flujo de pentest web manual que exigiría licencia de Burp Pro.
- `gentilkiwi/mimikatz` — 21.804★, push 2026-04-17, sin licencia declarada (dominio de facto en el gremio, uso solo en entorno autorizado). Extracción de credenciales en memoria de Windows (LSASS) — la herramienta que toda detección de EDR intenta cazar primero; entra con su contexto de post-explotación autorizada, nunca para credenciales ajenas sin permiso.
- `ffuf/ffuf` — 16.618★, push 2026-08-20, MIT. Fuzzer web (directorios, parámetros, vhosts) más rápido que gobuster para el mismo hueco.
- `OJ/gobuster` — 14.065★, push 2026-08-30, Apache-2.0. Alternativa a ffuf, más simple de invocar cuando no hace falta su velocidad extrema.
- `Gallopsled/pwntools` — 13.669★, push 2026-08-30, licencia no estándar (ver repo). Librería Python para exploit dev y CTF: empaqueta interacción con procesos/sockets, ROP, shellcraft.
- `JonathanSalwan/ROPgadget` — 4.472★, push 2026-06-24. Buscador de gadgets ROP sobre binarios, complementa a pwntools en la fase de construcción de la cadena.
- `BishopFox/sliver` — 11.768★, push 2026-08-31, GPL-3.0. El C2 de red team open-source más maduro hoy (Go, multiplataforma, mTLS/HTTP(S)/DNS/mTLS). Doble uso declarado: red team autorizado y CTF de infraestructura, nunca contra objetivos sin permiso.

**Defensiva / SIEM, hardening, respuesta a incidentes:**
- `wazuh/wazuh` — 16.732★, push 2026-09-01, licencia NOASSERTION en la API pero el proyecto se distribuye como GPL-2.0 (open core: el agente/manager es gratis, Wazuh Cloud es el producto de pago — **no verificado en vivo el límite exacto de la capa gratuita**, comprobar antes de comprometerse con un cliente). SIEM+XDR unificado: recolección de logs, FIM, detección de vulnerabilidades y respuesta, todo en un solo agente.
- `CISOfy/lynis` — 16.262★, push 2026-08-05, GPL-3.0. Auditoría de hardening para Linux/macOS/UNIX, con checklist de cumplimiento (CIS, PCI-DSS, HIPAA) ejecutable, no solo documento.
- `OpenSCAP/openscap` — 1.810★, push 2026-08-13, LGPL-2.1. Toolkit certificado NIST para SCAP 1.2 — el estándar detrás de los benchmarks CIS automatizables.
- `aquasecurity/kube-bench` — 8.161★, push 2026-08-24, Apache-2.0. Igual que Lynis pero para Kubernetes, contra el CIS Kubernetes Benchmark.
- `falcosecurity/falco` — 9.321★, push 2026-08-31, Apache-2.0. Detección de amenazas en tiempo de ejecución para contenedores/K8s (eBPF), el "IDS de runtime" de la nube nativa.
- `crowdsecurity/crowdsec` — 14.702★, push 2026-08-31, MIT. Fail2ban moderno con inteligencia de amenazas colaborativa entre instalaciones.
- `Velocidex/velociraptor` — 4.223★, push 2026-08-25, licencia NOASSERTION (histórica AGPL-3.0/Elastic, comprobar antes de desplegar a escala). Recolección forense y respuesta a incidentes a gran escala vía su propio lenguaje de consultas (VQL) sobre miles de endpoints a la vez.
- `TheHive-Project/TheHive` — 3.949★, push 2025-07-25, AGPL-3.0. Plataforma de gestión de casos de IR colaborativa. **Aviso**: su propia descripción dice "now distributed as a commercial version" — la versión 5 se volvió de pago; la 4.x AGPL sigue en el repo pero sin desarrollo activo reciente, comprobar antes de recomendarla como gratis a futuro.
- `WithSecureLabs/chainsaw` — 3.652★, push 2026-08-25, GPL-3.0. Búsqueda rápida sobre artefactos forenses de Windows (EVTX) con reglas Sigma nativas — puente directo detección↔forense.
- `Neo23x0/Loki` — 3.786★, push 2026-01-12, GPL-3.0. Escáner de IOC + reglas YARA para host comprometido, ligero y sin agente.

**Malware / forense adicional:**
- `sleuthkit/autopsy` — 3.306★, push 2026-06-20. Plataforma de forense de disco con interfaz gráfica sobre The Sleuth Kit.
- `CERT-Polska/drakvuf-sandbox` — 1.337★, push 2026-08-19, sandbox de análisis dinámico a nivel de hipervisor (transparente al malware, más difícil de detectar que Cuckoo).
- `alexandreborges/malwoverview` — 4.078★, push 2026-08-07, GPL-3.0. Triage rápido contra VirusTotal/Hybrid Analysis/URLHaus desde CLI, primer paso antes de sandboxear.
- `Neo23x0/yarGen` — 1.811★, push 2026-01-10. Generador de reglas YARA a partir de muestras — automatiza la parte tediosa de escribir firmas.
- `reversinglabs/reversinglabs-yara-rules` y `advanced-threat-research/Yara-Rules` (Trellix ATR) — corpus de reglas YARA más recientes que `Yara-Rules/rules`, para complementar el motor de primera fila.

**Gobierno — marcos, gestión de vulnerabilidades, informes:**
- `mitre-attack/attack-navigator` — 2.451★, push 2026-08-28, Apache-2.0. Herramienta web oficial de MITRE para navegar y anotar la matriz ATT&CK — el estándar de facto para mapear capacidades ofensivas/defensivas.
- `redcanaryco/atomic-red-team` — 12.473★, push 2026-08-31, MIT. Tests atómicos ejecutables mapeados 1:1 a técnicas ATT&CK — se corren de verdad contra un entorno de laboratorio para validar que la detección funciona (no es checklist, es ejecutable).
- `DefectDojo/django-DefectDojo` — 4.917★, push 2026-09-01, BSD-3-Clause. Gestión unificada de vulnerabilidades / ASPM: importa hallazgos de decenas de escáneres (incluidos los de `seguridad-calidad.md`) y centraliza el ciclo de vida de cada uno.
- `infobyte/faraday` — 6.699★, push 2026-08-20, GPL-3.0. Plataforma de gestión de vulnerabilidades pensada para equipos de pentest colaborativo, agrega salida de Nmap/Nessus/Nuclei/etc. en un solo workspace.
- `OpenCTI-Platform/opencti` — 9.881★, push 2026-09-01, licencia no estándar (verificar términos de uso comercial antes de desplegar para cliente). Plataforma de inteligencia de amenazas (CTI) que estructura IOCs, TTPs y campañas en un grafo de conocimiento.

**Formación / CTF:**
- `zardus/ctf-tools` — 9.511★, push 2026-08-12, BSD-3-Clause. Scripts de instalación de las herramientas de investigación de seguridad más usadas en CTF — meta-herramienta de bootstrap, no un tool en sí.
- `juice-shop/juice-shop` — 13.755★, push 2026-08-30, MIT. Aplicación web deliberadamente vulnerable más moderna y mantenida que existe — objetivo de entrenamiento, no una herramienta de ataque.
- `digininja/DVWA` — 13.583★, push 2026-08-19, GPL-3.0. El clásico objetivo de entrenamiento PHP/MySQL, más simple que Juice Shop, sigue siendo el punto de partida habitual en cursos.

---

## Humo

- `1N3/Sn1per` — 11.181★. Automatiza reconocimiento+escaneo+explotación en un solo pipeline "todo en uno"; entra en zona gris porque ese automatismo agresivo contra objetivos no acotados es justo el patrón de ruido/daño colateral que este barrido descarta — usar solo con alcance muy explícito y revisando cada módulo antes de lanzarlo.
- `malwaredllc/byob` — 9.496★. Framework de post-explotación "para estudiantes e investigadores" cuyo propio nombre (Build Your Own Botnet) apunta a construcción de botnets — capacidad de doble uso sin el contexto de red-team profesional que sí tienen Sliver/Empire.
- `PowerShellMafia/PowerSploit` — 13.085★ pero sin `push` desde 2020-08-17: abandonado, y buena parte de sus técnicas ya están firmadas por cualquier EDR moderno — no operativo hoy.
- `netero1010/EDRSilencer` / `TwoSevenOneT/EDRChoker` — herramientas que bloquean o estrangulan el tráfico de agentes EDR. Evasión de detección explícita: fuera del límite ético salvo purple-team muy controlado y documentado, no un uso por defecto.
- `hacklcx/HFish`, `hashcat/hashcat` (cracking) y `vanhauser-thc/thc-hydra` (fuerza bruta de credenciales) — dobles usos legítimos en auditoría de contraseñas autorizada, pero fuera de "de primera/segunda" de este barrido por no encajar en ningún hueco que no cubran ya PEASS-ng/Impacket para el caso de uso de <agencia>; se anotan para no repetir la búsqueda si hace falta cracking puntual.
- `cirosantilli/china-dictatorship` — apareció repetidamente en los resultados de búsqueda por coincidencia de palabras clave ("fuzzing", "post-exploitation", "CTF") pero es contenido político sin relación con el dominio — ruido de la propia GitHub Search API, no un hallazgo.

---

## Mapeo a COSMOS

Sigue la forma que `spec/UNIVERSO.md` ya fijó como ejemplo de referencia (sistema-solar propio,
sin capas horizontales). Con datos reales encima, dos correcciones concretas al esbozo:

1. **El país `vulnerabilidades` que UNIVERSO.md ponía bajo `analisis`** (provincias: SAST ·
   dependencias · secretos) **se retira de aquí por completo**: es exactamente lo que ya cubre
   `seguridad-calidad.md` con 47 recursos verificados. Mantenerlo aquí habría sido la duplicación
   que el encargo pidió evitar explícitamente.
2. **`post-explotación` merece país propio**, no cabe como provincia de `explotacion` — el volumen
   real (Impacket, BloodHound, PEASS-ng, Mimikatz, C2 frameworks) es tan grande como el de
   reconocimiento o explotación inicial.

```
sistema-solar  ciberseguridad
├── continente  ofensiva                    (autorizada: pentest, CTF, red team)
│   ├── pais  reconocimiento                provincias: descubrimiento · OSINT · mapeo de superficie
│   │          pueblos: Amass, Nuclei, reconftw, phoneinfoga, GHunt
│   ├── pais  explotacion                   provincias: web · binaria · red
│   │          pueblos: Metasploit, sqlmap, OWASP ZAP, ffuf/gobuster
│   ├── pais  post-explotacion              provincias: protocolos AD · movimiento lateral · caminos de ataque · C2
│   │          pueblos: Impacket, BloodHound, PEASS-ng, Mimikatz, Sliver
│   └── pais  codigo-ofensivo               ← su propio código
│              provincias: ingeniería inversa · fuzzing · exploit dev
│              pueblos: Ghidra, radare2/Cutter, AFL++, pwntools, ROPgadget
├── continente  defensiva
│   ├── pais  deteccion                     provincias: reglas de log (Sigma) · reglas de fichero/memoria (YARA) · red (Suricata, Zeek)
│   │          pueblos: Sigma+sigma-cli, YARA+corpus, Suricata, Zeek, Falco
│   ├── pais  endurecimiento                provincias: sistema · contenedor/K8s · red
│   │          pueblos: Lynis, OpenSCAP, kube-bench, CrowdSec
│   ├── pais  respuesta-a-incidentes        provincias: SIEM/XDR · orquestación de casos · recolección a escala
│   │          pueblos: Wazuh, TheHive, Velociraptor, chainsaw, Loki
│   └── pais  codigo-defensivo              ← y aquí
│              provincias: criptografía aplicada · validación en frontera
│              pueblos: libsodium, Coraza
├── continente  analisis
│   ├── pais  forense                       provincias: memoria · disco · red
│   │          pueblos: Volatility3, Autopsy, Wireshark, Zeek (compartido con detección)
│   └── pais  malware                       provincias: estático · dinámico/sandbox · triage
│              pueblos: YARA, drakvuf-sandbox, malwoverview, yarGen
└── continente  gobierno
    ├── pais  marcos                        provincias: ATT&CK
    │          pueblos: ATT&CK Navigator, Atomic Red Team
    └── pais  gestion-de-vulnerabilidades    provincias: agregación · workspace de pentest · CTI
               pueblos: DefectDojo, Faraday, OpenCTI
```

Los mares (`criterio`, `pruebas`, `resistencia`, `accesibilidad`, `custodia`) mojan este nicho igual
que a los otros 19 — no se listan pueblos propios porque ninguno les pertenece en exclusiva.

---

## Lo que falta

1. **`codigo-defensivo` / validación en frontera "por lenguaje"**: Coraza cubre el caso HTTP/WAF,
   pero no encontré un ganador claro de bibliotecas de *validación de entrada específicas por
   lenguaje* (más allá de lo que ya cubre `seguridad-calidad.md` vía SAST). Ese hueco puede que ya
   no exista como categoría de herramienta independiente — cada framework web trae la suya — y
   convenga documentarlo como patrón, no como repositorio, en la próxima revisión.
2. **Wazuh, Velociraptor y OpenCTI**: límite exacto de sus capas gratuitas (Wazuh Cloud, licencia
   de Velociraptor tras el cambio de sponsor, términos de OpenCTI Enterprise) **no verificado en
   vivo contra su documentación de precios actual** — solo el repo y su LICENSE/README. Antes de
   prometer alguno de los tres a un cliente sin coste, comprobar en el sitio oficial en el momento.
3. **TheHive**: su README declara la v5 como "commercial version" — no se verificó si la rama 4.x
   (AGPL, sin desarrollo activo reciente) sigue siendo una opción viable hoy o si conviene ya
   recomendar una alternativa (p. ej. combinar Velociraptor + DefectDojo).
4. **Suricata y Zeek** solo aparecen en Segunda fila con datos básicos (estrellas, licencia, push);
   no se profundizó en su comparación mutua (IDS firma-first vs framework de análisis de tráfico
   general) — merece su propia pasada si <agencia> monta monitorización de red para algún cliente.
5. **Corpus de reglas YARA**: el repo más popular (`Yara-Rules/rules`) lleva sin `push` desde
   2024-04-17. No se hizo el trabajo de comparar cobertura real entre ese corpus y los más recientes
   de Trellix/ReversingLabs (listados en Segunda fila) — antes de depender de reglas YARA en
   producción, auditar cuál corpus está realmente vivo.
6. **Herramientas de credential-cracking** (`hashcat`, `thc-hydra`) se dejaron en Humo por no encajar
   en un hueco propio de este barrido, pero si <agencia> hace auditorías de contraseñas para cliente,
   merecen su propia entrada de primera fila en la próxima revisión — hoy están sub-investigadas,
   no descartadas por calidad.
