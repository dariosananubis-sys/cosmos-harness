---
cosmos: lluvia
nombre: agua-condensada
moja: []
resumen: Los seis mares reescritos a densidad - 1546 a 1248 tokens reales, 44 normas conservadas y el exacto en verde.
---

# Agua condensada — el árbol cabe con el tokenizador que manda

Fecha: 2026-09-02 · Encargo de Darío via coordinador: *«si está inmejorable que lo suba, si no que
arregle y mejore todo lo mejorable»* — y no estaba inmejorable: **el árbol estaba en ROJO con el
tokenizador real** (4.279/4.000), y el aproximado acababa de dejar de mentir (tercer factor de
calibración del coordinador: 4.126, también rojo). La condición no negociable: **reescritura, no
recorte** — ninguna afirmación normativa podía perderse.

## Método: la lista primero, la tijera después

Antes de tocar una línea se inventariaron las afirmaciones normativas de cada mar leyendo el texto
viejo: **44 en total** (criterio 14 · pruebas 11 · revisión 6 · resistencia 6 · custodia 4 ·
accesibilidad 3). Esa lista es el contrato; la condensación solo podía quitar la prosa que las
envuelve. Cuatro pasadas de reescritura midiendo con tiktoken tras cada una, y las aserciones del
test escritas al final, contra el texto vigente — lo medido, no lo deseado.

## Números, por mar (tokens reales, cl100k_base)

```
                antes  despues
criterio         480  ->  325   (-155)  era el mas literario; toda la norma sigue
pruebas          380  ->  328   ( -52)  ya era denso: habia menos que ganar
revision         267  ->  209   ( -58)  los casos, comprimidos a su clausula minima
resistencia      183  ->  165   ( -18)
custodia         119  ->  115   (  -4)
accesibilidad    117  ->  108   (  -9)
TOTAL          1.546  -> 1.248  (-298)
```

Veredicto tras condensar:

```
exacto (/tmp/calib/bin/python -m cosmos medir --metodo exacto):
  Peor con agua ... 3.981 / 4.000 -> OK, quedan 19 tokens        (antes: ROJO -279)
aprox (con el factor de estructura nuevo del coordinador):
  Peor con agua ... 3.821 / 4.000 -> OK, quedan 179 tokens
```

**El margen exacto es de 19 tokens y se dice sin maquillar**: es verde, pero fino — cualquier
frase nueva en un mar o en el peor nicho lo consume. No se forzó más recorte para engordarlo
porque el siguiente token ya salía de la norma, no de la prosa; si hace falta holgura de verdad,
las palancas son el peor nicho (ciberseguridad, 2.733) o el presupuesto, y esa segunda es
decisión de Darío.

## Lo que se retiró a propósito, declarado (evidencia, nunca norma)

1. **criterio**: la anécdota del fichero de semilla que un ayudante editó sin permiso. La norma
   que ilustraba (lista previa de ficheros tocables; lo de fuera se para y pide permiso) sigue
   entera; el caso era su envoltorio.
2. **revision**: las cifras «once de once y nueve avisos» del caso que fijó la regla de encadenar
   revisores. Queda el hecho con dientes («el único defecto grave apareció en el código escrito
   para atender los avisos»); el marcador numérico era color.
3. **revision**: los «siete campos» del caso del contrato de campos. La norma y su remedio
   («se arranca el servicio y se restan las claves reales») quedan; el número era del incidente.
4. **criterio**: «se demuestra midiendo el árbol» y «se revisa comparando árboles» eran el mismo
   mecanismo dicho dos veces; fundidos en una afirmación que conserva las dos consecuencias
   (tocar-lo-justo se demuestra con árboles; lo reformateado no cuenta como cambio).

Nada más se ha quitado. Las 44 normas del inventario están en el texto nuevo, y no hay que
creerme: lo exige un test.

## La prueba de que no se perdió nada (y de que perderlo dolería)

`tests/test_agua_normativa.py` enumera **a mano** las 44 afirmaciones —la lista viene del texto
ANTERIOR, no deducida del vigente, que sería la tautología de siempre— y ancla cada una con sondas
literales del texto nuevo. Además cuadra la lista con los mares del disco (un mar nuevo sin lista
no vigilado se pone rojo) y exige el mínimo de 44 (un canario que mengua no vigila).

Sabotajes, con su veredicto:

| id | Sabotaje | Prueba que se puso roja | Veredicto |
|---|---|---|---|
| M54 | se borra de `criterio` la norma de mover-sin-reescribir | `test_cada_afirmacion_sigue_presente` | ROJO |
| M55 | se borra de `pruebas` «el test afirma lo medido, no lo deseado» | `test_cada_afirmacion_sigue_presente` | ROJO |

(Permanentes en `puente/tests/mutaciones.py`; la tabla queda en 55/55 vistas fallar.) Y un rojo de
trabajo que valida el método: una sonda inicial cruzaba un salto de línea y falló en verde-falso
inverso — se corrigió la sonda mirando el texto, no el texto mirando la sonda.

## Verificación (árbol con los cambios)

```
python3 -m cosmos validar                       -> COSMOS verde, 0 errores (E17 sin quejas del texto denso)
python3 -m unittest discover -s tests -t .      -> Ran 237 — OK (skipped=2)
python3 -m unittest discover -s puente/tests    -> Ran 116 — OK
python3 puente/tests/mutaciones.py              -> 55/55 invariantes vistas fallar
/tmp/calib/bin/python -m cosmos medir --metodo exacto -> OK, quedan 19
python3 -m cosmos medir                         -> OK, quedan 179
python3 -m cosmos acertar                       -> 68 % ajuste / 70 % validación, sin cambios
python3 -m puente.secretos --todo               -> limpio de nuevos
```

Sin credenciales, sin nombres de cliente, sin datos personales.
