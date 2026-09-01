---
cosmos: pueblo
nombre: bpftrace
padre: rendimiento/velocidad/perfilado
resumen: Pregunta al nucleo que esta pasando ahora mismo con una linea, sin escribir ni compilar un programa aparte.
---

https://github.com/bpftrace/bpftrace · Apache-2.0 · 10.302★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
sudo apt install bpftrace          # Linux; requiere root y nucleo con BTF

# que ficheros abre cada proceso, ahora mismo
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args->filename)); }'

# histograma de latencia de lectura de disco
sudo bpftrace -e 'tracepoint:block:block_rq_issue { @i[args->dev] = nsecs; }
                  tracepoint:block:block_rq_complete /@i[args->dev]/ {
                    @ms = hist((nsecs - @i[args->dev]) / 1000000); delete(@i[args->dev]); }'

sudo bpftrace -l 'tracepoint:syscalls:*'   # que se puede observar
```

Es la respuesta cuando el problema **no está en el proceso sino debajo**: qué ficheros abre, cuánto
espera en disco, qué llamadas al sistema se comen el tiempo, qué proceso ajeno está compitiendo. Un
perfilador de muestreo como `samply` o `py-spy` no lo ve, porque mira dentro de un proceso y aquí lo
que se mira es el núcleo. Gana a `strace` por coste: `strace` para el proceso en cada llamada y lo
ralentiza un orden de magnitud; esto agrega en el propio núcleo y se puede dejar corriendo en
producción.

Aviso de entorno, porque es la trampa habitual: **esto es del núcleo de Linux**. Desde un portátil de
otra familia se usa contra una máquina virtual o un servidor, no contra el propio sistema — en macOS
no hay equivalente directo (lo más cercano es `dtrace`, y la protección de integridad del sistema lo
limita).

Ojo: **pide root**, y un guion mal escrito puede añadir latencia notable al sistema que observa. Los
`tracepoint:` son estables entre versiones del núcleo; los `kprobe:` sobre funciones internas **no**,
así que un guion copiado de un artículo puede fallar o —peor— medir otra cosa en un núcleo distinto.
Comprobar con `bpftrace -l` antes de fiarse de un número.
