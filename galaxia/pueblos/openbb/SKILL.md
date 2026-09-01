---
cosmos: pueblo
nombre: openbb
padre: trading/datos-de-mercado
resumen: Decenas de proveedores conectables detras de una interfaz: cambiar de fuente sin tocar el codigo.
---

https://github.com/OpenBB-finance/OpenBB · AGPL-3.0 (leído en su `LICENSE`; la API de GitHub la reporta como `NOASSERTION`) · 72.557★ · último push 2026-07-30 (comprobado 2026-09-01)

```bash
pip install openbb
```

```python
from openbb import obb

# misma llamada, distinto proveedor: cambiar de fuente sin tocar el resto del código
precios = obb.equity.price.historical(
    "AAPL", start_date="2026-01-01", provider="yfinance"
).to_df()

# un proveedor con clave (de pago) se configura aparte; la interfaz esconde cuál es
# obb.user.credentials.fmp_api_key = "..."   # nunca en claro en el código
```

La pieza para centralizar precios, fundamentales y macro cuando una sola fuente no basta, y para no
quedarse atado a una que puede desaparecer. Gana a usar `yfinance` directo cuando hacen falta varias
fuentes o datos que Yahoo no da (fundamentales, macro, renta fija).

Ojo, aviso de coste: **varios de sus proveedores son gratis y otros exigen clave de pago**, y la
interfaz única **esconde cuál está detrás** — hay que mirar el proveedor concreto antes de prometerle
un dato a un cliente, porque `provider="fmp"` puede estar facturando sin que se note en el código. Y
la licencia es **AGPL-3.0**, igual que `backtesting-py`: uso propio sí, servicio a terceros obliga a
liberar. Para el histórico de cripto que de verdad se ejecutó, `trading/conectividad/ccxt`, no esto.
