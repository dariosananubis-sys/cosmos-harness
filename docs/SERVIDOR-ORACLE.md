# COSMOS en un servidor gratuito de Oracle: Claude por Telegram sin el Mac encendido

Escrito el 2026-09-03. Objetivo: una máquina encendida las 24 horas, con el repo clonado, Claude Code
logueado con la cuenta del dueño y el canal de Telegram activo, para hablar con el agente desde el
móvil. Coste: 0 € (Oracle Cloud Always Free) o unos 7 € al mes en Hetzner CX32 si Oracle no da máquina.

## Por qué no Render, Hermes ni «Claw Army»

Render no es un ordenador: no hay terminal persistente, el disco se borra al redesplegar y un plan con
8 GB de RAM para el juez sale caro. Hermes u OpenClaw en un servidor serían **otro agente**, con su
propia API de pago, sin la cuenta Max ni la configuración de este harness. Lo que hace falta es un
Linux normal con root: lo mismo que el Mac, pero sin pantalla.

## Qué corre en cada sitio

| Pieza | Servidor | Mac |
|---|---|---|
| Claude Code + canal de Telegram | sí, en tmux, arranca solo | sí, cuando esté abierto |
| Juez local (Ollama, `qwen2.5:7b`, 4,7 GB) | sí, lento en CPU ARM | sí |
| BrowserOS Neo (pueblo `browseros-neo`) | **no**: es un navegador de escritorio | sí |
| Navegador del agente en el servidor | `agent-browser` o `playwright` headless | Neo |

## Pasos del dueño en la consola de Oracle (unos 15 minutos)

1. Cuenta en https://www.oracle.com/cloud/free/ con tarjeta (no cobran; sirve para verificar).
   Región de origen: **Frankfurt** (`eu-frankfurt-1`) suele tener capacidad ARM; Madrid a veces no.
   La región de origen no se puede cambiar después.
2. Compute → Instances → Create instance:
   - Image: **Ubuntu 24.04** (aarch64).
   - Shape: **VM.Standard.A1.Flex**, 2 OCPU, 12 GB (es lo que queda en Always Free desde junio de 2026).
   - Networking: dejar la VCN por defecto con IP pública.
   - SSH keys → **Paste public key** → pegar el contenido de `~/.ssh/id_ed25519_cosmos_oracle.pub`
     del Mac (la clave ya está generada; se imprime con `cat ~/.ssh/id_ed25519_cosmos_oracle.pub`).
3. Si sale «Out of host capacity», reintentar en otra Availability Domain o más tarde. Es lo normal.
4. Apuntar la **IP pública** y pasársela a Claude. No hay que abrir ningún puerto: Telegram y Claude
   son conexiones salientes.

## Lo que hace Claude desde el Mac cuando tenga la IP

```bash
ssh -i ~/.ssh/id_ed25519_cosmos_oracle ubuntu@IP_PUBLICA 'bash -s' < docs/servidor-oracle/bootstrap.sh
```

El guion instala paquetes, swap, Bun, Claude Code, GitHub CLI, Ollama con el modelo del juez, el
plugin de Telegram y un servicio de usuario `cosmos-telegram` que levanta la sesión en tmux al
arrancar. Es idempotente: se puede relanzar.

## Lo que solo puede hacer el dueño en el servidor (tres pasos, una vez)

```bash
ssh -i ~/.ssh/id_ed25519_cosmos_oracle ubuntu@IP_PUBLICA
gh auth login                       # para clonar el repo privado; luego relanzar bootstrap.sh
cd ~/cosmos-harness && claude       # imprime una URL: abrirla en el móvil, entrar con la cuenta Max
  /telegram:configure <token-de-BotFather>
  /exit
systemctl --user enable --now cosmos-telegram
tmux attach -t cosmos               # Ctrl-b d para soltar sin cerrar
  /telegram:access pair <código-que-da-el-bot>
  /telegram:access policy allowlist
```

El token del bot puede ser el mismo que en el Mac, pero **solo una máquina a la vez** debe tener el
bot arrancado: dos sesiones con el mismo token se pelean por los mensajes.

## Lo que hay que saber

- La sesión corre con permisos sin preguntar. En un servidor propio con lista blanca de Telegram es
  asumible; el freno a acciones irreversibles no puede vivir solo en el prompt (misma lección que el
  pueblo `openclaw`).
- 12 GB de RAM con el juez cargado y Claude a la vez van justos: por eso el guion crea 4 GB de swap.
  Si el juez estorba, `COSMOS_MODELO_JUEZ=qwen2.5:3b bash bootstrap.sh` baja a 1,9 GB.
- Oracle puede recortar o retirar el tier gratuito sin aviso; ya lo redujo a la mitad en junio de 2026.
  El plan B es Hetzner CX32 con el mismo guion, sin cambiar nada.
- Fuentes: canales de Claude Code https://code.claude.com/docs/en/channels.md · Always Free
  https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
