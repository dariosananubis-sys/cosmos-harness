# Blockchain — barrido GitHub para COSMOS

Nicho 14 de `UNIVERSO.md`: contratos inteligentes, entornos y pruebas, **auditoría de contratos**,
interacción con nodos/RPC, indexación de cadena y billeteras. Verificado en vivo el 2026-09-01
contra `api.github.com` con token autenticado (`security find-internet-password -s github.com -w`,
nunca impreso ni escrito a fichero) — límite real de `/search/repositories` es **30
peticiones/minuto** (no 5.000/hora como el resto de la API: el primer intento sin pausa entre
llamadas devolvió `403 API rate limit exceeded`; con `sleep 3-4` entre consultas no volvió a fallar).
Repos concretos ya conocidos se resolvieron por `GET /repos/{owner}/{repo}` (cuota de 5.000/hora,
sin restricción de ráfaga) para confirmar estrellas, licencia, `pushed_at` y estado `archived`.
READMEs por `raw.githubusercontent.com`.

**Duro con el filtro**: se marca sin piedad todo lo que huela a esquema financiero. Las búsquedas por
"anchor solana framework" y similares devuelven decenas de repos de *presale*, *staking* y *airdrop*
de baja tracción (5-20★, sin licencia, sin actividad más allá del commit inicial) — plantillas de
lanzamiento de token, no herramienta. Ninguno entra en este documento; ni siquiera en Humo, porque no
merecen ni la mención individual.

---

## De primera

| Recurso | Estrellas | Último push | Licencia | Por qué gana |
|---|---:|---|---|---|
| `foundry-rs/foundry` | 10.577 | 2026-09-01 | Apache-2.0 | Toolkit de desarrollo Solidity en Rust (`forge`/`cast`/`anvil`/`chisel`): compila, testea, hace fuzzing **nativo** (sin plugin aparte) y levanta un nodo local de fork instantáneo. Es el estándar de facto nuevo frente a Hardhat por velocidad — los tests de un proyecto mediano corren en segundos, no minutos, algo que importa de verdad en un Mac de 8 GB donde no sobra CPU para esperar a un runtime JS. |
| `OpenZeppelin/openzeppelin-contracts` | 27.235 | 2026-09-01 | MIT | La librería de contratos estándar (ERC-20/721/1155, control de acceso, proxies upgradeables) más auditada del ecosistema. No es una herramienta de auditoría, pero es la base sobre la que se **audita menos** porque el código de partida ya pasó por auditorías externas repetidas — escribir desde cero lo que aquí ya existe es la forma más común de introducir una vulnerabilidad evitable. |
| `crytic/slither` | 6.357 | 2026-08-26 | AGPL-3.0 | Analizador estático de Trail of Bits para Solidity **y Vyper**. Detectores maduros (90+), el más usado en pipelines de auditoría profesional real, con salida estructurada apta para CI. Python, por lo que arrastra su intérprete — en un Mac de 8 GB no hay problema, es ligero comparado con levantar un nodo. |
| `crytic/echidna` | 3.172 | 2026-08-31 | AGPL-3.0 | Fuzzer de propiedades para contratos Ethereum, también de Trail of Bits: se le declaran invariantes (`echidna_*` o modo *assertion*) y genera secuencias de llamadas para intentar romperlas — complementa a Slither (estático) con ejecución real. Es el fuzzer de referencia que usan las auditorías serias, no el fuzzing superficial del `forge fuzz` de un solo test. |
| `Cyfrin/aderyn` | 794 | 2026-08-30 | GPL-3.0 | Analizador estático **en Rust**, no Python: mismo terreno que Slither pero mucho más rápido en repos grandes y con integración de editor (extensión VS Code oficial). Menos detectores que Slither todavía, así que la pareja correcta es "los dos, no uno solo" — no hay redundancia real entre ambos. |
| `a16z/halmos` | 1.028 | 2025-08-06 | AGPL-3.0 | Testing simbólico que reutiliza los tests de Foundry **ya escritos**: convierte cada test property-based en una prueba exhaustiva por ejecución simbólica sin reescribir nada, con Z3 por debajo. Confirmado en su propio README (*"leveraging existing tests for formal verification"*). Único con este mecanismo exacto en el barrido. **Aviso**: sin `push` desde 2025-08-06 (13 meses) — comprobar viveza del proyecto antes de apostar por él en un cliente nuevo. |
| `ConsenSysDiligence/mythril` | 4.265 | 2026-04-27 | MIT | Ejecución simbólica sobre bytecode EVM (no solo Solidity fuente): útil cuando solo hay el bytecode desplegado, caso frecuente al auditar un contrato de terceros ya en producción. Complementa a Slither/Echidna, que necesitan el código fuente. |
| `wevm/viem` + `wevm/wagmi` | 3.544 / 6.743 | 2026-09-01 / 2026-09-01 | NOASSERTION* / MIT | Pila TypeScript moderna para hablar con nodos/RPC y conectar wallets: `viem` es la librería base (tipado estricto, tree-shakeable, sin las dependencias pesadas de ethers v5), `wagmi` son los hooks de React sobre `viem`. Sustituye a `ethers.js` como opción por defecto en proyectos nuevos — mismo autor (`wevm`, antes `wagmi-dev`), desarrollo activo hoy mismo en ambos. *La licencia MIT está en el propio repo pero GitHub no la detecta automáticamente (`NOASSERTION`); no verificado por qué. |
| `otter-sec/anchor` (antes `coral-xyz/anchor`) | 5.124 | 2026-09-01 | Apache-2.0 | Framework de Solana en Rust: macros que generan la validación de cuentas, serialización Borsh y el cliente TS a partir del IDL. Es al desarrollo en Solana lo que Foundry es a Ethereum — sin él, escribir un programa nativo en Rust puro es mucho más verboso y propenso a errores de seguridad de cuentas (el fallo más común en auditorías de Solana). Ver nota de traspaso de organización más abajo. |
| `ponder-sh/ponder` | 1.123 | 2026-08-24 | MIT | Framework de indexación de cadena en TypeScript: un solo proceso (Node + SQLite/Postgres embebido opcional), sin la infraestructura de `graph-node` (Postgres + IPFS + el propio graph-node como tres servicios separados). Para indexar un contrato propio en un Mac de 8 GB, `ponder dev` arranca y reindexiza en caliente; montar `graph-node` local para lo mismo es mucho más pesado. Gana por huella de recursos en esta máquina concreta, no por cuota de mercado (`graphprotocol/graph-node` la tiene, ver Segunda fila). |

