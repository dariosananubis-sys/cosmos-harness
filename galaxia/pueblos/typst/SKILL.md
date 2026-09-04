---
cosmos: pueblo
nombre: typst
padre: documentos/publicacion
resumen: Composicion de documentos con sintaxis moderna y compilacion casi instantanea; sin el purgatorio de LaTeX.
---

https://github.com/typst/typst · Apache-2.0 · 55.818★ · último push 2026-09-01 (comprobado 2026-09-03)

```bash
brew install typst
```

```typst
// informe.typ
#set document(title: "Informe mensual")
#set page(numbering: "1")
#set text(font: "New Computer Modern", size: 11pt)

= Informe mensual

Ingresos totales: #let total = 12450.50 #total €

#table(
  columns: 3,
  [*Categoria*], [*Cantidad*], [*Total*],
  [Servicios], [12], [8.200 €],
  [Productos], [30], [4.250,50 €],
)
```

```bash
typst compile informe.typ informe.pdf
typst watch informe.typ informe.pdf     # recompila al guardar, sub-segundo
```

Gana a LaTeX en velocidad y en mensajes de error: compila en milisegundos donde LaTeX tarda
segundos por cada pasada, y un error de sintaxis señala la línea exacta en vez del clásico
`! Undefined control sequence` sin contexto útil. Es también un lenguaje de programación real por
debajo (variables, funciones, bucles) sin la capa de macros de TeX encima. Frontera con `quarto`:
aquel orquesta contenido narrativo con código ejecutado (R, Python, Julia) desde Markdown y puede
usar Typst como uno de sus motores de salida; esto es el motor de composición en sí, para quien
escribe el documento directamente en su sintaxis.

Ojo: el ecosistema de paquetes (plantillas, bibliografía, temas) es mucho más pequeño que el de
CTAN tras treinta años de LaTeX — una plantilla académica muy específica que exige una revista
puede no existir todavía, y hay que escribirla desde cero. Y es un lenguaje distinto de LaTeX, no
un compatible: un documento `.tex` no se migra automáticamente.
