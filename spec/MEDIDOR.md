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
| **Entrada base** | Índice de galaxia + océanos + mapa de descenso, sin ciudades ni pueblos | Se paga en **cada** sesión y en **cada** subagente, para siempre |
| **Entrada de nicho** | La base + el catálogo de ciudades y pueblos del nicho activo | Es el coste real al entrar en un oficio |
| **Agua condicional** | Los mares y lagos, que se cargan solos por `paths:` sin que nadie los invoque | No está en la entrada y se paga igual; ocultarlo es la fuga que este medidor existe para cazar |
| **Peor caso con agua** | Entrada del peor nicho + agua condicional | El techo real de una sesión de trabajo, y **el número que E16 compara con el presupuesto** |
| **Árbol** | La suma de todo el contenido del árbol, si se cargara entero | El contrafactual: lo que costaría no tener COSMOS |
| **Descarga** | `1 − entrada / árbol` | Qué fracción del sistema está disponible sin estar cargada |

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
cinco mares suman **817 tokens**, y `mar/criterio` (298) más `mar/resistencia` (83) se activan en
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

```
COSMOS  medir

  Entrada base .... 1.012 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±8%, heurística v1)
  Peor nicho ...... 1.655 tokens   (ciberseguridad, 26 pueblos)
  Agua condicional  817 tokens     (5 aguas por paths:, fuera de la entrada)
  Peor con agua ... 2.472 tokens   (peor nicho + agua condicional)
  Universo ........ 61.400 tokens  (estimado, ±8%)
  Descarga ........ 97,3 %
  Presupuesto ..... 4.000          OK, quedan 1.528 tokens en el peor caso con agua

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)

  Lo más caro de la entrada evaluada:
    1.  310 tok  índice de galaxia
    2.  280 tok  oceano/seguridad
    3.  190 tok  oceano/git
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
   automáticamente —y **dicho en voz alta**, no en silencio— si no hay tokenizador local.
3. Un test de que `no_medido` nunca se convierte en `0` en ninguna suma, ni en la salida JSON.
4. Un test de que un árbol vacío da entrada 0 y descarga `no_definida` — no `100 %`. Dividir entre
   cero y publicar un sobresaliente es el modo de fallo clásico de este tipo de métrica.
5. Un test de que un mar con cuerpo **sube** `entrada_con_agua` sin tocar `entrada`, y de que
   `entrada_con_agua ≤ universo`. Sin él, el agua vuelve a quedarse fuera del presupuesto en cuanto
   alguien refactorice, y nada se pone rojo.
