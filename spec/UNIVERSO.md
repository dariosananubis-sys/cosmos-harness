# El universo — 20 nichos completos

Encargo de Darío (2026-09-01), literal: *«también en ciberseguridad, y dentro de ciberseguridad pues
código… TODO ABSOLUTAMENTE LO QUE TENGA QUE VER con eso dentro de ese; eso es un ejemplo, igual que
el de trading y el de webs. Tienes que encontrar 20 nichos en total como esos para dejarlo perfecto,
y dentro de eso hacerlo perfecto. No me valen tonterías»*.

## El modelo: verticales, no capas

Un sistema solar es un **nicho completo**. Se lleva dentro **todo** lo suyo: sus herramientas, sus
técnicas, su vocabulario **y su código**. El que trabaja en ciberseguridad encuentra ahí dentro
también cómo se escribe código de seguridad; no tiene que ir a buscarlo a otro sitio.

Esto corrige el diseño anterior, que partía por capas horizontales (`codigo` por un lado, los temas
por otro). Estaba mal, y el motivo es concreto: **el código de un nicho no se parece al de otro**.
Un exploit, un bot que opera en un mercado y un tema de WordPress comparten la sintaxis y poco más —
cambian los fallos típicos, lo que se considera correcto, las bibliotecas y lo que significa
«terminado». Una capa `codigo` genérica no le sirve bien a ninguno de los tres.

## Y entonces, ¿qué pasa con lo que sí es transversal?

Que **es agua, no sólido**.

Que el código no salga malo, que haya pruebas de verdad, que sea accesible, que no filtre secretos:
eso atraviesa los 20 nichos sin pertenecer a ninguno. Ponerlo como sistema propio obligaría a
elegir; ponerlo como agua hace que **moje los 20 a la vez**, que es justo lo que se pidió al exigir
que dos capacidades se usen juntas.

| Mar | Qué impone, en todos los nichos |
|---|---|
| `criterio` | Qué **no** escribir: simplicidad, reutilización, límites del cambio, deuda |
| `pruebas` | Que un test afirme algo de verdad. Mutación, no cobertura decorativa |
| `resistencia` | Que falle de forma ruidosa: nunca cero donde toca «no lo sé» |
| `accesibilidad` | Que se pueda usar. Legal en Europa, además de correcto |
| `custodia` | Secretos, datos personales, RGPD. Nunca en claro, nunca de más |

`criterio` era un sistema solar en la versión anterior de este documento. Como mar es más fuerte:
poda igual en los veinte sitios sin que nadie tenga que acordarse de invocarlo.

---

## Los 20 nichos

| # | Nicho | Qué se lleva dentro, incluido su código |
|---|---|---|
| 1 | `ciberseguridad` | Ofensiva autorizada, defensa, forense, malware, criptografía, y el código de todo eso |
| 2 | `mercados` | Bots que operan: exchanges, ejecución, backtest honesto, riesgo, operación continua |
| 3 | `web` | Sitios y tiendas: CMS, maquetación, comercio electrónico, frontend, conversión |
| 4 | `agentes` | IA aplicada: orquestación, herramientas, memoria, recuperación, modelos locales |
| 5 | `datos` | Ingeniería y análisis: transformación, validación, almacenes, cuadros de mando |
| 6 | `extraccion` | Sacar datos del mundo: web, documentos, OCR, normalización |
| 7 | `infraestructura` | Que corra: contenedores, despliegue, nube, redes, copias, monitorización |
| 8 | `moviles` | Aplicaciones para móvil y escritorio, publicación y tiendas |
| 9 | `juegos` | Motores, bucle, física, activos, publicación |
| 10 | `medios` | Vídeo, imagen, audio y documentos, a escala y por lotes |
| 11 | `visibilidad` | Que te encuentren: SEO técnico, buscadores con IA, contenido |
| 12 | `saas` | Producto vendible: identidad, pagos, suscripciones, multi-cliente |
| 13 | `embebidos` | Hardware, firmware, sensores, protocolos de dispositivo |
| 14 | `blockchain` | Contratos inteligentes, su auditoría, y la infraestructura de cadena |
| 15 | `cientifico` | Cálculo numérico, simulación, análisis científico y reproducibilidad |
| 16 | `sistemas` | Bajo nivel: compiladores, runtime, concurrencia, rendimiento extremo |
| 17 | `automatizacion` | Que lo repetitivo se haga solo: flujos, integraciones, tareas programadas |
| 18 | `negocio` | La administración: presupuestos, facturas, contratos, seguimiento |
| 19 | `legal` | Cumplimiento, RGPD, licencias, propiedad intelectual, contratos técnicos |
| 20 | `conocimiento` | Documentación, formación, investigación y verificación de fuentes |

