---
cosmos: pueblo
nombre: celery
padre: automatizacion/flujos
resumen: Cola distribuida con reintento, retroceso exponencial y confirmacion tardia.
---

https://github.com/celery/celery · BSD-3-Clause · 28.848★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
pip install "celery[redis]"

cat > tareas.py <<'PY'
from celery import Celery

app = Celery("tareas", broker="redis://localhost:6379/0",
             backend="redis://localhost:6379/1")

@app.task(bind=True, acks_late=True,
          autoretry_for=(ConnectionError,), retry_backoff=True,
          retry_jitter=True, max_retries=5)
def emitir_factura(self, pedido_id):
    ...
PY

celery -A tareas worker --loglevel=info
python -c "from tareas import emitir_factura; emitir_factura.delay(1)"
```

Gana a `rq` (la cola simple del mismo ecosistema) en todo lo que importa de madrugada, y a `BullMQ`
—la equivalente del ecosistema de la web, con grafos de trabajos y panel de cola muerta— solo por
lenguaje: si el resto del sistema es Python, cambiar de tiempo de ejecución para tener una cola es
caro. `BullMQ` queda citada y fuera por presupuesto de catálogo.

A las tres de la mañana: `acks_late=True` devuelve la tarea a la cola si el proceso muere a mitad
(pero entonces **la tarea tiene que ser idempotente**, porque puede ejecutarse dos veces);
`autoretry_for` + `retry_backoff` reintentan con espera creciente; y al agotar los reintentos la
tarea queda en `FAILURE` en el backend de resultados.

Ojo: Celery **no trae cola muerta de serie**. Con el corredor Redis, una tarea que agota reintentos
desaparece salvo que se guarde en `on_failure` o se use la cola muerta nativa de RabbitMQ. Montarlo
sin eso es exactamente el fallo silencioso de las tres de la mañana. Y `acks_late` sin idempotencia
duplica cobros.
