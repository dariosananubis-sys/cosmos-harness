# Plan maestro — la herramienta definitiva

Encargo de Darío: *«el planning para la herramienta definitiva de todo, que tenga las herramientas
de <agencia> harness más todo lo esencial»*, con especialistas de verdad por oficio —«un experto
montando bots de trading», «un experto en código»— buscando por todo GitHub lo importante que hay
hoy. Y sin fugas de tokens.

Esas dos mitades parecen tirar en direcciones opuestas: cuantos más expertos, más contexto. **No lo
son, y esa es la idea entera del proyecto**: son opuestas solo si todo lo que existe está cargado.
Con contención estricta y carga perezosa, la galaxia puede crecer sin límite mientras el coste de
entrada se queda quieto. Por eso la taxonomía va primero y los expertos después: al revés se
construye otro harness de 30.000 tokens de prólogo, solo que con mejores skills dentro.

---

## 1. Qué es la herramienta

Una **galaxia de oficios**. Cada oficio es un experto de verdad —con sus herramientas ejecutables,
no con consejos— y ninguno se paga hasta que se entra en él.

Tres capas, y las tres tienen que existir para que esto funcione:

| Capa | Qué es | Estado |
|---|---|---|
| **Esqueleto** | La taxonomía, el validador, el medidor, el compilador | En construcción, núcleo funcionando |
| **Carne** | Los oficios: skills, agentes y herramientas reales por dominio | 13 barridos de GitHub en curso |
| **Sistema inmune** | Lo que impide que la galaxia se degrade: guardarraíles, presupuesto en rojo, válvula caducable | Especificado, por implementar |

La tercera capa es la que casi nadie tiene, y es la que decide si esto sigue siendo útil dentro de
seis meses o se convierte en el problema que vino a resolver. Un harness sin sistema inmune no se
estropea de golpe: engorda un párrafo cada vez, y cada párrafo tenía razón.

## 2. El mapa de la galaxia

Nueve sistemas solares. Un sistema solar es un **modo de trabajo**: cambia el vocabulario, cambian
las herramientas, cambia lo que cuenta como «terminado». No es una carpeta temática.

| Sistema solar | El oficio | Qué contiene |
|---|---|---|
| **codigo** | El ingeniero | Lenguajes, algoritmos, arquitectura, refactorización a escala, depuración difícil, rendimiento |
| **web** | El constructor de sitios | WordPress y Elementor, e-commerce, front-end, accesibilidad, conversión, SEO técnico y GEO |
| **mercados** | El que monta bots que operan | Exchanges y brokers, ejecución, backtesting honesto, gestión de riesgo, operación 24/7 |
| **inteligencia** | El que construye con modelos | RAG, modelos locales, fine-tuning, voz y visión, orquestación de agentes, MCP |
| **datos** | El que consigue y entiende los datos | Extracción, parseo de documentos, ETL, análisis, cuadros de mando |
| **medios** | El que produce a escala | Vídeo, imagen, audio, documentos, lotes de cientos de ficheros |
| **infraestructura** | El que hace que no se caiga | Contenedores, despliegue, servidores, copias verificadas, monitorización |
| **negocio** | El que cobra | Propuestas, precios, captación, seguimiento comercial, facturación |
| **guardia** | El que audita | Seguridad, análisis estático, dependencias, testing, RGPD, accesibilidad legal |

Cada uno con su **estrella** (su contexto permanente, que solo se enciende al entrar) y sus lunas
(subagentes propios). Dentro: continentes, países, provincias, ciudades y pueblos, según lo que cada
dominio necesite de verdad — nunca la cadena completa por obligación.

**Coste de entrada**: el índice son nueve líneas de sistema más los océanos. Da igual que la galaxia
tenga 40 pueblos o 400: el índice no crece con ellos. Ese es todo el truco, y es el que hace que las
dos mitades del encargo dejen de estar en conflicto.

## 3. La regla de admisión

**El riesgo real de este proyecto no es quedarse corto: es llenarlo de basura buena.**

Trece barridos de GitHub van a devolver cientos de recursos, y muchos serán razonables. Meterlos
todos reproduce exactamente el problema que COSMOS existe para resolver, y encima con la conciencia
tranquila de haber sido exhaustivo. Un catálogo de 300 skills mediocres es peor que uno de 40 buenas
por dos motivos: cuesta más y hace más difícil encontrar la que sirve.

Para entrar en la galaxia hay que pasar las cinco:

