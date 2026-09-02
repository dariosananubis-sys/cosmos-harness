---
cosmos: pueblo
nombre: quota-oficial
padre: agentes-ia/coste
resumen: Pregunta la cuota que queda al servicio en vez de adivinarla, y senala el pico dentro de la ventana.
---

`scripts/quota-oficial.py` y `scripts/quota-peak.py` — herramientas propias, no de GitHub.

```bash
python3 scripts/quota-oficial.py            # % real de la ventana de 5 h y de la semanal
python3 scripts/quota-peak.py               # pico en ventana rodante de 5 h
python3 scripts/quota-peak.py --horas 168   # pico semanal
```

`quota-oficial.py` pregunta a la fuente autoritativa (`GET
https://api.anthropic.com/api/oauth/usage`, el mismo recurso que alimenta el `/usage` del CLI):
devuelve `five_hour.utilization` y `seven_day.utilization` **sin consumir un solo token**, resolviendo
el `CLAUDE_CONFIG_DIR` activo a partir del proceso vivo y leyendo la credencial del llavero, con
reintento creciente. `quota-peak.py` dice en qué momento de la ventana se gastó el pico, que es lo que
el total no cuenta: sirve para atribuir el gasto a una tarea concreta.

Gana a estimar por transcripts, que es lo que hacía la consola antes: los `.jsonl` no dicen de qué
cuenta salió cada mensaje y el techo era un suelo observado, no el límite. Medido el 2026-08-13, la
barra estimada marcaba **100 %** cuando la real era **13 %**. Y gana a raspar la interfaz, que se
rompe al primer cambio de diseño.

Descartado a propósito: sondear con un `POST /v1/messages` de `max_tokens: 1` y leer las cabeceras
`anthropic-ratelimit-unified-*`. Funciona, pero cuesta tokens facturables por sondeo.

Ojo: el recurso de uso **no está documentado** — puede cambiar sin aviso, así que un fallo de este
guion no es motivo para dudar de la cuota. Y `quota-peak.py` mide un **suelo observado**, no el límite
oficial: si se llegó ahí sin corte, el techo real es mayor.
