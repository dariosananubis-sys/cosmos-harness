---
cosmos: lluvia
nombre: taxonomia-c01-c03
moja: []
resumen: Decision delegada - rendimiento partido en dos oficios, 8 aristas verdaderas en usa y juegos terminal declarado.
---

# Taxonomía C01/C03 — la decisión, con sus números

Fecha: 2026-09-02 · Decisión **delegada por Darío** (*«haz lo que Fable considere»*) tras dejar
C01 y C03 medidos y anotados en `cierre-menores`. Criterio que manda: el de `spec/UNIVERSO.md` —
**¿alguien contrataría esto?**. Todo lo de abajo se decidió mirando las fichas y los números, no
el informe de oídas; donde la conclusión fue «no se mueve nada», se dice y se explica, porque
decidir no mover también es decidir.

## C03.1 — `rendimiento` se parte: eran dos contratos con herramientas disjuntas

**Decisión: partir.** El sistema decía *«medir por qué va lento, depurar lo raro y su calidad»* —
un resumen que une dos oficios con una conjunción. Medido: sus dos continentes tenían 8 y 10
pueblos con **cero herramientas en común** (perfilado: `py-spy`, `samply`, `bpftrace`,
`hyperfine`, `rr`, `sanitizers`, `mimalloc`, `tokio` · calidad: `eslint`, `ruff`,
`golangci-lint`, `jscpd`, `ast-grep`, `openrewrite`, `serena`, `difftastic`, `mutmut`,
`stryker-js`). La prueba de UNIVERSO la pasan por separado —«mi API tarda tres segundos» y «entra
en este código heredado y déjalo mantenible» son dos clientes distintos— y es la misma prueba que
ya partió `datos` en `ingenieria-datos` + `analitica`. Y de los diez vecinos que citaban al nicho,
**nueve venían por la velocidad**: la entrada 9 que el informe llamaba «cajón de sastre» era el
perfilado cargando con el peso de los dos.

Cómo quedó:

- **`rendimiento`** (8): *«Que el código vaya rápido: medir por qué tarda y reproducir el fallo
  raro»*. Países `perfilado` y `depuracion` re-colgados directos del sistema; `mimalloc` y `tokio`
  sueltos (≤ 2, tolerado por el canario de estructura). Su estrella ya era 100 % de velocidad: no
  se toca.
- **`refactorizacion`** (10, nuevo oficio 22): *«Entrar en código ajeno y dejarlo mejor sin
  romperlo: cambio en masa, reglas y mutación»*. Países `reglas` (eslint, ruff, golangci-lint,
  jscpd), `transformacion` (ast-grep, openrewrite) y `mutacion` (mutmut, stryker-js); `serena` y
  `difftastic` sueltos. Estrella nueva con tres verdades que **ningún mar dice ya** — la primera
  redacción repetía la doctrina del patrón sintáctico de `mar/criterio` y E17 la cazó al 30 %
  (evidencia de que el guardarraíl funciona); la definitiva: el contrato es que el comportamiento
  no cambie · solo se reordena lo verificado · dejarlo más limpio no autoriza dejarlo más lento.
- Los dos continentes (`velocidad`, `calidad`) desaparecen: con la partición eran capas de un solo
  grupo, el antipatrón que `test_oficios_estructurados` prohíbe.
- Actualizado todo lo que citaba las rutas viejas: `mar/criterio` y `mar/pruebas` (ahora
  `refactorizacion` y `refactorizacion/mutacion`), el ejemplo de `spec/COMPOSICION.md` (su canario
  se puso rojo solo, como debía), `spec/REGISTRO.md` (22), los 5 encargos de ajuste con esperas
  `rendimiento/*` (renombrado mecánico de rutas, no ajuste de la métrica) y la prosa con cardinal
  de `cosmos/acertar.py`.

## C03.2 — los 4 de `trading` NO se mueven, y el porqué queda escrito

