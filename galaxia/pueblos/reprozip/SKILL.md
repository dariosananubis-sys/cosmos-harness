---
cosmos: pueblo
nombre: reprozip
padre: cientifico/reproducible
resumen: Empaqueta lo que la ejecucion uso de verdad rastreando sus llamadas al sistema, no lo que alguien declaro.
---

https://github.com/VIDA-NYU/reprozip · BSD-3-Clause · 362★ · último push 2026-02-04 (comprobado
2026-09-04, API de GitHub y `commits/HEAD.atom`: el último commit de HEAD es de 2026-01-18, casi ocho
meses; no archivado). Es el más pequeño y el menos activo de este país, y se dice.

```bash
pip install reprozip reprounzip reprounzip-docker    # el trazador exige Linux
```

```bash
# 1. en la maquina donde YA funciona (Linux):
reprozip trace python analisis.py --entrada datos/limpio.parquet
reprozip pack experimento.rpz

# 2. en cualquier otra maquina:
reprounzip docker setup experimento.rpz destino/
reprounzip docker run destino/
```

Es el mecanismo mas literal de reproducibilidad del nicho: observa las llamadas al sistema del
proceso real y recoge los binarios, las bibliotecas del sistema y los ficheros de datos que toco de
verdad. La diferencia con un `requirements.txt` o con `pixi` no es de comodidad, es de naturaleza:
aquellos declaran lo que alguien cree necesario, este captura lo que hizo falta. Para volver a
correr en otra maquina algo que ya funciono una vez, es la via corta.

Ojo, y es mucho — lo que no hace bien, dicho entero:

- El trazado usa `ptrace`, asi que **solo traza en Linux**: en macOS no se puede empaquetar nada
  nativamente, hay que trazar dentro de un contenedor o en una maquina Linux. `reprounzip` —la
  mitad que reproduce— si corre en el Mac.
- No captura la red. Si el guion descarga algo, el paquete grabara la llamada y no el servidor: el
  dia que ese URL muera, el `.rpz` deja de reproducir.
- No captura la GPU ni el hardware. Un paquete hecho con CUDA no vuelve a correr en un portatil.
- Congela una ejecucion, no un proyecto. No es sustituto de `pixi` para trabajar a diario; es el
  sello que se pone cuando el resultado ya esta y hay que poder demostrarlo dentro de dos anos.

Gana a `pixi` y a `dvc`, sus dos vecinos de este país, en la única pregunta que ninguno de los dos
contesta: **qué usó de verdad la ejecución**. `pixi` reproduce el entorno que alguien declaró en un
fichero de bloqueo; `dvc` reproduce la cadena de etapas con los datos que alguien enganchó. Los dos
parten de una declaración humana, y lo que no está declarado no viaja: la biblioteca del sistema que
se instaló a mano, el fichero de `/etc` que el guion lee, el binario auxiliar que se llama por
`subprocess`. `reprozip` no pregunta, observa.

Por eso se queda pese a su tamaño y su ritmo, y con el papel acotado: `pixi` para trabajar a diario,
`dvc` para encadenar etapas y versionar datos, y `reprozip` una sola vez, cuando el resultado ya está
y hay que poder demostrarlo dentro de dos años. Si ese sello no hace falta, este pueblo sobra —y esa
es la condición con la que se queda.
