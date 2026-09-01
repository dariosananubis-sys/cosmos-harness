# Revisión adversarial — catálogo por nicho

Premisa de entrada: **acotar el catálogo al nicho activo es mala idea**. Intenté demostrar que el
ahorro compra ceguera, que el agente deja de descubrir capacidades útiles y que la vista compilada
introduce estados más peligrosos que el catálogo global.

## Lo que intenté tumbar

### 1. «Si no ve los pueblos, no sabe que existe otro oficio»

Construí un árbol con `web` y `saas`, oculté todos los pueblos en el caso base y busqué qué quedaba.
Los dos sistemas solares siguieron apareciendo en el índice con nombre y resumen; también quedaron
las rutas intermedias del mapa de descenso. El agente pierde la lista de herramientas de `saas`,
pero no pierde el hecho de que `saas` existe ni la indicación de para qué sirve.

No pude demostrar la desaparición del oficio. Sí demostré una pérdida menor y real: el índice dice
que existe otro nicho, pero no permite saber si dentro está *la herramienta concreta* que resolvería
mejor el trabajo. Para descubrirla hay que descender explícitamente a ese nicho.

### 2. «Lo que no se ve no se puede descubrir»

Probé las rutas disponibles sin volver a cargar los 127 pueblos: el índice descubre los sistemas;
el catálogo estructural descubre continentes/países; `cosmos mapa` permite inspección fuera del
contexto inicial; y `cosmos medir --nicho n` materializa y cuantifica un nicho concreto. Para un
trabajo que cruza oficios, `--nicho` repetido y `--combinacion` exponen la unión exacta.

La defensa no es completa todavía. `usa:` era el mecanismo acordado para sugerir vecinos sin
arrastrarlos, pero E20 aún no existe y la galaxia actual no puede depender de ese campo. Hasta que se
implemente, clasificar mal una tarea puede ocultar una herramienta relevante y obliga al agente a
inferir el vecino a partir de las líneas del índice. Es un hueco de descubrimiento, no una fuga de
contexto, y debe mantenerse visible.

### 3. «El peor nicho cabe, luego cualquier trabajo cabe»

Intenté refutar E16 combinando varios nichos. Lo conseguí: la suma de tres catálogos puede ser más
cara que el peor nicho individual. E16 no garantiza que toda combinación posible quepa; garantiza
solo el escenario individual más caro, tal como pide el contrato. `medir --combinacion` hace visible
el coste transversal y compara esa selección con el presupuesto, pero no la convierte en una
invariante global.

Esto es un límite importante: si el runtime combina nichos sin medirlos, puede superar el presupuesto
aunque `validar` esté verde. No invalida el catálogo acotado, pero impide interpretar E16 como una
garantía sobre combinaciones arbitrarias.

### 4. «Cambiar de nicho borra trabajo»

Compilé una vista completa, modifiqué a mano una entrada de `saas` y después compilé solo `web`.
La entrada intacta de otro nicho se eliminó porque coincidía con el hash del compilador. La modificada
se preservó, se reportó y salió del manifiesto. Un elemento que nunca estuvo en el manifiesto siguió
siendo ajeno. No pude provocar borrado de trabajo no atribuible al compilador.

Sí queda un riesgo operativo: dos sesiones que compartan el mismo destino plano y trabajen en nichos
distintos se reemplazan la vista una a otra. El lock evita corrupción simultánea, pero no evita esa
alternancia semántica. Un destino por sesión/proyecto eliminaría el riesgo; el contrato actual no lo
resuelve.

### 5. «La mejora depende otra vez de acordarse de un flag»

Este ataque sí encontró una debilidad. Por compatibilidad, `cosmos compilar` sin `--nicho` conserva
la vista completa. Por tanto la propiedad de runtime acotado solo existe cuando quien integra COSMOS
invoca `compilar --nicho n`. El medidor y E16 ya son estructurales —sin flags miden base y peor
nicho—, pero la compilación todavía tiene este pie de memoria humana.

No lo oculto como detalle: contradice parcialmente el principio de que una regla que deba recordarse
está mal puesta. La siguiente decisión de integración debería hacer que el runtime declare su nicho
activo o rechazar la compilación completa fuera de un modo explícito de migración.

## Veredicto

No pude demostrar que el catálogo global fuera necesario para descubrir que existen otros nichos:
esa función barata permanece en el índice y en el mapa estructural. Tampoco pude romper la regla de
preservación por hash. La decisión central aguanta y elimina el crecimiento global causado por cada
pueblo nuevo.

No la considero libre de riesgos. Quedan tres: descubrimiento de vecinos debilitado hasta que exista
`usa:`/E20, combinaciones fuera del alcance de E16 y compilaciones de sesiones distintas sobre un
destino compartido. Además, la compatibilidad sin `--nicho` es un escape que puede reintroducir los
127 pueblos en el runtime. Esos límites deben acompañar cualquier afirmación de cierre.