---

## Segunda fila

- `NomicFoundation/hardhat` — 8.504★, push 2026-09-01, licencia `NOASSERTION` (es MIT en la práctica).
  Sigue siendo la opción correcta si el equipo ya vive en el ecosistema JS/TS y quiere el plugin más
  amplio (`hardhat-deploy`, `hardhat-verify`…) o `console.log()` dentro de Solidity para depurar —
  algo que Foundry no ofrece igual de cómodo.
- `argotorg/solidity` (antes `ethereum/solidity`) — 25.722★, push 2026-09-01, GPL-3.0. El compilador
  oficial. Ver nota de traspaso de organización.
- `Certora/CertoraProver` — 330★, push 2026-08-28, GPL-3.0, CLI real y buildable en local (confirmado
  leyendo su README: Java 19+, Rust, Z3/CVC5). **💰 Con matiz**: el propio README recomienda el uso
  vía su nube (`docs.certora.com`) en vez del build local, que es pesado (varios lenguajes y
  solvers SMT como dependencia). No se ha verificado en vivo el límite gratuito de su plan cloud —
  antes de prometerlo a un cliente, comprobar en `certora.com`. Es la verificación formal con
  especificación matemática propia (CVL) más seria del espacio; Halmos es la alternativa 100% local
  y gratis cuando no hace falta ese nivel.
- `Ackee-Blockchain/wake` — 374★, push 2026-06-21, ISC. Framework Python de testing + fuzzing con
  detectores de vulnerabilidades integrados — combina en una herramienta lo que Foundry+Slither+Echidna
  hacen por separado, a cambio de menos tracción y comunidad que cada uno por su lado.
- `protofire/solhint` — 1.126★, push 2026-08-13, MIT. El linter de Solidity de referencia (estilo +
  reglas de seguridad básicas), se usa junto a Slither, no en su lugar.
- `ethers-io/ethers.js` — 8.717★, push 2026-06-18, MIT. Sigue siendo mayoritario en proyectos
  existentes y en documentación de terceros; para un proyecto nuevo, `viem` gana en tipado y tamaño
  de bundle.
