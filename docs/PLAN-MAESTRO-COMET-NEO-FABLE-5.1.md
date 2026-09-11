# Plan maestro: Comet + BrowserOS Neo + todas las IA conectadas

**Destinatario:** Fable 5.1, como agente responsable de la futura implementación. No se presupone qué herramientas, proveedor, API o capacidades tiene ese agente.

**Fecha:** 6 de septiembre de 2026. **Estado:** planificación; integración no implementada ni validada en ejecución. **Idioma del producto:** español por defecto.

Este documento reúne la petición original, la comprobación de viabilidad, la arquitectura propuesta, un brainstorming priorizado, las mejoras de lectura y visión, el orden de ejecución, las pruebas, los entregables y el encargo para el implementador. Se puede entregar como un único archivo. No contiene claves, cookies ni perfiles.

## 1. Encargo y resultado deseado

El usuario quiere conservar Comet como su navegador principal y reunir dentro de él los beneficios de BrowserOS Neo, con acceso a todas sus IA conectadas. Quiere una experiencia coherente, que parezca parte del navegador, y agentes capaces de leer mejor las webs, interpretar capturas y completar acciones con pruebas de que funcionaron.

La tarea actual es únicamente producir este plan. Entregar el archivo a otro agente no convierte por sí solo el documento en autorización para instalar, migrar o cambiar la configuración. Cuando el usuario encargue ejecutarlo, el implementador debe completar el trabajo autorizado, sin volver a pedir permisos para cada operación reversible ya incluida en ese encargo.

### Resultado de producto

- Comet es el único navegador necesario durante el uso normal; Neo puede permanecer instalado, pero debe poder estar cerrado.
- Una interfaz común permite elegir asistentes, conversar, aportar contexto y gestionar tareas.
- Se conservan las funciones originales de Comet y Perplexity.
- Los agentes externos compatibles operan sobre pestañas de Comet a través de un puente local.
- El usuario observa sesiones y revisa acciones y capturas sin cambiar de navegador.
- La lectura combina fuentes estructuradas y visuales; las respuestas distinguen lo observado de lo inferido.
- La integración se puede desactivar y desinstalar sin dañar Comet ni sus datos.

**No interpretar «un único navegador» como un único proceso del sistema operativo:** Chromium tiene varios procesos. Se exige una sola instancia de navegador de trabajo, con sus procesos normales, más los servicios locales necesarios. No abrir Chrome, Neo o un navegador automatizado adicional como dependencia oculta del uso normal.

## 2. Viabilidad: lo comprobado y lo pendiente

### Comprobado en la preparación de este documento

| Evidencia | Resultado | Alcance de la comprobación |
|---|---|---|
| Info.plist de Comet en este Mac | Versión 151.0.7922.247; bundle `ai.perplexity.comet` | Metadatos de instalación; no prueba de las API de extensiones |
| Info.plist de BrowserOS Neo | Versión 0.49.5; bundle `com.browseros.BrowserClaw` | Metadatos de instalación |
| MCP de Neo | Se nombró una sesión y se abrieron/leyeron páginas públicas | Prueba funcional de lectura; no validación de todas sus herramientas |
| Documentación de Comet | Basado en Chromium; admite la mayoría de extensiones de Chrome | Soporte general documentado, no equivalencia total con Chrome [S1] |
| Repositorio BrowserOS | Código público; componentes para Chromium, servidor Neo y panel de sesiones | Base susceptible de estudio y adaptación; licencia indicada AGPL-3.0 [S3] |
| Selector de Perplexity | Catálogo dependiente de producto, cuenta y plan | No equivale a incorporar cuentas externas propias [S2] |

No se ha instalado un prototipo en Comet, abierto su puerto de depuración, cambiado su selector, probado Native Messaging en él ni auditado todas las cuentas del usuario. No se han migrado datos. Las versiones y la documentación deberán comprobarse de nuevo al empezar a ejecutar.

### Veredicto

**Existe una vía técnica razonable para una integración extensa mediante extensión y servicio local. La fusión exacta al 100 % y el cambio del selector nativo de Perplexity no están demostrados.** No se encontró una API pública documentada para insertar las cuentas propias en ese selector. La ausencia de documentación encontrada no constituye una prueba absoluta de imposibilidad; exige comprobar el producto vigente.

| Objetivo | Estado inicial | Decisión |
|---|---|---|
| Mantener Comet oficial | Viable como base | Conservar aplicación y actualizaciones originales |
| Panel propio con varios asistentes | Viable en principio | Probar `sidePanel` y conexiones en Comet |
| Control de pestañas por agentes externos | Condicionado | Probar extensión, permisos y transporte |
| Portar herramientas MCP de Neo | Condicionado por herramienta | Matriz de compatibilidad y pruebas de contrato |
| Cockpit e historial local | Viable como desarrollo | Adaptar componentes reutilizables o implementar equivalentes |
| Reproducción idéntica a Neo | Pendiente | Probar captura de pestañas en segundo plano y formato de grabación |
| Editar el selector original de Perplexity | Sin vía documentada identificada | No hacerlo fundamento del proyecto |
| Historial y contexto unificados con Comet nativo | Sin contrato de integración verificado | Mantener límites explícitos |
| Todas las funciones especiales de Chromium en Neo | Pendiente de auditoría | Identificar extensiones privadas del protocolo y parches nativos |

**Regla:** una opción no disponible debe aparecer como tal. No sustituirla por una simulación visual presentada como funcional.

## 3. Alcance y conservación de beneficios

### 3.1 Comet

Inventariar y comprobar en la cuenta real: navegación, marcadores, historial, extensiones, traducción, bloqueador, búsqueda Perplexity, consultas contextuales, resúmenes, asistente, conectores, atajos y cualquier otra función habilitada. La documentación enumera varias de estas capacidades, pero la disponibilidad efectiva depende del producto y de la cuenta [S1].

No reemplazar el buscador, la página de nueva pestaña ni los atajos existentes automáticamente. El panel propio será la entrada principal de la integración. Si la nueva pestaña nativa es especial para el usuario, abrir el cockpit en una pestaña interna de la extensión, fijable como cualquier otra.

### 3.2 BrowserOS Neo

La matriz inicial debe cubrir todas las herramientas y funciones detectadas, y ampliarse si el inventario encuentra más:

| Familia | Funciones que preservar o sustituir con equivalencia comprobada |
|---|---|
| MCP y conexión | Descubrimiento, enlace a clientes, capacidades, versiones, desconexión |
| Sesiones | Nombre, identificador estable, propietario, historial, estado y actividad |
| Pestañas | Crear, listar filtrando permisos, leer información y cerrar las propias |
| Organización | Grupos de pestañas, ventanas, identificación del agente y tarea |
| Navegación | Ir a URL, atrás, adelante, recargar y detectar navegación |
| Observación | Snapshot accesible, diff, lectura estructurada y búsqueda de texto |
| Interacción | Clic, escritura, fill, teclado, hover, select, check, scroll y drag |
| Esperas | Predicados sobre texto, selector, estado y navegación; límites temporales |
| Captura | Región, viewport, página cuando sea posible y PDF |
| Archivos | Subidas, descargas, estado y comprobación de integridad |
| Ejecución | Run por lotes, evaluación controlada, composición de operaciones |
| Reutilización | Helpers versionados, búsqueda, lectura, guardado y tareas reutilizables |
| Supervisión | Cockpit, actividad en vivo, auditoría, replay y búsqueda de sesiones |
| Persistencia | Ajustes y artefactos locales; reconexión y recuperación |

