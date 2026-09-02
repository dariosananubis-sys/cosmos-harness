---
cosmos: pueblo
nombre: time-machine
padre: trading/bots/codigo-de-bot
resumen: Fija el reloj del proceso en el test, para probar cierres de vela y esperas sin esperarlas.
---

https://github.com/adamchainz/time-machine · MIT · 994★ · último push 2026-08-28 (comprobado 2026-09-01)

```bash
pip install time-machine
```

```python
import datetime as dt, time_machine

# probar el cambio de hora sin esperar a octubre y sin dormir
@time_machine.travel("2026-10-25 02:59:00 +02:00")
def test_cierre_de_vela_en_cambio_de_hora():
    ahora = dt.datetime.now(dt.timezone.utc)
    # ... la vela cierra, el enfriamiento arranca: todo con este reloj fijo
    assert ahora.year == 2026
```

Un bot está lleno de tiempo: la vela cierra a una hora exacta, el enfriamiento dura veinte minutos,
la orden caduca, el cobro de financiación cae cada ocho horas. Probar eso durmiendo no es probarlo, y
el fallo aparece justo el día del cambio de hora o al cruzar la medianoche en otro huso. Fijado el
reloj, el mismo test da el mismo resultado siempre — la mitad de la simulación determinista.

Gana a `spulec/freezegun` (4.525★, último push 2025-08-19) por dos motivos: lleva un año publicando
y aquella no, y **sustituye el reloj a bajo nivel** en vez de parchear cada función, así que no
arrastra la suite entera. Ojo: solo controla el reloj **de este proceso** — la otra mitad de la
simulación determinista es que ningún componente lea la hora por su cuenta (ni el mercado simulado,
ni un servicio externo). Y viaja el reloj del proceso de test, no el del mercado real: no sirve para
«adelantar» un bot en vivo, solo para las pruebas.
