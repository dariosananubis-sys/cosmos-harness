---
cosmos: pueblo
nombre: ponder
padre: blockchain/cadena
resumen: Indexa los eventos de un contrato en un solo proceso, sin montar tres servicios para responder una consulta.
---

https://github.com/ponder-sh/ponder · MIT · 1.123★ · último push 2026-08-24 (comprobado por API de GitHub el 2026-09-01).

```bash
npm create ponder@latest -- --dir mi-indice
cd mi-indice && npm install
```

```ts
// ponder.config.ts
import { createConfig } from 'ponder'
import { http } from 'viem'
import { abiToken } from './abis/abiToken'

export default createConfig({
  chains:    { mainnet: { id: 1, rpc: http(process.env.PONDER_RPC_URL_1) } },
  contracts: { Token: { chain: 'mainnet', abi: abiToken,
                        address: '0x0000000000000000000000000000000000000000',
                        startBlock: 20000000 } },
})
```

```ts
// src/index.ts
import { ponder } from 'ponder:registry'
import { transferencia } from 'ponder:schema'

ponder.on('Token:Transfer', async ({ event, context }) => {
  await context.db.insert(transferencia).values({
    id: event.id, de: event.args.from, a: event.args.to, cantidad: event.args.value,
  })
})
```

```bash
npm run dev        # indexa y sirve GraphQL/SQL en http://localhost:42069
```

Gana a `graphprotocol/graph-node` (3,1k estrellas, Apache-2.0) por huella de recursos, no por cuota
de mercado: aquel exige levantar Postgres, IPFS y el propio nodo como tres servicios separados, lo
que en un Mac de 8 GB con Docker es viable pero pesado; este es un proceso que arranca y reindexa en
caliente. Para un contrato propio, la eleccion sensata; para un indice publico compartido, el
estandar sigue siendo el otro.

Y lo que no hace bien: reindexar desde un bloque antiguo son horas de llamadas al RPC, no minutos, y
el limite lo pone tu proveedor. Si cambias el esquema, se reindexa entero — no hay migracion en
caliente.

Aviso de dinero: el RPC publico no aguanta un reindexado. Hace falta uno propio o el plan gratuito
de un proveedor, y en cuanto el rango de bloques crece, ese plan se agota. Es el coste escondido de
este pueblo.
