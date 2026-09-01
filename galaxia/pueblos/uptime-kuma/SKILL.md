---
cosmos: pueblo
nombre: uptime-kuma
padre: infraestructura/vigilancia
resumen: Comprueba desde fuera que los servicios responden y avisa cuando dejan de hacerlo.
---

https://github.com/louislam/uptime-kuma · MIT · 90.830★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
docker run -d --restart=always --name uptime-kuma \
  -p 3001:3001 -v uptime-kuma:/app/data louislam/uptime-kuma:2
# panel en http://localhost:3001

# monitor de empuje: la tarea programada avisa de que sigue viva
# (la URL la da el propio panel al crear un monitor de tipo Push)
curl -s "http://localhost:3001/api/push/<CLAVE_EMPUJE>?status=up&msg=OK"
```

Comprobación **desde fuera**, que es la única que detecta la caída entera: un vigilante que corre en
la misma máquina que se cayó no avisa de nada. Gana a `Gatus` y a `Zabbix` por coste de arranque —un
contenedor y cero ficheros de configuración— para el caso real de la casa, que es vigilar unas
decenas de sitios de cliente y sus certificados.

Sus **monitores de empuje** cubren además el interruptor de hombre muerto de una tarea programada: si
la copia nocturna no llama, salta la alerta. Por eso queda fuera la herramienta dedicada solo a
vigilar tareas programadas: se solapa.

Frontera con `acceso-remoto`: aquel repara desde dentro, este mira desde fuera y avisa. Si lo que se
cae es justo el canal por el que entrarías a arreglarlo, el aviso llega y no sirve de nada — por eso
entran los dos.

Ojo: el estado vive en SQLite dentro del volumen, y **copiar ese fichero en caliente da una base
corrupta**. La copia se hace con `sqlite3 ... ".backup"` o parando el contenedor. Y su
configuración se edita solo por el panel: no hay fichero declarativo, así que reconstruir la
instancia desde cero es trabajo a mano — ahí `Gatus`, que sí es declarativo, es mejor herramienta.
