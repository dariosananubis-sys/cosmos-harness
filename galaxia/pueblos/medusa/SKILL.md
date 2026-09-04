---
cosmos: pueblo
nombre: medusa
padre: blockchain/auditoria
resumen: Fuzzer de contratos en paralelo sobre go-ethereum, con corpus y varios workers a la vez.
---

https://github.com/crytic/medusa · AGPL-3.0 · 485★ · último push 2026-05-14 (comprobado 2026-09-03). De
Trail of Bits, mismo equipo que `slither` y `echidna`.

```bash
go install github.com/crytic/medusa@latest
```

```json
// medusa.json — configuracion minima
{
  "fuzzing": {
    "workers": 10,
    "testLimit": 100000,
    "testing": {
      "propertyTesting": { "enabled": true, "testPrefixes": ["medusa_"] }
    }
  }
}
```

```solidity
// test/InvariantesToken.sol — mismo estilo de propiedad que echidna_*, con otro prefijo
contract InvariantesToken is Token {
    function medusa_suministro_constante() public view returns (bool) {
        return totalSupply() == 1_000_000e18;
    }
}
```

```bash
medusa fuzz --config medusa.json
```

Inspirado explícitamente en `echidna` y del mismo equipo, así que comparte el modelo de propiedad
declarada y secuencia de llamadas hasta romperla. La diferencia es el motor: va sobre
`go-ethereum` en vez de una implementación propia, corre varios workers en paralelo de serie (no hay
que orquestarlo aparte) y guarda el corpus de secuencias que aumentan cobertura para reutilizarlo
entre campañas.

Ojo de vida, y hay que decirlo antes de recomendarlo por delante de su hermano: `medusa` lleva desde
2026-05-14 sin push (unos cuatro meses a fecha de esta comprobación) mientras `echidna` sigue con
commits la semana de esta auditoría. No está archivado y el equipo es el mismo, pero el ritmo de
mantenimiento hoy es de `echidna`, no de este. Entra igualmente porque el paralelismo nativo pesa en
un contrato grande y porque compartir equipo con `slither`/`echidna` da garantía de que un fallo de
seguridad se atiende aunque el desarrollo de features esté parado.

`mythril`, que fue el otro vecino de este país, se retiró del catálogo el 2026-09-03: llevaba parado
desde 2025-01-31 (comprobado en vivo ese día, con el mismo comando de esta ficha), más de un año sin
commits. Para bytecode de un contrato ya desplegado sin fuente el país se queda sin opción viva —es un
hueco declarado, no un olvido—; para código fuente propio, `slither` + `echidna`/`medusa` cubren el
hueco con mantenimiento vivo.

Ojo de uso: el motor de propiedades es el mismo concepto que `echidna` pero el prefijo de función y
el fichero de configuración son distintos (JSON aquí, YAML allá) — no son intercambiables sin
adaptar el test. Y como todo fuzzer, un `testLimit` alcanzado sin fallos no es una prueba de que no
los haya: es que esas secuencias, con ese límite, no los encontraron.
