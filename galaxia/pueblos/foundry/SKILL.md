---
cosmos: pueblo
nombre: foundry
padre: blockchain
resumen: Compila, prueba y hace fuzzing de contratos, y levanta un nodo bifurcado al instante.
---

https://github.com/foundry-rs/foundry - Apache-2.0 - 10.577 estrellas - ultimo push 2026-09-01
(comprobado por API de GitHub el 2026-09-01).

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

```bash
forge init contador && cd contador
forge build
forge test -vvv
forge test --match-test testFuzz -vv        # el fuzzing es nativo, sin complemento
anvil &                                     # nodo local en 127.0.0.1:8545
anvil --fork-url https://<tu-rpc>/<tu-clave> --fork-block-number 20000000 &
```

Gana a `NomicFoundation/hardhat` (8,5k estrellas) en velocidad: las pruebas se escriben en Solidity
y corren en un motor en Rust, asi que un proyecto mediano pasa de minutos a segundos — que en un Mac
de 8 GB, donde no sobra CPU para esperar a un tiempo de ejecucion de JavaScript, se nota en cada
iteracion. Hardhat sigue siendo lo correcto si el equipo ya vive en JS/TS, quiere su catalogo de
complementos o depende del `console.log()` dentro de Solidity.

Y lo que no hace bien: `forge test` en verde no es una auditoria. El fuzzing de `forge` prueba una
funcion con entradas al azar; no busca la secuencia de llamadas que rompe una invariante economica
—eso es `echidna`— ni lee el contrato entero buscando patrones —eso es `slither`. Confundir las tres
cosas es como se despliega un fallo.

Un fallo desplegado no se parchea: se abandona el contrato y se migra el estado. Por eso el orden
aqui es probar en `anvil` bifurcado, pasar los tres analizadores, y solo entonces mirar la red real.

Aviso de dinero: `forge script --broadcast` contra una red real gasta comision de red de verdad.
Todo lo de arriba corre en local a coste cero; el despliegue no.
