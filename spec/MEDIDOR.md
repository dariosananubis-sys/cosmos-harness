# Especificación del medidor — para implementar

Escribe esta pieza **Codex**. Revisa **Claude**, con premisa invertida.

## Qué es

`cosmos medir` responde a una sola pregunta con un número: **¿cuánto contexto se paga por existir,
antes de que el agente haga nada?**

Es la pieza que convierte «no hay fugas» de opinión en hecho. Sin ella, COSMOS sería otro documento
de buenas intenciones, y ya hay muchos.

## Las magnitudes

| Magnitud | Qué es | Por qué importa |
|---|---|---|
| **Entrada base** | Índice de galaxia + océanos + mapa de descenso + ríos, sin pueblos | Se paga en **cada** sesión y en **cada** subagente, para siempre |
| **Entrada de nicho** | La base + el catálogo de pueblos del nicho activo | Es el coste real al entrar en un oficio |
| **Agua condicional** | Los mares y lagos, que se cargan solos por `paths:` sin que nadie los invoque | No está en la entrada y se paga igual; ocultarlo es la fuga que este medidor existe para cazar |
| **Peor caso con agua** | Entrada del peor nicho + agua condicional | El techo real de una sesión de trabajo, y **el número que E16 compara con el presupuesto** |
| **Universo** | La suma de todo el contenido del árbol, si se cargara entero (`NUCLEO.md` §3) | El contrafactual: lo que costaría no tener COSMOS |
| **Descarga** | `1 − entrada / universo` (la fórmula normativa vive en `NUCLEO.md` §3) | Qué fracción del sistema está disponible sin estar cargada |

La descarga es la métrica de cabecera. Un harness monolítico tiene descarga 0: todo lo que existe,
está cargado. Un COSMOS sano vive por encima de 0,95.

Ojo con leerla al revés: una descarga alta **no** significa que el sistema sea bueno, significa que
lo que existe no se paga hasta usarse. Un árbol enorme de basura tendría descarga excelente. Por
eso la descarga se publica siempre junto a la entrada en tokens absolutos, y es la **entrada del
peor nicho individual más el agua condicional** la que tiene presupuesto y la que pone rojo el
validador.

## El agua no se puede quedar fuera del número

Un mar no aparece en `contexto_inicial`: entra «por `paths:` que matchea». Formalmente es correcto,
y durante un tiempo sirvió de excusa para no contarlo. Medido en la galaxia real el 2026-09-01: los
los mares sumaban **817 tokens** aquel día (hoy lo dice `cosmos medir`: «Agua condicional»), y `mar/criterio` (298) más `mar/resistencia` (83) se activan en
**cualquier fichero `.py`**. El peor nicho publicado eran 1.771 tokens; el coste real de abrir un
Python del proyecto, 2.152. El medidor decía «quedan 2.229» sin ver un tercio del gasto.

Publicar «no aparece en la entrada» y callar el resto es la misma mentira que sumar `no_medido`
como cero, solo que por omisión. Por eso el agua condicional es una magnitud publicada, con su
desglose, y entra en el número que decide rojo o verde. Definición normativa en `NUCLEO.md` §3.

## Casos que se miden

- Sin flags, `cosmos medir` publica el caso base y calcula los nichos uno a uno para identificar el
  peor.
- `--nicho web` activa ese catálogo. El flag se puede repetir para medir una selección concreta.
- `--combinacion web,saas,cumplimiento` es la escritura compacta de la misma unión y materializa el
  coste de un trabajo transversal.

E16 siempre se evalúa contra el peor nicho individual, aunque el caso base quepa. Una combinación
explícita puede ser más cara que ese peor nicho; el comando la compara con el presupuesto y lo dice,
pero no convierte esa combinación elegida a mano en una propiedad global del árbol.

## Honestidad del método: no se dice «medido» si es estimado

Regla dura, y es la más importante de esta spec.

Este proyecto no gasta en APIs (`GOAL.md` §5), así que el conteo exacto del tokenizador del modelo
no siempre está disponible. Por tanto el medidor tiene dos métodos y **jamás publica un número sin
decir con cuál lo obtuvo**:

| Método | Cuándo | Qué se publica |
|---|---|---|
| `exacto` | Hay un tokenizador local instalado (`tiktoken` u otro), detectado en tiempo de ejecución | El número, y el nombre del tokenizador |
| `aprox` | No lo hay. Por defecto | El número, la palabra **estimado**, y el error medido de la heurística |

Nunca hay un tercer modo silencioso. Si el medidor no puede ver algo, lo reporta como `no_medido`
y **no lo suma como cero**: un cero se lee como «no cuesta nada», y esa es exactamente la mentira
que hace que los harness engorden sin que nadie lo note.

Esto vale también para lo que COSMOS no controla. El contexto real de una sesión incluye el system
prompt del producto, las definiciones de tools y los servidores MCP conectados. COSMOS **no** puede
medir eso desde fuera, así que:

```
Entrada COSMOS ......... 2.145 tokens  (estimado, ±8%)
Fuera de COSMOS ........ no_medido     (system prompt, tools, MCP)
```

No `0`. `no_medido`. La diferencia entre las dos palabras es la diferencia entre un informe útil y
uno que tranquiliza.

