---
cosmos: pueblo
nombre: viem
padre: blockchain/cadena
resumen: Cliente de nodo en TypeScript con tipos estrictos y sin el peso de la biblioteca de la generacion anterior.
---

https://github.com/wevm/viem · MIT segun el `LICENSE` del repo (la API de GitHub la devuelve como `NOASSERTION`, sin verificar por que) · 3.544★ · último push 2026-09-01 (comprobado por API de GitHub el 2026-09-01). Los ganchos de React estan en el paquete hermano `wevm/wagmi` (6.743★, MIT).

```bash
npm install viem
```

```ts
import { createPublicClient, http, formatEther } from 'viem'
import { mainnet } from 'viem/chains'

const cliente = createPublicClient({
  chain: mainnet,
  transport: http('https://<tu-rpc>/<tu-clave>'),
})

const bloque = await cliente.getBlockNumber()
const saldo  = await cliente.getBalance({ address: '0x0000000000000000000000000000000000000000' })
console.log(bloque, formatEther(saldo))
```

Sustituye por defecto a `ethers-io/ethers.js` (8,7k estrellas, MIT) en proyectos nuevos: tipado real
derivado del ABI —el ABI escribe los tipos de la llamada, asi que un nombre de funcion mal escrito
falla al compilar y no en produccion—, se poda lo que no se usa, y se desarrolla hoy. `ethers` sigue
siendo mayoritario en proyectos existentes y en la documentacion de terceros, que es un motivo real
para no migrar un proyecto que funciona.

Frontera con `foundry`: aquel es para escribir y probar el contrato; esto es para lo que lo consulta
desde fuera.

Y lo que no hace bien: no protege de nada. Firmar y enviar una transaccion con `walletClient` gasta
comision de red de verdad y es irreversible — no hay confirmacion, ni simulacion por defecto, ni red
de seguridad. Antes de cualquier escritura, `simulateContract`, y la clave privada jamas en el
codigo ni en un `.env` commiteado.

Aviso de dinero: `http()` sin URL usa el RPC publico de la cadena, que va justo de limite. Un RPC
propio serio es un servicio de pago; el plan gratuito de los proveedores llega para desarrollo.
