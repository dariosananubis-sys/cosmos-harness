---
cosmos: pueblo
nombre: backtesting-py
padre: trading/backtesting
resumen: Bucle vela a vela de un solo activo: el modelo mental donde cuesta mas hacerse trampa sin verlo.
---

El contrapeso del barrido masivo. Como itera en el tiempo, cada decision solo puede usar lo que ya
habia ocurrido: el sesgo de anticipacion no entra por descuido, tiene que escribirse a proposito.

Modela: comision por operacion y relleno dentro del rango de la vela, con ordenes de mercado, limite
y stop. No modela: cartera de varios instrumentos, libro de ordenes, latencia ni liquidez — si tu
tamano mueve el precio, este motor no lo sabe.

Licencia con copyleft de red: libre para un bot propio o de cliente, obliga a liberar el codigo si se
ofrece como servicio a terceros por internet.
