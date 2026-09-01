---
cosmos: pueblo
nombre: xlsxwriter
padre: analitica
resumen: Genera la hoja de calculo que el cliente abrira, con formulas vivas, formatos y graficos nativos.
---

https://github.com/jmcnamara/XlsxWriter · BSD-2-Clause · 3.968★ · último push 2026-08-04 (comprobado
por API de GitHub el 2026-09-01)

```bash
pip install XlsxWriter
```

```python
import xlsxwriter

libro = xlsxwriter.Workbook("informe.xlsx")
hoja = libro.add_worksheet("Ventas")

euro = libro.add_format({"num_format": "#,##0.00 €"})
neg  = libro.add_format({"bold": True})

hoja.write_row("A1", ["Categoria", "Unidades", "Importe"], neg)
datos = [("A", 120, 3400.5), ("B", 80, 2100.0), ("C", 45, 990.25)]
for i, fila in enumerate(datos, start=1):
    hoja.write_row(i, 0, fila)
    hoja.write_number(i, 2, fila[2], euro)

# formula VIVA: el cliente cambia una unidad y el total se recalcula solo
hoja.write_formula(len(datos) + 1, 2, f"=SUM(C2:C{len(datos)+1})", euro)
hoja.conditional_format(1, 2, len(datos), 2, {"type": "3_color_scale"})

grafico = libro.add_chart({"type": "column"})
grafico.add_series({"categories": ["Ventas", 1, 0, len(datos), 0],
                    "values":     ["Ventas", 1, 2, len(datos), 2]})
hoja.insert_chart("E2", grafico)
hoja.autofit()
libro.close()
```

El informe que de verdad se usa en una pyme se abre en una hoja de cálculo, no en un panel web. Y la
diferencia entre un CSV y esto es que aquí el cliente **puede seguir trabajando**: la fórmula se
recalcula, el formato de moneda no se pierde y el gráfico es un objeto del propio programa, no una
imagen pegada.

Gana a `openpyxl`, que es el rival real y hace las dos direcciones, en lo que importa cuando solo hay
que escribir: soporta más de la especificación —formato condicional, validación de datos, gráficos
con series bien definidas, `autofit`— y escribe en flujo con `constant_memory`, así que una hoja de
cien mil filas no se construye entera en RAM. Si además hay que **leer** un `.xlsx` existente, este no
sirve y ahí gana `openpyxl`.

Frontera con `gspread`: aquel cuando la hoja vive en la nube del cliente y es la interfaz; esto cuando
hay que entregar un fichero.

Y lo que no hace bien:

- **Solo escribe.** No abre, no lee, no modifica un fichero existente. Un encargo de «actualiza esta
  plantilla» no es para este pueblo.
- **Las fórmulas no se evalúan aquí.** El fichero guarda la fórmula y un resultado en blanco hasta que
  alguien lo abre; si algo consume ese `.xlsx` sin abrirlo (otro guion, un importador), lee celdas
  vacías. Para ese caso se escribe también el valor calculado con `write_formula(..., value=...)`.
- **`constant_memory` obliga a escribir en orden**, fila a fila y de arriba abajo: volver atrás a
  cambiar una celda deja de funcionar.
- El formato es OOXML: lo abren Excel, LibreOffice y Google Sheets, pero los gráficos complejos no se
  ven idénticos en los tres.