**Decisión: quedarse.** `hypothesis`, `time-machine`, `toxiproxy` y `tenacity` viven en
`trading/bots/codigo-de-bot`, cuyo resumen declara el criterio: *«aquí un fallo no lanza una
excepción, deja una posición abierta»*. Ese país es un conjunto curado para el cliente que
contrata «un bot que no revienta con dinero dentro» — sus fichas están escritas para ese trabajo
(cierres de vela, cortar la red entre el bot y el mercado). Moverlos a `refactorizacion` habría
agrupado por tema («son de testing») en vez de por encargo, que es exactamente la categoría
temática que UNIVERSO expulsa; y «tres sitios para lo mismo» del informe conflaba prácticas
distintas: mutación (calibrar la red), propiedades (generar lo que nadie escribiría) e inyección
de fallos (red rota a propósito) no son la misma cosa con tres nombres. La regla «una herramienta
vive en un solo sitio» se cumple: cero duplicados medidos.

## C03.3 — la mitad «instrumental» de `agentes-ia` NO se expulsa: es el país `coste`

**Decisión: quedarse.** Los 8 señalados (`auditar-gasto`, `quota-oficial`,
`cuentas-del-asistente`, `medir-contexto`, `captura-recortada`, `ordenes-entre-ventanas`,
`diario-sin-duplicados`, `playbook-obligatorio`) ya cuelgan de países con encargo propio — casi
todos de `agentes-ia/coste`, cuyo resumen es un contrato real de 2026: *«saber lo que cuesta cada
sesión y bajarlo: cuota, contexto y elección de modelo»*. Leídas las fichas, están destiladas
(la de `playbook-obligatorio` lo dice literal: *«aquí no queda nada de eso»*) y ninguna nombra
agencia, cliente ni cuenta concreta. Operar agentes sin quemar cuota ES parte del oficio de
agentes hoy; expulsarlas a un nivel nuevo de «mantenimiento» habría creado justo el cajón que el
informe temía, pero fuera del mapa.

## C03.4 — el criterio de colocación de los E2E, declarado

**Decisión: ninguna herramienta se mueve; el criterio se escribe.** La herramienta vive con el
encargo que la contrata: `maestro` hace QA de publicación móvil y vive en `moviles/publicacion`;
`playwright` es, en este catálogo, el navegador real de `extraccion/fuentes-web` (su ficha habla
de conducir navegadores para sacar contenido, no de suites de test). No hay dos criterios: hay
uno —por encargo— y una lectura de `playwright` como «herramienta E2E» que su ficha no sostiene.
Lo que sí queda al descubierto y se anota como hueco, no como colocación errónea: **el encargo
«pruebas E2E de mi web» no tiene herramienta en `web`** («cero repetidos» impide duplicar
playwright; si el hueco duele, la entrada nueva será otra herramienta o una ficha repartida de
otra forma — decisión futura, no de hoy).

## C01 — ocho aristas nuevas, cada una una afirmación; `juegos` queda terminal a propósito

No se cerró la simetría por cerrarla: cada arista tiene una historia de trabajo real que la cruza.

| Arista | Por qué es verdad |
|---|---|
| `ciberseguridad -> blockchain` | La auditoría de contratos ES trabajo de seguridad; el propio resumen de blockchain dice que ahí está el valor |
| `ciberseguridad -> embebidos` | El pentest de dispositivo acaba en firmware, buses y protocolos: el conocimiento vive allí |
| `extraccion -> automatizacion` | El scrape programado que rompe en silencio a las tres de la mañana es el caso canónico del vecino |
| `blockchain -> trading` | En DeFi el contrato y el bot que opera sobre él son el mismo encargo (creación de mercado, ejecución) |
| `web -> moviles` | «La tienda quiere su app»: el camino React→React Native/Expo es literalmente el argumento de venta de esas fichas |
| `modelos-locales -> cientifico` | Evaluar un modelo es un experimento: si no se repite, no es resultado |
| `rendimiento -> refactorizacion` | Lo medido hay que arreglarlo sin romperlo |
| `refactorizacion -> rendimiento` | Y lo arreglado no puede quedar más lento: el vecino pone el número |

