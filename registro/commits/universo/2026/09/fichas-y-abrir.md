---
cosmos: lluvia
nombre: fichas-y-abrir
moja: []
resumen: Parte del arreglo de F10, F15, F20, F21, F22, F24 y un hallazgo nuevo, F25.
---

# El mapa daba direcciones que no llevaban a ningún sitio

Seis fallos del especialista y uno que salió al arreglarlos. Todos comparten forma: algo
**decía** una cosa y **hacía** otra, y nada lo vigilaba.

## F10 — el agua mojaba a todo el mundo por igual

`abrir --con-agua` devolvía los seis mares enteros para cualquier nodo. El filtro comparaba
el nicho contra el glob de `moja` (`nicho in str(moja)`), y como **todos** los `moja`
empiezan por `**/`, la comprobación acertaba siempre. `trading` y `cumplimiento`, que no
comparten nada, recibían idéntica lista: 1.499 tokens de cuerpo en cada apertura. Era el
«cargarlo todo por si acaso» del `GOAL.md` §2, dentro del comando cuyo docstring cita ese
mismo párrafo.

El error estaba en la premisa, no en el `or`: **`moja` es un glob de ficheros, no una
etiqueta de oficio**. Ahora `abrir --tocando <fichero>` casa la ruta real con
`_glob_a_regex`, el mismo motor que usa E11, y sin fichero no devuelve agua — adivinar qué
se toca es indistinguible de devolverlo todo. Y lista **nombre y resumen**, nunca el cuerpo.

    trading + estrategia.py -> criterio, resistencia, revision
    trading + tests/x.py    -> criterio, pruebas, resistencia, revision
    web     + index.html    -> accesibilidad

## F22 — la estrella se enganchaba por el nombre suelto

`ilumina` se comparaba contra `{referencia, nombre}`. `NUCLEO.md` §1 exige la ruta completa
justamente para que dos nodos homónimos bajo padres distintos no se confundan; aceptar el
nombre reabría esa puerta. Hoy no mordía porque no hay colisiones — que es exactamente lo
que §1 dice vigilar con un canario, no lo que autoriza a relajarlo.

## F20 — 38 fichas nombraban guiones que no existían

Citaban `cosecha/<script>`, una ruta relativa a la raíz de COSMOS que `compilar` no copia y
`proyectar` no lleva a ninguna parte: en un proyecto proyectado, esas 38 skills nombraban
ficheros ausentes. Se han colocado los 69 guiones dentro del directorio de su pueblo
(`scripts/`, como los nueve que ya lo hacían) y reescrito las citas. Los 69 pasaron antes el
escáner de secretos; los tres hallazgos eran falsos positivos (`ta**sk-**notification`,
`ejemplo@dominio.com`).

## F24 — dos convenciones de ficha conviviendo

207 fichas con `· MIT · 3.968★ ·` y 45 con ` - MIT - 3.968 estrellas - `. Normalizadas a la
primera, que además lleva la fecha de comprobación. La fecha no se ha inventado: sale del
commit que introdujo cada ficha. Comprobado que no se perdió prosa — las únicas palabras
que desaparecieron del corpus son `cosecha` (165), `estrellas` (48) y `ultimo` (46).

Queda abierto el otro medio F24: **un commit de 38 lleva una identidad de máquina**.
Limpiarlo reescribe la historia y obliga a `--force-with-lease` sobre `main`, que necesita
el sí explícito de Darío. Preparado, no ejecutado.

## F15 y F21 — la spec decía lo que hubo, no lo que hay

`mar/revision` llevaba semanas en el árbol y `spec/UNIVERSO.md` seguía anunciando cinco
mares. Y la motivación de E17 usaba como ejemplo a cazar justo el caso que E17 **deja
pasar**. Ahora la spec separa las dos formas de duplicar —reedición y reformulación— y
publica la tabla medida, con el límite en su sitio.

## F25 — hallazgo nuevo: E17 no hacía lo que su spec decía

Al medir para F21 salió que el «mecanismo» documentado —*trocear en n-gramas de 4 palabras
(shingles)*— **no es el implementado**. E17 compara conjuntos de palabras con contenido,
frase contra frase, con un mínimo de 3 compartidas. La spec describía un algoritmo que el
código no tiene. Reescrita para decir el real.

## Lo que impide que vuelva a pasar

Tres canarios nuevos, los tres vistos fallar:

- `tests/test_abrir.py` — 5 sabotajes del filtro de agua y del emparejado de estrella.
- `tests/test_spec_al_dia.py` — los mares de la spec contra los del disco, y el recuento
  escrito en prosa contra la tabla.
- `tests/test_e17_limite.py` — las cifras publicadas salen de la función. Falsear una en la
  spec pone la prueba roja.

Es la lección de siempre en este repositorio: **lo que se escribe a mano se desincroniza**.
Donde no se puede generar, se compara.
