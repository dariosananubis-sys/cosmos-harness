---
cosmos: pueblo
nombre: hammerspoon
padre: automatizacion/escritorio
resumen: Automatiza la propia maquina: ventanas, atajos globales y eventos del sistema.
---

https://github.com/Hammerspoon/hammerspoon · MIT · 16.029★ · push 2026-07-08 (comprobado 2026-09-01)

```bash
brew install --cask hammerspoon

mkdir -p ~/.hammerspoon
cat > ~/.hammerspoon/init.lua <<'LUA'
-- atajo global: cmd+alt+R recarga la configuracion
hs.hotkey.bind({"cmd", "alt"}, "R", function()
  hs.alert.show("recargando"); hs.reload()
end)

-- reaccionar a que se monte un disco externo
hs.caffeinate.watcher.new(function(ev)
  if ev == hs.caffeinate.watcher.systemDidWake then hs.alert.show("despierto") end
end):start()
LUA
# Ajustes del sistema > Privacidad y seguridad > Accesibilidad: dar permiso a Hammerspoon
```

Gana a `skhd` + `yabai` (el otro camino habitual en este escritorio) porque es un solo proceso con
un lenguaje entero detrás: ventanas, atajos, red, portapapeles, USB y energía se programan con la
misma API, sin encadenar tres demonios. Y gana a los guiones nativos del sistema porque puede
**reaccionar a eventos**, no solo ejecutarse cuando alguien lo lanza.

Frontera con el demonio que atiende mensajes del nicho de agentes: aquel recibe encargos y los
ejecuta hasta el final; este reacciona a un evento local del escritorio.

Ojo: es **solo macOS** y necesita permiso de Accesibilidad concedido a mano — no se puede provisionar
por guion, así que una máquina nueva siempre lleva un paso manual. Su último empujón es de julio de
2026: mantenido, pero no de desarrollo diario; comprobar la compatibilidad tras una actualización
mayor del sistema antes de depender de él.
