---
cosmos: pueblo
nombre: rotki
padre: trading/ejecucion
resumen: Cuadra lo que dice el mercado con lo que dice tu registro, y calcula lo que hay que declarar.
---

https://github.com/rotki/rotki · AGPL-3.0 · 3.998★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
brew install --cask rotki      # aplicación de escritorio; corre al lado del bot
```

Cierra el único hueco que ningún motor cubre: que el saldo que cree el bot y el saldo real coincidan,
y que de ahí salga un número presentable a Hacienda con método de coste y ejercicio fiscal. Es una
**aplicación de escritorio**, no una librería que el bot invoque: lee las operaciones por la interfaz
del mercado (clave de **solo lectura**) y las contrasta contra su propia contabilidad. Todo en local
— claves e histórico no salen de la máquina.

Uso mínimo, todo por su interfaz gráfica: 1) crear una cuenta local cifrada; 2) añadir el mercado con
una clave API de **solo lectura** (nunca con permiso de operar ni de retirar); 3) importar el
histórico; 4) el informe de ganancias y pérdidas por ejercicio fiscal sale de ahí.

No sustituye al registro del propio bot: lo **audita**. Si los dos números no cuadran, el que miente
casi siempre es el del bot — por eso cuelga directo del sistema solar, es la vara contra la que se
mide la contabilidad interna. Ojo: licencia **AGPL-3.0** y una capa de pago opcional (rotki Premium)
que **no hace falta** para esto — la versión libre calcula el informe fiscal; la de pago añade
estadísticas y límites mayores. Y el número fiscal vale lo que valga el método de coste elegido
(FIFO, etc.): es una decisión que hay que fijar y declarar, no un dato objetivo.
