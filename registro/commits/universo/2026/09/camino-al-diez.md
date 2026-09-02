---
cosmos: lluvia
nombre: camino-al-diez
moja: []
resumen: Catalogo en arbol indentado, el verbo buscar, holdout sellado, juez local preparado y limites de maquina fuera.
---

# Camino al diez — lo que faltaba, con permiso para robar de otros arneses

Fecha: 2026-09-02 · Orden de Darío: *«¿Lo podrías convertir en un 10?»* → *«coge cosas de otros
arneses de todo internet si lo necesitas»* → *«implementa lo que necesites de manera super
coherente sin romper nada»*. Y el destino cambió de máquina: *«se va a correr en un muy buen M3
Pro de 18 GB… lo de los recursos quítalo del arnés si puedes»*. El coordinador desbloqueó 1-3 y
aparcó la evaluación por API (dinero: decisión de Darío, no nuestra).

## 1. El catálogo en árbol indentado — robado del repo-map de aider

El peor nicho pagaba **1.452 tokens reales** en su catálogo y el 40 % eran prefijos de ruta
repetidos: `ciberseguridad/analisis/cadena-de-suministro/` delante de cinco pueblos seguidos. La
idea viene del repo-map de aider (jerarquía comprimida bajo presupuesto de tokens; fuente:
aider.chat/docs/repomap.html — sin su grafo de referencias, porque aquí el árbol ya declara la
jerarquía): **un pueblo paga su nombre, y su sitio lo dice la indentación**. E18 ya garantizaba el
nombre único global y `cosmos abrir <nombre>` resuelve; los hijos directos del sistema conservan
`<nicho>/` como ancla.

- Catálogo de ciberseguridad: líneas propias **1.452 → 1.093** (−359, tiktoken).
- La selección la comparten render y contra-métrica por construcción
  (`medir.nodos_de_catalogo`): no pueden divergir, que es como nació el fallo M14.
- `acertar` conserva las palabras de la ruta en el texto puntuable —esa información el agente la
  sigue viendo, en la sangría— y su cifra no se movió con el cambio de formato (33-34/50 antes y
  después; el ±1 lo causó añadir el río `buscar` al catálogo, no el formato).
- `spec/NUCLEO.md` reescrito en su definición normativa del catálogo; el orden por rango (H5)
  queda sustituido por la forma: la jerarquía ahora se ve, no se infiere.
- Factor de calibración re-medido sobre el corpus nuevo: 1,369 frente al 1,381 publicado —
  desviación del 0,9 % **del lado conservador** (el aproximado sobreestima el coste): el factor
  publicado se conserva y queda anotado en `docs/CALIBRACION.md`.

## 2. `cosmos buscar` — el verbo que faltaba, y ya estaba escrito

COSMOS sabía decidir, medir, cargar y aplanar; no sabía ENCONTRAR: quien no conocía el árbol leía
el índice, adivinaba, y si fallaba volvía al grep que este proyecto existe para eliminar. El motor
estaba escondido dentro de la contra-métrica. `cosmos buscar <consulta sin comillas>` expone el
mismo BM25 (comparten `_lineas_del_catalogo` y `_ordenar`): **desde hoy `acertar` puntúa el camino
real** — antes, el 66 % medía una función interna que ningún agente podía invocar.

Con su `rio/buscar` (momento trabajo: cuesta su línea de catálogo, 32 tokens exactos de entrada,
pagados de sobra por el punto 1), salida 1 cuando no encuentra («sin resultados» dicho, no
inventado), rojo con motivo si la raíz del árbol no existe, y una lección de argparse cazada al
probar: el posicional `raiz` heredado de `base()` se tragaba la primera palabra de la consulta.

## 3. Holdout nuevo y SELLADO — y la cifra honesta del árbol es un 40 %

El holdout anterior no lo quemó la mala fe: alguien abrió su detalle para ver qué fallaba y lo
contaminó sin querer. El sello existe para impedir ESE gesto:

- Conjunto nuevo de 20 encargos en lenguaje de cliente (el quemado queda archivado como
  `encargos-validacion-quemada-2026-09-02.*`). Esperas verificadas solo por existencia contra el
  árbol; escritos sin mirar resúmenes ni ranking — el mismo estatus epistémico que los originales,
  declarado: quien los escribió ha visto el árbol entero hoy, y por eso el sello importa.