---

## Cómo se estructura un nicho por dentro

Ejemplo desarrollado con `ciberseguridad`, que es el que se puso de referencia. Los demás siguen la
misma forma: **continentes** (grandes disciplinas), **países** (familias de capacidades),
**provincias** (grupos de skills hermanas), **pueblos** (skills atómicas).

```
sistema-solar  ciberseguridad
├── continente  ofensiva            (autorizada: pentest, CTF, red team)
│   ├── pais  reconocimiento        provincias: descubrimiento · huella · OSINT
│   ├── pais  explotacion           provincias: web · binaria · escalada
│   └── pais  codigo-ofensivo       ← su propio código vive aquí
│              provincias: exploits · fuzzing · desarrollo de herramientas
├── continente  defensiva
│   ├── pais  deteccion             provincias: reglas · registro · caza
│   ├── pais  endurecimiento        provincias: sistema · red · contenedor
│   └── pais  codigo-defensivo      ← y aquí
│              provincias: validación en frontera · criptografía aplicada
├── continente  analisis
│   ├── pais  forense               provincias: memoria · disco · red
│   ├── pais  malware               provincias: estático · dinámico · desempaquetado
│   └── pais  vulnerabilidades      provincias: SAST · dependencias · secretos
└── continente  gobierno
    └── pais  cumplimiento          provincias: marcos · auditoría · informes
```

Fíjate en `codigo-ofensivo` y `codigo-defensivo`: **el código vive dentro del nicho**, y son dos
países distintos porque escribir un exploit y escribir una validación en frontera son dos oficios
que no comparten ni los fallos típicos ni lo que cuenta como correcto.

Y sobre los tres continentes: los mares `criterio`, `pruebas` y `custodia` los mojan igual que a
todos los demás. Nadie los invoca a mano.

## Lo que «perfecto» significa aquí

*«No me valen tonterías»* se traduce en un filtro, no en un adjetivo. Para que algo entre en un
nicho:

1. **Se ejecuta.** Herramienta, script o validador. Un documento con consejos que un modelo bueno ya
   sabe **no entra**, por muchas estrellas que tenga.
2. **Es el mejor de su hueco.** Uno por trabajo, no cinco parecidos. Si hay dos candidatos, se dice
   por qué gana el que gana; si empatan de verdad, entran los dos y se dice cuándo usar cada uno.
3. **Cuesta cero.** Nada que pida tarjeta, API de pago ni suscripción nueva.
4. **Está vivo.** Mantenido, y su ecosistema no lo ha dejado atrás.
5. **Se ha usado una vez.** Antes de quedarse, se prueba en un caso real.

Y la regla que sostiene todas las demás: **lo que no se invoca en tres meses se archiva.** No se
borra, sale del catálogo — porque el catálogo se paga en todas las sesiones, y un nicho lleno de
cosas que nadie usa es exactamente la tontería que no vale.

## Ciberseguridad: el límite que no se cruza

Trabajo defensivo, auditoría autorizada, CTF, formación e investigación. Nada de técnicas
destructivas, ataques de denegación, objetivos masivos, compromiso de cadena de suministro ni
evasión de detección con fines maliciosos. Las herramientas de doble uso entran con su contexto de
uso legítimo declarado.

No es una nota al pie: es parte de la definición del nicho, y va en su estrella para que se cargue
siempre que alguien entre a trabajar ahí.
