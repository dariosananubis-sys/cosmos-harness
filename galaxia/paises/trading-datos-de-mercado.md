---
cosmos: pais
nombre: datos-de-mercado
padre: trading
resumen: De donde salen los precios cuando el mercado no es cripto, y a que se renuncia por no pagarlos.
---

Vale para renta variable, divisas e indices; en cripto el propio mercado da su historico y no hace
falta nada de aqui.

Una vela mal formada o un hueco sin declarar produce un backtest precioso y falso. La comprobacion
—que no falten barras, que el maximo sea mayor que el minimo, que el volumen no sea cero donde hubo
precio— se hace con `ingenieria-datos/validacion/pandera` antes de guardar, y el almacen es
`ingenieria-datos/motor/duckdb` sobre Parquet: aguanta anos de series sin montar un servidor.
