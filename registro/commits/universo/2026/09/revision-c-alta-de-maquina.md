---
cosmos: lluvia
nombre: revision-c-alta-de-maquina
moja: []
resumen: Los 22 bugs del alta de maquina arreglados con test y mutacion; --seco es seco y manual devuelve lo que habia.
---

# Revisión C: el alta de máquina, arreglada entera

**Fecha:** 2026-09-04 · **Encargo:** «arréglalo» sobre `progress/revision-2026-09-04/C-alta-de-maquina.md`,
los 22 hallazgos reproducidos de un revisor adversarial sobre `configurar`, `instalar`, `enganchar`,
`proyectar` y el vigilante de modelos. · **Escribe:** `cosmos/configurar.py`, `cosmos/cli.py`,
`cosmos/guardarrailes.py`, `cosmos/estado.py`, `puente/modelos.py`, `puente/proyectar.py`,
`tests/test_revision_c.py`, `puente/tests/test_proyectar.py`, `puente/tests/mutaciones.py`, README.

## Qué había de fondo

Tres familias, no veintidós bugs sueltos:

- **`--seco` que escribía.** `--modelos quitar --seco` descargaba el agente de launchd de verdad,
  `--autonomia manual --seco` deshacía, `--lanzador --seco` escribía el shim y `--oficios … --seco`
  dejaba perfil y credenciales. La ayuda decía «con --llavero, --autonomia o --modelos»; ahora `--seco`
  vale para todas las caras y cada una lo demuestra en su test.
- **Respaldos que no devolvían lo que había.** `--autonomia manual` sobre un usuario con
  `defaultMode = acceptEdits` lo dejaba sin `permissions` y culpaba a «alguien»; `{"permissions": {}}`
  no volvía byte a byte; `enganchar --sesion` dos veces guardaba como original el fichero ya
  enganchado y `desenganchar` devolvía los cinco hooks llamándolo «byte a byte»; sin respaldo,
  `desenganchar` reformateaba un `settings.json` ajeno y le borraba `"Stop": []`. Ahora la poda
  repone el valor previo, conserva los padres vacíos, el primer respaldo se queda y una lista vacía
  del usuario es del usuario.
- **Verdes que no miraban.** `estado --maquina` daba `modelos ok` con un intérprete borrado en el plist
  y en el hook, y `credenciales ok` con el fichero en 644. `proyectar sincronizar` pisaba
  `autoMemoryEnabled: true` del anfitrión y `comprobar` lo exigía; convertía CRLF a LF entero y
  mandaba el bloque al final desplazando lo escrito después. Ahora sólo se añaden claves ausentes,
  se lee en bytes y el bloque se sustituye donde está.

Más los sueltos: el hook `SessionStart` con espacios en la ruta no ejecutaba nunca (ahora los
argumentos van citados y `estado` los lee con `shlex`); `&` en una ruta rompía el plist (escapado);
`--lanzador --forzar` sobre un symlink pisaba el destino del enlace; un pre-push ajeno se callaba;
`estado --maquina` no admitía `--directorio`; `instalar --autonomia libre` interactivo preguntaba
igual; una skill enlazada del anfitrión abortaba `proyectar`; `quitar` dejaba `~/.cosmos/bin` vacío.

## Lo medido

| Comprobación | Resultado |
|---|---|
| núcleo con tokenizador real | 432 tests, OK (1 salto declarado; antes 413) |
| puente | 148 tests, OK (antes 144) |
| mutaciones | 111/111 vistas fallar (M89–M111 nuevas; M80 re-anclada porque la poda cambió de función) |
| `cosmos validar` | verde |
| `puente.secretos --todo` | limpio de nuevos |

Un cambio de contrato, dicho: `proyectar` **ya no impone** sus ajustes en `.claude/settings.json`
del repo ajeno; el test que afirmaba el pisado (`autoMemoryEnabled` a `false`) ahora afirma lo
contrario y el README lo cuenta. El estado `inseguro` es nuevo en el inventario de máquina.

## Lo que queda abierto

- Los dos plausibles del informe: la carrera del reponedor con el CLI (última escritura gana) y
  el valor de `--llavero` visible en `ps` durante `security add-generic-password`.
- Dos revisores más (núcleo `cosmos/` y `puente/` de sesión y secretos) se pararon a medias por
  cuota; no hay informe de esos ángulos.
