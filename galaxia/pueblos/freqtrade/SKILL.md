---
cosmos: pueblo
nombre: freqtrade
padre: trading/motores
resumen: Bot completo de cripto con protecciones integradas que cortan solas tras una racha mala.
---

https://github.com/freqtrade/freqtrade · GPL-3.0 · 53.899★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade && ./setup.sh -i
```

```bash
# el subcomando que ningún otro bot trae de fábrica: cazar el sesgo que uno se mete solo
freqtrade lookahead-analysis --strategy MiEstrategia --timerange 20260101-20260601
freqtrade recursive-analysis  --strategy MiEstrategia

# backtest con las protecciones activadas (por defecto no cuentan)
freqtrade backtesting --strategy MiEstrategia --enable-protections
```

Entra por las **protecciones**: parada por pérdidas repetidas, límite de caída y periodo de
enfriamiento vienen de serie y se configuran, no se programan. Un bot sin cortacircuitos no se pone
en vivo. La cuenta seca usa literalmente la misma clase de estrategia que el vivo, así que no hay un
modo simulado que pueda divergir por su cuenta. Descartados los dos bots todo en uno rivales
(`jesse-ai/jesse`, `Drakkar-Software/OctoBot`): menos actividad, y el segundo empuja a su nube de
pago.

Ojo, su backtest **declara sus asunciones sin adornarlas y hay que leerlas**: rellena al precio
pedido, **SIN deslizamiento**, siempre que ese precio caiga dentro del máximo y el mínimo de la
vela. Trabaja sobre velas, así que no ve el libro ni la latencia. En cuanto la estrategia dependa de
entrar a un precio concreto dentro de la vela, el resultado del backtest está inflado — es el bot
cripto más usado (53.9k estrellas) y su motor no modela deslizamiento, y no es un defecto oculto, lo
documenta él mismo. Lo que sí es mérito suyo, y no tiene ningún otro: `lookahead-analysis` y
`recursive-analysis` como subcomandos de primera clase — la forma barata de cazar la trampa que uno
mismo se ha metido sin darse cuenta.
