---
cosmos: pueblo
nombre: nextflow
padre: cientifico/reproducible
resumen: Tuberia declarada como grafo de procesos que corre igual en portatil, cluster HPC o la nube, sin reescribirla.
---

https://github.com/nextflow-io/nextflow · Apache-2.0 · 3.478★ · último push 2026-09-02 (comprobado
2026-09-03)

```bash
curl -s https://get.nextflow.io | bash    # deja el binario ./nextflow; requiere Java 17+
```

```groovy
// main.nf
process PROCESAR {
    container 'python:3.12-slim'          // o conda '...'; el entorno viaja con el proceso
    input:  path muestra
    output: path "resultado_${muestra}.txt"
    script: "python3 procesar.py ${muestra} > resultado_${muestra}.txt"
}

workflow {
    Channel.fromPath('datos/*.parquet') | PROCESAR
}
```

```bash
nextflow run main.nf -resume              # -resume reanuda solo lo que cambio, con cache por hash
nextflow run main.nf -profile slurm       # el mismo fichero corre en un cluster HPC sin tocarlo
```

Rival directo de `snakemake`, aunque hoy vive en el país vecino `cientifico/experimentos` de este
mismo sistema solar: ambos declaran una tubería como grafo de dependencias con el entorno fijado por
paso. La diferencia que pesa es el ecosistema de ejecución: `nextflow` trae de fábrica perfiles para
SLURM, AWS Batch, Google Cloud Batch y Kubernetes sin cambiar una línea del flujo, mientras que
`snakemake` necesita un complemento de ejecutor por cada uno. Es la base de `nf-core`, el catálogo de
tuberías de bioinformática más grande que hay, lo que en la práctica significa que gran parte del
trabajo ya está escrito y solo hay que adaptarlo.

Gana a `snakemake` también en la caché de reanudación: `-resume` decide por **hash del contenido** de
cada entrada, no por marca de tiempo del fichero — el mismo falso verde que la ficha de `snakemake`
señala en sí misma (un `touch` reejecutando todo) no se da aquí.

Ojo: el lenguaje es Groovy sobre la JVM, así que hay que tener Java instalado y el arranque de cada
ejecución paga el coste de esa máquina virtual — en un guion muy corto se nota más que en `snakemake`
o `just`, que no cargan una JVM. Y el falso verde propio: `-resume` compara el hash de las **entradas
declaradas**, no de todo lo que el proceso pudiera leer por fuera del canal — un proceso que lee un
fichero de configuración sin declararlo como `input:` no dispara la reejecución cuando ese fichero
cambia, y el resultado queda obsoleto en silencio. Y el instalador por `curl | bash` ejecuta código
remoto sin revisar: para producción, leer el guion antes.
