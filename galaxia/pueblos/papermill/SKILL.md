---
cosmos: pueblo
nombre: papermill
padre: analitica
resumen: Ejecuta un cuaderno con parametros distintos y deja cada ejecucion guardada como prueba.
---

https://github.com/nteract/papermill · BSD-3-Clause · 6.477★ · último push 2026-07-06 (comprobado por
API de GitHub el 2026-09-01)

```bash
pip install papermill ipykernel
```

```python
# en el cuaderno de origen, UNA celda etiquetada como "parameters" en sus metadatos
mes = "2026-01"
cliente = "<SLUG_DEL_CLIENTE>"
```

```bash
# una ejecucion por cliente y mes, cada una con su cuaderno de salida
for c in cliente-a cliente-b cliente-c; do
  papermill informe.ipynb "salidas/${c}-2026-01.ipynb" -p cliente "$c" -p mes 2026-01
done

# y a HTML para mandarlo
jupyter nbconvert --to html --no-input salidas/cliente-a-2026-01.ipynb
```

El valor no es ejecutar el cuaderno: es que **la ejecución queda guardada con sus parámetros dentro**.
Tres meses después, cuando el cliente discute una cifra, existe el fichero exacto que la produjo, con
qué valores y con qué salida —no «el cuaderno», que desde entonces se ha tocado nueve veces.

Gana a `jupyter nbconvert --execute`, que es la alternativa que ya viene instalada: aquel ejecuta el
cuaderno pero **no acepta parámetros**, así que el mes y el cliente acaban escritos a mano dentro del
código, y cada informe es una copia del cuaderno con una línea cambiada. Ese es el patrón que produce
catorce cuadernos casi iguales y ninguno correcto.

Frontera con `marimo`, que es el vecino: para lo que se escriba de cero, aquel es mejor porque no
tiene estado oculto. Este entra por lo que ya existe — el cuaderno de Jupyter que el cliente o un
compañero ya usa y que no se va a reescribir para automatizarlo.

Y lo que no hace bien:

- **Hereda el estado oculto del cuaderno.** Papermill ejecuta de arriba abajo, así que corrige el
  desorden de ejecución, pero no ve una celda que depende de una variable que ya no se define: eso
  falla en la ejecución, y solo si de verdad falla.
- **Un cuaderno que tarda cuarenta minutos tarda cuarenta minutos por cliente.** No paraleliza ni
  cachea nada.
- **Si la celda no está etiquetada `parameters`, los `-p` se inyectan igual y no se usan**: la
  ejecución sale en verde con los valores por defecto. Es el falso verde de este pueblo, y se detecta
  mirando la celda inyectada en el cuaderno de salida.
- Ritmo de desarrollo bajo (último empujón 2026-07-06, dos meses antes de esta comprobación): estable
  y muy usado, pero no esperar novedades.
