---
cosmos: pueblo
nombre: reprozip
padre: cientifico
resumen: Empaqueta lo que la ejecucion uso de verdad rastreando sus llamadas al sistema, no lo que alguien declaro.
---

https://github.com/VIDA-NYU/reprozip · BSD-3-Clause · 362★ · último push 2026-02-04 (comprobado 2026-09-01)
(comprobado por API de GitHub el 2026-09-01). Siete meses sin movimiento: es el mas pequeno y el
menos activo de este nicho, y se dice.

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

Y lo que no hace bien, que es mucho y hay que decirlo entero:

- El trazado usa `ptrace`, asi que **solo traza en Linux**. En un Mac de 8 GB no se puede empaquetar
  nada nativamente: hay que trazar dentro de un contenedor o en una maquina Linux. `reprounzip`
  —la mitad que reproduce— si corre en el Mac.
- No captura la red. Si el guion descarga algo, el paquete grabara la llamada y no el servidor: el
  dia que ese URL muera, el `.rpz` deja de reproducir.
- No captura la GPU ni el hardware. Un paquete hecho con CUDA no vuelve a correr en un portatil.
- Congela una ejecucion, no un proyecto. No es sustituto de `pixi` para trabajar a diario; es el
  sello que se pone cuando el resultado ya esta y hay que poder demostrarlo dentro de dos anos.

Por su tamano y su ritmo, entra como herramienta de sellado puntual, no como pieza del flujo diario.
