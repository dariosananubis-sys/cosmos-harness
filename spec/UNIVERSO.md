# El universo — 20 oficios

Encargo de Darío, en tres correcciones sucesivas que llevan al mismo sitio:

1. *«Tienes que encontrar 20 nichos en total… y dentro de eso hacerlo perfecto. No me valen tonterías»*
2. *«En ciberseguridad, y dentro de ciberseguridad pues código: TODO lo que tenga que ver con eso dentro»*
3. *«Los nichos son muy generales creo»* — y tenía razón.

## La prueba que decide si algo es un nicho

> **¿Alguien contrataría esto?**

«Bots de trading» sí. «Ciberseguridad» sí. **«Datos» no** — nadie contrata «datos»: contrata un
pipeline que no se rompa, o un cuadro de mando que no mienta. Son dos oficios distintos, con
herramientas distintas y clientes distintos, y meterlos juntos no ayuda a nadie.

La versión anterior de este documento fallaba esa prueba en cinco casos: `datos`, `agentes`,
`medios`, `sistemas` y `conocimiento` eran **categorías temáticas**, no oficios. Se han partido en
los trabajos reales que contenían, y lo que no pasaba la prueba ha salido.

## Los 20

| # | Nicho | El trabajo por el que te contratan |
|---|---|---|
| 1 | `ciberseguridad` | Auditar, defender y analizar: pentest autorizado, forense, malware, y su código |
| 2 | `trading` | Un bot que opera solo, con backtest honesto y riesgo controlado |
| 3 | `web` | Un sitio o una tienda que carga, convierte y no se cae |
| 4 | `moviles` | Una aplicación en las tiendas, mantenible y que no consume batería |
| 5 | `juegos` | Un juego que se publica: motor, bucle, activos, distribución |
| 6 | `saas` | Un producto de suscripción: identidad, pagos, multi-cliente, facturación |
| 7 | `agentes-ia` | Agentes que hacen trabajo real, con herramientas, memoria y evaluación |
| 8 | `modelos-locales` | IA que corre en tu máquina: privacidad, coste cero por uso, sin depender de nadie |
| 9 | `ingenieria-datos` | Un pipeline que valida antes de cargar y avisa cuando se rompe |
| 10 | `analitica` | Cuadros de mando y métricas de negocio en los que se puede confiar |
| 11 | `extraccion` | Sacar datos de la web y de documentos, legal y sin fallar en silencio |
| 12 | `infraestructura` | Que corra 24/7: despliegue, copias restaurables, monitorización |
| 13 | `visibilidad` | Que te encuentren, en buscadores clásicos y en los de IA |
| 14 | `video` | Producción audiovisual por lotes, no pieza a pieza |
| 15 | `voz` | Transcribir, doblar y sintetizar a escala |
| 16 | `automatizacion` | Que lo repetitivo se haga solo, y se entere si falla |
| 17 | `blockchain` | Contratos inteligentes y **su auditoría**, que es donde está el valor |
| 18 | `embebidos` | Hardware que habla: firmware, sensores, protocolos de dispositivo |
| 19 | `cientifico` | Cálculo y simulación **reproducibles**: si no se repite, no es resultado |
| 20 | `cumplimiento` | RGPD, accesibilidad legal, licencias: lo que evita la multa |

### Qué salió, y por qué

| Salió | Motivo | Dónde vive ahora |
|---|---|---|
| `datos` | Categoría, no oficio | Partido en `ingenieria-datos` y `analitica` |
| `agentes` | Categoría | Partido en `agentes-ia` y `modelos-locales` |
| `medios` | Categoría | Partido en `video` y `voz` |
| `sistemas` | No se contrata «bajo nivel» | País dentro de quien lo necesite; el perfilado, en el mar `criterio` |
| `conocimiento` | Documentar no es un encargo en sí | Provincia dentro de cada nicho |
| `negocio` | Es trabajo interno, no se vende | Sus herramientas, dentro de `saas` y `automatizacion` |
| `legal` | Muy amplio | Estrechado a `cumplimiento`, que es lo accionable |

## Los mares — lo transversal, que no es un nicho