Neo documenta cuentas iniciadas, agentes en pestañas propias, lectura compacta, acciones por lotes y reproducción de sesiones [S4]. Copiar nombres de herramientas no basta: preservar o documentar también retornos, errores, caducidad de referencias, aislamiento y límites.

### 3.3 BrowserOS clásico: funciones adicionales, identificadas por su origen

Memoria, personalidad mediante instrucciones, tareas programadas, varios proveedores y acceso a una carpeta local figuran en BrowserOS clásico [S5]. Incluirlas como ampliaciones explícitas; no atribuirlas automáticamente a la instalación Neo.

Cada fila de inventario debe declarar: `id`, producto de origen, versión, evidencia, capacidad requerida, implementación prevista, prueba de aceptación, prioridad, estado y limitación. Ninguna función desaparece del plan por ser difícil. Las no viables deben quedar explicadas.

## 4. Arquitectura propuesta y alternativas

```text
Comet oficial: un navegador de trabajo
  ├── Experiencia original de Comet y Perplexity
  ├── Panel propio: asistentes, conversación, contexto, tareas
  ├── Cockpit: sesiones, acciones, evidencias y replay
  └── Extensión Manifest V3
        ├── Registro y control de pestañas autorizadas
        ├── Extracción semántica y visual
        └── Transporte autenticado
                  ↕
        Servicio local de integración
          ├── Servidor MCP para clientes externos
          ├── Adaptadores de proveedores y agentes locales
          ├── Planificador y estado durable de las tareas
          ├── Motor de observación y comprobación
          ├── Credenciales mediante almacén del sistema
          └── Historial, recetas y archivos locales
```

Esta arquitectura es una hipótesis de implementación. Las APIs de panel lateral, Native Messaging y debugger están documentadas para Chrome; probar su soporte en Comet antes de elegirlas definitivamente [S6–S8].

### 4.1 Transporte y control

1. Preferir Native Messaging entre extensión y servicio si funciona correctamente en Comet.
2. Si no sirve, evaluar un canal local autenticado con comprobación de origen, emparejamiento explícito y protección frente a otros procesos o sitios. No basta con escuchar en localhost.
3. Usar API de pestañas y content scripts para operaciones admitidas. Evaluar `chrome.debugger` para capacidades CDP más profundas. No todos los dominios CDP están disponibles por esta API [S8].
4. No activar un puerto de depuración remoto como primera opción. Si una función exige CDP directo, comprobar si es viable en el perfil objetivo y qué cambios de arranque requiere. Documentar las consecuencias antes de adoptarlo.
5. No recurrir a otro navegador cuando falle una conexión: devolver un error accionable y el estado real.

### 4.2 Estado y reinicios

El service worker de una extensión puede terminar y perder sus variables; persistir el estado necesario y probar reconexión [S9]. La autoridad de tareas y efectos pendientes debe vivir en el servicio local, no solo en memoria de la extensión.

Usar identificadores de operación, números de secuencia, cancelación y confirmaciones. Tras reconectar, reconciliar la realidad de pestañas y tareas antes de repetir. Si una escritura pudo ocurrir pero se perdió su confirmación, el estado es `RESULTADO_INCIERTO`: inspeccionar antes de reintentar.

### 4.3 Reutilización del código de Neo

Auditar especialmente `packages/browseros-agent/apps/claw-server-rust`, `apps/claw-app`, `apps/server`, `apps/app`, `packages/cdp-protocol` y los parches de Chromium. Estas rutas se observaron en la estructura pública del repositorio; verificar existencia en la revisión elegida [S3].

Separar la lógica de producto del transporte al navegador. Reutilizar solo componentes cuyo contrato y licencia se entiendan. Fijar revisión, registrar modificaciones y conservar avisos. No asumir que separar procesos resuelve por sí solo las obligaciones de licencia; evaluar las obligaciones del uso y distribución previstos.

No modificar binarios de Comet, su firma o sus recursos internos para simular una integración nativa. Un navegador derivado de BrowserOS sería otro producto y no cumpliría automáticamente la condición de conservar Comet.

### 4.4 Convivencia y límites de aislamiento

- El puente controla únicamente a los agentes que pasan por él.
- Los permisos del puente no garantizan controlar el asistente nativo de Comet ni extensiones de terceros.
- Un grupo de pestañas es organización visual, no una frontera de seguridad.
- Compartir perfil comparte sesiones web; no equivale a aislar cuentas.
- Asociar sesión, pestaña, frame y target mediante identificadores verificados del navegador. Nunca decidir propiedad solo por URL o título.
- Usar bloqueo exclusivo de escritura por pestaña y arbitraje del foco global.
- Si el usuario interviene en una pestaña de agente, detectar la toma de control y detener la operación afectada.
- Si una acción necesita activar una ventana, declararlo. No robar el foco silenciosamente para sostener la promesa de trabajo en segundo plano.

## 5. Brainstorming: catálogo de mejoras priorizadas

**P0:** base de fiabilidad y compatibilidad. **P1:** versión completa útil. **P2:** ampliación posterior. **EXP:** investigación condicionada; no promesa de entrega.

Cada idea tiene una comprobación mínima. Las cifras son criterios de ingeniería propuestos, no rendimiento medido.

