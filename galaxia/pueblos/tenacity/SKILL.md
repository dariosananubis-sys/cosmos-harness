---
cosmos: pueblo
nombre: tenacity
padre: trading/bots/codigo-de-bot
resumen: Reintento con espera creciente y limite declarado, en vez de un while con sleep escrito a mano.
---

https://github.com/jd/tenacity · Apache-2.0 · 8.770★ · último push 2026-08-06 (comprobado 2026-09-01)

```bash
pip install tenacity
```

```python
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type

# LEER es idempotente: reintentar el saldo es seguro
@retry(
    retry=retry_if_exception_type(ConnectionError),
    wait=wait_exponential_jitter(initial=1, max=30),   # espera creciente + ruido
    stop=stop_after_attempt(5),                         # y un límite, no infinito
)
def leer_saldo(cliente):
    return cliente.fetch_balance()
```

La reconexión es donde un bot muere de madrugada. Aquí se declara qué excepciones se reintentan,
cuántas veces, con cuánta espera y con cuánto ruido aleatorio para no golpear todos a la vez — y
sobre todo, cuándo se deja de reintentar. No tuvo rival: `litl/backoff`, el envoltorio de reintento
más citado del ecosistema, está **archivado** (2.695★, último push 2024-05-02).

Ojo, la regla que lo vuelve peligroso si se ignora: reintentar el **ENVÍO** de una orden solo es
seguro si la orden lleva identificador propio de cliente y el mercado lo respeta. Sin eso, el
reintento no recupera nada, **duplica la posición**. Leer antes de reintentar y reintentar la
lectura, no el envío. Por eso el ejemplo reintenta `fetch_balance`, no `create_order`. Leído en
estricto, esta pieza es agua transversal: se reintenta en cualquier proyecto, aquí el fallo da
pérdida en vez de excepción.
