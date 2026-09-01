# Infraestructura y DevOps — que las cosas corran y no se caigan

Barrido GitHub para COSMOS. Dominio: contenedores/orquestación, CI/CD, IaC, proxies inversos,
self-hosting, bases de datos en producción (backup/restore/réplicas), monitorización/alertas,
redes/DNS, TLS, colas/cron, gestión de secretos.

Método: WebSearch (16 consultas, hasta agotar el presupuesto de sesión) + WebFetch directo a las
páginas de GitHub de los candidatos más fuertes para verificar estrellas/licencia/actividad en
vivo. `curl` a la API de GitHub quedó bloqueado por rate-limit de IP compartida (403, "API rate
limit exceeded") — no es una limitación de la tarea, es la red de este Mac; documentado por si se
repite.

Fecha del barrido: 2026-09-01. Estrellas aproximadas al momento de la consulta.

---

## De primera

Máximo 10. Elegidos por: cero coste, self-hosted real, mecanismo verificable (no prosa), y peso
puesto en backup/recuperación porque "una copia que nunca se ha restaurado no es una copia".

1. **[awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted)** — 316k★, lista
   curada de software libre auto-alojable por categoría. **Por qué gana**: es el índice maestro —
   antes de evaluar una herramienta nueva, mirar aquí si ya hay una entrada madura evita reinventar
   la búsqueda. Mecanismo: lista Markdown mantenida por PR, con criterios de inclusión (licencia
   libre, sin llamada obligatoria a servicio de pago).

2. **[Caddy](https://github.com/caddyserver/caddy)** — 75.4k★, Apache-2.0, activo. **Por qué gana**:
   único servidor web mainstream con HTTPS automático de fábrica (ACME/Let's Encrypt/ZeroSSL
   integrado, sin cron de renovación aparte). Un `Caddyfile` de 3 líneas reemplaza nginx+certbot+cron.
   Mecanismo: reverse proxy + terminación TLS + renovación automática vía ACME embebido.

3. **[Gitea](https://github.com/go-gitea/gitea)** (+ Gitea Actions) — 57.7k★, MIT, activo.
   **Por qué gana**: git self-hosted y CI/CD en el mismo binario — evita montar un servidor de git
   Y un runner de CI por separado (elimina la necesidad de Woodpecker/Drone para una agencia
   pequeña). Actions reutiliza sintaxis de GitHub Actions. Mecanismo: servidor Go monolítico +
   runners Actions opcionales vía Docker.

4. **[restic](https://github.com/restic/restic)** — 35.8k★, BSD-2, muy activo. **Por qué gana**:
   backup cifrado + deduplicado con foco explícito en que "lo importante es el restore, no el
   backup" — trae `restic restore` y `restic mount` (FUSE) para verificar sin reconstruir todo.
   Mecanismo: snapshots incrementales cifrados a S3/SFTP/local/Backblaze, comando `check` de
   integridad del repositorio.

5. **[borgmatic](https://github.com/borgmatic-collective/borgmatic)** — 2.3k★, GPL-3.0, activo.
   **Por qué gana**: es la pieza que le falta a un backup "hecho a mano" — orquesta BorgBackup con
   config declarativa YAML, corre comprobaciones de integridad programadas (`checks: repository /
   archives` cada N semanas) y **empuja el resultado a un dead-man's-switch** (Healthchecks, Uptime
   Kuma, ntfy, Cronitor, Pushover…). Convierte "hice un backup" en "algo me avisa si el backup
   falla o no llega".

6. **[Healthchecks](https://github.com/healthchecks/healthchecks)** (self-hosted) — 10.3k★,
   BSD-3-Clause, activo (Python/Django). **Por qué gana**: es el dead-man's-switch que cierra el
   círculo de backups/crons — cada job hace un `curl` de "sigo vivo" al terminar; si no llega a
   tiempo, alerta. Sin esto, un cron roto falla en silencio para siempre. Mecanismo: servidor HTTP
   que espera pings periódicos + reglas de "no llegó a tiempo" → email/Slack/ntfy/webhook.

7. **[Uptime Kuma](https://github.com/louislam/uptime-kuma)** — ~90k★ (fuente: wiki del proyecto,
   ago-2026), activo. **Por qué gana**: monitorización de disponibilidad (HTTP, TCP, DNS, ping) con
   UI propia y página de estado pública, sin depender de un SaaS externo. Complementa a Healthchecks
   (que vigila "¿corrió el job?") vigilando "¿responde el sitio?".

8. **[ntfy](https://github.com/binwiederhier/ntfy)** — 33.9k★, Apache-2.0/GPLv2 dual, activo.
   **Por qué gana**: notificaciones push a móvil/escritorio vía `curl -d "mensaje" ntfy.sh/topico`,
   sin broker de mensajería ni cuenta de terceros — binario Go único + SQLite. Es el receptor barato
   al que apuntan borgmatic, Healthchecks y Uptime Kuma cuando algo se rompe.

9. **[sops](https://github.com/getsops/sops)** (+ [age](https://github.com/FiloSottile/age) como
   backend de cifrado) — 23k★, MPL-2.0, activo. **Por qué gana**: cifra secretos **dentro del propio
   repo git**, sin levantar un servidor de secretos — para una agencia con pocos proyectos es
   proporción correcta frente a Vault/Infisical (que exigen Postgres+Redis corriendo 24/7).
   Mecanismo: cifra valores de un YAML/JSON con una clave age/PGP, el diff en git queda cifrado.

10. **[VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics)** — 17.6k★, Apache-2.0,
    activo. **Por qué gana**: base de datos de métricas compatible con Prometheus pero con "hasta 7x
    menos RAM y 7x menos almacenamiento" según el propio proyecto — para monitorizar 1-3 VPS de
    cliente, un solo binario VictoriaMetrics + Grafana pesa mucho menos que Prometheus+Thanos.

---

## Segunda fila

- **[Portainer](https://github.com/portainer/portainer)** — GUI de gestión Docker/K8s con roles
  multiusuario; más pesado que Dockge, compensa solo si varias personas necesitan permisos distintos.
- **[Dockge](https://github.com/louislam/dockge)** — 24.2k★, gestor visual de `compose.yaml` (del
  mismo autor que Uptime Kuma), edita/levanta/para stacks reales sin abstraer el fichero compose.
  Más simple que Portainer; buena opción por defecto para 1-2 admins.
- **[Watchtower](https://github.com/containrrr/watchtower)** — auto-actualiza contenedores a la
  última imagen. **Escéptico**: puede romper producción en silencio (una imagen `latest` con breaking
  change se despliega sola a las 3am). Preferir Diun (solo avisa) + bump manual revisado.
- **[Diun](https://github.com/crazy-max/diun)** — notifica cuando hay imagen Docker nueva, sin
  aplicar el cambio. Complementa a Watchtower quitándole el auto-apply peligroso.
- **[Traefik](https://github.com/traefik/traefik)** — proxy inverso con descubrimiento nativo por
  labels de Docker/K8s y ACME integrado. Config más verbosa que Caddy; compensa en entornos
  multi-tenant o con Kubernetes real.
- **[Nginx Proxy Manager](https://github.com/NginxProxyManager/nginx-proxy-manager)** — GUI sobre
  nginx+Let's Encrypt; útil si el equipo no quiere tocar un Caddyfile.
- **[Woodpecker CI](https://github.com/woodpecker-ci/woodpecker)** — 7.8k★, Apache-2.0, ~100MB RAM
  servidor + ~30MB agente. CI/CD ligero cuando el git host NO es Gitea (p.ej. ya se usa Forgejo o
  GitHub y se quiere runner propio).
- **[k3s](https://github.com/k3s-io/k3s)** — Kubernetes ligero (CNCF). **Proporción**: solo compensa
  con >1 servidor, autoscaling real o >10 servicios con ciclos de deploy independientes; para una
  agencia con webs de cliente en VPS individuales es sobreingeniería casi siempre — Docker Compose
  basta.
- **[OpenTofu](https://github.com/opentofu/opentofu)** — 30k★, MPL-2.0, activo. Fork de Terraform
  bajo Linux Foundation tras el cambio de licencia de HashiCorp (BSL); drop-in compatible, mismo
  HCL. Preferible a Terraform si se empieza de cero hoy.
- **terraform-aws-modules / Azure Verified Modules / terraform-google-modules** — módulos oficiales
  de cada nube, los más descargados del Registry (`iam` 235M+, `vpc` 126M+ descargas). Usar antes de
  escribir HCL desde cero para recursos comunes (VPC, IAM, buckets).
- **[Ansible](https://github.com/ansible/ansible)** — sin agente, SSH puro. Buen punto intermedio
  antes de justificar Terraform completo: para "configurar 3 VPS iguales" sobra con Ansible, no
  hace falta estado remoto ni providers.
- **pgbackrest / wal-g** — backup PITR (point-in-time recovery) específico de Postgres con archivado
  continuo de WAL; usar cuando `pg_dump` ya no basta (bases grandes, RPO bajo). Más pesado de operar
  que restic/borgmatic — solo para la base de datos que de verdad importa.
- **[Kopia](https://github.com/kopia/kopia)** — backup con deduplicación + UI web y app de
  escritorio; alternativa a restic cuando hace falta interfaz gráfica para quien no usa terminal.
- **Prometheus + Grafana (stack clásico)** — la referencia del sector, pero exige más operación
  (retención, cardinalidad, Alertmanager aparte) que VictoriaMetrics+Grafana para el mismo resultado.
- **[Netdata](https://github.com/netdata/netdata)** — monitorización en tiempo real de un solo host,
  cero configuración; buen primer paso antes de montar un stack completo.
- **[Infisical](https://github.com/Infisical/infisical)** — gestor de secretos self-hostable con UI,
  25k+★. Requiere Postgres+Redis corriendo siempre — justificado solo cuando el equipo crece y sops
  en git deja de ser cómodo de rotar/compartir.
- **[OpenBao](https://github.com/openbao/openbao)** — fork de Vault bajo Linux Foundation (MPL) tras
  el cambio de licencia de HashiCorp; mismo modelo de secretos dinámicos que Vault, sin BSL.
- **[Renovate](https://github.com/renovatebot/renovate)** — abre PRs automáticos para subir
  versiones de dependencias/imágenes base; mantiene CVEs a raya sin el riesgo de auto-apply de
  Watchtower (el cambio pasa por review antes de mergear).
- **Tailscale / [Headscale](https://github.com/juanfont/headscale) / [Netbird](https://github.com/netbirdio/netbird)**
  — VPN mesh sobre WireGuard para llegar a paneles de admin sin abrir puertos al público; Headscale y
  Netbird son las opciones con control-plane 100% self-hosted (Tailscale gestionado depende de su
  nube, aunque el dataplane sea WireGuard).
- **[wg-easy](https://github.com/wg-easy/wg-easy)** — WireGuard con UI web, alternativa mínima a una
  VPN mesh completa cuando solo hace falta acceso punto a punto.
- **[cloudflared](https://github.com/cloudflare/cloudflared)** — Cloudflare Tunnel; expone un
  servicio sin abrir firewall. **Nota**: depende de la capa gratuita de Cloudflare — no es
  self-hosted puro, es una dependencia de un tercero (gratis hoy, pero es su infraestructura).
- **[Sentry self-hosted](https://github.com/getsentry/self-hosted)** — 9.5k★. **Proporción al
  revés, a propósito**: para autoalojarlo hacen falta Postgres + Redis + ClickHouse + Relay +
  Symbolicator + nginx a la vez — ejemplo de cuándo NO compensa migrar de un SaaS gratuito de error
  tracking a self-hosted para un cliente pequeño.

## Humo

- **[Coolify](https://github.com/coollabsio/coolify)** — PaaS self-hosted estilo Heroku/Vercel sobre Docker, deploys con un clic.
- **[gethomepage/homepage](https://github.com/gethomepage/homepage)** — dashboard único que lista todos los servicios auto-alojados.
- **[Glances](https://github.com/nicolargo/glances)** — monitor de recursos de un solo host, terminal + web.
- **[AdGuard Home](https://github.com/AdguardTeam/AdGuardHome)** — DNS + bloqueo de anuncios en un binario Go, DoH/DoT integrado.
- **Pi-hole** — el sinkhole DNS clásico, la comunidad más grande, corre en una Raspberry Pi.
- **Technitium DNS Server** — servidor DNS completo (recursivo + autoritativo + DHCP), más que un bloqueador.
- **acme.sh** — cliente ACME más popular por estrellas, 80+ proveedores DNS para wildcard certs.
- **Certbot (EFF)** — cliente ACME de referencia, mayor ecosistema de plugins.
- **[acme-ca-server](https://github.com/knrdl/acme-ca-server)** — CA ACME privada self-hosted (un "Let's Encrypt" interno para redes cerradas).
- **[Databasus](https://github.com/databasus/databasus)** — backup Postgres nuevo con PITR + verificación de restore + UI web; listado en el catálogo oficial de postgresql.org desde ene-2026, aún por ver rodaje real.
- **[DBackup](https://github.com/Skyfay/dbackup)** — backup multi-motor (MySQL/Postgres/Mongo/MSSQL/Redis…) con UI web y múltiples destinos.
- **[Databasement](https://github.com/David-Crty/databasement)** — gestor de backup multi-BD con UI web y túnel SSH.
- **[cronpilot](https://github.com/orangecoding/cronpilot)** — gestor de cron self-hosted con UI móvil y push por ntfy.
- **[Chadburn](https://github.com/PremoWeb/chadburn)** — cron nativo de Docker, reacciona a labels de contenedores.
- **OpenObserve / SigNoz / Perses / qryn** — stacks de observabilidad "todo en uno" que sustituyen Prometheus+Loki+Tempo+Grafana en un binario o pocos servicios.
- **[n8n](https://github.com/n8n-io/n8n)** — automatización de flujos self-hosted (alternativa a Zapier); sirve como orquestador de tareas programadas más rico que cron cuando hay lógica condicional.
- **Temporal** — motor de workflows duraderos; solo se justifica con orquestación a escala real, no para las tareas programadas de una agencia pequeña.

---

## Mapeo a COSMOS

```
sistema-solar  Software / Ingeniería (todo el conocimiento técnico de COSMOS)
└─ planeta     Ingeniería y Producto
   └─ continente  Operaciones y Plataforma
      └─ país         INFRAESTRUCTURA Y DEVOPS   ← este dominio
         ├─ provincia  Contenedores y Orquestación
         │   ├─ ciudad  Docker / Compose        → pueblos: Dockge, Portainer, Watchtower, Diun
         │   └─ ciudad  Kubernetes ligero        → pueblos: k3s (solo si toca el umbral de proporción)
         ├─ provincia  CI/CD
         │   └─ ciudad  Runners self-hosted      → pueblos: Gitea Actions, Woodpecker CI
         ├─ provincia  Infraestructura como Código
         │   ├─ ciudad  Terraform / OpenTofu     → pueblos: OpenTofu, módulos oficiales por nube
         │   └─ ciudad  Config management        → pueblos: Ansible
         ├─ provincia  Servidores y Proxies Inversos
         │   └─ ciudad  TLS automático           → pueblos: Caddy, Traefik, Nginx Proxy Manager
         ├─ provincia  Self-hosting y Alojamiento Propio
         │   └─ ciudad  Catálogo                 → pueblo: awesome-selfhosted (índice maestro)
         ├─ provincia  Bases de Datos en Producción
         │   ├─ ciudad  Copias de seguridad       → pueblos: restic, borgmatic, Kopia, pgbackrest, wal-g
         │   └─ ciudad  Verificación de restore    → pueblo: comando `check`/`restore` de cada uno (no opcional)
         ├─ provincia  Monitorización y Alertas
         │   ├─ ciudad  Métricas                  → pueblos: VictoriaMetrics, Prometheus+Grafana, Netdata
         │   └─ ciudad  Uptime / dead-man's-switch → pueblos: Uptime Kuma, Healthchecks, ntfy, Gotify
         ├─ provincia  Redes y DNS
         │   ├─ ciudad  VPN mesh de administración → pueblos: Tailscale, Headscale, Netbird, wg-easy
         │   └─ ciudad  DNS/filtrado               → pueblos: AdGuard Home, Pi-hole, Technitium
         ├─ provincia  Certificados TLS
         │   └─ ciudad  ACME                       → pueblos: acme.sh, Certbot, acme-ca-server
         ├─ provincia  Colas y Trabajos Programados
         │   └─ ciudad  Cron con vigilancia         → pueblos: Healthchecks, cronpilot, Chadburn, n8n
         └─ provincia  Gestión de Secretos
             └─ ciudad  Cifrado en git vs servidor   → pueblos: sops+age (sin servidor), Infisical, OpenBao
```

Nota: la frontera entre "país" (este dominio) y los países vecinos de COSMOS (p. ej. un país de
"IA / Agentes" que cubriría E2B, microsandbox, Beam, Flowise, Dify) es que aquí solo entra lo que
hace correr y sobrevivir servicios propios — no plataformas de agentes de IA en sí, aunque comparten
mecanismo de sandboxing/contenedores con la provincia de Contenedores.

## Lo que falta

- **Cero verificación en vivo.** Todo el barrido es lectura de páginas públicas de GitHub
  (WebSearch + WebFetch); no se instaló, desplegó ni restauró nada. La afirmación "hace copias
  verificables" es lo que cada proyecto documenta de sí mismo, no una restauración presenciada por
  este agente. Antes de recomendar cualquiera de estos a un cliente real, probar el ciclo completo
  backup→restore en un entorno de prueba.
- **Presupuesto de WebSearch agotado a media tarea** ("200 of 200" saltó tras 16 consultas — parece
  un límite compartido de la cuenta/sesión, no un tope razonable para este barrido). Las últimas
  8 búsquedas planeadas (sops/age, healthchecks, riesgo watchtower/diun, colas ligeras, OpenTofu,
  ntfy/gotify, dockge/coolify, pgbackrest/wal-g) se resolvieron vía WebFetch directo a GitHub en su
  lugar — dato fiable pero sin la comparativa de terceros que trae una búsqueda normal.
- **`curl` a la API de GitHub bloqueado por rate-limit de IP** (403 "API rate limit exceeded",
  compartida con otro tráfico de esta red) — por eso las estrellas de la segunda fila y del humo se
  apoyan en snippets de búsqueda en vez de en WebFetch verificado uno a uno; puede haber desviación
  de un 10-20% en esas cifras.
- **Kubernetes real (operators, Helm charts, GitOps con ArgoCD/Flux)** no se exploró a fondo más
  allá de la nota de proporción con k3s — si algún cliente cruza el umbral de "más de un servidor",
  este dominio necesita un sub-barrido propio.
- **Colas de mensajería de verdad** (RabbitMQ, NATS, BullMQ/Redis Streams) quedaron fuera — la
  sección de "colas y trabajos programados" se resolvió con cron+vigilancia (Healthchecks,
  cronpilot, Chadburn) y n8n como orquestador ligero, no con brokers de mensajería per se. Si COSMOS
  necesita colas de trabajo pesadas (no solo tareas programadas), falta ese ángulo.
- **Gestión de secretos en Kubernetes** (External Secrets Operator, Sealed Secrets) no se cubrió —
  relevante solo si k3s deja de ser hipotético.
- Sin datos de clientes, IPs ni credenciales en este fichero, según lo pedido.
