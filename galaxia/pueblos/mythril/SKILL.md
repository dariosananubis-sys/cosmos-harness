---
cosmos: pueblo
nombre: mythril
padre: blockchain
resumen: Ejecucion simbolica sobre el codigo maquina: sirve cuando del contrato ajeno solo hay lo que esta desplegado.
---

https://github.com/ConsenSysDiligence/mythril · MIT · 4.265★ · último push 2026-04-27 (comprobado 2026-09-01)
(comprobado por API de GitHub el 2026-09-01). Cuatro meses sin movimiento: vivo, pero no es de los
que publican cada semana.

```bash
pipx install mythril
```

```bash
myth analyze contrato.sol --solv 0.8.26
myth analyze -a 0x0000000000000000000000000000000000000000 --rpc https://<tu-rpc>/<tu-clave>
myth analyze --bin-runtime -f bytecode.txt -o json
```

`slither` y `echidna` necesitan el codigo fuente. Este trabaja sobre el bytecode con ejecucion
simbolica, que es lo unico que hay al auditar un contrato de terceros ya desplegado — la mitad de
los encargos reales. Por eso no compite con ellos: se ejecuta despues, sobre lo desplegado, para
comprobar que lo que corre es lo que se leyo.

Que clase de fallo detecta y cual no. Detecta: reentrada, desbordamiento de enteros, `delegatecall`
a destino arbitrario, dependencia de la marca de tiempo, `selfdestruct` alcanzable, llamadas sin
comprobar — todo lo que se puede alcanzar explorando caminos de ejecucion. No detecta: nada de la
logica de negocio, nada de la economia del protocolo, y muy poco de lo que este detras de una
profundidad de exploracion que no le da tiempo a alcanzar.

Y el falso verde de este en concreto: la ejecucion simbolica no termina. Por defecto se corta por
tiempo, asi que "sin hallazgos" puede significar "no llego". Hay que fijar y leer los limites
(`--execution-timeout`, `--max-depth`) y decir en el informe cuales fueron; un veredicto sin esos
numeros no vale.

Aviso de dinero: analizar por `--rpc` contra un proveedor de nodo consume su cuota. Con un plan
gratuito llega para un contrato; para un barrido, no.