## Calibración de la heurística

`aprox` no puede ser «bytes entre cuatro y a correr». Se implementa una heurística documentada y se
**mide su error** contra el método exacto sobre un corpus del propio repo, en castellano y en
inglés, con markdown, tablas y bloques de código —que es lo que de verdad se va a contar.

El error medido se publica en `docs/CALIBRACION.md` con la fecha y el corpus, y el medidor lo cita
en su salida. Si nadie ha calibrado nunca, la salida dice `±desconocido`, no un margen inventado.

Un margen de error inventado es peor que ninguno: da una precisión falsa sobre la que alguien
tomará una decisión.

## Salida

El ejemplo es el árbol de juguete versionado (`cosmos medir --config ejemplo.toml`), no la
galaxia: un bloque copiado a mano de un árbol que crece envejece en silencio a los cinco minutos
—es H11, y el parte de F12 lo repitió—. Este se reproduce entero con ese comando (salvo la última
línea, «Vista compilada», que lleva la ruta local del clon), y `tests/test_coherencia_b.py` lo
reejecuta y compara el bloque: si divergen, la suite se pone roja (revisión B-04, que encontró
siete cifras caducadas justo debajo de este párrafo). El número que vale para la galaxia es
siempre el que imprime `cosmos medir` hoy.

```
COSMOS  medir

  Entrada base .... 134 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±5,2 % medio (peor fichero 33,6 %), heurística v3)
  Peor nicho ...... 203 tokens   (construccion, 2 pueblos)
  Agua condicional  31 tokens   (2 aguas por paths:, fuera de la entrada)
  Nicho activo .... 203 tokens   (construccion; 2 pueblos)
  Peor con agua ... 234 tokens   (el peor caso + agua condicional; nicho activo: construccion)
  Universo ........ 440 tokens   (estimado, ±5,2 % medio (peor fichero 33,6 %), heurística v3)
  Descarga ........ 53,9 %
  Presupuesto ..... 4.000     OK, quedan 3753 tokens con el margen calibrado (+5,2 %) en el peor caso con agua (construccion); ≈ 129 herramienta(s) más en ese nicho

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)

  Lo más caro de la entrada evaluada:
    1.  91 tok  catálogo visible
    2.  75 tok  índice de galaxia
    3.  20 tok  oceano/operaciones-reversibles
```

`--detalle` desglosa nodo a nodo. `--json` para máquinas. `--metodo exacto` falla en voz alta si no
hay tokenizador, en vez de caer en `aprox` sin avisar: un fallback silencioso convierte una medida
exacta en una estimación sin que el que lee el número se entere.

## El desglose es la herramienta de trabajo

«Lo más caro de la entrada» ordenado de mayor a menor es lo que hace el sistema **accionable**.
Cuando el presupuesto se pasa, nadie tiene que adivinar qué recortar: la lista dice exactamente
dónde está el peso, y casi siempre son dos o tres nodos, no cincuenta.

## Verificación exigida

1. Un test con un árbol de tokens conocidos a mano: el medidor tiene que dar ese número.
2. Un test de que `aprox` y `exacto` no divergen más que el error publicado, saltado
   automáticamente —y **dicho en voz alta**, no en silencio— si no hay tokenizador local. Y
   **alguien que no lo salte**: el trabajo `calibracion` del CI instala el tokenizador y corre la
   suite con `COSMOS_EXIGE_TOKENIZADOR=1` (auditoría D-08: en ninguna instalación por defecto se
   ejecutaba, así que el ±5,2 % llevaba días sin auditor).
3. Un test de que `no_medido` nunca se convierte en `0` en ninguna suma, ni en la salida JSON.
4. Un test de que un árbol vacío da entrada 0 y descarga `no_definida` — no `100 %`. Dividir entre
   cero y publicar un sobresaliente es el modo de fallo clásico de este tipo de métrica.
5. Un test de que un mar con cuerpo **sube** `entrada_con_agua` sin tocar `entrada`, y de que
   `entrada_con_agua ≤ universo`. Sin él, el agua vuelve a quedarse fuera del presupuesto en cuanto
   alguien refactorice, y nada se pone rojo.
6. Un test de que **dos aguas que mojan el mismo fichero se cobran las dos**, y otro de que un agua
   que no solapa con la más cara tampoco se cae del número. El 2026-09-02 el medidor agrupó el agua
   «por extensión» y publicó el grupo más caro: sobre un árbol con `**/*.spec.*` y `**/*.ts` daba
   240 tokens donde `src/app.spec.ts` carga 480 (F06). La premisa —que nadie toca un `.py` y un
   `.css` a la vez— es falsa: el agua entra por `paths:` y **se queda toda la sesión**, que es lo
   que esta tabla llama «el techo real de una sesión de trabajo». La definición buena es la de
   `NUCLEO.md` §3, la suma de toda el agua condicional, y no se cambia sin cambiar la spec.
7. Un test de que el **rótulo cuenta lo mismo que el número**: «N aguas por paths:» tiene que ser
   `len(agua_condicional(árbol))`. Decía 5 habiendo 6, porque publicaba el tamaño del grupo ganador.