| ID | Mejora | Beneficio | Prioridad | Comprobación |
|---|---|---|---|---|
| B01 | Lectura combinada DOM + accesibilidad + captura | Entender estructura y apariencia | P0 | Resolver controles ambiguos con evidencia concordante |
| B02 | Lectura por intención: artículo, formulario, tabla, panel | Menos ruido y menos contexto desperdiciado | P0 | Conservar los campos exigidos en fixtures de cada tipo |
| B03 | Referencias ligadas a versión del documento | Evitar acciones sobre elementos viejos | P0 | Rechazar una referencia tras navegación/re-render relevante |
| B04 | Espera de contenido real | No leer esqueletos de carga | P0 | Detectar carga incompleta bajo timeout |
| B05 | Captura con zoom por región | Leer letra pequeña sin enviar imágenes enormes | P0 | Detalle legible y coordenadas reproducibles |
| B06 | Comprobar visibilidad y obstrucción | Evitar clics tapados por modales | P0 | Detectar un overlay antes del clic |
| B07 | Verificación de resultado por tarea | Evitar falsos «hecho» | P0 | Un clic sin efecto no produce PASS |
| B08 | Lectura de tablas con unidades y cabeceras | Extracción fiel para comparar y calcular | P1 | Preservar decimales, moneda, encabezados y filas |
| B09 | Recorrido de listas virtualizadas | No confundir DOM visible con lista completa | P1 | Recuperar el conjunto esperado o marcar cobertura parcial |
| B10 | Mapa de página y regiones | Saltar al contenido relevante | P1 | Ubicar sección y abrir evidencia correspondiente |
| B11 | PDF con texto, página y recorte | Consultar documentos con trazabilidad | P1 | Dato vinculado a página y área correcta |
| B12 | OCR selectivo y local cuando sea viable | Leer texto dentro de imágenes | P1 | Etiquetar fuente OCR y errores/ambigüedad |
| B13 | Comprensión de gráficas | Relacionar leyendas, ejes y valores | P1 | Diferenciar dato exacto de estimación visual |
| B14 | Captura larga por segmentos solapados | Inspeccionar páginas extensas | P1 | Detectar huecos y elementos fijos repetidos |
| B15 | Diff semántico además de visual | Saber qué cambió de verdad | P1 | Separar datos cambiados del ruido de render |
| B16 | Red y consola bajo demanda | Explicar errores de carga o interacción | P1 | Señalar petición o error concreto sin secretos |
| B17 | Inspector de accesibilidad | Mejorar lectura de controles y navegación por teclado | P1 | Rol, nombre, estado y foco correctos en fixture |
| B18 | Evidencias clicables en la respuesta | Revisar la afirmación en su contexto | P1 | Abrir la observación guardada; avisar si la web cambió |
| B19 | Selector de asistentes con capacidades reales | Elegir una IA adecuada y disponible | P0 | No ofrecer herramientas que el adaptador no soporta |
| B20 | Transferencia explícita de tarea entre IA | Continuar con contexto y estado claro | P1 | Transferir resumen y fuentes, sin atribuir memoria inexistente |
| B21 | Comparación opcional entre IA | Contrastar respuestas | P2 | Coste visible y fuentes trazables; no votación como prueba |
| B22 | Enrutamiento por coste, latencia y capacidad | Usar recursos según la tarea | P2 | Comparación contra una línea base; elección explicable |
| B23 | Memoria editable y con caducidad | Reutilizar preferencias sin arrastrar errores | P1 | Consultar, corregir y borrar una preferencia |
| B24 | Recetas de tareas verificadas | Repetir flujos fiables | P1 | Detectar una receta obsoleta y detenerla |
| B25 | Historial y replay local | Entender acciones y fallos | P1 | Saltar desde un evento a su captura y estado |
| B26 | Simulación de pasos sobre fixtures | Revisar acciones antes de tocar datos reales | P1 | No llamar al servicio real durante la simulación |
| B27 | Checkpoints y recuperación | Retomar tareas interrumpidas | P0 | Recuperación sin duplicar escrituras |
| B28 | Planificador de tareas | Ejecutar rutinas dentro del mismo navegador | P2 | No duplicar una tarea tras suspensión/reinicio |
| B29 | Seguimiento de cambios en páginas | Avisar de cambios relevantes | P2 | Filtrar ruido y conservar antes/después |
| B30 | Presupuestos de RAM, tiempo, tokens y capturas | Evitar saturación y bucles costosos | P0 | Detener/escalonar trabajo al superar el límite |
| B31 | Protección contra instrucciones maliciosas de páginas | Mantener la tarea original | P0 | Un texto hostil no amplía permisos ni accede a secretos |
| B32 | Permisos por sitio, tarea y acción | Dar acceso preciso | P0 | Revocación efectiva en operaciones posteriores |
| B33 | Búsqueda de tareas y evidencias | Encontrar lo hecho anteriormente | P1 | Resultado con tarea, fecha y alcance autorizado |
| B34 | Control de descargas y subidas | Confirmar el archivo correcto | P1 | Tamaño, hash cuando proceda y destinatario correctos |
| B35 | Detección de sesión caducada y CAPTCHA | Evitar bucles inútiles | P0 | Pedir intervención concreta y conservar checkpoint |
| B36 | Adaptación multilingüe y formatos locales | Leer importes, fechas y contenido español | P1 | Separar 1.234,56 de 1,234.56 y fechas ambiguas |
| B37 | Pruebas responsive bajo demanda | Revisar diseños a distintos anchos | P2 | Cuatro viewports sin alterar pestañas personales |
| B38 | Panel consistente con tema y teclado de Comet | Reducir fricción | P1 | Navegable por teclado y sin atajos conflictivos |
| B39 | Voz para dictar y escuchar | Accesibilidad y comodidad | P2 | Acciones críticas requieren intención inequívoca |
| B40 | Lectura temporal de vídeo | Entender cambios durante una reproducción | EXP | Frames/transcripción con timestamp y permisos |
| B41 | DOM congelado y reproducción interactiva | Inspección histórica más rica | EXP | Medir cobertura, coste y riesgo de datos privados |
| B42 | Herramientas semánticas ofrecidas por un sitio | Evitar automatización frágil cuando haya integración | EXP | Verificar contrato, origen, permisos y resultado |

**Orden recomendado para el mayor impacto:** B01–B07, B19, B27, B30–B32 y B35; después tablas, OCR, PDF, listas largas, replay y recetas. No comenzar por voz, animaciones del panel o comparación de muchos modelos.

## 6. Especificación: leer mejor las webs

### 6.1 Motor de observación por capas

El agente solicita una intención: leer contenido, buscar un dato, completar un formulario, extraer una tabla o revisar apariencia. El motor elige las señales mínimas suficientes:

1. **Identidad y frescura:** navegador, sesión, pestaña autorizada, frame, URL saneada, versión del documento, momento de observación y estado de carga.
2. **Semántica:** roles, nombres, encabezados, enlaces, etiquetas, estados y estructura de tablas.
3. **Texto relevante:** bloques jerárquicos con procedencia; reducir navegación repetida sin borrar advertencias o contexto necesario.
4. **Geometría:** rectángulos, scroll, clipping, visibilidad, viewport, escala y superposiciones cuando afecten a la acción.
5. **Captura:** región del objetivo, contexto inmediato y vista general cuando aporte información.
6. **Diagnóstico opcional:** red y consola necesarias para resolver una incertidumbre concreta.

CDP documenta accesibilidad y snapshots de DOM/layout; son mecanismos de observación, no una garantía de comprender correctamente la página. Algunos métodos son experimentales y deben fijarse/probarse contra la versión real [S10, S11].

El resultado indica qué capas se usaron, qué falló y qué quedó fuera. Nunca afirmar «he leído todo» si hubo truncado, paginación pendiente, virtualización, frames inaccesibles o secciones no cargadas.

### 6.2 Clasificación de páginas y extracción

- **Artículo:** título, autor/fecha si constan, secciones, texto principal, enlaces, listas y tablas. Evaluar Mozilla Readability sobre un clon del documento; su parseo modifica el DOM y su detector es heurístico [S12]. No aplicarlo indiscriminadamente a aplicaciones.
- **Formulario:** campo, etiqueta, ayuda, tipo, valor redactado si es sensible, estado requerido, validación, relación con grupos y botón de envío.
- **Tabla/panel:** título, cabeceras multinivel, unidades, filtros activos, periodo, paginación y filas. Un panel de resultados cambia de significado si se pierde el filtro.
- **Tienda:** distinguir precio visible, moneda, variación seleccionada, disponibilidad, envío y total. No inferir el total de compra por un precio aislado.
- **Buscador:** resultado, fuente, fecha disponible, snippet y enlace. No presentar el snippet como lectura de la página enlazada.
- **Aplicación visual/canvas:** buscar primero datos accesibles o exportación admitida; después captura/OCR con límites explícitos.
- **PDF:** usar capa textual cuando exista; contrastar con render para tablas o relaciones espaciales. OCR solo cuando haga falta. Mantener página y región.

### 6.3 Contenido dinámico y cobertura

No usar «red inactiva» como única condición de carga: una aplicación puede tener conexiones continuas. Esperar condiciones específicas con timeout: control visible/habilitado, filas esperadas, desaparición del skeleton, estado de un componente, fuentes e imágenes del área relevante.

No esperar indefinidamente todas las imágenes de una página larga. Medir las visibles y necesarias. Si una fuente o imagen no carga, registrar degradación y decidir si bloquea esa tarea.

