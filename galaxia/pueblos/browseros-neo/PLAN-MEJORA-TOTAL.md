# Plan total para mejorar la visión y fiabilidad de BrowserOS Neo

Estado: planificación final para ejecutar en casa. Este documento no modifica la instalación actual.

Esta carpeta es un paquete portable de planificación, no un paquete ejecutable. Para ejecutar el plan harán falta el arnés completo o un kit independiente que se construirá en las fases descritas abajo. Los dos Markdown no prometen contener scripts, dependencias, perfil ni instalador.

## Decisión final

La arquitectura recomendada es:

1. BrowserOS Neo como único navegador persistente, dueño de los logins, pestañas y acciones.
2. MCP nativo de Neo como vía normal, barata y segura para operar.
3. Chrome DevTools MCP como inspector bajo demanda, conectado al CDP dinámico del mismo Neo.
4. Herramientas deterministas existentes para viewports, métricas, antes/después y comparación visual.
5. Un orquestador de evidencia que obligue a cruzar señales antes de afirmar que algo está bien o mal.

No se sustituye Neo por Stagehand, Playwright MCP, Claude in Chrome ni otro navegador. Esas opciones duplican capacidades, contexto o RAM. Stagehand queda como laboratorio futuro para flujos semánticos que realmente lo necesiten; Playwright se usa mediante CLI y skills donde aporte determinismo; Claude in Chrome no será el centro porque el navegador dedicado ya resuelve perfil, aislamiento y replay.

## Qué significa que la IA vea mejor

No significa enviar una captura más grande al modelo. Significa que cada afirmación importante se sostenga con las señales adecuadas:

| Pregunta | Señal principal | Confirmación |
|---|---|---|
| ¿Qué elemento es? | Snapshot accesible y DOM | Rol, nombre, estado, `aria` y selector |
| ¿Dónde está? | Cajas `getBoundingClientRect()` | Captura recortada y viewport verificado |
| ¿Se ve bien? | Captura visual | Métricas de geometría y comparación antes/después |
| ¿Funcionó el clic? | `diff` de la acción | Estado final, URL o respuesta de red |
| ¿Falló la página? | Consola y red | DOM final y captura no vacía |
| ¿Es un fallo real? | Dos vías independientes | Repetición con recursos sanos |
| ¿Quedó terminado? | Manifiesto de evidencias | Revisor adversarial de solo lectura |

## Principios innegociables

- Un solo Chromium persistente.
- El MCP nativo actúa; DevTools inspecciona por defecto y solo actúa como escotilla explícita.
- Cada agente usa sus propias pestañas y una sesión nombrada.
- El puerto se descubre desde la configuración y se valida con `/json/version`; nunca se fija a mano.
- CDP, MCP y servidor solo deben ser accesibles desde loopback.
- Nada de cookies, perfiles, cabeceras de autorización o secretos en logs, Markdown o contexto del modelo.
- Capturas recortadas por defecto; pantalla completa únicamente si la composición global lo exige.
- `NO MEDIDO`, carga incompleta o recursos saturados nunca cuentan como aprobado.
- No se corrige un defecto visual detectado por una sola señal.
- Cualquier integración nueva debe poder desactivarse sin alterar Neo.

## Arquitectura objetivo

```text
Agente
  |
  +-- Operación normal --> MCP nativo de Neo --> pestaña propia --> diff asentado
  |
  +-- Inspección puntual --> adaptador DevTools bajo demanda --> CDP dinámico de Neo
  |                         +-- captura recortada
  |                         +-- consola
  |                         +-- red
  |                         +-- snapshot/DOM
  |                         +-- trazas y Lighthouse cuando proceda
  |
  +-- QA determinista --> web-foto / web-gate / diff visual / sondas DOM
  |
  +-- Evidencia --> manifest.json + artefactos con hash + veredicto reproducible
```

El adaptador DevTools no arrancará Chrome. Se conectará al BrowserClaw existente mediante `--browser-url`. Como Chrome DevTools MCP solo garantiza soporte oficial para Chrome, la primera fase es una prueba de compatibilidad de lectura contra BrowserClaw; si falla, se conserva el CDP nativo y no se fuerza la integración.

## Estructura del kit futuro

