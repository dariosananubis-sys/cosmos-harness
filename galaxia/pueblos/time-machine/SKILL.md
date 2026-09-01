---
cosmos: pueblo
nombre: time-machine
padre: trading/codigo-de-bot
resumen: Fija el reloj del proceso en el test, para probar cierres de vela y esperas sin esperarlas.
---

Un bot esta lleno de tiempo: la vela cierra a una hora exacta, el enfriamiento dura veinte minutos,
la orden caduca, el cobro de financiacion cae cada ocho horas. Probar eso durmiendo no es probarlo, y
el fallo aparece justo el dia del cambio de hora o al cruzar la medianoche en otro huso.

Fijado el reloj, el mismo test da el mismo resultado siempre, que es la mitad de la simulacion
determinista; la otra mitad es que ningun componente lea la hora por su cuenta.

Gana a la libreria de congelar el tiempo mas conocida —cuatro veces mas estrellas— por dos motivos:
lleva un ano publicando y aquella no, y sustituye el reloj a bajo nivel en vez de parchear cada
funcion, asi que no arrastra la suite entera.