Cinco aguas que mojan los 20 sin pertenecer a ninguno. No se invocan: actúan siempre que se toca su
terreno.

| Mar | Qué impone |
|---|---|
| `criterio` | Qué **no** escribir: simplicidad, reutilización, límites del cambio, deuda, perfilado antes de optimizar |
| `pruebas` | Que un test afirme algo. Mutación, no cobertura decorativa |
| `resistencia` | Que falle de forma ruidosa: nunca un cero donde toca «no lo sé» |
| `accesibilidad` | Que se pueda usar. Legal en Europa, además de correcto |
| `custodia` | Secretos y datos personales: nunca en claro, nunca de más |

## Los vecinos: cómo se cruzan los nichos

Decisión de Darío: **cada nicho apunta a sus vecinos, y no duplica nada.**

Un trabajo real cruza varios — montar una tienda es `web` + `saas` (cobrar) + `visibilidad` (que la
encuentren) + `cumplimiento` (que no te multen). El nicho lo dice, con `usa:`:

```yaml
---
cosmos: sistema-solar
nombre: web
padre: ""
resumen: Un sitio o una tienda que carga, convierte y no se cae.
usa:
  - saas          # para cobrar
  - visibilidad   # para que la encuentren
  - cumplimiento  # aviso legal, cookies, accesibilidad
---
```

`usa:` **sugiere, no arrastra**. Al entrar en `web` se te dice que para cobrar existe `saas`; no se
carga solo. Una dependencia automática sería una cadena de arrastre —cargas uno y vienen cinco— que
es como un gestor de paquetes acaba trayendo medio internet.

Y lo importante: **una herramienta vive en un solo sitio**. Si `stripe` está en `saas`, `web` lo
apunta con `usa:`, no se lo copia. Cero repetidos, que es una regla dura del encargo.

## Qué significa «de lo mejor del mundo»

Cada nicho se llena con lo mejor que exista **hoy** para ese trabajo, buscado en GitHub y verificado
en vivo (estrellas, último push, licencia, si el ecosistema lo dejó atrás). Cinco criterios, y los
cinco son eliminatorios:

1. **Se ejecuta.** Herramienta, script o validador. Un documento con consejos que un modelo bueno ya
   sabe no entra, por muchas estrellas que tenga.
2. **Es el mejor de su hueco.** Uno por trabajo. Si hay dos candidatos, se dice por qué gana el que
   gana; si de verdad empatan, entran los dos y el resumen de cada uno **dice en qué se distingue
   del otro**.
3. **Cuesta cero.** Nada que pida tarjeta, API de pago ni suscripción nueva.
4. **Está vivo.** Mantenido, y su ecosistema no lo ha superado.
5. **Se ha usado una vez.** Antes de quedarse, se prueba en un caso real.

Y la regla que lo sostiene: **lo que no se invoca en tres meses se archiva.** No se borra — sale del
catálogo, porque el catálogo se paga en todas las sesiones.

## El límite que hace que esto no se descontrole

Medido el 2026-09-01 con 66 herramientas montadas: entrada **2.572 tokens de 4.000**, y **1.713 de
esos 2.572 son el catálogo** — el 67%. Cada herramienta añade su línea, y esa línea se paga en cada
sesión y en cada subagente, para siempre.

Traducido: hay sitio para **unas 5 o 6 herramientas por nicho**, no cincuenta. Por eso el criterio 2
es eliminatorio y por eso pasarse de presupuesto pone el validador en **rojo**, no en aviso.

Esta es la restricción que convierte «lo mejor del mundo» en una decisión y no en una acumulación.
Sin ella, «llenar 20 nichos» acaba siendo meter 300 herramientas y volver exactamente al problema
que COSMOS existe para resolver.

## Ciberseguridad: el límite que no se cruza

Trabajo defensivo, auditoría autorizada, CTF, formación e investigación. Nada destructivo, ni
denegación de servicio, ni objetivos masivos, ni compromiso de cadena de suministro, ni evasión de
detección con fines maliciosos. Las herramientas de doble uso entran con su contexto de uso legítimo
declarado.

Va en la estrella del nicho, para que se cargue siempre que alguien entre a trabajar ahí.
