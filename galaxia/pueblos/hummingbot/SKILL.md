---
cosmos: pueblo
nombre: hummingbot
padre: trading/motores
resumen: Creacion de mercado con cuenta de papel contra el libro real, sin claves de ningun mercado.
---

https://github.com/hummingbot/hummingbot · Apache-2.0 · 19.738★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
# arranca en Docker; guía oficial de instalación
docker run -it --name hummingbot hummingbot/hummingbot:latest
```

```bash
# dentro de la consola de hummingbot: papel contra el libro real, sin claves
>>> connect binance_paper_trade
>>> create               # asistente de estrategia (pure market making, etc.)
>>> start
>>> status               # posición e inventario en curso
```

Entra por eso: es el único de aquí que deja correr un bot completo contra **precios de verdad sin
exponer una clave ni un euro**. Las claves, cuando llegan, van a un almacén local cifrado y no a un
fichero de configuración en claro. Distinto de `freqtrade`: allí se apuesta a una dirección con
protecciones que cortan; aquí se **pone precio en los dos lados** (creación de mercado) y el riesgo
es quedarse con inventario. Separa los conectores por tipo de riesgo —mercado centralizado que
custodia tus fondos frente a descentralizado que no—, que es una distinción de dinero, no de código.

Ojo, dos avisos. Su cuenta de papel es **simulación en vivo, no un backtest histórico**: empareja
contra el libro real de ahora, así que no sirve para probar una estrategia contra el pasado — no
confundir papel con backtest. Y la cifra de volumen que anuncia su propio material (miles de
millones) es **autodeclarada y no está comprobada** por este barrido — no se repite a un cliente
como si fuera un dato verificado.
