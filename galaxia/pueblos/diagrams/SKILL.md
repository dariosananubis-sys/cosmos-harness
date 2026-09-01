---
cosmos: pueblo
nombre: diagrams
padre: documentos/diagramas
resumen: Arquitectura de nube dibujada como codigo, con los iconos oficiales de cada proveedor y del orquestador.
---

https://github.com/mingrammer/diagrams · MIT · 42.575★ · push 2026-08-16 (comprobado 2026-09-01)

```bash
brew install graphviz && pip install diagrams

python - <<'PY'
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

with Diagram("web", filename="web", outformat="png", show=False):
    ELB("balanceador") >> EC2("api") >> RDS("datos")
PY
# deja web.png en el directorio
```

`mermaid` vive dentro del texto y `d2` compone mejor el diagrama autónomo, pero **ninguno de los dos
tiene el catálogo de iconos oficiales** de AWS, Azure, GCP, Kubernetes, OCI y compañía. Cuando el
diagrama es de infraestructura y tiene que reconocerse de un vistazo en una reunión, ese catálogo es
la diferencia. Se escribe en Python, así que el diagrama se regenera con el código en integración
continua en vez de envejecer en una carpeta.

Ojo: la colocación la decide Graphviz y **no se controla bien**. A partir de veinte o treinta nodos
sale un enredo que no se arregla desde el código, solo empujando con `Cluster` y con el orden de
declaración; para ese tamaño, `d2`. Y necesita Graphviz instalado en el sistema: sin él,
`pip install` funciona y la ejecución falla con un error de ejecutable no encontrado que no dice qué
hay que instalar.
