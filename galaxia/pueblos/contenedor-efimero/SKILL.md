---
cosmos: pueblo
nombre: contenedor-efimero
padre: infraestructura
resumen: Un trabajo es un contenedor que nace y muere: espera con limite, registro antes del borrado y progreso en vivo.
---

`cosecha/docker-ephemeral-runner.js` — el ciclo completo de crear, arrancar, esperar, leer el
registro y borrar, con el orden que importa: los logs se leen ANTES de borrar. Con borrado
automatico el contenedor puede desaparecer antes de que nadie los lea, y el fallo queda sin
explicacion.

`cosecha/docker-wait-with-timeout.js` — la espera del contenedor con limite duro: al vencer lo mata.
Sin esto, un contenedor colgado congela la cola entera y nadie se entera hasta que alguien pregunta.

`cosecha/docker-job-log-markers.js` — separa los flujos del registro de Docker y define un protocolo
minimo de progreso por la salida estandar. Evita montar una API o un socket aparte solo para saber
por que paso va el trabajo.

`cosecha/docker-orphan-container-cleanup.js` — decide al arrancar que contenedores de un proceso
anterior muerto hay que parar y borrar.

`cosecha/pg-secret-file-connection.js` — la cadena de conexion se arma desde un fichero de secreto,
con la variable de entorno solo como sustitucion explicita para pruebas.

Nada de esto compite con un orquestador de cientos de nodos: es el trozo que hace falta cuando un
trabajo por contenedor se resuelve en una maquina y montar un orquestador seria mas caro que el
problema.
