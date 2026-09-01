---
cosmos: pueblo
nombre: openclaw
padre: agentes-ia/herramientas
resumen: Demonio que atiende mensajes de consola, chat y trabajos programados y los ejecuta hasta el final.
---

https://github.com/openclaw/openclaw · **licencia sin SPDX** (fichero `LICENSE` en el repo) · 388.435★ ·
último push 2026-09-01 (comprobado 2026-09-01). Node ≥ 22.

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
# alternativa: npm install -g openclaw@latest --allow-scripts=openclaw
openclaw onboard --install-daemon
```

Es el origen del canal autónomo que ya se usa en esta casa. Su arquitectura declarada —«gateway
confiable, ejecución no confiable, política determinista»— es la razón de que entre: la política de
permisos vive **separada** de la ejecución de herramientas, así que un canal de mensajería no autoriza
por sí mismo lo que el agente puede hacer.

Gana a `cosecha/telegram-bridge.py`, el puente propio que reenvía a la consola del asistente y
devuelve la salida: aquello resuelve el mismo hueco para un solo canal, y esto atiende consola, chat y
trabajos programados con la misma configuración.

Ojo, y es lo que más caro sale: **la licencia no tiene identificador SPDX** — GitHub la devuelve como
`NOASSERTION`. Antes de redistribuir nada derivado hay que leer el fichero, no fiarse del campo. Y el
instalador por `curl | bash` ejecuta código remoto sin revisar: para producción, leer el guion antes.
El daemon queda escuchando, así que el freno de acciones irreversibles no puede vivir solo en el
prompt.
