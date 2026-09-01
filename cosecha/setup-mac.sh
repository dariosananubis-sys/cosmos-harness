#!/bin/zsh
# Optimización Mac (Apple Silicon, macOS 26+) — replica el setup del MacBook Air M5 (2026-07-16)
# Idempotente: se puede re-ejecutar sin romper nada. Pensado para MacBook e iMac.
# Uso: zsh tools/mac-optimizacion/setup-mac.sh
set -e

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"

echo "== 1/6 Homebrew =="
if ! command -v brew >/dev/null; then
  echo "ERROR: Homebrew no está instalado. Instálalo primero desde https://brew.sh y re-ejecuta."
  exit 1
fi

echo "== 2/6 Instalar Stats (monitor) + topgrade (updater) =="
brew list --cask stats >/dev/null 2>&1 || brew install --cask stats
brew list topgrade >/dev/null 2>&1 || brew install topgrade
open -a Stats 2>/dev/null || true

echo "== 3/6 Limpieza Homebrew =="
brew cleanup --prune=all
brew autoremove

echo "== 4/6 Servicios innecesarios al login =="
# Ollama a demanda, no al arranque (si existe)
if brew services list 2>/dev/null | grep -q "^ollama.*started"; then
  brew services stop ollama
  echo "   ollama parado — arrancar a demanda con 'ollama serve'"
fi

echo "== 5/6 topgrade automático (días 1 y 15, 11:00) =="
mkdir -p ~/.local/bin ~/Library/Logs/topgrade-auto

cat > ~/.local/bin/topgrade-auto.sh <<'WRAPPER'
#!/bin/zsh
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:$PATH"
LOG_DIR="$HOME/Library/Logs/topgrade-auto"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/topgrade-$(date +%Y%m%d-%H%M).log"
if ! ping -c1 -t3 1.1.1.1 >/dev/null 2>&1; then
  echo "$(date) sin red, se omite la ejecución" >> "$LOG"
  exit 0
fi
if topgrade -y -c --disable system --disable self_update >> "$LOG" 2>&1; then
  RESULT="✅ topgrade completado sin errores"
else
  RESULT="⚠️ topgrade terminó con avisos — revisa el log"
fi
ls -t "$LOG_DIR"/topgrade-*.log 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null
osascript -e "display notification \"$RESULT\" with title \"Mantenimiento Mac\" subtitle \"$(basename "$LOG")\"" 2>/dev/null
WRAPPER
chmod +x ~/.local/bin/topgrade-auto.sh

cat > ~/Library/LaunchAgents/com.example.topgrade-auto.plist <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.example.topgrade-auto</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>$HOME/.local/bin/topgrade-auto.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <dict><key>Day</key><integer>1</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Day</key><integer>15</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
    </array>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/topgrade-auto/launchd.out.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/topgrade-auto/launchd.err.log</string>
</dict>
</plist>
PLIST
launchctl bootout gui/$(id -u)/com.example.topgrade-auto 2>/dev/null || true
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.example.topgrade-auto.plist
echo "   LaunchAgent cargado: $(launchctl list | grep topgrade-auto || echo 'ERROR — revisar')"

echo "== 6/6 Chequeo de procesos zombis =="
PPCPU=$(ps -axo pcpu,comm | grep "[P]erfPowerServices" | awk '{print int($1)}' | head -1)
if [ -n "$PPCPU" ] && [ "$PPCPU" -gt 50 ]; then
  echo "   ⚠️ PerfPowerServices al ${PPCPU}% CPU — bug conocido. Ejecuta: sudo pkill PerfPowerServices"
else
  echo "   PerfPowerServices OK"
fi

cat <<'MANUAL'

======================================================
PASOS MANUALES (System Settings, 2 min):
 1. Spotlight → "Privacidad de búsqueda…" (al final del panel)
    → añadir las carpetas de código con node_modules pesados.
 2. Solo PORTÁTILES: Batería → Límite de carga → 80%.
 3. Opcional (ahorro GPU en macOS 26): Accesibilidad → Pantalla
    → Reducir transparencia.
 4. Stats: click en su icono de la barra de menú → configurar
    módulos (CPU, RAM presión, y Batería en portátiles).
NO instalar: CleanMyMac, limpiadores de RAM, antivirus de pago.
======================================================
MANUAL
echo "Setup completado."
