---
cosmos: pueblo
nombre: snakemake
padre: cientifico
resumen: Cada regla declara sus entradas y salidas y fija su propio entorno paso a paso.
---

https://github.com/snakemake/snakemake - MIT - 2.854 estrellas - ultimo push 2026-08-31 (comprobado
por API de GitHub el 2026-09-01).

```bash
pipx install snakemake
```

```python
# Snakefile
MUESTRAS = ["m1", "m2", "m3"]

rule all:
    input: expand("resultados/{m}.txt", m=MUESTRAS)

rule procesar:
    input:  "datos/{m}.parquet"
    output: "resultados/{m}.txt"
    conda:  "entornos/analisis.yaml"     # cada regla fija su propio entorno
    threads: 2
    shell:  "python src/procesar.py {input} > {output}"
```

```bash
snakemake -n                          # simulacro: dice que reejecutaria y por que
snakemake --cores 4 --use-conda
snakemake --dag | dot -Tsvg > grafo.svg
```

Gana a un `Makefile` —que es la alternativa honesta, no un rival de paja— en dos cosas concretas:
los comodines con nombre (`{m}`) evitan escribir una regla por muestra, y `conda:` / `container:` por
regla hacen que la propia tuberia fije su entorno paso a paso en vez de depender de lo que hubiera
instalado ese dia. Frontera con `dbt-core`: aquel encadena consultas dentro de un almacen de datos,
este encadena ficheros y procesos de cualquier tipo.

Y lo que no hace bien: decide por marca de tiempo de los ficheros, no por hash del contenido. Un
`touch` sobre una entrada reejecuta todo; copiar los ficheros con `cp` sin `-p` cambia las fechas y
lo mismo. Si lo que importa es "cambio el DATO", eso lo hace `dvc`, y los dos se usan juntos sin
problema.

Y el falso verde de siempre en este pueblo: `snakemake` sin argumentos, si todos los ficheros de
salida ya existen, dice "Nothing to be done" y sale con codigo 0. Eso no significa que la tuberia
funcione — significa que no la ha ejecutado. Antes de fiarse, `snakemake -n` para ver el plan, y
`--forceall` en una carpeta limpia para comprobar de verdad.
