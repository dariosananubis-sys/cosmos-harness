# Contrato de instalación para Claude

Trabaja en castellano. Este repositorio instala la conexión base de BrowserOS Neo y conserva un plan avanzado; no contiene el inspector avanzado terminado.

## Orden obligatorio

1. Lee `README.md`, `INSTALL-CLAUDE.md` y `docs/01-PLAN-MEJORA-TOTAL.md`.
2. Ejecuta `python3 -m unittest discover -s tests -v`.
3. Ejecuta `python3 scripts/preflight.py --json`.
4. Si Neo no existe, abre únicamente `https://browseros.ai/neo/` y sigue el instalador oficial.
5. Abre Neo una vez y deja que genere su configuración local.
6. No importes sesiones ni contraseñas sin que el propietario esté presente y lo autorice.
7. Ejecuta `./scripts/install-claude.sh --check` y después `--apply`.
8. Inicia una sesión nueva de Claude Code para que cargue el MCP.
9. Verifica con una llamada real: abre una pestaña propia, visita `https://example.com`, lee el título y cierra solo esa pestaña.
10. Registra versión, URL MCP en loopback y resultado. Nunca registres `install_id`, cookies, tokens o cabeceras.

## Prohibiciones

- No copies el perfil del equipo de origen.
- No publiques ni pegues secretos.
- No fijes el puerto CDP observado en otro ordenador.
- No selecciones pestañas por “activa”, URL o título cuando haya varias.
- No instales `chrome-devtools-mcp` directamente como herramienta con capacidad de escritura.
- No uses `@latest` en una configuración persistente.
- No expongas MCP o CDP a `0.0.0.0`, `::` o la LAN.
- No cambies ni cierres pestañas ajenas.
- No conviertas `NO_MEDIDO` en aprobado.

## Si se implementa la mejora avanzada

Hazlo en una rama separada y en el orden del plan. Primero crea fixtures y pruebas negativas; después el descubrimiento dinámico, el broker de propiedad y el proxy de solo lectura. El proxy debe exponer únicamente snapshot, captura, consola y red redactada. Si no puede demostrar el vínculo sesión Neo, página y `targetId`, debe fallar cerrado.

No declares la mejora instalada hasta que pasen:

- Compatibilidad con el Neo realmente instalado.
- Rechazo de herramientas mutantes.
- Rechazo de una pestaña ajena sin revelar sus metadatos.
- Cambio de puerto tras reinicio.
- Página blanca válida frente a render incompleto.
- Límite de sesiones y saturación como `NO_MEDIDO`.
- Escaneo de secretos.
- Rollback ensayado.
- Revisión adversarial independiente sobre el árbol final.

## Autoridad

Todo lo reversible y local puede ejecutarse. Para pagar, borrar datos, enviar información a terceros, tocar producción o ampliar acceso de red, detente y solicita autorización explícita.
