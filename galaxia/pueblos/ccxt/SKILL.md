---
cosmos: pueblo
nombre: ccxt
padre: trading/conectividad
resumen: Una sola interfaz para mas de cien mercados de cripto, con peticiones y flujo continuo incluidos.
---

https://github.com/ccxt/ccxt · MIT · 43.823★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
pip install ccxt
```

```python
import ccxt

mercado = ccxt.binance()      # solo lectura: sin claves, no puede operar

velas = mercado.fetch_ohlcv("BTC/USDT", timeframe="1h", limit=500)
libro = mercado.fetch_order_book("BTC/USDT")

# redondear al tick y al lote del mercado ANTES de enviar, con sus funciones
precio = mercado.price_to_precision("BTC/USDT", 63123.4567)
cant   = mercado.amount_to_precision("BTC/USDT", 0.0033333)
```

La capa que evita reescribir el cliente por cada mercado: interfaz unificada REST **y** flujo
continuo (la parte de WebSocket, que antes era de pago, ya viene incluida gratis) para más de cien
mercados de cripto. Cubre también el histórico de velas, que es lo que hace innecesario un pueblo
aparte de datos de mercado para cripto — y es el histórico que de verdad se ejecutó en ese mercado,
no un raspado como `yfinance`.

Ojo, dos cosas de dinero. La clave de mercado va cifrada (`infraestructura/sops`) y **nunca con
permiso de retirada de fondos** — solo lectura y operar. Y la interfaz es unificada pero **no
idéntica**: tipos de orden, comisiones y límites cambian por mercado, y algunos métodos existen en
uno y no en otro (`mercado.has['fetchOHLCV']` lo dice antes de asumirlo). El redondeo a tick y lote
es obligatorio: mandar un precio con más decimales de los que el mercado acepta es un rechazo, o algo
peor.