- `cosmos acertar --sellar` escribe `pruebas/encargos-validacion.SELLO` (sha256 del contenido
  exacto, versionado). Con el sello vigente, **ninguna salida enseña el detalle por encargo de la
  validación** —`--json` lo redacta con el porqué—; editar el fichero invalida el sello y el CLI
  avisa; romperlo es borrar el `.SELLO`, y ese gesto queda en git.
- Primera lectura del holdout sellado: **ajuste 33/50 (66 %) · validación 8/20 (40 %) · brecha 26
  puntos**, cantada por el propio comando. El 70 % del conjunto quemado era puntería sobre examen
  visto; **la cifra publicable del árbol hoy es 40 %**, no se maquilla y no se persigue: se mejora
  el árbol en general y se vuelve a medir.

## 4. El juez local — preparado para el M3 Pro, jamás arrancado aquí

`acertar --juez MODELO` cierra el bucle que el léxico no puede: ¿un modelo DE VERDAD baja por
donde debe? Cero coste (ollama, stdlib `urllib`, sin dependencias) y una regla de hierro en el
código: **este módulo nunca arranca un modelo** — se conecta a un servidor ya levantado o falla
limpio con salida 2 explicando que levantarlo es decisión de quien opera la máquina. Ejercitado
entero sin modelo doblando el borde más externo (el transporte): prompt, extracción de ruta del
ruido (gana la más larga: contestar la hoja no se puntúa como la raíz), y el mismo `_acierta` de
la contra-métrica. Corre sobre el conjunto de AJUSTE: al holdout sellado no se le acerca nada que
produzca salida por encargo. En el M3 Pro: `ollama serve` + `cosmos acertar --juez <modelo>`.
La evaluación por API sigue aparcada: es dinero y la orden es de Darío (coste según proveedor y
tamaño del conjunto; con 50 encargos y un modelo frontier, del orden de céntimos por pasada).

## 5. Los límites de la máquina vieja, fuera del contenido

35 menciones a «8 GB»/«ocho gigas» en 31 fichas y una estrella, calibradas al Mac de 8 GB donde se
escribió el árbol — y el arnés va a correr en 18 GB. El criterio se conserva como principio, la
cifra de una máquina concreta se va: la estrella de `modelos-locales` dice ahora *«la memoria de
la máquina es el criterio eliminatorio»*, y las fichas hablan de «memoria justa» o comparan
tamaños de modelo con «la memoria libre real». Los tamaños de los modelos y herramientas (hechos
de las herramientas) se conservan todos.

## Números finales (el exacto manda)

```
                          antes    despues
Peor nicho (cbs) ......   2.733 -> 2.406   (catalogo en arbol, +rio/buscar)
Peor con agua (exacto)    3.981 -> 3.654   margen  19 -> 346
Peor con agua (aprox)     3.821 -> 3.546   margen 179 -> 454 (±5,2 % declarado; el exacto manda)
acertar ajuste .......    34/50 -> 33/50   (±1 por el candidato nuevo rio/buscar; no se persigue)
acertar validacion ...    70 % quemado -> 40 % SELLADO y publicable
```

## Sabotajes de esta tanda, con su veredicto

| id | Sabotaje | Prueba que se puso roja | Veredicto |
|---|---|---|---|
| M56 | el ranking de `buscar` se invierte | `test_codigo_duplicado_lleva_a_las_reglas_de_refactorizacion` | ROJO |
| M57 | el catálogo vuelve a pagar la ruta completa por línea | `test_catalogo_web_contiene_solo_pueblos_de_web` | ROJO |
| M58 | la redacción del sello desaparece de `--json` | `test_como_dict_redacta_solo_la_validacion` | ROJO |
| M59 | la extracción de ruta se queda con el primer candidato | `test_si_nombra_varias_gana_la_mas_larga` | ROJO |

(Permanentes en `puente/tests/mutaciones.py`: la tabla queda en 59/59.)

## Lo que aún separa esto del 10 redondo

Medir «fuera de COSMOS» (system prompt + tools reales de cada sesión) sigue `no_medido` — es
integración con el harness anfitrión, no una tarde. Y la evaluación con modelo frontier espera la
orden de gasto. Con lo de hoy: el verbo existe, la métrica mide el camino real, el holdout no se
puede quemar por descuido, el juez espera al M3 Pro, y el árbol cabe con 346 tokens de margen
reales.

Sin credenciales, sin nombres de cliente, sin datos personales.