La futura ejecución generará un paquete separado y versionado. No se crea en esta tarea:

```text
neo-vision-kit/
  README.md
  package.json
  package-lock.json
  bin/
    neo-preflight
    neo-inspect
    neo-evidence
  lib/
    discover-config
    ownership-broker
    devtools-readonly-proxy
    redact-network
    capture-validator
    resource-governor
  policy/
    devtools-readonly.json
  fixtures/
    static/
    react-input/
    shadow-modal/
    js-rendered/
    lazy-assets/
    expected.json
  tests/
  schemas/
    evidence-manifest.schema.json
```

El kit declarará sus dependencias del arnés. Si reutiliza `tools/claw/claw.py`, `tools/web-foto.py`, `tools/web-gate.py` o `tools/web-diff-visual.py`, comprobará que existen y que su versión es compatible; si no, fallará cerrado. La alternativa preferida para llevarlo sin todo el arnés será extraer únicamente la lógica necesaria y sus pruebas, sin copiar credenciales ni datos de cliente.

## Fase 0. Copia, inventario y reversibilidad

Objetivo: poder volver al estado anterior en minutos.

Trabajo:

1. Registrar versiones de Neo, Chromium, servidor, Node, Codex y Claude.
2. Copiar solo las configuraciones que se vayan a editar con `umask 077`, directorio 700 y ficheros 600; rechazar destinos o fuentes que sean enlaces simbólicos.
3. Guardar hashes antes y después.
4. Inventariar clientes MCP activos sin copiar sus secretos.
5. Registrar puertos actuales y comprobar qué interfaces escuchan.
6. Preparar un interruptor único para desactivar el inspector sin tocar Neo.

Gate de salida:

- Restauración ensayada sobre copias.
- Ningún perfil, cookie o secreto dentro del repositorio o paquete portable.
- Estado inicial documentado con hashes.

## Fase 1. Descubrimiento dinámico y preflight

Objetivo: eliminar puertos fijos, navegador fantasma y mediciones inválidas.

Se construirá un preflight pequeño que:

1. Localice la aplicación por su bundle verificado y resuelva su carpeta de datos; el path actual `~/Library/Application Support/BrowserClaw/.browseros/config.json` será un candidato, no una constante universal.
2. Extraiga `proxy`, `cdp` y `server` sin mostrar `install_id`.
3. Compruebe proceso, MCP y `GET /json/version`.
4. Verifique que la versión de Chromium declarada coincide con la respuesta CDP.
5. Compruebe que la pestaña objetivo pertenece a la sesión del agente.
6. Mida sesiones vivas, swap y presión de memoria.
7. Aborte con un motivo concreto si el entorno no es fiable.

El descubrimiento debe producir exactamente un `config.json` válido cuya versión coincida con la aplicación y cuyo CDP responda. Cero o varios candidatos válidos terminan en error explícito; no se elige por antigüedad, nombre parecido ni primer resultado.

Correcciones incluidas en la futura implementación:

- Sustituir los candidatos CDP antiguos del fallback de `tools/claw/claw.py` por descubrimiento seguro y validado.
- No confundir “MCP responde” con “navegador utilizable”.
- No arrancar Neo con un `--remote-debugging-port` adicional.

Gate de salida:

- Funciona tras tres reinicios consecutivos aunque cambie el puerto CDP.
- Falla cerrado si falta la configuración, el endpoint no es Chromium válido o hay demasiadas sesiones.
- No imprime datos sensibles.

## Fase 2. Inspector DevTools bajo demanda

Objetivo: añadir visión técnica profunda sin duplicar navegador.

Prototipo recomendado:

- `chrome-devtools-mcp@<versión-exacta-validada>` conectado mediante `--browser-url=http://127.0.0.1:<puerto-detectado>`; nunca `@latest` en la configuración persistida.
- Versión de Node, versión del paquete e integridad fijadas en `package-lock.json` después del smoke test.
- Estadísticas de uso desactivadas.
- Consulta CrUX desactivada por defecto para que las URLs no salgan del equipo durante trazas.
- Cabeceras de red sensibles redactadas.
- Capturas WebP o JPEG limitadas de tamaño para inspección; PNG solo para diff exacto.
- Arranque solo durante una inspección y cierre al terminar.
- Proxy local con allowlist cerrada; “solo lectura” será un control técnico, no una instrucción al modelo.