Y una **re-cableada**: `agentes-ia` citaba `rendimiento` y ahora cita `refactorizacion` — el
agente vive en código ajeno y su instrumental allí (`serena`, `ast-grep`) es de la otra mitad.

Grafo antes → después (medido): 46 → **54 aristas** · 22 → **28 recíprocas** · huérfanos
7 → **1**. El que queda, `juegos`, es deliberado y está declarado como TERMINAL en
`tests/test_universo_navegable.py`: a un estudio de juegos se llega por el encargo, ningún otro
oficio manda allí a nadie — inventarle una arista habría sido el trámite que el criterio prohíbe.

## Presupuesto y métrica — los números, como pide la delegación

- **Aproximado**: peor con agua 3.935 → **3.959** / 4.000 (margen 65 → **41**). El coste es la
  línea 22 del índice; se compensó en parte recortando los dos resúmenes de sistema y las rutas
  que el agua citaba.
- **Exacto** (`/tmp/calib/bin/python`, tiktoken): 4.248 → **4.279** (rojo declarado −248 →
  **−279**). Sigue siendo el rojo con canario de `docs/CALIBRACION.md`; esta tanda lo empeora en
  31 tokens y queda dicho aquí, no disimulado.
- **Acierto**: ajuste 33/50 (66 %) → **34/50 (68 %)**; validación **14/20 (70 %)**, sin cambios.
  Las esperas se renombraron mecánicamente a las rutas nuevas; el holdout sigue QUEMADO y su cifra
  no es publicable — no se persiguió (la subida de ajuste es un encargo de linters que ahora
  aterriza en un oficio cuyo resumen dice «reglas»).
- **Inventario**: 22 sistemas, 22 estrellas, 8 continentes (−2), 76 países (+3), 247 pueblos,
  412 nodos + este parte, 528 pares co-cargables. Re-medido el paisaje E17 completo tras la
  estrella nueva: **cero pares** co-cargables comparten hoy ≥3 palabras con contenido — la prosa
  de `NUCLEO.md` §10 mezclaba la cifra fresca con la medición vieja y se reescribió anclada a su
  fecha (patrón I10).

## Sabotajes de esta tanda, con su veredicto

| id | Sabotaje | Prueba que se puso roja | Veredicto |
|---|---|---|---|
| M51 | se quita la arista `ciberseguridad -> blockchain` | `test_ningun_oficio_sin_citar_salvo_los_declarados` | ROJO |
| M52 | el título de UNIVERSO vuelve a decir 21 | `test_universo_anuncia_los_oficios_que_hay` | ROJO |
| M53 | `mutmut` se recuelga de `rendimiento` | `test_los_dos_oficios_existen_y_cada_mitad_esta_en_el_suyo` | ROJO |

(Permanentes en `puente/tests/mutaciones.py`: la tabla queda en 53/53 vistas fallar.) Además, un
rojo no buscado que vale como prueba del sistema: la primera estrella de `refactorizacion`
duplicaba doctrina de `mar/criterio` y **E17 la rechazó al 30 %** antes de que ningún revisor la
viera — el guardarraíl que esta taxonomía paga hizo exactamente su trabajo.

## Verificación (todo sobre el árbol con los cambios)

```
python3 -m cosmos validar                       -> COSMOS verde, 0 errores
python3 -m unittest discover -s tests -t .      -> Ran 234 — OK (skipped=2)
python3 -m unittest discover -s puente/tests    -> Ran 116 — OK
python3 puente/tests/mutaciones.py              -> 53/53 invariantes vistas fallar
python3 -m cosmos medir                         -> OK, quedan 41 tokens (ciberseguridad)
python3 -m cosmos acertar                       -> 68 % ajuste / 70 % validación (holdout quemado)
python3 -m puente.secretos --todo               -> limpio de nuevos
```

Sin credenciales, sin nombres de cliente, sin datos personales.
