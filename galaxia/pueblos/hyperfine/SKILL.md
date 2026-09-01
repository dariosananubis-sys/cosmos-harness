---
cosmos: pueblo
nombre: hyperfine
padre: rendimiento/perfilado
resumen: Compara dos comandos cualesquiera con calentamiento y estadistica, en vez de cronometrar a ojo una vez.
---

https://github.com/sharkdp/hyperfine · Apache-2.0 (o MIT) · 28.781★ · push 2026-04-30 (comprobado 2026-09-01)

```bash
brew install hyperfine

hyperfine --warmup 3 './version-vieja datos.txt' './version-nueva datos.txt'
hyperfine --warmup 3 --prepare 'sync' --export-json medicion.json \
  -L hilos 1,2,4,8 './prog --hilos {hilos}'
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

Ojo: **mide el proceso entero, arranque incluido**. Para algo que tarda milisegundos, el arranque del
intérprete domina la medición y la comparación no dice nada del código; ahí hace falta un banco de
pruebas dentro del proceso. Y su último empujón es de abril de 2026: es una herramienta madura y
estable, no abandonada, pero conviene saberlo.