Allowlist expuesta al agente en modo inspector:

- `take_snapshot` y `take_screenshot`.
- `list_console_messages` y `get_console_message`.
- `list_network_requests` y `get_network_request`, siempre después de redacción.

El proxy rechazará navegación, creación o cierre de páginas, clic, teclado, formularios, subida, `evaluate_script`, emulación, extensiones, WebMCP, PWA, herramientas de terceros y heapsnapshots. Lighthouse y trazas quedarán fuera del modo normal y solo se habilitarán en una ejecución diagnóstica separada sobre una pestaña propia, porque pueden recargar, instrumentar o consumir muchos recursos.

### Vínculo de propiedad entre Neo y CDP

DevTools ve todos los targets del perfil y por sí solo no respeta la propiedad del MCP de Neo. Antes de exponer una página al inspector se aplicará este contrato:

1. Neo crea la pestaña desde la sesión nombrada y devuelve su identificador de página.
2. Neo escribe en esa pestaña una propiedad efímera no enumerable con clave y nonce aleatorios.
3. El broker interno recorre los targets CDP y solo lee esa propiedad mediante una expresión fija, no suministrada por el modelo.
4. Debe existir exactamente un target coincidente.
5. Se guarda el vínculo temporal `{sesion_neo, pagina_neo, targetId, nonce}`.
6. El proxy DevTools solo acepta ese `targetId`; ni siquiera expone al modelo la lista completa de pestañas.
7. Neo elimina la marca al cerrar la inspección.

Si Neo no puede escribir o retirar la marca, si aparecen cero o varios targets, o si cambia el target durante el flujo, el inspector se desactiva y el resultado es `NO_MEDIDO`. Seleccionar por URL, título o pestaña activa queda prohibido.

Prueba de compatibilidad obligatoria:

1. Listar la misma pestaña que ve Neo.
2. Tomar snapshot sin navegarla.
3. Tomar una captura recortada.
4. Leer consola y red.
5. Confirmar que no abre otra ventana ni otro perfil.
6. Intentar deliberadamente una herramienta bloqueada y exigir rechazo.
7. Intentar apuntar a una pestaña ajena y exigir rechazo antes de revelar URL, título o contenido.
8. Cerrar el inspector y comprobar que Neo sigue funcionando.

Si una de esas pruebas falla por ser BrowserClaw y no Chrome oficialmente soportado, no se parchea Neo. Se usa su CDP directo con una capa propia mínima para esas lecturas.

Gate de salida:

- Cero Chromium adicional.
- Mismo vínculo verificable sesión-página-target antes y después; URL y `targetId` solos no prueban propiedad.
- Neo conserva logins, historial, replay y propiedad de pestañas.
- Inspector apagado al finalizar.

## Fase 3. Protocolo de observación multisensor

Objetivo: que el agente no saque conclusiones visuales de una sola fuente.

Antes de actuar:

1. Confirmar URL, título, viewport, escala y pestaña propia.
2. Esperar `document.fonts.ready`.
3. Esperar a que las imágenes visibles tengan `complete` y `naturalWidth > 0`.
4. Esperar contenido real en rejillas que se rellenan por JavaScript.
5. Registrar errores de consola y peticiones fallidas iniciales.
6. Tomar snapshot accesible únicamente del área relevante.
7. Obtener geometría de objetivo y contenedores ascendentes.
8. Tomar una captura recortada con margen alrededor del objetivo.

Después de actuar:

1. Leer el `diff` asentado de Neo.
2. Verificar estado final por DOM, no por ausencia de error.
3. Verificar URL, texto visible o respuesta de red esperada.
4. Tomar una segunda captura solo si el cambio es visual.
5. Comparar consola y red antes/después.
6. Guardar evidencia mínima y descartar datos sensibles.

Regla de decisión:

- Acción funcional: dos señales concordantes.
- Afirmación visual: captura más geometría o captura más diff estable.
- Fallo crítico: reproducción en una sesión limpia o una segunda vía independiente.

Gate de salida:

- Diez flujos de prueba variados completados sin reutilizar referencias caducadas ni pestañas ajenas.
- Ningún aprobado basado solo en “la herramienta no dio error”.

