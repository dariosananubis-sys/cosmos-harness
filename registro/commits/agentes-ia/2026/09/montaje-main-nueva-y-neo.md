---
cosmos: lluvia
nombre: montaje-main-nueva-y-neo
moja: []
resumen: Main reescrita montada en la maquina de 18 GB; browseros-neo entra como pueblo con el kit; todo verde salvo el perfil.
---

# La main nueva sobre la máquina de 18 GB, y Neo dentro del árbol

**Fecha:** 2026-09-04 · **Encargo:** bajar la `main` reescrita (auditoría 360, autonomía, modelos,
`anfitrion: claude-code`), montarla entera en esta máquina y meter en el árbol la configuración de
BrowserOS Neo que vive en `dariosananubis-sys/browseros-neo-vision-kit`. · **Escribe:**
`galaxia/pueblos/browseros-neo/`, `PROGRESS.md`, `spec/VALIDADOR.md`, este parte.

## Lo que había y lo que se hizo con ello

`origin/main` llegó con historia reescrita (`0c09370`) y las ramas de trabajo del 02-09 borradas en
remoto. La rama local `trabajo-2026-09-02` se abandonó sin fusionar: sus commits ya estaban dentro
de la nueva `main` con otra firma (`7b86b20`). Lo que había sin versionar del 03-09 —el pueblo
`browseros-neo`, su parte y la guía del servidor Oracle— se respaldó antes de tocar nada y se
volvió a poner sobre la `main` nueva.

El pueblo se comparó fichero a fichero con el clon fresco del kit (`aa3de00`): `scripts/`,
`tests/`, contrato, instalación y plan son idénticos byte a byte. No hay nada del kit que el
árbol no tenga. Los 30 tests del kit pasan desde el directorio del pueblo.

## El montaje, verbo a verbo

- `cosmos arrancar`: verde, 307 pueblos en la vista (70 creadas, 11 obsoletas eliminadas).
- `configurar --autonomia`: ya estaba en `libre` (ajustes de usuario, `bypassPermissions`); no se tocó.
- `configurar --modelos instalar`: reponedor, agente launchd, hook de sesión y los atajos
  `maxcode`/`ultracode`; 6 entradas repuestas en `~/.claude.json`.
- `configurar --lanzador`: `~/.local/bin/cosmos` apunta a este clon.
- `enganchar --sesion`: pre-commit y guardarraíles; `.claude/settings.json` quedó byte a byte igual
  que el versionado (la versión anterior con rutas absolutas de miniconda se descartó).
- Venv de calibración en `~/.cosmos/calib` con `requirements-dev.txt` fijado; el de `/tmp/calib` ya
  no se cita en la doc.

## Lo medido

| Comprobación | Resultado |
|---|---|
| `cosmos validar` | verde, 0 errores |
| núcleo con `COSMOS_EXIGE_TOKENIZADOR=1` | 413 tests, OK (1 salto declarado) |
| puente | 144 tests, OK |
| mutaciones | 86/88 vistas fallar; M31 y M72 «no aplicable, el código cambió» — venían así de la `main` nueva |
| `puente.secretos --todo` | limpio de nuevos; 3 conocidos inventariados |
| `cosmos medir` | 178.060 tokens estimados; presupuesto OK, quedan 31 tokens en el peor nicho (ciberseguridad) |
| `cosmos estado --maquina` | python3, git, claude, autonomía, modelos y lanzador ok; tmux y perfil faltan |

Los dos únicos rojos de la suite eran los esperables al añadir nodos: la cifra «los N nodos de la
galaxia real» de `spec/VALIDADOR.md` (489 → 492, un pueblo y dos partes) y el bloque de `cosmos
estado` de `PROGRESS.md`. Se regeneraron con el comando, no a mano.

## Lo que queda, y de quién es

- **Perfil** (`cosmos configurar`): pregunta qué oficios y herramientas usa Darío; es su decisión,
  no se inventó una. Sin perfil, `credenciales` queda `no_comprobado`.
- **Push**: los commits son locales; subirlos es del dueño.
- **Presupuesto**: 31 tokens de margen en ciberseguridad; la próxima herramienta en ese nicho
  obliga a condensar o a saltar E16 con motivo.
- Del parte del 03-09 siguen abiertos el cortafuegos de macOS, los puertos 9010/9011 en todas
  las interfaces y el token de BotFather para Telegram.
