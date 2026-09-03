---
cosmos: pueblo
nombre: yfinance
padre: trading/mercado/datos-de-mercado
resumen: Historico gratis de acciones, divisas e indices a cambio de ninguna garantia de seguir manana.
---

https://github.com/ranaroussi/yfinance · Apache-2.0 · 25.136★ · último push 2026-08-27 (comprobado 2026-09-01)

```bash
pip install yfinance
```

```python
import yfinance as yf

# solo para prototipar: sin garantía de que la llamada siga funcionando mañana
df = yf.Ticker("AAPL").history(period="1y", interval="1d")
print(df[["Open", "High", "Low", "Close", "Volume"]].tail())
```

No es una interfaz oficial: **raspa el frontal** de un portal financiero, se rompe cuando ese portal
cambia y su uso queda en zona gris de sus condiciones. Se acepta porque para prototipar no hay nada
gratis mejor, y porque el coste de que falle es un script roto, no una pérdida. Gana a `openbb` para
el caso simple (una fuente, renta variable) por no arrastrar la capa de proveedores.

Ojo: **no vale para cripto a nivel de tick**, ni para nada que vaya a producción — un bot en vivo que
dependa de esto se para el día que Yahoo cambie el HTML. Para cripto, `trading/ejecucion/conectividad/ccxt` da
el histórico del propio mercado, que además es el que se ejecutó de verdad. Y los datos ajustados por
dividendos que devuelve pueden cambiar entre descargas: para un backtest reproducible, guardar la
serie una vez (en `ingenieria-datos/motor/duckdb` sobre Parquet) y no re-descargar en cada corrida.
