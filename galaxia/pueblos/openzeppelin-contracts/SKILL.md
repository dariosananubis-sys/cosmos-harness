---
cosmos: pueblo
nombre: openzeppelin-contracts
padre: blockchain
resumen: Los estandares ya auditados: reescribirlos es como se mete un fallo evitable.
---

https://github.com/OpenZeppelin/openzeppelin-contracts - MIT - 27.235 estrellas - ultimo push
2026-09-01 (comprobado por API de GitHub el 2026-09-01).

```bash
forge install OpenZeppelin/openzeppelin-contracts     # con Foundry
npm install @openzeppelin/contracts                   # con Hardhat
```

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract MiToken is ERC20, Ownable {
    constructor(address duenyo) ERC20("Ejemplo", "EJM") Ownable(duenyo) {
        _mint(duenyo, 1_000_000e18);
    }
    function acunar(address a, uint256 n) external onlyOwner { _mint(a, n); }
}
```

Entra como pueblo siendo biblioteca porque su valor es lo que evita escribir, no lo que ejecuta.
Frente a escribir el ERC-20, el control de acceso o el proxy actualizable a mano —que es la
alternativa real, y la forma mas comun de meter un fallo evitable—, aqui el codigo de partida ya
paso por auditorias externas repetidas. Frente a `solmate`/`solady`, mas pequenos y baratos en gas,
este gana en cobertura y en que el auditor lo reconoce de un vistazo.

Y lo que no hace bien: importar esto no hace seguro tu contrato. El fallo se mete en la parte que
escribes tu, y sobre todo en como combinas las piezas — un `Ownable` cuyo duenyo es una direccion
que perdiste, un proxy actualizable sin separacion de almacenamiento, un `ERC20` con un gancho que
reentra. La biblioteca reduce la superficie; no la elimina.

Y hay que fijar la version. La v5 rompio API respecto a la v4 (`Ownable` ahora exige duenyo en el
constructor, entre otras). Copiar un ejemplo de un blog de 2023 sobre la v5 no compila, y peor:
copiar una mitad si compila. En `foundry.toml` / `package.json`, version exacta.

Un fallo desplegado no se parchea: se abandona el contrato. Por eso la version se congela antes de
desplegar, no despues.
