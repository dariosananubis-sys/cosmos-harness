---
cosmos: pueblo
nombre: quantconnect-lean
padre: trading/bots/motores
resumen: Comision, deslizamiento y relleno con un modelo distinto por mercado, no uno generico para todo.
---

https://github.com/QuantConnect/Lean · Apache-2.0 · 21.435★ · último push 2026-08-31 (comprobado 2026-09-01)

```bash
pip install lean         # el CLI; el motor y el backtest local son gratis
lean init
```

```bash
# backtest local, sin nube ni datos de pago
lean backtest "MiAlgoritmo"

# el realismo es desmontable: en el algoritmo se fija el modelo por mercado
#   self.set_brokerage_model(BrokerageName.INTERACTIVE_BROKERS_BROKERAGE)
#   security.set_slippage_model(...)   # se lee, se cambia y se discute por venue
```

Es el motor que trata el realismo como **piezas intercambiables y auditables**: se puede leer,
cambiar y discutir el modelo de coste de cada mercado por separado, en vez de heredar un supuesto
único. Frente a `nautilus-trader`, mismo hueco de motor completo: aquel garantiza que simulación y
vivo comparten semántica; este da el realismo desmontado en modelos que se auditan uno a uno.

**Modela**: comisiones por bróker, deslizamiento, relleno, restricciones del venue, multiactivo con
acciones, futuros, opciones, divisas y cripto. **No modela**: la posición de tu orden en la cola del
libro — si tu orden es grande respecto al libro, cree que se llena entera. Ojo con la marca: el motor
y el CLI corren en local y son gratis; **la nube y los datos premium de su empresa son de pago** y no
hacen falta — no confundir el motor libre con el servicio de QuantConnect al presupuestar a un
cliente.