- `ethereum/web3.py` — librería Python equivalente a ethers/viem, necesaria si el resto del stack
  (scripts de auditoría, bots de monitorización) ya está en Python.
- `paradigmxyz/reth` — 5.761★, push 2026-09-01, Apache-2.0. Cliente de ejecución de Ethereum en Rust,
  modular y rápido: la alternativa real a pagar un proveedor de RPC (Alchemy/Infura) es correr tu
  propio nodo. **Aviso de recursos**: un nodo completo de Ethereum necesita cientos de GB de disco y
  se recomienda 16 GB+ de RAM para sincronizar con margen — en un Mac de 8 GB solo tiene sentido en
  modo *light*/consulta puntual contra un RPC ajeno gratuito, no para correr el nodo entero.
- `anza-xyz/agave` — 1.900★, push 2026-09-01, Apache-2.0. El cliente validador de Solana **vivo**;
  ver nota de traspaso más abajo, no confundir con `solana-labs/solana`.
- `solana-foundation/solana-web3.js` — 2.748★, push 2026-08-31, MIT. SDK JS oficial de Solana.
- `rainbow-me/rainbowkit` — 2.835★, push 2026-05-12, MIT. Componente React de conexión de wallet
  listo, construido sobre `wagmi` + `viem` — capa de UI, no sustituye a `wagmi`.
- `WalletConnect/walletconnect-monorepo` — 1.683★, push 2026-09-01, licencia `NOASSERTION`. Protocolo
  de conexión wallet↔dApp. Requiere un Project ID gratuito de su Cloud (no pide tarjeta, pero sí
  cuenta) — no es "coste cero sin registro" estricto, es freemium sin fricción de pago.
- `graphprotocol/graph-node` — 3.146★, push 2026-08-25, Apache-2.0. El indexador estándar de la
  industria (subgrafos), pero exige levantar Postgres + IPFS + el propio graph-node como tres
  procesos — en un Mac de 8 GB es viable con Docker pero notablemente más pesado que Ponder para un
  solo contrato propio.
- `subsquid/squid-sdk` — 1.337★, push 2026-08-31, Apache-2.0. Alternativa a Ponder/Graph en
  TypeScript, orientada a *bulk* histórico rápido vía red SQD; segunda opción sólida si Ponder no
  encaja.
- `CosmWasm/cosmwasm` (1.145★, Apache-2.0) y `use-ink/ink` (1.455★, Apache-2.0) — contratos en Rust
  para Cosmos SDK y Polkadot/Substrate respectivamente. Se mencionan porque el nicho no es solo EVM,
  pero fuera de ese ecosistema no hay suficiente profundidad de auditoría (Slither/Echidna no
  aplican) para tratarlos igual que la pila EVM.

---

## Humo

- Decenas de repos de "Solana anchor NFT/presale/staking dapp" (5-20★, sin licencia, un solo commit)
  que aparecen en cualquier búsqueda de "anchor solana framework": plantillas de lanzamiento de
  token con cero mantenimiento — no se listan por nombre porque ninguno pasa el filtro de "vivo" ni
  de "mejor de su hueco", y varios son literalmente el andamiaje de un esquema de venta anticipada de
  token, exactamente lo que Darío pidió marcar sin piedad.
- `trailofbits/manticore` — **archivado** (confirmado: bandera `archived: true` en la API y aviso
  literal en su README, *"Project is archived […] no longer internally developed and maintained"*).
  Era el motor de ejecución simbólica de referencia antes de Halmos/Mythril; hoy no se recomienda
  empezar un proyecto nuevo con él.
- `eth-brownie/brownie` — no archivado técnicamente, pero su propio README lo dice sin ambigüedad:
  *"Brownie is no longer actively maintained […] Check out Ape Framework"*. El sucesor real es
  `ApeWorX/ape` (1.052★, Apache-2.0, push 2026-08-27) si se necesita un framework Python (no Rust)
  para desarrollo — no entró en Segunda fila por tener menos tracción que Foundry, pero es la opción
  correcta si el equipo exige Python en vez de Rust/Solidity puro.
