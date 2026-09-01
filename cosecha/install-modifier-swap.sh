#!/usr/bin/env bash
# Intercambia Command <-> Option en un teclado externo (por defecto GMK67),
# dejando intacto el teclado interno del Mac.
#
# Uso:
#   ./install-modifier-swap.sh            # autodetecta el teclado externo
#   ./install-modifier-swap.sh --list     # solo lista teclados y sale
#   ./install-modifier-swap.sh 0x36b0 0x3002   # fuerza VendorID / ProductID
#   ./install-modifier-swap.sh --uninstall     # revierte y borra el agente
set -euo pipefail

LABEL="com.example.keyboard-modifier-swap"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

list_keyboards() {
  hidutil list --matching '{"PrimaryUsagePage":1,"PrimaryUsage":6}' 2>/dev/null |
    awk '/^Devices:/{d=1;next} d && $NF=="0" {print}'
}

if [[ "${1:-}" == "--list" ]]; then
  echo "Teclados externos detectados (Built-In = 0):"
  list_keyboards
  exit 0
fi

if [[ "${1:-}" == "--uninstall" ]]; then
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  hidutil property --set '{"UserKeyMapping":[]}' >/dev/null
  echo "Swap desinstalado. Reconecta el teclado para volver al mapeo por defecto."
  exit 0
fi

if [[ $# -eq 2 ]]; then
  VID_HEX="$1"; PID_HEX="$2"
else
  read -r VID_HEX PID_HEX _ < <(list_keyboards | head -1)
  if [[ -z "${VID_HEX:-}" ]]; then
    echo "ERROR: no encuentro ningun teclado externo conectado." >&2
    echo "Conectalo y reintenta, o pasa VendorID/ProductID a mano (--list para verlos)." >&2
    exit 1
  fi
fi

VID=$((VID_HEX)); PID=$((PID_HEX))
echo "Teclado objetivo: VendorID=$VID ($VID_HEX)  ProductID=$PID ($PID_HEX)"

# E2=LeftAlt E3=LeftGUI(Cmd) E6=RightAlt E7=RightGUI(Cmd) — se intercambian por pares.
MAPPING='{"UserKeyMapping":[{"HIDKeyboardModifierMappingSrc":0x7000000E3,"HIDKeyboardModifierMappingDst":0x7000000E2},{"HIDKeyboardModifierMappingSrc":0x7000000E2,"HIDKeyboardModifierMappingDst":0x7000000E3},{"HIDKeyboardModifierMappingSrc":0x7000000E7,"HIDKeyboardModifierMappingDst":0x7000000E6},{"HIDKeyboardModifierMappingSrc":0x7000000E6,"HIDKeyboardModifierMappingDst":0x7000000E7}]}'

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>$LABEL</string>
	<key>ProgramArguments</key>
	<array>
		<string>/usr/bin/hidutil</string>
		<string>property</string>
		<string>--matching</string>
		<string>{"VendorID":$VID,"ProductID":$PID}</string>
		<string>--set</string>
		<string>$MAPPING</string>
	</array>
	<key>RunAtLoad</key>
	<true/>
	<key>LaunchEvents</key>
	<dict>
		<key>com.apple.iokit.matching</key>
		<dict>
			<key>com.apple.device-attach</key>
			<dict>
				<key>IOProviderClass</key>
				<string>IOUSBDevice</string>
				<key>idVendor</key>
				<integer>$VID</integer>
				<key>idProduct</key>
				<integer>$PID</integer>
				<key>IOMatchLaunchStream</key>
				<true/>
			</dict>
		</dict>
	</dict>
	<key>StandardOutPath</key>
	<string>/tmp/gmk67-modifier-swap.log</string>
	<key>StandardErrorPath</key>
	<string>/tmp/gmk67-modifier-swap.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
hidutil property --matching "{\"VendorID\":$VID,\"ProductID\":$PID}" --set "$MAPPING" >/dev/null

echo "OK. Swap Command<->Option aplicado y persistido en $PLIST"
echo "Se reaplica solo cada vez que reconectes el teclado o reinicies."
