---
cosmos: pueblo
nombre: echidna
padre: blockchain
resumen: Se le declara la invariante y genera llamadas hasta romperla, ejecutando de verdad.
---

https://github.com/crytic/echidna - AGPL-3.0 - 3.172 estrellas - ultimo push 2026-08-31 (comprobado
por API de GitHub el 2026-09-01). De Trail of Bits.

```bash
brew install echidna
```

```solidity
// test/InvariantesToken.sol — se declara la propiedad, no el caso de prueba
contract InvariantesToken is Token {
    function echidna_suministro_constante() public view returns (bool) {
        return totalSupply() == 1_000_000e18;
    }
    function echidna_saldo_no_supera_suministro() public view returns (bool) {
        return balanceOf(msg.sender) <= totalSupply();
    }
}
```

```bash
echidna test/InvariantesToken.sol --contract InvariantesToken --test-mode property
echidna . --contract InvariantesToken --config echidna.yaml --test-limit 100000
```

Complementa a `slither`, no lo sustituye: aquel lee el codigo, este lo ejecuta. Genera secuencias de
llamadas hasta romper la invariante declarada y, cuando la rompe, imprime la secuencia exacta que lo
consigue — que es lo que convierte un hallazgo en un caso de prueba. Frente al fuzzing nativo de
`forge`, la diferencia es el alcance: aquel prueba una funcion con entradas al azar, este prueba el
contrato como maquina de estados a lo largo de muchas transacciones.

Que clase de fallo detecta y cual no. Detecta: la secuencia de llamadas que viola una propiedad que
tu has escrito. No detecta nada de lo que no hayas declarado — si la invariante esta mal formulada o
falta, `echidna` da verde para siempre. Aqui el falso verde no es del programa: es de quien escribio
las propiedades.

Aviso de maquina: 100.000 secuencias en un contrato mediano son minutos de CPU al maximo. En un Mac
de 8 GB conviene fijar `--test-limit` y no dejarlo corriendo mientras se trabaja.
