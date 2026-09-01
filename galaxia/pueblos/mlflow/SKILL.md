---
cosmos: pueblo
nombre: mlflow
padre: agentes-ia/evaluacion
resumen: Registra ejecuciones, trazas y evaluaciones de un agente en un servidor propio y gratuito.
---

https://github.com/mlflow/mlflow · Apache-2.0 · 27.764★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
pip install mlflow
mlflow server --host 127.0.0.1 --port 5000     # servidor propio, sin cuenta ni tarjeta
```

```python
import mlflow
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("agente-de-extraccion")

with mlflow.start_run():
    mlflow.log_param("modelo", "local-4b-q4")
    mlflow.log_metric("aciertos", 0.82)
    mlflow.log_artifact("progress/verify_extraccion.md")
```

Gana a `langwatch/langwatch` (3.520★) y a `openlit/openlit` (2.736★), los dos observatorios de agentes
más jóvenes de su hueco, en dos cosas medibles: una década de madurez detrás y **ninguna capa de pago
obligatoria** — el servidor se levanta en local con un comando. Además guarda experimentos, así que
cubre a la vez «qué hizo el agente» y «qué modelo era mejor», que en los otros dos son dos productos.

Ojo: el trazado automático (`mlflow.<libreria>.autolog()`) solo cubre las librerías que MLflow
instrumenta. Un agente escrito a mano sobre el SDK oficial hay que instrumentarlo a mano: sin eso, la
interfaz sale vacía y parece que no se ejecutó nada. Y `mlflow server` sin `--host 127.0.0.1` escucha
en todas las interfaces sin autenticación.
