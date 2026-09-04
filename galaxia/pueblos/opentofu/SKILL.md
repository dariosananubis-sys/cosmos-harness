---
cosmos: pueblo
nombre: opentofu
padre: infraestructura/despliegue
resumen: Aprovisiona infraestructura cloud declarativa; fork de Terraform bajo licencia MPL, no BUSL.
---

https://github.com/opentofu/opentofu · MPL-2.0 · 30.025★ · último push 2026-09-02 (comprobado 2026-09-03)

```bash
brew install opentofu
```

```bash
# main.tf minimo
# resource "local_file" "ejemplo" {
#   filename = "RUTA/AL/PROYECTO/salida.txt"
#   content  = "gestionado por opentofu"
# }

tofu init
tofu plan     # que va a crear/cambiar/destruir, sin tocar nada todavia
tofu apply
```

Se elige `opentofu` y no `terraform` por la licencia, no por el motor: son el mismo lenguaje
(HCL) y el mismo modelo de estado porque `opentofu` nace en 2023 como fork 1:1 del último
Terraform en MPL-2.0, justo antes de que HashiCorp cambiara la licencia de las versiones nuevas a
BUSL (Business Source License) — una licencia que **restringe usarlo dentro de un producto que
compita** con HashiCorp, y que revierte a open source solo a los 4 años. `opentofu` vive bajo la
Linux Foundation con licencia MPL de verdad, sin esa cláusula ni esa fecha de caducidad, con
compatibilidad de proveedores y módulos del ecosistema Terraform existente.

Ojo: al ser un fork joven, algunas features muy recientes de Terraform (las de después de 2023)
tardan más en llegar o no llegan igual. El estado (`.tfstate`) sigue siendo el punto frágil de
siempre: si se pierde o se desincroniza del mundo real, `opentofu` no lo adivina — hay que
`import` o reconciliar a mano. Y como con cualquier IaC: `apply` sin revisar `plan` puede destruir
un recurso vivo de producción sin previo aviso si el código cambió el identificador de un recurso.
