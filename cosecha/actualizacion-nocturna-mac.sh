#!/bin/bash
# Actualización nocturna desatendida del Mac.
#
# Qué hace:
#   1. Programa que el iMac se encienda/despierte solo todas las noches a las 03:00.
#   2. Activa la comprobación automática de actualizaciones (hoy está sin definir,
#      por eso el Mac lleva en 14.2.1 desde diciembre de 2023 pese a tener
#      AutomaticallyInstallMacOSUpdates=1).
#   3. Deja que el instalador nativo de macOS aplique las actualizaciones.
#
# Por qué NO usa `softwareupdate -i --restart` desde un LaunchDaemon:
#   en Apple Silicon, instalar una actualización de macOS por CLI exige las
#   credenciales de un usuario propietario del volumen (--user/--stdinpass).
#   Eso obligaría a guardar la contraseña del usuario en disco. El mecanismo nativo
#   de macOS hace lo mismo sin almacenar credenciales: solo necesita que el Mac
#   esté encendido y con corriente. Por eso lo único que faltaba era despertarlo.
#
# Uso:  sudo bash tools/mac-mantenimiento/actualizacion-nocturna.sh
# Deshacer: sudo bash tools/mac-mantenimiento/actualizacion-nocturna.sh --revertir

set -euo pipefail

SU_PLIST=/Library/Preferences/com.apple.SoftwareUpdate

if [[ $EUID -ne 0 ]]; then
  echo "Este script necesita sudo:  sudo bash $0" >&2
  exit 1
fi

# --- Guardarraíl: no actualizar macOS sin backup ---------------------------
# En Apple Silicon, subir de versión es puerta de un solo sentido: no se puede
# volver a 14.2.1 sin borrar el disco y restaurar. Si no hay copia reciente,
# un fallo en la actualización se lleva el trabajo por delante.
if [[ "${1:-}" != "--revertir" && "${1:-}" != "--sin-backup" ]]; then
  ULTIMO=$(tmutil latestbackup 2>/dev/null || true)
  if [[ -z "$ULTIMO" ]]; then
    echo "AVISO — no hay backup de Time Machine accesible."
    echo
    tmutil destinationinfo 2>/dev/null | grep -E "^Name" | sed 's/^/  destino configurado: /'
    echo "  volúmenes montados: $(ls /Volumes | tr '\n' ' ')"
    echo
    echo "  Conecta el disco de Time Machine, deja que termine una copia y vuelve"
    echo "  a lanzar este script. Activar la actualización automática sin copia"
    echo "  reciente es asumir un riesgo que no hace falta asumir."
    echo
    echo "  Si aun así quieres seguir:  sudo bash $0 --sin-backup"
    exit 1
  fi
  echo "Último backup: $ULTIMO"
  echo
fi

if [[ "${1:-}" == "--revertir" ]]; then
  echo "== Revirtiendo =="
  pmset repeat cancel
  echo "  · Encendido nocturno cancelado."
  defaults write "$SU_PLIST" AutomaticallyInstallMacOSUpdates -bool false
  echo "  · Instalación automática de macOS desactivada."
  echo "Hecho. Las actualizaciones vuelven a ser manuales."
  exit 0
fi

echo "== 1/3 · Encendido nocturno =="
# wakeorpoweron: despierta si está dormido, enciende si está apagado.
# MTWRFSU = los siete días de la semana.
pmset repeat wakeorpoweron MTWRFSU 03:00:00
pmset -g sched | sed 's/^/  /'

echo
echo "== 2/3 · Actualizaciones automáticas =="
defaults write "$SU_PLIST" AutomaticCheckEnabled -bool true
defaults write "$SU_PLIST" AutomaticDownload -bool true
defaults write "$SU_PLIST" AutomaticallyInstallMacOSUpdates -bool true
defaults write "$SU_PLIST" CriticalUpdateInstall -bool true
defaults write "$SU_PLIST" ConfigDataInstall -bool true
softwareupdate --schedule on >/dev/null 2>&1 || true

for k in AutomaticCheckEnabled AutomaticDownload AutomaticallyInstallMacOSUpdates \
         CriticalUpdateInstall ConfigDataInstall; do
  printf '  %-38s = %s\n' "$k" "$(defaults read "$SU_PLIST" "$k" 2>/dev/null || echo '?')"
done

echo
echo "== 3/3 · Comprobación =="
echo "  El Mac se despertará/encenderá a las 03:00 cada día."
echo "  Con corriente conectada y sin nadie usándolo, macOS instalará las"
echo "  actualizaciones pendientes y reiniciará por su cuenta."
echo
echo "  IMPORTANTE: deja el iMac enchufado y NO lo apagues por el interruptor"
echo "  trasero, o pmset no podrá encenderlo."
echo
echo "Listo."
