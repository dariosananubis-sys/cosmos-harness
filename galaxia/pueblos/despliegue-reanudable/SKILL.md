---
cosmos: pueblo
nombre: despliegue-reanudable
padre: infraestructura
resumen: Fases con dependencias que se reanudan sin repetir efectos y paran solas en el paso irreversible.
---

Rescatado de la skill `resumable-deployment` de un arnes propio. El nucleo viaja con el pueblo:
`scripts/deployment_core.py` (780 lineas), **sin red y sin dependencias**, mas un `ejemplo-plan.json`
que se puede correr tal cual.

```bash
python3 scripts/deployment_core.py plan ejemplo-plan.json
#   Orden: preflight -> backup -> publicar -> verificar
#   Plan valido
```

El plan es un DAG de fases declaradas como datos. `plan` lo valida **sin ejecutar nada, sin red y sin
sondas**, y sale con `1` si hay algo mal. Comprobado el 2026-09-02: un ciclo devuelve `PLAN INVALIDO:
ciclo entre fases ['a','b']`; una fase que muta o que declara un `gate` y no trae sonda devuelve
`mutating_phase_without_probe` y `gate_without_probe`.

Las tres decisiones que lo hacen util, y que son lo que un modelo no improvisa bien:

- **La sonda manda sobre el registro.** Cada fase que muta lleva una comprobacion independiente que
  dice si el efecto ya existe. El registro de estado solo sirve para mirar; si se pierde o miente, la
  sonda decide. Asi reanudar no repite efectos.
- **Solo se reintenta lo declarado idempotente.** Un gate humano, una compra o un cambio irreversible
  se intentan una vez. Reintentar «por si acaso» es como se cobra dos veces.
- **Un fallo bloquea a sus descendientes, no a las ramas independientes**, asi que un tropiezo no
  para el despliegue entero.

Gana a `n8n` y `windmill`, que estan en `automatizacion` y tambien reintentan: aquellos son
orquestadores con interfaz y motor propio, y su reintento **no distingue lo irreversible**. Gana a un
`Makefile`, que es la alternativa casera, en que `make` decide por fecha de fichero y no sabe
preguntar al sistema real si el efecto ya paso.

Ojo: esto es un **nucleo**, no un desplegador. No habla con tu servidor: tu escribes el `run` y el
`probe` de cada fase, y la calidad del resultado es exactamente la calidad de esas sondas — una sonda
que consulta una respuesta publica puede estar leyendo una cache, un proxy o un dominio aparcado, y
entonces el despliegue se declara hecho sin serlo. El subcomando `plan` valida la **forma** del grafo:
que exista y sea coherente, no que sea el despliegue correcto.
