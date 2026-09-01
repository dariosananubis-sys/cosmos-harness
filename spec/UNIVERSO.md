# El universo — 26 oficios en 7 galaxias

Encargo: *«mínimo 20 ámbitos nicho que me hagan el mejor harness y que no sean basura… serían 20
sistemas solares y el general es el universo, y cada uno dentro tiene que estar repletísimo, sin
errores, de herramientas que sean perfectas»*.

Son **26**, porque salieron 26 oficios que de verdad se distinguen entre sí. No se rellena hasta un
número redondo: un sistema solar que no es un oficio propio es un nivel de relleno, y un nivel de
relleno cuesta y no informa.

**Un sistema solar es un modo de trabajo**, no un tema: cambia el vocabulario, cambian las
herramientas y cambia lo que cuenta como terminado. Si dos candidatos comparten las tres cosas, son
uno solo.

---

## artesanía — construir software bien

| Sistema | Resumen (su frontmatter) |
|---|---|
| `codigo` | Lenguajes, algoritmos, refactorización a escala, perfilado y depuración difícil. |
| `criterio` | Qué NO escribir: simplicidad, reutilización, límites del cambio y deuda. |
| `arquitectura` | Límites entre partes, contratos, acoplamiento y decisiones que cuesta deshacer. |
| `sistemas` | Bajo nivel: concurrencia, memoria, rendimiento extremo y comportamiento del runtime. |

`codigo` y `criterio` van **separados a propósito** y se cargan juntos. Es la petición explícita del
encargo, y el motivo está en `spec/COMPOSICION.md`: más capacidad sin más criterio produce más
código de más. Uno propone y el otro poda; fundirlos deja que el que propone se autoevalúe.

## producto — lo que se entrega

| Sistema | Resumen |
|---|---|
| `web` | Sitios y tiendas: maquetación, comercio electrónico, rendimiento y conversión. |
| `moviles` | Aplicaciones para móvil y escritorio: ciclo de vida, publicación y tiendas. |
| `interfaz` | Diseño de interacción, sistemas de diseño y accesibilidad de verdad. |
| `juegos` | Motores, bucle de juego, física, activos y publicación. |

## máquina — dónde corre

| Sistema | Resumen |
|---|---|
| `infraestructura` | Contenedores, despliegue, servidores, copias verificadas y monitorización. |
| `nube` | Servicios gestionados, coste por uso, permisos y límites de cada proveedor. |
| `redes` | Protocolos, DNS, certificados, proxies y diagnóstico de lo que no conecta. |
| `embebidos` | Hardware, microcontroladores, sensores y comunicación con dispositivos. |

## mente — construir con modelos

| Sistema | Resumen |
|---|---|
| `modelos` | Recuperación, ajuste fino, modelos locales, visión y voz. |
| `agentes` | Orquestación, herramientas, memoria, evaluación y agentes que corren solos. |
| `investigacion` | Buscar, contrastar y sintetizar información, distinguiendo fuente de rumor. |
| `lenguaje` | Traducción, internacionalización, corrección y análisis de texto. |

## materia — datos y dinero

| Sistema | Resumen |
|---|---|
| `datos` | Transformación, validación, análisis y cuadros de mando que no engañan. |
| `almacenes` | Modelado, consultas, índices, migraciones y bases de datos en producción. |
| `extraccion` | Sacar datos de webs y documentos, de forma legal y que falle de forma ruidosa. |
| `mercados` | Bots que operan: conexión, ejecución, backtesting honesto y riesgo. |

## mundo — el negocio y su entorno

| Sistema | Resumen |
|---|---|
| `negocio` | Presupuestos, facturas, contratos, seguimiento y automatización administrativa. |
| `visibilidad` | Que te encuentren: SEO técnico, buscadores con IA, contenido y marca. |
| `medios` | Producir a escala: vídeo, imagen, audio y documentos, por lotes. |
| `conocimiento` | Documentación, formación y material que otro pueda seguir sin ti. |

## guardia — que no se rompa y no te demanden

| Sistema | Resumen |
|---|---|
| `seguridad` | Auditoría defensiva, análisis estático, dependencias y secretos. |
| `pruebas` | Tests que afirman algo: unidad, integración, extremo a extremo y mutación. |
| `cumplimiento` | RGPD, accesibilidad legal, licencias y lo que exige la norma europea. |

---

## Las siete galaxias, y por qué siete

Una galaxia agrupa oficios que **se cargan juntos a menudo**. No es una estantería temática: es una
apuesta sobre qué se usa con qué.

| Galaxia | Une |
|---|---|
| `artesania` | Todo lo que toca el código fuente |
| `producto` | Todo lo que ve el cliente final |
| `maquina` | Todo lo que hace que siga en pie |
| `mente` | Todo lo que se construye con modelos |
| `materia` | Todo lo que trata datos como materia prima |
| `mundo` | Todo lo que convierte el trabajo en dinero |
| `guardia` | Todo lo que audita a los demás |

`guardia` es la única que se define por su **relación** con las otras en vez de por su materia, y
está bien así: audita, y por eso se carga junto a lo que audita, nunca sola.

## Qué se quedó fuera, y por qué

Decir qué no entra vale tanto como la lista, porque explica el criterio:

- **`rendimiento`** — se reparte entre `sistemas` (bajo nivel) y `web` (carga de página). Como
  sistema propio se solaparía con los dos y no tendría herramientas exclusivas.
- **`devops`** — no es un oficio, es una forma de organizarse. Sus herramientas ya están en
  `infraestructura` y `pruebas`.
- **`blockchain`** — oficio real, pero hoy sin encaje en el trabajo. Candidato si aparece.
- **`ciencia`** (computación científica, simulación) — mismo caso.
- **`soporte`** (atención a cliente, incidencias) — candidato en cuanto haya volumen que lo pida.
- **`marketing`** como sistema propio — lo que un modelo hace ya sin ayuda no necesita oficio. Lo
  que sí es infraestructura ejecutable está en `negocio` y `visibilidad`.

Un candidato entra cuando tiene **herramientas propias que no son de nadie más**. Mientras sus
herramientas vivan en otro sistema, es una provincia de ese sistema, no un sistema.

## Qué significa «repletísimo»

Cada sistema se llena con lo que pasa la **regla de admisión** de `PLAN-MAESTRO.md` §3: mecanismo
en vez de prosa, coste cero, un dueño claro, un resumen que informe, y haberse usado una vez.

«Repletísimo» **no** es «con todo lo que había». Un sistema con 40 herramientas mediocres es peor
que uno con 8 buenas: cuesta más y esconde la que sirve. Lleno significa **que no falte nada de lo
que hace falta**, no que no quepa nada más.

Y hay un aviso que conviene tener delante desde el principio: **el catálogo de nombres se paga
siempre**. Cada pueblo añade su línea al contexto de entrada. Por eso hay presupuesto, por eso
pasarse es rojo, y por eso lo que no se invoca en tres meses se archiva.
