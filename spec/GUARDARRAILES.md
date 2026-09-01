# Guardarraíles — cómo COSMOS se hace inevitable

Escribe esta pieza **Codex**. Revisa **Claude**, con premisa invertida.

## El hallazgo que obliga a este fichero

De la auditoría de un harness real (`research/PATRONES-HARNESS.md`, antipatrón A1): ese repo tiene
un auditor de fugas de tokens, bien escrito y mecánico. Al ejecutarlo contra su propio estado, dijo:

```
FUGA revisor-adversarial.md (paths:**, ~2187 tok/sesión) -> pasar a lazy
VEREDICTO: FUGA NUEVA
```

El auditor funciona perfectamente. La fuga llevaba ahí lo bastante como para no ser la última regla
añadida. **Un validador que nadie ejecuta es exactamente igual de útil que no tenerlo**, y esa es la
lección más cara de toda la investigación.

Así que la conclusión para COSMOS es dura: `cosmos validar` **no puede depender de que alguien se
acuerde de correrlo**. Si dependiera de eso, COSMOS sería una exhortación con tests — precisamente
lo que el `GOAL.md` dice que no es.

## Los tres enganches

| Enganche | Cuándo corre | Qué hace |
|---|---|---|
| **pre-commit** | Antes de cada commit del repo que usa COSMOS | `cosmos validar`. Si rojo, el commit no ocurre |
| **sesión** | Al arrancar una sesión de agente | `cosmos validar --rapido`. Si rojo, lo dice en la primera línea |
| **CI** | En cada push, si hay CI | `cosmos validar` completo |

Ninguno es obligatorio para usar COSMOS, y los tres se instalan con `cosmos enganchar`. Pero el que
no instala ninguno **tiene el mismo sistema que el harness auditado**: uno que sabe detectar su
propia degradación y no lo hace nunca.

`cosmos enganchar` es explícito y reversible: escribe el hook, dice exactamente qué escribió y
dónde, y `cosmos desenganchar` lo quita. Nada se instala solo al importar el paquete. Un sistema
que se engancha sin que se lo pidan es un sistema que la gente arranca de raíz a la primera
molestia, y con razón.

## La válvula de escape (obligatoria, no opcional)

Del catálogo de mecanismos (patrón 9): **todo guardarraíl duro sin válvula de escape acaba
desactivado a la fuerza.** No es una posibilidad: es lo que pasa. Alguien tiene una urgencia real un
viernes, el guard le estorba, y lo desactiva entero — y ya no vuelve.

Por eso COSMOS trae la suya, y está diseñada para que usarla sea más cómodo que saltarse el sistema:

```
cosmos saltar E16 --motivo "importando 40 skills, se reorganiza el lunes" --caduca 7d
```

| Propiedad | Regla |
|---|---|
| **Acotada** | Se salta un código concreto, nunca "todo" |
| **Con motivo** | Obligatorio y libre. Sin motivo no hay salto |
| **Caducable** | Obligatorio. Máximo 30 días. Sin caducidad no hay salto |
| **Registrada** | Log append-only en `.cosmos/saltos.log`, que nunca se reescribe |
| **Visible** | Con un salto activo, toda salida dice `verde (1 salto activo: E16, caduca en 5 d)` |
| **Ruidosa al caducar** | Al vencer vuelve el rojo, y el mensaje recuerda el motivo que se escribió |

Un salto **nunca** se convierte en permanente por inercia. Si al caducar sigue haciendo falta, se
renueva a mano, con motivo nuevo, y el log guarda las dos entradas. Que renovar cueste un minuto es
el punto: es lo que distingue una excepción de una costumbre.

La palabra «verde» no aparece nunca sola habiendo saltos activos. Un verde que oculta un salto es
una mentira, y basta una para que nadie vuelva a creerse ninguno.

## E17 — duplicación por paráfrasis

La investigación encontró el punto ciego exacto del auditor auditado, y es instructivo: su detector
de duplicación compara frases **literales** de más de 70 caracteres. En ese repo, dos políticas
están explicadas tres veces cada una —6.343 bytes en canales siempre cargados— y el detector dice
«cero duplicación», porque las tres versiones están **parafraseadas**.

Es un fallo perfectamente comprensible: nadie copia y pega dos veces la misma política. Se
reescribe con otras palabras, en otro sitio, meses después, sin recordar que ya estaba. Por eso la
duplicación real de un harness es **casi siempre** paráfrasis, y por eso un detector literal está
ciego justo donde hace falta que vea.

COSMOS añade una invariante a las 16 de `VALIDADOR.md`:

> **E17** — Dos nodos que están simultáneamente en el contexto de entrada no pueden solaparse por
> encima del umbral configurado.

Mecanismo, con biblioteca estándar y sin red:

1. Normalizar: minúsculas, sin acentos, sin puntuación, sin palabras vacías del idioma.
2. Trocear en **n-gramas de 4 palabras** (shingles).
3. Comparar por similitud de Jaccard, por pares, **solo entre los nodos siempre cargados**.
4. Por encima de `umbral_solapamiento` (por defecto 0,25), error con las frases que más pesan.

Los n-gramas cazan la paráfrasis que la comparación literal no ve, porque una reescritura conserva
casi siempre tramos de cuatro palabras. No caza una reformulación completa con vocabulario distinto
—eso necesitaría semántica, y la semántica necesita un modelo, y un modelo cuesta dinero, que este
proyecto no gasta (`GOAL.md` §5). Se dice claramente en la salida y en la documentación: **E17 caza
la paráfrasis, no la reformulación total.** Un límite declarado se puede tener en cuenta; uno
oculto, no.

La comparación se hace **solo entre los siempre-cargados**. Dos pueblos de sistemas distintos pueden
parecerse todo lo que quieran: nunca coinciden en contexto, así que su parecido no cuesta nada. El
coste solo existe cuando las dos copias se pagan a la vez, y ahí es donde mira la invariante.

## Verificación exigida

1. Un test por enganche: instalarlo, romper el árbol, comprobar que **efectivamente** bloquea. Un
   hook instalado que no bloquea es peor que ninguno, porque además tranquiliza.
2. Un test de que la válvula caduca: con caducidad vencida, vuelve el rojo.
3. Un test de que un salto activo **nunca** produce una salida que diga solo «verde».
4. Un test de E17 con un par parafraseado de verdad —no dos copias literales— que exija el rojo.
5. Un test de que E17 **no** salta entre dos nodos que nunca coinciden en contexto.
6. Un test de que `cosmos desenganchar` deja el repo exactamente como estaba.