- `ConsenSysDiligence/mythx-cli` — el CLI existe (94★, MIT) pero es solo un cliente para el servicio
  MythX de ConsenSys; sin `push` desde 2024-03-20 (2,5 años) y sin confirmación en vivo de que el
  backend siga operativo — no verificado, tratar como posible servicio descontinuado hasta comprobar
  en el momento de usarlo.
- `solana-labs/solana` — **archivado** (confirmado por API, último push 2025-01-22). Sigue siendo el
  resultado más citado en tutoriales y READMEs de terceros para "instalar el cliente de Solana", pero
  ya no es el repo real — ver nota de traspaso.

---

## Mapeo a COSMOS

```
sistema-solar  blockchain
├── continente  desarrollo-de-contratos
│   ├── pais  entornos-y-pruebas
│   │      provincias: compilación · testing · fuzzing integrado · scripting de despliegue
│   │      pueblos: Foundry, Hardhat
│   └── pais  librerias-de-contratos
│          provincias: estándares auditados · patrones de acceso y upgradabilidad
│          pueblos: OpenZeppelin Contracts, CosmWasm, ink!
├── continente  auditoria                      ← el código propio del nicho vive aquí
│   ├── pais  analisis-estatico
│   │      provincias: detectores en Python · detectores en Rust
│   │      pueblos: Slither, Aderyn
│   ├── pais  fuzzing-y-ejecucion-simbolica
│   │      provincias: fuzzing de invariantes · ejecución simbólica sobre bytecode
│   │      pueblos: Echidna, Mythril, Wake
│   └── pais  verificacion-formal
│          provincias: pruebas simbólicas sobre tests existentes · especificación matemática
│          pueblos: Halmos, Certora Prover (💰 nube)
├── continente  interaccion-con-cadena
│   ├── pais  librerias-cliente
│   │      provincias: TypeScript · Python
│   │      pueblos: viem+wagmi, ethers.js, web3.py
│   ├── pais  nodos-y-rpc
│   │      provincias: cliente de ejecución (Ethereum) · cliente validador (Solana)
│   │      pueblos: reth, Agave
│   ├── pais  desarrollo-solana
│   │      provincias: framework de programas · SDK cliente
│   │      pueblos: Anchor, solana-web3.js
│   └── pais  indexacion
│          provincias: indexador ligero de proceso único · protocolo estándar de subgrafos
│          pueblos: Ponder, The Graph (graph-node), Subsquid
└── continente  billeteras
    └── pais  conexion-de-wallet
           provincias: protocolo de conexión · componentes de interfaz listos
           pueblos: WalletConnect, RainbowKit
```

---

## Lo que falta

1. **Traspasos de organización, tres casos verificados y sin anunciar en la mayoría de tutoriales**:
   `coral-xyz/anchor` → `otter-sec/anchor`, `ethereum/solidity` → `argotorg/solidity`, y
   `solana-labs/solana` (archivado) → `anza-xyz/agave`. Cualquier README, curso o script antiguo que
   apunte a las URLs viejas sigue funcionando por la redirección de GitHub, pero clonar por HTTPS con
   `git clone` a veces no sigue el alias igual que la API — verificar la URL activa antes de
   documentarla en un runbook de cliente.
2. **Límite gratuito exacto de Certora Cloud** no verificado en vivo (el README solo dice "se
   recomienda usar la nube"; no hay confirmación de cuota gratuita para proyectos open-source vs.
   comercial) — comprobar en `certora.com` en el momento, no asumir gratis.
3. **PHP/Ruby/Move/Cairo fuera de alcance**: el barrido se centró en EVM (Solidity) + Solana (Rust);
   lenguajes de contratos más nuevos (Move de Aptos/Sui, Cairo de StarkNet) no se cubrieron — si un
   cliente concreto los necesita, repetir el barrido específico para ese lenguaje.
4. **`WalletConnect`/`Reown` cambio de marca**: el repo sigue en la org `WalletConnect` pero el
   producto se rebautizó "Reown" en su documentación pública — no verificado en vivo si el repo
   también migrará de nombre; usar la URL del repo, no el nombre de marca, al citarlo.
5. **Ninguna herramienta de auditoría de este barrido cubre bridges/cross-chain** como categoría
   propia (el vector de mayor pérdida económica histórica en el espacio) — Slither/Echidna/Mythril
   analizan el contrato individual, no la lógica de mensajería entre cadenas; queda fuera de este
   documento y merecería su propio barrido si un cliente trabaja con bridges.
