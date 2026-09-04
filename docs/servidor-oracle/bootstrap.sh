#!/usr/bin/env bash
# Deja una máquina Ubuntu 24.04 ARM (Oracle Always Free, VM.Standard.A1.Flex) lista para
# correr COSMOS con Claude Code, el canal de Telegram y el juez local con Ollama.
#
# Se ejecuta UNA vez como el usuario normal (ubuntu), no como root:
#   bash bootstrap.sh
# Es idempotente: cada paso comprueba si ya está hecho antes de repetirlo.
#
# Lo que NO hace, porque necesita al dueño delante:
#   - el login de Claude Code (`claude` la primera vez imprime una URL para el móvil)
#   - el token del bot de Telegram (`/telegram:configure <token>` dentro de Claude)
#   - el clon del repo privado (necesita `gh auth login` o una deploy key)
set -euo pipefail

REPO_URL="${COSMOS_REPO:-https://github.com/dariosananubis-sys/cosmos-harness.git}"
REPO_DIR="$HOME/cosmos-harness"
MODELO_JUEZ="${COSMOS_MODELO_JUEZ:-qwen2.5:7b}"

paso() { printf '\n\033[1m== %s\033[0m\n' "$*"; }

paso "Paquetes base"
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
  git tmux curl unzip ca-certificates python3 python3-venv python3-pip build-essential ripgrep jq >/dev/null

paso "Cortafuegos de Oracle: el kernel de la imagen trae iptables con todo cerrado salvo SSH."
# Telegram y Claude son conexiones SALIENTES, así que no hay que abrir nada. Se deja constancia.
sudo iptables -L INPUT -n --line-numbers | head -5 || true

paso "Swap de 4 GB (Ollama con 12 GB de RAM va justo si el juez y Claude coinciden)"
if ! swapon --show | grep -q swapfile; then
  sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile >/dev/null && sudo swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
fi

paso "Bun (los plugins de canales de Claude Code son guiones Bun)"
if ! command -v bun >/dev/null && [ ! -x "$HOME/.bun/bin/bun" ]; then
  curl -fsSL https://bun.sh/install | bash
fi
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"

paso "Claude Code (instalador nativo, sin Node)"
if ! command -v claude >/dev/null; then
  curl -fsSL https://claude.ai/install.sh | bash
fi
claude --version

paso "GitHub CLI (para clonar el repo privado con tu cuenta)"
if ! command -v gh >/dev/null; then
  sudo mkdir -p -m 755 /etc/apt/keyrings
  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null
  sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
  sudo apt-get update -qq && sudo apt-get install -y -qq gh >/dev/null
fi

paso "Ollama y el modelo del juez ($MODELO_JUEZ)"
if ! command -v ollama >/dev/null; then
  curl -fsSL https://ollama.com/install.sh | sh
fi
sudo systemctl enable --now ollama >/dev/null 2>&1 || true
ollama list | grep -q "^${MODELO_JUEZ%%:*}" || ollama pull "$MODELO_JUEZ"

paso "Plugin de Telegram de Claude Code"
claude plugin marketplace add anthropics/claude-plugins-official >/dev/null 2>&1 || true
claude plugin list 2>/dev/null | grep -q telegram || claude plugin install telegram@claude-plugins-official --scope user

paso "Repositorio COSMOS"
if [ ! -d "$REPO_DIR/.git" ]; then
  if gh auth status >/dev/null 2>&1; then
    gh repo clone "${REPO_URL#https://github.com/}" "$REPO_DIR"
  else
    echo "El repo es privado. Haz 'gh auth login' (o copia una deploy key) y vuelve a lanzar este guion." >&2
    exit 0
  fi
fi

paso "Servicio de usuario: la sesión de Claude con Telegram vive en tmux y arranca sola"
mkdir -p "$HOME/.config/systemd/user"
cat > "$HOME/.config/systemd/user/cosmos-telegram.service" <<EOF
[Unit]
Description=COSMOS - Claude Code con canal de Telegram (tmux)
After=network-online.target

[Service]
Type=forking
WorkingDirectory=$REPO_DIR
Environment=PATH=$HOME/.bun/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/tmux new-session -d -s cosmos -c $REPO_DIR 'claude --channels plugin:telegram@claude-plugins-official --dangerously-skip-permissions'
ExecStop=/usr/bin/tmux kill-session -t cosmos
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF
sudo loginctl enable-linger "$USER" >/dev/null 2>&1 || true
systemctl --user daemon-reload

cat <<'FIN'

Listo. Faltan tres pasos que solo puede dar el dueño, en este orden:

  1. cd ~/cosmos-harness && claude
       -> imprime una URL: ábrela en el móvil, entra con tu cuenta y pega el código.
  2. Dentro de esa sesión:
       /telegram:configure <token-de-BotFather>
       /exit
  3. systemctl --user enable --now cosmos-telegram
     tmux attach -t cosmos            # para mirar; Ctrl-b d para salir sin cerrarla
       -> escribe al bot desde el móvil, te da un código de 6 letras, y en la sesión:
       /telegram:access pair <código>
       /telegram:access policy allowlist

Comprobar: systemctl --user status cosmos-telegram
FIN