## Fase 4. Captura visual fiable

Objetivo: imágenes pequeñas, comparables y libres de defectos fantasma.

Viewports base:

- 390 px: móvil.
- 768 px: tableta.
- 1024 px: transición crítica.
- 1440 px: escritorio.

Para cada viewport:

1. Fijar el tamaño después de cada navegación.
2. Verificar `document.documentElement.clientWidth`.
3. Comprobar que el ancho real de la captura coincide.
4. Detectar scroll horizontal antes de recortar.
5. Desactivar animaciones para comparación, no para prueba funcional.
6. Calentar imágenes y esperar fuentes.
7. Capturar por regiones solapadas si la página es larga.
8. Generar miniatura de navegación y recortes originales para el detalle.
9. Usar PNG para diffs y WebP/JPEG para contexto del modelo.
10. Calcular histograma, entropía y porcentaje de píxeles uniformes como señal de alerta, nunca como veredicto único.

Una imagen blanca o minimalista solo se rechaza si además falla su oráculo: URL final, DOM o texto esperado, paint timing, recursos requeridos o dimensiones. Una página deliberadamente blanca puede ser válida y debe existir como fixture de control positivo.

No se automatizará un veredicto final solo con diferencia de píxeles. Se distinguirán cambios de posición, cambios de contenido y ruido de render, y una persona o un revisor visual deberá mirar el montaje cuando el resultado sea crítico.

Gate de salida:

- Misma página repetida tres veces produce geometría estable dentro de tolerancia.
- Una captura sospechosa no puede aprobar el flujo hasta que sus oráculos independientes confirmen si es válida o incompleta.
- Los cuatro viewports quedan identificados dentro del propio manifiesto.

## Fase 5. Consola, red, accesibilidad y rendimiento

Objetivo: explicar por qué algo se ve o funciona mal.

Se recogerá, de forma selectiva:

- Errores y advertencias nuevas de consola con origen y stack cuando exista.
- Peticiones fallidas, bloqueadas o lentas; cabeceras sensibles siempre redactadas.
- Estado de navegación, redirects y código HTTP final.
- Árbol accesible, nombre, rol, estado, foco y orden de tabulación del flujo probado.
- Lighthouse solo en auditorías que lo pidan, separado de fidelidad visual.
- Traza de rendimiento solo para un problema concreto, con CrUX desactivado por defecto.
- Heap snapshot únicamente para fugas de memoria reproducibles, nunca como rutina.

Gate de salida:

- Cada error técnico apunta a una petición, mensaje o nodo concreto.
- No se vuelcan cookies, `Authorization`, formularios ni contenido privado al contexto.
- Una mala puntuación de rendimiento no se presenta como defecto visual y viceversa.

## Fase 6. Interacción robusta

Objetivo: evitar clics que “funcionaron” sin cambiar nada y escrituras corruptas.

Reglas implementables:

- `fill` solo en campos comprobados como vacíos.
- Para React con valor previo: setter nativo más evento `input`, seguido de lectura del valor real.
- Re-snapshot después de navegación o re-render; nunca reutilizar referencias.
- Para componentes que ignoran `element.click()`: clic físico por coordenadas del rectángulo actual.
- En CDP directo: `Page.bringToFront` antes de teclado o puntero.
- Capturar el payload de red o el estado persistido cuando un toast desaparece demasiado rápido.
- Antes de enviar, comprar, borrar o tocar producción: guardarraíl y autorización explícita.

Gate de salida:

- Suite con input vacío, input React ocupado, modal, pestaña en segundo plano, navegación y re-render.
- El valor enviado coincide exactamente con el valor esperado.

## Fase 7. Gobernador de recursos

Objetivo: que la IA no confunda saturación con un fallo de la web.

El gobernador:

1. Cuenta sesiones reales, no procesos envoltorio.
2. Impide iniciar QA si ya hay tres sesiones.
3. Registra swap y presión antes y después.
4. Cierra solo pestañas y procesos creados por el flujo.
5. Serializa capturas pesadas e inspecciones DevTools.
6. Degrada de captura a DOM y red cuando solo se necesita diagnóstico técnico.
7. Marca el resultado `NO MEDIDO` si el render se produjo bajo saturación.

