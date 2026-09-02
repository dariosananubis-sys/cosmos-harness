---
cosmos: pueblo
nombre: ib-async
padre: trading/ejecucion/conectividad
resumen: Cliente asincrono mantenido para la pasarela del broker que da acceso a mercados clasicos.
---

https://github.com/ib-api-reloaded/ib_async · BSD-2-Clause · 1.728★ · último push 2026-08-19 (comprobado 2026-09-01)

```bash
pip install ib_async
# requiere TWS o IB Gateway corriendo; la cuenta de papel de IBKR es gratis
```

```python
from ib_async import IB, Stock

ib = IB()
ib.connect("127.0.0.1", 7497, clientId=1)     # 7497 = puerto de la cuenta de papel

contrato = Stock("AAPL", "SMART", "USD")
ib.qualifyContracts(contrato)
print(ib.reqMktData(contrato).last)

ib.disconnect()
```

Continuación mantenida del cliente histórico `ib_insync`, que su autor archivó en 2024. Es la única
vía razonable a **acciones, futuros y opciones** desde Python, y trae reconexión y resincronización
de estado, que es justo donde se cae un bot que lleva semanas encendido. La cuenta de papel del
bróker es gratuita, así que la conectividad real se prueba sin arriesgar capital ni pedir permiso.

Ojo: no habla con el bróker directamente, **habla con TWS o IB Gateway**, que tiene que estar
corriendo y con la API habilitada — un bot 24/7 depende de que ese proceso de escritorio siga vivo,
y ahí está el punto de fallo real. Y para renta variable estadounidense existe otra interfaz pensada
desde el origen para bots (`alpaca-py`, también con cuenta de papel gratis), pero es un bróker de
Estados Unidos: **comprobar si admite la residencia antes de contar con ella** — este barrido no lo
verificó.
