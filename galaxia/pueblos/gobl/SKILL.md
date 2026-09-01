---
cosmos: pueblo
nombre: gobl
padre: saas/facturacion
resumen: Modela la factura una vez en formato neutral y la emite a cada normativa con un complemento.
---

https://github.com/invopop/gobl · Apache-2.0 · 306★ · push 2026-09-01 (comprobado 2026-09-01)

```bash
go install github.com/invopop/gobl.dev/cmd/gobl@latest

gobl build factura.json                # valida y calcula impuestos
gobl sign  factura.json -o firmada.json

# conversores por normativa, cada uno su repositorio:
#   https://github.com/invopop/gobl.facturae        Apache-2.0 ·  7★ · push 2026-08-17
#   https://github.com/invopop/gobl.verifactu       AGPL-3.0  · 15★ · push 2026-08-17
#   https://github.com/invopop/gobl.es.ticketbai    AGPL-3.0  ·  7★ · push 2026-08-17
go install github.com/invopop/gobl.verifactu/cmd/gobl.verifactu@latest
gobl.verifactu convert firmada.json -o verifactu.xml
```

Es un **cambio de arquitectura, no un conversor más**: la factura se modela una vez en un formato
neutral con sus impuestos calculados y firmada, y se emite N veces a cada normativa con un
complemento. Las bibliotecas sueltas de cada norma (`facturae-php`, `tbai-php-lib` y compañía)
quedan citadas y fuera: cubren una jurisdicción cada una y obligan a reimplementar la lógica de
negocio por cada país al que se venda.

**Normas y territorios que cubre** (por complemento, no en el núcleo):
- **Facturae 3.2.x** — factura electrónica a la administración española vía FACe. España.
- **Verifactu** — sistemas de facturación verificable del Reglamento aprobado por el RD 1007/2023 y
  la Orden HAC/1177/2024. España, territorio común.
- **TicketBAI** — Bizkaia, Gipuzkoa y Álava, cada una con su variante. País Vasco.
- Además, formatos europeos generales (EN 16931 / UBL) por otros complementos del mismo proyecto.

Ojo, y es lo primero que hay que mirar: **la normativa española de facturación cambia y las fechas de
obligatoriedad se han movido varias veces** (Verifactu y la factura electrónica entre empresas de la
Ley 18/2022 «Crea y Crece» llevan varios aplazamientos). Los calendarios NO se han podido verificar
en vivo en esta pasada —cupo de búsqueda agotado el 2026-09-01—, así que **antes de prometer una
fecha a un cliente hay que confirmarla en el BOE o en la sede de la AEAT**. Esta ficha cita las
normas, no su calendario.

Ojo técnico: `gobl` valida y firma, pero **no presenta**. El envío al servicio de la administración,
sus certificados y su gestión de errores están fuera; y las estrellas de los conversores son de un
dígito, así que un cambio de esquema del organismo puede tardar en llegar. Antes de facturar de
verdad, probar contra el entorno de pruebas del organismo y tener plan si el conversor se queda
atrás.
