# El registro — commits y memoria, clasificados como todo lo demás

Encargo de Darío (2026-09-01): *«que en el momento que lo usemos, todos los commits y memorias
guardadas estén organizadas dentro de otra carpeta; que esté dentro, pero por la parte exterior que
sean por ejemplo commits o algo de eso, y dentro de ahí TODO SÚPER CLASIFICADO COMO EL HARNESS»*.

Es la misma idea aplicada a lo que el trabajo va dejando atrás: **una puerta por fuera, y detrás la
misma taxonomía**. Sin esto, el harness estaría ordenado y su historia sería un montón — y la
historia es lo que más crece.

## La forma

```
registro/                       ← la puerta: una sola, y se ve desde fuera qué hay
├── commits/                    ← qué se hizo
│   └── <nicho>/<año>/<mes>/
├── lluvia/                     ← qué se aprendió (la memoria)
│   └── <nicho>/
├── informes/                   ← qué se investigó
│   └── <nicho>/
└── decisiones/                 ← qué se decidió y no se puede deshacer barato
    └── <nicho>/
```

`<nicho>` es uno de los 25 sistemas solares de `spec/UNIVERSO.md`, más `universo` para lo que afecta
a todo. **La misma clasificación que el harness, aplicada a su historia.**

## Por qué por nicho y no por fecha

Por fecha es lo cómodo de escribir y lo inútil de leer. Nadie busca «lo del 3 de marzo»: se busca
«lo que aprendimos de bots de trading», y eso está repartido en catorce fechas.

La fecha sigue estando —dentro de `commits/`, que es lo único que se consulta de forma
cronológica—, pero **el primer corte es el nicho**, porque es como se busca.

Efecto secundario que importa: al escribir una entrada hay que elegir su nicho, y esa pequeña
fricción obliga a decidir de qué era. Lo que no se sabe clasificar suele ser lo que no se entendió.

## Las cuatro carpetas

| Carpeta | Qué guarda | Cuándo se escribe |
|---|---|---|
| `commits/` | Qué se hizo y por qué, más allá del mensaje de commit | Al cerrar un trabajo |
| `lluvia/` | Hechos consolidados: memoria durable | Cuando algo se aprende y va a hacer falta |
| `informes/` | Investigaciones y diagnósticos reutilizables | Al resolver algo raro |
| `decisiones/` | Lo irreversible con alternativa real descartada | Al decidir, no después |

`lluvia` se llama así porque en la taxonomía la memoria es agua: **se evapora del contexto y
precipita donde hace falta**. No está cargada; se consulta.

## Formato: el mismo frontmatter de siempre

Una entrada del registro es un nodo como cualquier otro, y el validador la trata igual:

```yaml
---
cosmos: lluvia
nombre: backtest-sin-comisiones-miente
moja: []
resumen: Un backtest sin comisiones ni deslizamiento infla el resultado hasta invertirlo.
---
```

`moja: []` no es una formalidad, es **la** regla de esta carpeta: una memoria no se carga sola, se
consulta. Y no es una convención que haya que recordar — E10 la exige.

Que sean nodos de verdad tiene tres consecuencias que valen el esfuerzo:

1. El validador **también las comprueba**: nada de resúmenes vacíos ni entradas huérfanas.
2. El medidor las cuenta, y como su `moja` está vacío, **cuestan cero al entrar**.
3. Se buscan igual que todo lo demás. Una memoria que no se encuentra no existe.

## La regla de oro del registro

> **El registro nunca entra en el contexto de entrada.**

Ni una línea. Es historia, y la historia se consulta, no se lleva puesta. Un registro que se cargara
solo crecería sin techo y se comería el presupuesto en un mes — que es, exactamente, cómo un harness
acaba con 27.000 tokens de prólogo.

Por eso ninguna entrada lleva alcance en absoluto, y el validador lo rechaza (E10). No basta con
prohibir `moja: ["**"]`: un `moja: ["puente/**"]` tampoco se carga —una lluvia entra solo por
consulta— pero **sí se cobra**, porque `agua_condicional` mete en el presupuesto toda agua no
oceánica con alcance. Medido el 2026-09-01, al conectar el registro al árbol: dos entradas con
`moja` sumaban **7.700 tokens** al peor caso, por documentos que no se abren nunca. La regla de
arriba dejó de ser un párrafo y pasó a ser E10.

Para que el validador las vea, `cosmos.toml` declara `[raiz] registro`. Sin esa línea el registro
está escrito y el árbol no lo mira, que es como estuvo hasta el 2026-09-01.

## Qué se escribe y qué no

**Sí**: una causa raíz que costó encontrar · un panel con truco · un límite de plan o de API que
rompe algo · una decisión con alternativa real descartada · algo que pensarías «esto ya me pasó y no
me acuerdo de cómo lo arreglé».

**No**: lo que el propio código ya cuenta · lo que se ve en `git log` · lo que solo importaba en esa
conversación · un resumen de lo que hiciste hoy.

La prueba: **¿esto le ahorra tiempo a alguien dentro de tres meses?** Si no, no se escribe. Un
registro lleno de entradas de relleno hace más lento encontrar la que sirve, y esa es la única forma
en que un archivo puede hacer daño.
