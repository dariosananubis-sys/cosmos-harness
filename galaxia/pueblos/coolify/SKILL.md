---
cosmos: pueblo
nombre: coolify
padre: infraestructura/despliegue
resumen: PaaS autoalojado (deploy git push, SSL, bases de datos) en tu propio servidor; sin cuota mensual.
---

https://github.com/coollabsio/coolify · Apache-2.0 · 61.334★ · último push 2026-09-02 (comprobado 2026-09-03)

```bash
# instalacion sobre un servidor propio ya aprovisionado (con ansible/opentofu, por ejemplo)
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

```bash
# desde la UI (http://SERVIDOR-DEL-PROYECTO:8000) se conecta un repo git y cada push a la rama
# elegida dispara build + deploy automatico; o por API:
curl -X POST https://SERVIDOR-DEL-PROYECTO/api/v1/deploy \
  -H "Authorization: Bearer TOKEN-DEL-PROYECTO" \
  -d "uuid=UUID-DE-LA-APP"
```

Gana a Vercel/Render/Railway en que corre en **tu propio servidor**: mismo flujo de "conecta el
repo y haz push para desplegar", certificados SSL automáticos y bases de datos con un clic, pero
sin cuota mensual por proyecto ni límites de un plan gratuito — el coste es el servidor donde
corre, ya pagado o propio. Encaja justo después de `ansible`/`opentofu` en este mismo país: esos
preparan y configuran el servidor, `coolify` es la capa de deploy continuo encima.

Ojo: **tú eres el operador** — parches de seguridad, backups del propio Coolify y capacidad del
servidor son responsabilidad de quien lo instala, a diferencia de un PaaS gestionado. Un solo
servidor sin failover es un punto único de fallo: si cae la máquina, caen todos los despliegues
que gestiona. Y es un proyecto activo pero más joven que las alternativas gestionadas: cambios de
versión mayor pueden requerir migración manual de la configuración. Y el instalador por
`curl | bash` ejecuta código remoto sin revisar: para producción, leer el guion antes.