1. **Mecanismo, no prosa.** Trae algo ejecutable —script, validador, plantilla— o conocimiento
   específico y verificable que un modelo bueno no tenga ya. Si es una lista de consejos sensatos,
   fuera: eso ya lo sabe.
2. **Coste cero.** Nada que pida tarjeta, API de pago ni suscripción nueva. Se trabaja con lo que ya
   está pagado y con herramientas locales.
3. **Un dueño.** Cuelga de un padre concreto. Si no se sabe de quién es, no entra: los huérfanos son
   el principio del montón.
4. **Un resumen que informe.** 120 caracteres que digan qué hace y en qué se distingue de su vecina.
   Si el resumen es el nombre otra vez, la skill no está lista para entrar.
5. **Se ha usado una vez.** Antes de quedarse, se prueba en un caso real. Lo que nunca se ha usado
   no se sabe si funciona, y ocupa igual.

Y una regla de salida, que importa tanto como las de entrada: **lo que no se invoca en tres meses se
archiva**. No se borra —se archiva, y se puede recuperar— pero sale del catálogo, porque el catálogo
se paga en todas las sesiones.

## 4. Las fases

### Fase 1 — Esqueleto *(en curso)*

El validador, el medidor y el compilador funcionando, con la disciplina de haberse visto fallar:
un test por invariante que la rompe a propósito y exige el rojo.

**Terminado cuando**: todas las invariantes tienen su prueba de rojo, el medidor da un número con su
método declarado, y el compilador resuelve el hueco de las skills anidadas.

### Fase 2 — Sistema inmune

Los enganches (pre-commit, sesión, CI), la válvula de escape caducable y con registro, y E17 contra
la duplicación por paráfrasis.

**Terminado cuando**: un árbol que se pasa de presupuesto **no se puede commitear**, y la válvula se
ha visto caducar y volver a poner el rojo.

Esta fase es la que casi se salta todo el mundo, y sin ella las otras dos se deshacen solas. El
harness auditado tenía un detector de fugas perfectamente funcional y una fuga viva de 2.187 tokens
por sesión: el detector estaba bien, nadie lo ejecutaba.

### Fase 3 — Poblar los oficios

Los 13 barridos pasan la regla de admisión y se colocan. Sistema por sistema, midiendo la entrada
después de cada uno: si sube, se ha colado algo en el nivel equivocado.

**Terminado cuando**: los nueve sistemas tienen contenido real, y la entrada sigue por debajo del
presupuesto **con la galaxia entera dentro**. Ese es el resultado que demuestra la tesis del
proyecto.

### Fase 4 — Migrar el harness actual

Traer lo que funciona del harness existente, ya identificado: los guardarraíles que fallan solos,
el gate que recalcula el veredicto en vez de leerlo, la prueba de lectura atada a la sesión.
Reescritos genéricos, sin arrastrar el vocabulario de negocio.

**No se toca el harness actual hasta que COSMOS esté probado.** Primero funciona, luego se migra.

### Fase 5 — Los oficios que no existen

Cada barrido devuelve una sección «lo que falta»: capacidades sin nada bueno disponible. Ahí es
donde hay algo que construir que no tiene nadie — y, si algo de esto va a valer dinero, es más
probable que esté ahí que en la enésima integración que ya existe.

## 5. Cómo se sabe si funciona

Cuatro números, todos medibles y ninguno opinable:

| Métrica | Qué dice | Objetivo |
|---|---|---|
| **Entrada** | Tokens que se pagan por existir, antes del primer turno | Bajo presupuesto, con la galaxia llena |
| **Descarga** | Fracción del sistema disponible sin estar cargada | > 0,95 |
| **Océanos** | Reglas globales permanentes | ≤ 7, y que no crezca |
| **Invariantes vistas fallar** | Comprobaciones que han dado rojo de verdad | Todas |

La cuarta es la que da valor a las otras tres. Un validador que nunca ha dicho rojo no se distingue
de uno roto, y los números que publique no valen nada.

## 6. Lo que este plan no promete

Se pidió una herramienta para hacerse millonario. Lo que aquí se construye es la mitad del problema
que se puede resolver con ingeniería: ejecutar más rápido, más barato y con menos errores en nueve
oficios a la vez. La otra mitad —qué se vende, a quién y por cuánto— no la decide el harness.

Se dice aquí, una vez, para que el plan se juzgue por lo que sí hace: **que un trabajo que hoy lleva
dos días se haga en dos horas, y que dentro de seis meses siga costando lo mismo entrar** — que es
justo lo que hoy no pasa.