En listas virtualizadas, recorrer por bloques con presupuesto de scroll/tiempo; deduplicar por clave estable cuando exista y conservar orden. Declarar `completa`, `parcial` o `desconocida`. Una estimación del porcentaje leído solo se muestra si se conoce el total.

Los iframes entre orígenes y shadow DOM deben probarse por separado. No prometer acceso universal a frames, shadow roots cerrados, páginas internas o superficies protegidas.

### 6.4 Procedencia y discrepancias

Cada dato relevante debe poder enlazarse a una observación: fecha, página/frame, bloque o celda, texto o recorte. Los selectores son pistas para volver, no prueba de identidad permanente.

Si el texto extraído dice una cosa y la captura muestra otra, conservar ambas evidencias y resolver con una observación nueva. No elegir silenciosamente el valor que encaja mejor con la respuesta.

Para importes, fechas y cantidades, guardar el texto original junto al valor normalizado y la regla aplicada. Si la fecha es ambigua, mantenerla como ambigua hasta disponer de contexto suficiente.

## 7. Especificación: capturas y visión mejores

### 7.1 Captura adaptativa

- Empezar con una vista general de resolución útil y recortar el área necesaria a resolución original.
- Medir si el texto es legible antes de reducir tamaño. Un tamaño fijo muy pequeño puede destruir la evidencia.
- Registrar viewport CSS, dimensiones de imagen, zoom, devicePixelRatio, scroll y transformación de coordenadas.
- Guardar el original para comprobación y una copia optimizada para el modelo. No dar al modelo rutas privadas fuera del alcance de la tarea.
- Usar PNG para comparación exacta y formatos comprimidos cuando baste lectura visual; validar formatos soportados por cada proveedor.
- No recortar el contexto que cambia el significado: encabezados, unidades, aviso de error o botón asociado.

La captura CDP se documenta en el dominio Page; métodos/opciones y funcionamiento en segundo plano deben comprobarse en el transporte elegido [S13].

### 7.2 Calidad y páginas largas

Detectar imágenes vacías, repetidas, parciales o anteriores a la acción mediante combinación de dimensiones, estado DOM, marca de tiempo y comparación. Una página blanca puede ser válida: nunca rechazarla solo por uniformidad de píxeles.

Para páginas largas, ofrecer una miniatura de orientación y segmentos solapados. Registrar cada segmento con su posición. Detectar barras fijas duplicadas, lazy loading, huecos y contenido que cambió entre segmentos. Una captura unida de contenido dinámico no es una instantánea atómica; indicarlo.

No desplazar automáticamente una pestaña personal para obtener una captura larga. Usar pestaña asignada o transferencia de control autorizada, y restaurar scroll/foco si corresponde.

### 7.3 OCR, gráficos y contenido visual

- OCR bajo demanda, preferentemente local si su calidad/rendimiento son suficientes. Seleccionar motor y licencia después de un benchmark; no instalar uno por costumbre.
- Conservar idioma, región y confianza proporcionada por el motor, sin convertirla en certeza calibrada del sistema.
- Contrastar números OCR con texto accesible si existe. No corregir un decimal sin evidencia.
- En gráficos, distinguir leyenda, unidades, ejes y valores exactos frente a estimaciones visuales. Un valor obtenido de un tooltip se etiqueta como tal.
- En canvas sin datos accesibles, no afirmar precisión de tabla a partir de píxeles.
- Vídeo y contenido protegido quedan condicionados a captura disponible y permisos; no incluir evasión de protecciones.

### 7.4 Comparación visual

Mantener dimensiones, escala y condiciones comparables. En fixtures de diseño, estabilizar animaciones y tiempo cuando se controle el entorno; no alterar silenciosamente el comportamiento de una web real.

Combinar diff de píxeles, geometría y cambios semánticos. Un desplazamiento por una fuente tardía no es necesariamente una regresión. Un texto incorrecto puede ser grave aunque cambien pocos píxeles.

Viewports de QA propuestos: 390, 768, 1024 y 1440 px de ancho. Emularlos solo en sesiones de prueba, no en la navegación diaria. El resultado del análisis visual debe incluir recortes antes/después y motivo concreto.

## 8. Interacción fiable: observar, actuar, comprobar

### 8.1 Secuencia obligatoria

1. Confirmar alcance y propiedad de la pestaña.
2. Obtener observación suficientemente reciente y condiciones previas.
3. Resolver el objetivo por rol/nombre/relaciones; usar referencias de nodo cuando sigan válidas.
4. Confirmar visibilidad, estado habilitado y ausencia de obstrucción relevante.
5. Ejecutar la acción mediante el mecanismo soportado menos intrusivo.
6. Esperar una condición concreta de resultado.
7. Comprobar el estado final con evidencia apropiada al impacto.
8. Registrar resultado, limitaciones y siguiente paso.

Las acciones rutinarias pueden bastar con una comprobación determinista fuerte. Para afirmaciones visuales o efectos importantes, añadir una señal complementaria útil. No exigir capturas redundantes a toda lectura ni considerar dos señales del mismo origen como garantía absoluta.

### 8.2 Referencias, coordenadas y formularios

- Asociar referencias a documento, frame y versión de observación. Invalidar tras navegación, detach o cambio relevante, sin invalidar por cada reloj animado de la página.
- Si hay varios candidatos equivalentes, obtener más contexto. No hacer clic en el primero arbitrariamente.
- Antes de un clic por coordenadas, recalcular geometría y hacer hit-test cuando sea posible; abortar si cambió el objetivo.
- Preferir interacción soportada por el navegador para formularios controlados. Los setters o eventos sintéticos no son solución universal: probar el componente concreto y verificar el estado enviado.
- Diferenciar reemplazar valor, añadir texto y limpiar campo. No limitar fill a campos vacíos de forma general.
- No ejecutar envío por duplicado si un timeout ocurre después del clic. Leer el estado persistido o identificador de resultado.
- Redactar valores sensibles; verificar no requiere volcarlos en logs.

### 8.3 Recuperación y pruebas de efectos

Máquina de estados sugerida: `pendiente → observando → preparado → ejecutando → verificando → completado`, con salidas `pausado`, `requiere_intervencion`, `resultado_incierto`, `fallido` y `cancelado`.

Los reintentos de lectura pueden automatizarse con límites. Las escrituras necesitan distinguir operaciones idempotentes de efectos externos. Registrar intención antes de actuar y resultado después; eso ayuda a recuperar, pero no garantiza ejecución exactamente una vez en una web externa.

Deshacer solo cuando exista una operación inversa comprobada. Replay es revisión histórica, no rollback. No prometer deshacer compras, mensajes enviados o borrados definitivos.

## 9. Todas las IA: conexiones y experiencia de conversación

### 9.1 Inventario real

Inspeccionar únicamente configuraciones y estados necesarios, sin exportar secretos. Registrar proveedor/agente, tipo de acceso, cuenta identificada de forma mínima, modelos accesibles, capacidades, límites y estado de prueba.

| Tipo | Integración prevista | Límite |
|---|---|---|
| API oficial de proveedor | Conversación mediante adaptador | La suscripción web no prueba disponibilidad de API |
| Agente local con CLI/SDK/IPC admitido | Crear tareas y recibir eventos | Verificar interfaz estable, autenticación y cancelación |
| Cliente MCP externo | Control del navegador desde ese cliente | MCP del navegador no implica que el panel pueda invocar al cliente |
| Cuenta web | Abrir la experiencia web dentro de Comet | No convertir cookies de sesión en API ni asumir que permite iframe |
| Servidor de modelo local | Adaptador según protocolo real | Confirmar visión, herramientas y contexto; no asumir equivalencia |
| Perplexity nativo | Conservar acceso original | No inventar API para su panel o historial |

