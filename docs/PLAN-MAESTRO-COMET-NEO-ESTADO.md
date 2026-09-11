# Plan maestro Comet + Neo: dónde está la implementación

El plan (`PLAN-MAESTRO-COMET-NEO-FABLE-5.1.md`, en esta carpeta) se implementó a partir del 2026-09-06 en un repositorio propio, fuera de este arnés:

- **Código y documentación:** `~/comet-neo-integration` (git, rama `main`, Apache-2.0).
- **Estado real:** `PROGRESS.md` de ese repositorio (formato del plan §20).
- **Evidencia y acta de aceptación:** `docs/acceptance-report.md`, `docs/compatibility-report.md`, `docs/evidencia/` (sin datos personales).
- **Instalación, rollback, privacidad, limitaciones:** `docs/installation.md`, `docs/rollback.md`, `docs/privacy-and-data.md`, `docs/known-limitations.md`.
- **Datos privados de ejecución** (socket, logs, evidencia con caducidad, copias previas de configuraciones): `~/Library/Application Support/comet-neo-integration/`.

Estado 07/09/2026: extensión cargada en el Comet real y piloto superado (36/36 con y sin Neo). Para cargar la última versión (OCR, panel con memoria y tareas): pulsar ↻ en la tarjeta de la extensión en `comet://extensions` o reiniciar Comet. Comprobaciones manuales pendientes: `bun scripts/prueba-manual-real.ts` (barra de depuración y T19).

Este fichero es solo un puntero; no forma parte de la galaxia de COSMOS.
