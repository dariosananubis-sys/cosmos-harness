---
cosmos: pueblo
nombre: slither
padre: blockchain/auditoria
resumen: Analizador estatico de contratos con noventa detectores maduros y salida para tuberia.
---

https://github.com/crytic/slither · AGPL-3.0 · 6.357★ · último push 2026-08-26 (comprobado por API de GitHub el 2026-09-01). De Trail of Bits.

```bash
pipx install slither-analyzer
pipx inject slither-analyzer solc-select
solc-select install 0.8.26 && solc-select use 0.8.26
```

```bash
slither .                                   # detecta el proyecto Foundry/Hardhat solo
slither . --print human-summary
slither . --checklist --json informe.json   # salida estructurada, apta para tuberia
slither . --exclude-informational --fail-high
```

Gana al analizador estatico generalista del nicho de seguridad (`semgrep` y compania) porque aquel
no conoce el modelo de ejecucion de la cadena, y aqui casi todo el riesgo vive justo ahi:
reentrada, orden de las operaciones de estado, `delegatecall`, control de acceso, colision de
almacenamiento en proxies. Frente a `Cyfrin/aderyn` (794 estrellas, GPL-3.0, en Rust y mas rapido
en repos grandes), este tiene mas de noventa detectores maduros y es el que aparece en las
auditorias profesionales; la pareja correcta es los dos, no uno.

Que clase de fallo detecta y cual no. Detecta: patrones conocidos sobre el codigo fuente —
reentrada, variables sin inicializar, visibilidad, uso de `tx.origin`, aritmetica sospechosa,
llamadas sin comprobar. No detecta: que la logica economica del contrato sea incorrecta, que una
invariante se rompa tras una secuencia concreta de llamadas (eso es `echidna`), ni nada sobre un
contrato del que solo hay bytecode (eso lo hacía `mythril`, retirado del catálogo el 2026-09-03). Un `slither` limpio significa "no hay
patrones conocidos", no "el contrato es seguro" — es el falso verde mas caro del nicho.

Necesita el codigo fuente y que compile. Sin `solc` de la version correcta, no analiza nada.