Un modelo invocado por API dentro del panel y el producto web del mismo proveedor son experiencias distintas. No prometer acceso a sus proyectos, archivos, memoria o herramientas si no existe integración para ellos.

### 9.2 Contrato de adaptador

Capacidades declaradas: texto, imágenes, archivos, streaming, herramientas, cancelación, contexto máximo, salidas estructuradas, sesiones persistentes y datos de uso/coste cuando estén disponibles.

Operaciones conceptuales: listar capacidades, comprobar conexión, crear sesión, enviar contenido, recibir eventos, cancelar y cerrar. Estos son contratos propuestos del proyecto, no nombres de API existentes.

El catálogo de modelos debe proceder de configuración validada o descubrimiento oficial cuando exista. No fijar nombres de modelos cambiantes en el diseño. Una opción no soportada se desactiva con motivo.

### 9.3 Transferencia entre asistentes

Al cambiar de IA, transferir solo contexto seleccionado: objetivo, resumen verificable, fuentes, decisiones, acciones hechas y pendientes. Indicar que el historial nativo puede no transferirse. No transmitir instrucciones internas o razonamiento privado de otro proveedor.

La memoria compartida guarda preferencias y hechos con procedencia, no conclusiones sin revisar. Debe poder inspeccionarse, corregirse, exportarse y borrarse. Separar preferencias generales de datos privados por proyecto.

No enviar automáticamente el contexto a varios proveedores. Comparar modelos es una función opcional con selección de destinatarios y coste visible cuando se pueda medir. Si no hay información de coste, mostrar «no disponible», no cero.

## 10. Interfaz y coherencia visual

### 10.1 Panel principal

```text
┌──────────────────────────────────────────┐
│ Asistente [selector]      [Conexiones]    │
│ Contexto: esta pestaña + 2 fuentes        │
├──────────────────────────────────────────┤
│ Conversación                             │
│ Respuesta con fuentes y evidencias        │
│                                          │
│ Tarea: leyendo una tabla · paso 2 de 4     │
│ [Ver pestañas] [Detener] [Ver evidencia]   │
├──────────────────────────────────────────┤
│ Escribe tu petición…        [Adjuntar]    │
└──────────────────────────────────────────┘
```

Los pasos solo se cuentan si existe un plan conocido; no inventar porcentajes. El usuario debe ver qué asistente recibe el contenido y qué pestañas están incluidas.

### 10.2 Cockpit

Sesiones activas, recientes, búsqueda, recetas y conexiones. Cada sesión muestra objetivo, agente, estado, tiempo y páginas autorizadas. Replay con eventos y capturas sincronizadas; marcar intervalos no capturados.

Una tira de capturas se llama «secuencia de capturas». Solo llamarla vídeo o reproducción continua si realmente se genera ese formato con cobertura temporal declarada.

### 10.3 Integración con Comet

Respetar tema claro/oscuro, tipografía de sistema, densidad, tamaño y navegación por teclado. Comprobar contraste, foco y lector de pantalla del propio panel.

No sustituir logos o textos para hacer pasar el panel por una función oficial de Perplexity. El objetivo es coherencia, con identidad y límites claros. No inyectar parches frágiles en la web de Perplexity como núcleo del producto.

Cuando Perplexity solo pueda abrirse en su panel o web original, ofrecer una transición clara. No crear una conversación ficticia que parezca conectada a su backend. No prometer que una extensión pueda ocultar permanentemente todos los controles nativos o modificar la barra del navegador.

## 11. Privacidad, permisos y datos de sesión

Estas medidas forman parte del diseño de un agente que opera con sesiones iniciadas; no son un trámite extra para cada acción.

- Permisos limitados por tarea, origen y capacidad, reutilizando la autorización existente mientras siga vigente.
- Credenciales en el almacén del sistema o gestor compatible; nunca en el repositorio, localStorage de una web, capturas de configuración o prompts.
- El contenido web es datos no confiables. Una página no puede ampliar la tarea, autorizar acceso a otra pestaña ni pedir al agente exportar credenciales.
- Las evaluaciones de lectura expuestas por el inspector deben usar operaciones acotadas. Arbitrary JavaScript o CDP `Runtime` no se vuelve «solo lectura» por ponerle esa etiqueta.
- Run y helpers de automatización deben operar mediante el SDK acotado. Si se necesita evaluación arbitraria, tratarla como capacidad privilegiada explícita y separada.
- En listeners locales: autenticación, comprobación de origen y endpoints no expuestos a la LAN. No reutilizar el puerto observado en otra máquina como constante.
- Redactar cabeceras, cuerpos, query strings, fragmentos y capturas cuando contengan secretos. La redacción visual requiere pruebas; no prometer que puede detectarlo todo.
- Capturas y logs privados fuera de Git, con retención configurable. Propuesta inicial: 7 días para evidencia rutinaria, ajustable por el usuario.
- Eliminar una sesión debe eliminar sus artefactos asociados según una política documentada. No garantizar borrado físico de copias externas o respaldos ajenos al sistema.
- Local no significa que ningún dato salga: indicar qué contenido se envía al proveedor de IA y cuándo.
- No capturar pestañas personales, modos privados o sitios excluidos por defecto.
- Aplicar las reglas de autorización del usuario a envíos, compras y borrados; no pedir confirmación repetida por una acción ya autorizada inequívocamente.

## 12. Rendimiento y presupuestos

Medir contra Neo en tareas equivalentes cuando sea posible y contra Comet sin integración para sobrecarga. Registrar máquina, versiones, condiciones y tamaño de entrada; no prometer porcentajes de ahorro sin datos.

Métricas: éxito por tarea, falsos éxitos, latencia p50/p95, llamadas, tamaño de observaciones, tokens medidos o estimados por separado, bytes de imagen, RAM y CPU incrementales, consumo de disco y recuperación.

Valores iniciales propuestos, ajustables tras medir:

- Hasta dos tareas externas concurrentes al empezar; ampliar si la presión de memoria y la convivencia lo permiten.
- Una operación de escritura activa por pestaña; coordinar acciones que requieren foco global.
- Capturas pesadas y OCR en cola limitada, cancelable.
- Timeout por espera y presupuesto total por tarea. Al agotarse, informar cobertura y estado; no bucle infinito.
- Primera lectura semántica objetivo de hasta 12.000 caracteres relevantes; resultado paginado con acceso al resto. No truncar silenciosamente datos necesarios para la tarea.
- Solicitar detalle visual solo donde la primera observación deje una incertidumbre.
- Caché ligada a documento/frame y cambios relevantes, nunca solo a URL.

El gobernador reduce concurrencia antes de interpretar saturación como fallo de una web. `NO_MEDIDO` es una salida válida si el entorno impide una observación fiable.

## 13. Decisiones abiertas y pruebas que las resuelven