Gate de salida:

- Ningún fan-out de navegadores.
- Ninguna pestaña de Darío u otro agente cerrada o navegada.
- Un gate interrumpido libera sus recursos sin matar Neo.

## Fase 8. Evidencia y veredicto reproducible

Objetivo: que “está bien” tenga prueba y se pueda revisar después.

Cada ejecución producirá una carpeta temporal con:

- `manifest.json`: fecha, URL final, versión, viewport, sesión, target, estado de recursos y checks.
- Snapshot accesible recortado o resumen estructurado.
- Capturas relevantes con SHA-256.
- Resumen de consola y red ya redactado.
- Métricas DOM y geometría.
- Resultado antes/después cuando exista cambio.
- Veredicto `PASS`, `FAIL` o `NO_MEDIDO` y la razón concreta.

La evidencia privada tendrá caducidad y no se meterá en Git por defecto. Los artefactos de cliente se guardarán solo donde indique el proyecto y con la política de datos correspondiente.

Gate de salida:

- Otro proceso puede verificar hashes y repetir el caso con el manifiesto.
- Un revisor adversarial de solo lectura puede confirmar o refutar el veredicto sin usar la explicación del ejecutor.

## Fase 9. Pruebas de aceptación

La suite usará fixtures locales versionados. Cada fixture declarará en `expected.json`: URL, estado inicial, acción, estado final, selectores o roles esperados, peticiones permitidas, errores provocados, viewports, tolerancia geométrica y hashes de las referencias cuando corresponda. Sin ese contrato, una ejecución solo puede ser exploratoria y no puede aprobar el sistema.

Matriz mínima:

1. Página pública estática.
2. SPA React con input controlado.
3. Panel con login ya iniciado.
4. Modal y menú en shadow DOM.
5. Página con imágenes lazy y fuentes web.
6. Página con contenido pintado por JavaScript.
7. Flujo con redirect y petición fallida.
8. Responsive en 390, 768, 1024 y 1440.
9. Dos casos distintos: página blanca válida y render incompleto inválido, cada uno con oráculo explícito.
10. Dos agentes con pestañas separadas para comprobar propiedad.
11. Reinicio de Neo con cambio de puerto CDP.
12. Saturación simulada que debe terminar en `NO_MEDIDO`, no en falso fallo.

Criterio de aprobación total:

- Todas las pruebas críticas pasan tres veces consecutivas.
- Cero secretos en artefactos y logs.
- Cero navegación o cierre de pestañas ajenas.
- Cero navegadores duplicados.
- Todos los fallos provocados son detectados.
- Todos los escenarios no medibles quedan explícitamente como `NO_MEDIDO`.
- Rollback ejecutado una vez con éxito.

No se prometerá “cero errores” como frase absoluta. Se entregará un sistema con gates definidos, fallos provocados, repetición y revisión independiente; eso es verificable.

## Orden de ejecución recomendado

| Orden | Entrega | Prioridad | Riesgo |
|---|---|---|---|
| 1 | Preflight y descubrimiento dinámico | Crítica | Bajo |
| 2 | Prueba DevTools de solo lectura | Crítica | Medio por compatibilidad Chromium |
| 3 | Gobernador de sesiones y RAM | Crítica | Bajo |
| 4 | Protocolo snapshot + DOM + captura | Alta | Bajo |
| 5 | Captura fiable y detector de imagen inválida | Alta | Medio |
| 6 | Consola y red redactadas | Alta | Medio por privacidad |
| 7 | Interacción robusta | Alta | Medio |
| 8 | Manifiesto y hashes | Alta | Bajo |
| 9 | Matriz de aceptación y revisión adversarial | Crítica | Bajo |
| 10 | Documentación de instalación y rollback | Crítica | Bajo |

## Opciones evaluadas

### Chrome DevTools MCP: elegido como inspector condicionado

Ventajas:

- Se conecta a un navegador existente por `--browser-url`.
- Expone captura, snapshot, consola, red, Lighthouse, trazas y memoria.
- Permite comprimir y limitar capturas.

Condición:

- BrowserClaw es Chromium y el soporte oficial declarado es Chrome. Se adopta solo si el smoke test contra la versión instalada pasa sin alterar Neo.

