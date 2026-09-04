---
cosmos: pueblo
nombre: plan-auditado
padre: agentes-ia/instrumentacion
resumen: Audita el plan antes de creerselo: campos, tipos, dependencias que existen y rastro de lo que dice estar hecho.
origen: propio
---

`scripts/audit-harness.sh` — herramienta propia, no de GitHub. Solo lectura.

```bash
chmod +x scripts/audit-harness.sh
scripts/audit-harness.sh                      # audita los proyectos del repo actual
scripts/audit-harness.sh ruta/al/proyecto     # solo uno
```

Valida `feature_list.json` como un contrato: campos obligatorios, tipos, estado dentro de los
permitidos, criterios de aceptación con su prefijo `R<n>:` y —el que se cuela siempre— que cada
`depends_on` apunte a un identificador que **existe de verdad**. Un plan con una dependencia fantasma
parece completo y bloquea en silencio.

La segunda mitad separa lo declarado de lo demostrado: si una tarea dice estar terminada, exige su
línea en el LEDGER; si dice llevar diseño previo, exige el `design.md`.

Gana a `jq` a mano en un punto concreto: si `jq` no está instalado, en vez de saltarse la comprobación
usa un lector propio. Una validación que se desactiva sola cuando falta una dependencia es peor que no
tenerla, porque **pasa en verde**.

Ojo: valida el esquema y el rastro, no la calidad del plan. Una feature con criterios de aceptación
bien formados y vacíos de contenido pasa el auditor sin una queja.