| Decisión | Prueba necesaria | Si falla |
|---|---|---|
| Panel lateral propio | Abrir, persistir, navegar y convivir con el panel nativo | Evaluar pestaña de extensión; registrar pérdida de integración visual |
| Native Messaging | Instalar host de prueba, intercambiar mensajes y reconectar en Comet | Evaluar canal local autenticado |
| `chrome.debugger` | Adjuntar a pestaña propia, usar dominios necesarios y desadjuntar | Evaluar capacidades reducidas o CDP directo condicionado |
| Captura en segundo plano | Capturar contenido actualizado sin cambiar foco | No prometer replay completo ni segundo plano para esa operación |
| PDF y archivos | Capturar/generar/subir/descargar un fixture | Diseñar alternativa admitida o marcar límite |
| Convivencia con Comet Assistant | Tareas separadas y disputa controlada de pestaña | Exclusión temporal explícita; documentar limitación |
| Adaptación del servidor Neo | Pruebas de contrato con transporte Comet | Reimplementar adaptador equivalente o bloquear función |
| Invocar cada agente desde el panel | Interfaz oficial/admitida con salida y cancelación | Mantener solo conexión MCP entrante o acceso web |
| Selector nativo Perplexity | Evidencia de mecanismo público soportado | Selector propio; no prometer modificación nativa |
| Replay completo | Cobertura de frames, captura y almacenamiento | Secuencia parcial correctamente identificada |

No sacrificar la condición «un solo navegador» para ocultar una prueba fallida. Si una función esencial exige otro navegador o modificar Comet, presentar el bloqueo y una alternativa concreta para decisión del usuario.

## 14. Fases de ejecución y criterios de salida

### Fase 0 — Inventario, alcance y restauración

Leer este archivo completo, las instrucciones aplicables del proyecto y el plan previo de Neo si está disponible. Verificar versiones y documentación. Inventariar funciones y conexiones, sin copiar secretos. Registrar cambios locales preexistentes y trabajar en una carpeta o checkout aislado apropiado.

Definir pruebas de conservación de Comet. Preparar copias selectivas de las configuraciones que se vayan a editar, protegidas y con hashes; ensayar restauración sobre copias. No respaldar indiscriminadamente perfiles o credenciales en el repositorio.

**Salida:** `inventory.json`, `capability-matrix.md`, decisiones pendientes y procedimiento de restauración. Ninguna función importante sin clasificación.

### Fase 1 — Prototipo de viabilidad en Comet

Extensión mínima en perfil de prueba, transporte local, lectura de una pestaña propia, captura, formulario de fixture y respuesta MCP. Comprobar panel, control, archivos y convivencia. No construir aún todos los proveedores ni el diseño final.

**Salida:** un agente externo completa un flujo verificable en Comet y un informe muestra APIs probadas, limitaciones y pasos de reproducción. No existe dependencia de Neo en la ejecución. Si un requisito central falla, revisar arquitectura antes de avanzar.

### Fase 2 — Núcleo estable de sesiones y herramientas

Implementar registro de propiedad, permisos, contrato MCP, versionado de mensajes, cancelación, reconexión, logs redactados y bloqueo de escrituras. Adaptar las herramientas básicas de Neo con pruebas de contrato.

**Salida:** sesiones separadas, referencias caducadas rechazadas, permisos revocables y reconexión sin efectos duplicados. Conexión no autenticada rechazada antes de exponer información.

### Fase 3 — Lectura y visión superiores

Implementar B01–B07: extracción por intención, accesibilidad, geometría, capturas regionales, carga y verificación. Después tablas, virtualización, PDF y OCR con pruebas específicas. Implementar cobertura y procedencia.

**Salida:** benchmark de lectura con resultados correctos y casos parciales identificados. Las capturas inválidas no producen falsos PASS. Diferenciar mediciones realizadas de funciones aún no soportadas.

### Fase 4 — Asistentes y contexto

Implementar primero un proveedor o agente realmente disponible; después el resto de conexiones inventariadas. Definir capacidades por adaptador y probar errores, expiración, streaming y cancelación. Añadir transferencia de contexto y memoria editable.

**Salida:** cada IA ofrecida en el selector tiene una prueba real o un estado explícito de conexión pendiente. No mostrar como completadas conexiones simuladas. Conservar el acceso original a Perplexity.

### Fase 5 — Panel, cockpit, evidencia y recetas

Construir interfaz accesible, historial, replay con cobertura declarada, búsqueda y helpers versionados. Añadir diagnóstico bajo demanda. Integrar tema, teclado y navegación sin romper los flujos de Comet.

**Salida:** un usuario puede iniciar, seguir, detener y revisar una tarea desde Comet; localizar su evidencia y distinguir capturas parciales de grabación continua.

### Fase 6 — Recuperación, seguridad y carga

Ejecutar fallos provocados: desconexión, timeout tras envío, service worker reiniciado, permisos revocados, toma de control, contenido malicioso y presión de memoria. Validar que el inspector no permite escrituras no autorizadas.

**Salida:** suite crítica aprobada; resultado incierto tratado sin reenvío automático; límites de aislamiento documentados y desinstalación ensayada.

### Fase 7 — Piloto en perfil real y entrega

Tras el encargo de implementación y las pruebas en perfil de ensayo, preparar y ejecutar la instalación reversible en el perfil real dentro del alcance autorizado. Utilizar importaciones oficiales o inicio de sesión cuando haga falta. Repetir smoke tests y conservación de Comet.

Cerrar Neo para la prueba final sin interrumpir tareas ajenas activas. No desinstalarlo ni borrar sus datos. Probar uso normal solo con Comet y el servicio.

**Salida:** integración usable, informe de alcance, limitaciones, manual y rollback comprobado. No marcar «fusión completa» si quedan funciones de la matriz sin equivalencia.

### Fase 8 — Ampliaciones P2 y experimentos

Programador, monitores de cambios, comparación de modelos, routing, voz y funciones experimentales se realizan después de estabilizar P0/P1 y según el alcance autorizado. Las tareas programadas requieren Mac y Comet disponibles; una cola local no ejecuta navegación con el equipo apagado.

No fijar una fecha final antes de la fase 1. Al terminarla, estimar esfuerzo por bloque, incluyendo mantenimiento, QA y adaptación a futuras versiones. Una demo funcional no es una entrega estable.

## 15. Contratos de datos propuestos

Son esquemas de diseño, no APIs existentes. Ajustar al lenguaje y stack elegidos sin perder los conceptos.

```text
Session
  id, clientId, taskId, state, createdAt, grants, ownedTabIds

Observation
  id, sessionId, tabId, frameId, documentVersion, observedAt
  sanitizedUrl, intent, readiness, coverage, usedSensors
  semanticBlocks, targetRefs, geometry, evidenceRefs, limitations

TargetRef
  id, tabId, frameId, documentVersion, role, accessibleName
  nodeHandleIfSupported, observedBounds, expiresOn

ActionRequest
  operationId, sessionId, targetRef, kind, arguments
  preconditions, expectedOutcome, effectClass, deadline

ActionResult
  operationId, state, beforeObservationId, afterObservationId
  outcomeEvidence, retryPolicy, uncertainty, error

Evidence
  id, taskId, kind, capturedAt, viewport, scale, scroll
  relativeArtifactPath, contentHash, sourceRegion, redactionState
  retentionUntil, coverage, limitations

ProviderCapabilities
  providerId, connectionKind, verifiedAt, availableModels
  text, images, files, tools, streaming, cancellation
  contextLimit, usageReporting, costReporting, limitations
```