### CDP nativo: fallback obligatorio

Ventajas:

- Ya existe, no añade dependencias y controla exactamente el mismo navegador.
- Permite `Page`, `Runtime`, `Network`, `DOM` e `Input`.

Coste:

- Hay que construir la capa de redacción, selección de target, timeouts y evidencias que DevTools MCP ya aporta.

### Playwright MCP: no elegido como segunda capa permanente

- Duplica buena parte del árbol accesible y la automatización de Neo.
- Su propio proyecto recomienda CLI + skills a agentes de código cuando importa el coste de contexto.
- Playwright CLI sigue siendo útil para QA determinista y reutilizar las herramientas existentes.

### Stagehand: reservado

- Puede conectarse a un Chromium existente por CDP.
- Añade otra abstracción semántica, dependencia de modelos y posible coste de API.
- Solo se probará si existen flujos donde las acciones nativas y deterministas no sean suficientes.

### Claude in Chrome: no elegido como núcleo

- Añade otra superficie de control sobre un problema que Neo ya resuelve.
- El objetivo es que Claude, Codex y otros agentes compartan el mismo navegador dedicado mediante MCP, no depender de una extensión concreta.

## Seguridad antes de usarlo en casa

1. Usar `lsof` como precheck y fallar si un listener aparece en `*`, `0.0.0.0` o `::`; confirmar además la inaccesibilidad desde otra máquina de la LAN o una prueba de red equivalente controlada.
2. Investigar por qué 9010 y 9011 aparecen en todas las interfaces pese a `allow_remote_in_mcp=false`.
3. No exponer, reenviar ni tunelizar CDP.
4. Desactivar estadísticas de Chrome DevTools MCP.
5. Desactivar CrUX por defecto.
6. Activar redacción de cabeceras de red.
7. Restringir escrituras del inspector a una carpeta temporal.
8. No copiar el perfil de este Mac dentro de la carpeta portable.
9. Iniciar sesión o importar desde Chrome mediante el flujo oficial en el equipo de destino.
10. Mantener secretos únicamente en el vault del equipo de destino.

## Traslado a casa

Esta carpeta contiene solo documentación y se puede copiar después de revisar sus hashes y repetir el escaneo de secretos. No basta por sí sola para ejecutar el sistema.

En el equipo de casa:

1. Instalar o actualizar BrowserOS Neo desde su fuente oficial.
2. Abrirlo y conectar el agente mediante MCP.
3. Importar sesiones de forma interactiva; no usar una copia de esta carpeta como perfil.
4. Llevar el arnés completo o construir el `neo-vision-kit` independiente descrito arriba; verificar todas sus dependencias antes de continuar.
5. Ejecutar el inventario y generar una fotografía nueva: rutas, versiones y puertos pueden cambiar.
6. Aplicar las fases en el orden indicado.
7. No añadir DevTools MCP de forma permanente hasta que pase su smoke test.
8. Ejecutar toda la matriz de aceptación.
9. Guardar el informe final, hashes y procedimiento de rollback.

## Rollback previsto

Si la mejora falla:

1. Parar el inspector DevTools.
2. Retirar únicamente su entrada MCP o wrapper.
3. Restaurar las configuraciones modificadas desde la copia con hash.
4. Reiniciar el cliente agente, no el perfil de Neo.
5. Verificar MCP nativo, pestaña propia, snapshot, acción y diff.
6. Confirmar que logins, pestañas y replay siguen intactos.

Neo no se desinstala, no se borra su perfil y no se toca ninguna sesión como parte del rollback.

## Entregable final esperado al terminar la futura ejecución

- Integración reversible y documentada.
- Preflight dinámico.
- Inspector bajo demanda o fallback CDP nativo.
- Skill de observación multisensor.
- Gobernador de recursos.
- Captura fiable con detección de imagen inválida.
- Redacción de datos sensibles.
- Manifiesto de evidencia con hashes.
- Suite de aceptación completa.
- Informe adversarial independiente.
- Manual de instalación, uso y rollback para el equipo de casa.

## Fuentes primarias

- [BrowserOS Neo](https://browseros.ai/neo/)
- [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Stagehand v4: Browser y CDP](https://docs.stagehand.dev/v4/configuration/browser#connecting-over-cdp)
