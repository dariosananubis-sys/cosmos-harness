---
cosmos: pueblo
nombre: volatility3
padre: ciberseguridad/analisis/forense
resumen: Saca procesos, conexiones y claves de un volcado de RAM sin la maquina viva.
---

https://github.com/volatilityfoundation/volatility3 · Volatility Software License 1.0 (licencia propia, la API de GitHub la reporta como `NOASSERTION`) · 4.366★ · último push 2026-08-19 (comprobado 2026-09-01)

```bash
pipx install volatility3
```

```bash
# qué procesos había vivos en el instante del volcado
vol -f volcado.raw windows.pslist

# procesos ocultos al listado normal (comparación por recorrido de pool)
vol -f volcado.raw windows.psscan

# conexiones de red y su proceso dueño
vol -f volcado.raw windows.netscan

# extraer el ejecutable de un proceso sospechoso a disco
vol -f volcado.raw -o ./extraido/ windows.dumpfiles --pid 1234
```

Se usa la versión tres y no la dos (`volatilityfoundation/volatility`, 8.063★ históricas pero sin
publicar desde 2025-05-16): las estrellas están en la vieja y el desarrollo en esta. Gana a
`Velocidex/velociraptor` (4.223★) para este caso concreto porque Velociraptor recoge a escala sobre
máquinas vivas, y aquí se analiza un volcado ya tomado, sin sistema al que preguntar.

Ojo, dos cosas. **La licencia no es estándar**: es propia de la fundación, hay que leerla antes de
redistribuir nada o de empotrarla en un producto de cliente. Y necesita **símbolos** del sistema
volcado; si no los encuentra, muchos complementos devuelven tabla vacía en lugar de fallar, así que
una salida vacía se comprueba con `windows.info` antes de concluir que no había nada.
