---
cosmos: pueblo
nombre: ordenes-entre-ventanas
padre: agentes-ia/herramientas
resumen: Entrega ordenes de la interfaz interactiva a las OTRAS ventanas abiertas; la propia va siempre la ultima.
---

`cosecha/mandar-a-terminales.py` — hay ordenes que solo existen dentro de la sesion interactiva
(compactar, limpiar, retomar): no tienen API, asi que ningun canal automatico puede lanzarlas. Esto
las entrega tecleandolas en las demas ventanas del editor, y protege la regla que importa: nunca se
escribe en la terminal desde la que corre, y si se pide incluirla, va la ultima.

Su valor real es el registro de lo que NO funciona, comprobado y no supuesto: escribir al dispositivo
de terminal va a su salida y no a la entrada del proceso; el mecanismo del sistema disenado para
inyectar teclas esta denegado en este sistema operativo; y el arbol de accesibilidad del editor no
dice que terminal tiene el foco, asi que hay que calibrar ciclando una vuelta entera y mirando la
cabecera. Sin eso se pierde una tarde para llegar al mismo sitio.

No es el canal para repartir trabajo — para eso esta el demonio que atiende mensajes y trabajos
programados, que habla por API y no depende de teclazos. Esto es solo para lo que unicamente existe
dentro de la interfaz de texto.
