# Instalación guiada por Claude en otro equipo

## Resultado esperado

Al terminar la instalación base:

- BrowserOS Neo está instalado y abierto.
- Claude Code tiene un MCP de usuario llamado `browseros-neo` apuntando a una URL loopback descubierta en ese equipo.
- Una sesión nueva de Claude puede abrir, leer y cerrar su propia pestaña.
- No se ha copiado ningún perfil, cookie o secreto.

La capa DevTools de mejora visual seguirá pendiente hasta implementar y validar su proxy de solo lectura.

## 1. Obtener la guía

```bash
gh repo clone dariosananubis-sys/browseros-neo-vision-kit
cd browseros-neo-vision-kit
```

Si GitHub solicita autenticación, el propietario debe iniciar sesión en su propia cuenta. Claude no debe pedir ni recibir el token en el chat.

## 2. Validar el repositorio

```bash
git status --short
python3 -m unittest discover -s tests -v
bash -n scripts/install-claude.sh
```

Debe haber cero cambios locales y todos los tests deben pasar.

## 3. Instalar BrowserOS Neo

### macOS

1. Abrir `https://browseros.ai/neo/`.
2. Descargar el instalador oficial para macOS.
3. Mover la aplicación a `/Applications` mediante el instalador oficial.
4. Verificar la firma antes de abrir:

```bash
codesign --verify --deep --strict /Applications/BrowserClaw.app
spctl --assess --type execute /Applications/BrowserClaw.app
```

El nombre visible puede cambiar de BrowserClaw a BrowserOS Neo. Si la ruta difiere, localizar la aplicación por su bundle y verificar esa ruta; no renombrarla para que coincida con esta guía.

5. Abrir Neo y completar su inicialización.
6. Importar datos de Chrome solo mediante la interfaz oficial y con el propietario presente.

### Windows

1. Abrir `https://browseros.ai/neo/` y descargar el instalador oficial para Windows.
2. Antes de ejecutar, comprobar que la firma Authenticode sea válida desde las propiedades del fichero o PowerShell.
3. Abrir Neo una vez y completar su inicialización.
4. Ejecutar el preflight con `py scripts\preflight.py --json --config RUTA_AL_CONFIG` si el descubrimiento automático no encuentra su configuración.

El soporte de Neo para Windows está documentado por el fabricante. La ruta concreta del sidecar no está verificada en este repositorio y no debe inventarse.

## 4. Ejecutar el preflight

```bash
python3 scripts/preflight.py --json
```

El resultado base correcto contiene:

- `base_ready: true`.
- `mcp_url` con host `127.0.0.1`, `localhost` o `::1`.
- `mcp_tcp: true`.
- Ningún identificador de instalación o dato de sesión.

`inspector_ready` puede ser `false` sin bloquear la instalación base; solo indica que CDP no está preparado para la futura capa avanzada.

## 5. Conectar Claude Code

Primero comprobar sin escribir:

```bash
./scripts/install-claude.sh --check
```

Si el descubrimiento automático no encuentra el runtime, propagar la misma ruta explícita al instalador:

```bash
./scripts/install-claude.sh --check --config RUTA_AL_CONFIG
./scripts/install-claude.sh --apply --config RUTA_AL_CONFIG
```

Después aplicar:

```bash
./scripts/install-claude.sh --apply
```

El script usa el comando oficial equivalente a:

```bash
claude mcp add --transport http --scope user browseros-neo URL_LOCAL_DETECTADA
```

No edita el JSON de Claude a mano. Si ya existe el mismo servidor con la misma URL, termina sin cambios. Si existe con otra URL, se detiene para no pisar una configuración previa. La comprobación no imprime la configuración existente: solo informa si está presente y si coincide.

La aplicación es transaccional: guarda una copia local con permisos restrictivos, verifica la entrada creada y revierte una creación parcial. Si detecta cambios concurrentes ajenos, los conserva y deja la copia para recuperación manual.

Si una interrupción brusca deja `pending.json`, una nueva aplicación se detiene. Ejecutar `--rollback`: solo retirará la entrada si nombre, scope, transporte y URL coinciden exactamente con la intención guardada.

## 6. Verificación real

1. Cerrar la sesión actual de Claude Code.
2. Abrir una sesión nueva en este repositorio.
3. Ejecutar `claude mcp get browseros-neo` y exigir estado conectado.
4. Pedir a Claude:

```text
Usa BrowserOS Neo. Nombra la sesión neo-smoke, abre una pestaña propia con https://example.com, confirma que el título es Example Domain y cierra únicamente esa pestaña.
```

La instalación solo pasa si la llamada real funciona. Que el puerto responda no basta.

## 7. Rollback

El instalador guarda estado únicamente cuando crea la entrada MCP. Para retirarla:

```bash
./scripts/install-claude.sh --rollback
```

El rollback no desinstala Neo, no borra su perfil y no toca sesiones. Si la entrada ya existía antes, el script no la elimina. Si alguien cambia la entrada después de instalarla, el rollback falla cerrado y tampoco la elimina.

## 8. Siguiente fase

Para implementar la mejora visual completa, continuar con `docs/01-PLAN-MEJORA-TOTAL.md`. No instalar DevTools directamente hasta que existan el broker de propiedad, la allowlist efectiva, la redacción de red y sus pruebas negativas.
