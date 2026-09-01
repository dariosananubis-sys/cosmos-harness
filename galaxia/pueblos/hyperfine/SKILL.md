---
cosmos: pueblo
nombre: hyperfine
padre: rendimiento/velocidad/perfilado
resumen: Compara dos comandos cualesquiera con calentamiento y estadistica, en vez de cronometrar a ojo una vez.
---

https://github.com/sharkdp/hyperfine · Apache-2.0 (o MIT) · 28.781★ · push 2026-04-30 (comprobado 2026-09-01)

```bash
brew install hyperfine

# EN CALIENTE: "¿es de verdad más rápida la nueva?", con la caché ya llena
hyperfine --warmup 3 './version-vieja datos.txt' './version-nueva datos.txt'

# EN FRÍO: "¿cuánto tarda la primera vez, con el fichero de verdad?"
#   sin --warmup a propósito, y tirando la caché de disco antes de CADA repetición
sudo -v
hyperfine --prepare 'sudo purge' './version-nueva /ruta/al/fichero-grande-real'

# barrido de un parámetro, con la salida en JSON para el informe
hyperfine --warmup 3 --export-json medicion.json -L hilos 1,2,4,8 './prog --hilos {hilos}'
```

`samply` dice **dónde** se va el tiempo dentro de un proceso; esto dice **si** la versión nueva es de
verdad más rápida que la vieja, y con cuánta confianza. Hace calentamiento, repite hasta tener
muestra, da media y desviación típica y avisa cuando los valores atípicos sugieren interferencia
externa. Gana al `time` del intérprete de órdenes en lo único que importa: **un cronometraje único
está contaminado** por la caché fría y por lo que hubiera corriendo al lado, y es exactamente el
número que se suele publicar en un informe.

Sirve para cualquier binario o guion, no solo para código propio, así que es también la forma honesta
de comprobar una mejora antes de anunciarla — y la pareja obligada de `mimalloc`, que se mide antes y
después.

Ojo, y son los dos avisos que separan una medición que decide de una que adorna:

- **`--warmup` mide en caliente, y eso es una respuesta, no la respuesta.** Un banco de pruebas
  diminuto con la caché llena contesta «cuánto tarda la vez cincuenta», que casi nunca es la
  pregunta del usuario. Para el frío está `--prepare`, y ahí hay trampa de plataforma: la receta que
  trae su propia documentación es de Linux (`echo 3 | sudo tee /proc/sys/vm/drop_caches`) y **en
  macOS ese fichero no existe**. `sync` tampoco vale —vacía escrituras pendientes, no la caché de
  lectura—, así que un `--prepare 'sync'` en un Mac mide caliente aparentando lo contrario, y sale
  un número bonito que nadie podrá reproducir el lunes. Lo que sí tira la caché aquí es
  `sudo purge` (`/usr/sbin/purge`): funciona, es global y es lento, o sea que la tanda dura minutos
  y conviene lanzarla con la máquina libre.
- **Por debajo de 5 ms el número es en buena parte ruido del intérprete de órdenes.** Por defecto
  ejecuta a través de `/bin/sh` y **resta una estimación calibrada** del arranque de ese intérprete;
  cuando el comando tarda menos que la propia corrección, lo que se publica es el error de la resta.
  Ahí va `-N` / `--shell=none`, y entonces el comando no admite sintaxis de consola (`*`, `~`).

Y lo tercero, que es de encuadre: **mide el proceso entero, arranque incluido**. Para una función de
milisegundos, el arranque del intérprete domina y la comparación no dice nada del código; eso pide un
banco de pruebas dentro del proceso, no esto. Su último empujón es de abril de 2026: herramienta
madura y estable, no abandonada, pero conviene saberlo.