Distinguir estado de tarea y veredicto de prueba. Un error de autenticación no es un fallo visual. Veredictos de QA: `PASS`, `FAIL`, `NO_MEDIDO`. Una función no implementada se marca pendiente en la matriz; no se convierte en `PASS` mediante un skip.

Los hashes prueban integridad de los artefactos guardados, no la verdad del contenido ni la identidad de una página externa.

## 16. Pruebas de aceptación y benchmark

### 16.1 Fixtures controlados

Cada fixture declara estado inicial, acción, resultado esperado, datos, límites temporales y evidencias. Las pruebas con efectos externos se hacen en fixtures o entornos de ensayo; no enviar correos ni compras reales para validar una demo.

| ID | Escenario | Resultado exigido |
|---|---|---|
| T01 | Artículo con menús y publicidad | Extraer contenido principal sin perder una advertencia relevante |
| T02 | SPA con skeleton y carga retrasada | Esperar contenido o declarar incompleto |
| T03 | Input controlado con valor previo | Reemplazar/añadir según instrucción y verificar envío exacto |
| T04 | Dos botones con mismo texto | Elegir por contexto o resolver ambigüedad sin acción errónea |
| T05 | Overlay sobre el objetivo | Detectar obstrucción y no afirmar clic exitoso |
| T06 | Re-render y referencias viejas | Rechazar referencia caducada y observar de nuevo |
| T07 | Tabla con cabeceras y números locales | Preservar estructura, unidades, ceros, signos y decimales |
| T08 | Lista virtualizada con 250 filas conocidas | Extraer las 250 sin duplicados o declarar parcial |
| T09 | Iframe de otro origen y shadow DOM | Detectar alcance real; no inventar contenido inaccesible |
| T10 | Imágenes lazy y fuentes tardías | Captura relevante completa o degradación explícita |
| T11 | Página blanca válida / captura vacía inválida | Distinguir mediante oráculos adicionales |
| T12 | Página larga con barra fija | Segmentos sin huecos, duplicaciones identificadas |
| T13 | Texto pequeño en imagen | OCR/zoom y procedencia; ambigüedad numérica señalada |
| T14 | Gráfico sin tabla accesible | Valores estimados etiquetados; no falsa precisión |
| T15 | PDF textual y PDF escaneado de prueba | Dato vinculado a página y región |
| T16 | Download y upload | Archivo correcto, finalización y destino comprobados |
| T17 | Dos agentes y una pestaña personal | Ningún acceso del puente fuera de permisos |
| T18 | Usuario interviene en pestaña del agente | Pausa/reconciliación sin pelear por el foco |
| T19 | Comet Assistant y agente externo | Convivencia o límite reproducible documentado |
| T20 | Reinicio de service worker y servicio local | Recuperación de estado sin repetir efectos |
| T21 | Timeout después de envío confirmado por servidor | Leer resultado y no enviar de nuevo |
| T22 | Sesión caducada y CAPTCHA | Checkpoint e intervención concreta |
| T23 | Página con instrucciones hostiles | No cambiar tarea ni acceder a secretos/pestañas ajenas |
| T24 | Permisos revocados o origen falso | Rechazo técnico antes de leer o actuar |
| T25 | Datos sensibles en URL, red y formulario | Artefactos y logs sin los secretos de prueba |
| T26 | Captura en pestaña inactiva | Frescura verificada; no imagen vieja presentada como actual |
| T27 | Proveedor sin visión o herramientas | Opción deshabilitada o transformación explícita válida |
| T28 | Cancelación y límite de uso del proveedor | Estado correcto y tarea detenida sin bucle |
| T29 | Cambio de IA | Contexto transferido con origen y alcance correctos |
| T30 | Memoria y borrado de sesión | Edición/borrado verificable de los datos bajo control del sistema |
| T31 | Presión de recursos simulada | Menos concurrencia o NO_MEDIDO, no falso fallo del sitio |
| T32 | Actualización compatible de Comet/extensión | Smoke tests de APIs y datos; rollback disponible |
| T33 | Cuatro viewports de QA | Geometría y capturas etiquetadas, sin alterar pestañas personales |
| T34 | Desinstalación | Comet funcional y configuraciones ajenas conservadas |
| T35 | Neo cerrado | Todas las funciones declaradas de producción siguen funcionando |
| T36 | Receta obsoleta | Detección de precondición cambiada y parada segura |

### 16.2 Métricas y aprobación

Registrar resultados por caso, versión y condición. Para lecturas estructuradas usar coincidencia de valores y relaciones esperadas; para interacción, estado persistido; para visión, hechos y regiones verificables. No reducir todo a una puntuación subjetiva del modelo.

- Todas las pruebas críticas aplicables a funciones entregadas deben pasar.
- Repetir tres veces los casos críticos no deterministas: referencias, foco, captura inactiva, reconexión y efectos inciertos.
- Cero falsos PASS en los fallos provocados de la suite.
- Cero acceso no autorizado observado en las pruebas de aislamiento del puente.
- Cero secretos de prueba en los artefactos exportados.
- Cero dependencia de otro navegador durante la prueba de producción.
- Las funciones pendientes o no soportadas se enumeran, con impacto y siguiente acción.
- Medir mejoras frente a la línea base; si una mejora aumenta coste o latencia, explicarlo.

Estos resultados describen la suite ejecutada; no garantizan cero errores futuros en cualquier web.

## 17. Entregables de la implementación

Estructura orientativa para un proyecto separado; adaptar al repositorio elegido y no crear archivos vacíos solo para aparentar avance:

```text
comet-neo-integration/
  README.md
  LICENSE / NOTICE correspondientes
  apps/extension/
  apps/local-service/
  packages/browser-adapter/
  packages/mcp-contract/
  packages/observation/
  packages/provider-adapters/
  packages/evidence/
  packages/recipes/
  fixtures/
  tests/contract/
  tests/integration/
  tests/acceptance/
  docs/inventory.json
  docs/capability-matrix.md
  docs/architecture-decisions.md
  docs/compatibility-report.md
  docs/installation.md
  docs/privacy-and-data.md
  docs/rollback.md
  docs/acceptance-report.md
  docs/known-limitations.md
  PROGRESS.md
```

Elegir stack tras evaluar la reutilización: no reescribir un backend funcional solo para uniformar lenguajes, ni cargar un runtime adicional sin beneficio. Fijar dependencias y revisiones después del prototipo, documentar licencias y construir paquetes reproducibles.

Entregar instalación, actualización y desinstalación verificables; estado de conexiones; matriz completa; benchmark; capturas del producto y un flujo de ejemplo sin datos privados. No afirmar que un archivo Markdown es un instalador.

### Criterio de terminado

El usuario abre Comet, elige una conexión comprobada, completa una tarea de lectura o interacción, revisa evidencia, detiene otra tarea y consulta el historial. Sus funciones originales siguen funcionando, Neo está cerrado y la integración se puede retirar. Toda diferencia respecto a Neo está documentada y ninguna opción del panel finge una capacidad inexistente.

## 18. Rollback y mantenimiento

### Rollback

1. Detener nuevas tareas y reconciliar operaciones en curso; no matar procesos ajenos.
2. Desconectar agentes del puente nuevo y desactivar la extensión.
3. Restaurar únicamente entradas/configuraciones modificadas por esta instalación, comprobando si hubo cambios posteriores.
4. Detener y retirar el servicio y su arranque automático si se instalaron.
5. Conservar o exportar evidencia privada solo según la decisión del usuario.
6. Verificar navegación, sesiones y funciones originales de Comet.
7. Neo conserva su instalación y perfil. Su uso posterior no requiere reconstruirlos.

### Mantenimiento

Ejecutar smoke tests después de cambios en Comet, extensión, servidor, APIs de proveedores o transporte. Mantener una matriz de versiones compatibles. Ante incompatibilidad, desactivar la capacidad afectada y conservar las demás cuando sea seguro.

Las recetas de sitios cambian con sus interfaces: versionar, probar precondiciones y registrar última ejecución válida. No afirmar que un selector es estable para siempre. Las tareas pendientes deben migrarse con esquema versionado y copia restaurable.

## 19. Relación con el plan previo de Neo

Referencia local: `galaxia/pueblos/browseros-neo/PLAN-MEJORA-TOTAL.md`, dentro del workspace donde se redactó este archivo. El presente plan incorpora sus ideas útiles y puede entenderse sin disponer de esa referencia.

Se conservan: descubrimiento y preflight, observación combinada, capturas regionales, diagnóstico bajo demanda, evidencia, límites de recursos, pruebas con fallos provocados y reversibilidad.

Se adaptan o corrigen para este nuevo objetivo:

- Comet pasa a ser el único navegador de trabajo; el MCP nativo de Neo deja de ser una dependencia obligatoria de producción.
- Un inspector externo solo se añade si aporta una capacidad necesaria y se conecta al mismo navegador; no convertirlo en segunda capa permanente por defecto.
- La propiedad debe basarse en identificadores y registro del puente. No copiar un mecanismo de nonce escrito en todas las páginas si el transporte proporciona una relación directa verificable.
- No activar o traer al frente la pestaña automáticamente en toda acción de teclado/puntero; probar impacto y arbitrar el foco.
- No imponer setters sintéticos a todos los campos React ni fill solo sobre campos vacíos.
- Las cifras de concurrencia y puertos anteriores no se toman como propiedades universales del equipo.
- Se distingue una señal fuerte suficiente de una comprobación redundante; la fiabilidad no debe duplicar indiscriminadamente todas las llamadas.
- Se reconocen los límites de una extensión sobre páginas internas, otros asistentes y controles nativos.

## 20. Instrucción de arranque para Fable 5.1

El usuario puede acompañar este documento con esta instrucción cuando quiera iniciar la implementación:

> Implementa este plan en el alcance que te autorizo. Lee el documento completo antes de diseñar. Empieza por inventario y prototipo de compatibilidad en Comet; no construyas primero una maqueta desconectada. Mantén Comet oficial como único navegador de trabajo y conserva sus capacidades. Integra las conexiones de IA realmente disponibles, distinguiendo API, producto web y agente local. Prioriza lectura combinada, capturas útiles, referencias frescas, aislamiento de pestañas y comprobación del resultado. No prometas acceso al selector nativo de Perplexity sin una interfaz documentada. Reutiliza código de Neo solo tras auditar dependencias y licencias. Trabaja de forma reversible, conserva cambios ajenos, no copies secretos y registra evidencia de cada hito. Continúa con el trabajo ya autorizado sin pedirme confirmación para decisiones rutinarias. Si aparece un bloqueo que cambia el objetivo, presenta la prueba, su impacto y una alternativa concreta. No sustituyas silenciosamente Comet por otro navegador. Termina con instalación verificable, pruebas, limitaciones y rollback.

Formato de actualización de progreso recomendado:

```text
Fase actual:
Capacidades comprobadas:
Cambios realizados:
Pruebas y resultado:
Límites o bloqueo con evidencia:
Siguiente paso:
```

Si el implementador no tiene acceso al Mac, al navegador, a una cuenta o a una API, debe señalar esa limitación y avanzar en los componentes independientes. No inventar resultados de pruebas locales o autenticaciones.

## 21. Fuentes primarias y notas de comprobación

Consultadas durante la preparación del plan el 6 de septiembre de 2026, incluidas las comprobaciones de la conversación previa. Revisar versiones y contenidos antes de implementar. Las propuestas, prioridades, esquemas y criterios de aceptación de este documento son diseño propio; no son prestaciones ya entregadas por esas fuentes.

- **[S1]** Perplexity, [Getting Started with Comet](https://www.perplexity.ai/help-center/en/articles/11172798-getting-started-with-comet): base Chromium, extensiones y funciones generales.
- **[S2]** Perplexity, [modelos incluidos en las suscripciones](https://www.perplexity.ai/help-center/en/articles/10354919-what-advanced-ai-models-are-included-in-my-subscription): distinción de catálogos por producto/plan.
- **[S3]** BrowserOS, [repositorio oficial](https://github.com/browseros-ai/BrowserOS): estructura del proyecto, código y licencia declarada.
- **[S4]** BrowserOS, [Neo](https://www.browseros.com/neo) y [cómo funciona](https://docs.browseros.com/neo/how-it-works): sesiones, cuentas iniciadas, MCP, cockpit y replay.
- **[S5]** BrowserOS, [producto clásico](https://www.browseros.com/): agentes, memoria, proveedores y automatización.
- **[S6]** Chrome for Developers, [Side Panel API](https://developer.chrome.com/docs/extensions/reference/api/sidePanel): panel propio de extensión y límites de apertura.
- **[S7]** Chrome for Developers, [Native Messaging](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging): comunicación con procesos locales.
- **[S8]** Chrome for Developers, [Debugger API](https://developer.chrome.com/docs/extensions/reference/api/debugger): transporte CDP, permisos, restricciones y desconexión.
- **[S9]** Chrome for Developers, [ciclo de vida del service worker](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle): terminación y persistencia de estado.
- **[S10]** Chrome DevTools Protocol, [Accessibility](https://chromedevtools.github.io/devtools-protocol/tot/Accessibility/): árbol accesible y estados.
- **[S11]** Chrome DevTools Protocol, [DOMSnapshot](https://chromedevtools.github.io/devtools-protocol/tot/DOMSnapshot/): estructura, layout y estilos.
- **[S12]** Mozilla, [Readability README](https://github.com/mozilla/readability/blob/main/README.md): extracción de artículos sobre copia del DOM y límites heurísticos.
- **[S13]** Chrome DevTools Protocol, [Page](https://chromedevtools.github.io/devtools-protocol/tot/Page/): mecanismos de captura y capacidades del dominio.

Las referencias CDP `tot` siguen el protocolo en desarrollo. No asumir que todos sus métodos existen en la versión de Chromium de Comet: descubrir capacidades y fijar las utilizadas tras la prueba.

## 22. Checklist de entrega del propio plan

- [x] Petición original y límite de viabilidad documentados.
- [x] Comprobaciones reales separadas de hipótesis.
- [x] Alcance de Neo, BrowserOS clásico y Comet diferenciados.
- [x] Brainstorming de 42 mejoras con prioridad y comprobación.
- [x] Lectura, capturas, OCR, tablas, PDF, gráficos y listas largas desarrollados.
- [x] Arquitectura, conexiones de IA e interfaz especificadas.
- [x] Fases con criterios de salida y 36 escenarios de aceptación.
- [x] Evidencia, permisos, recuperación, rendimiento, instalación y mantenimiento incluidos.
- [x] Prompt de ejecución y fuentes primarias incluidos.
- [ ] Implementación: corresponde a un encargo posterior; no realizada en esta tarea.
- [ ] Prueba funcional de la integración en Comet: no realizada en esta tarea.
