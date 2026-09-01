# Las 23 huerfanas de la cosecha: entran o se van — cierre

Fecha: 2026-09-01 · Arbol: `galaxia/` · Config: `galaxia.toml` · Cierra el hueco que dejo
[`integracion-cosecha.md`](integracion-cosecha.md).

**Estado fijado** (el arbol muta mientras se escribe): base `243ec87`, arbol sin commitear, 20
ficheros sucios al empezar. Al cerrar: **199 pueblos**, `cosecha/` con **73 ficheros** (eran 79).

El hueco: de los 79 ficheros de `cosecha/`, 56 tenian pueblo y **23 no**. Estaban en el repositorio
sin estar en el mapa — ni se usan ni se encuentran. Se cierran los 23 sin tercera opcion: **17
entran** (en 10 pueblos nuevos y 1 ampliado) y **6 se borran**.

## 1. La tabla de las 23

| Fichero | Decision | Nicho / motivo |
|---|---|---|
| `audit-harness.sh` | entra | `agentes-ia/construccion` → **plan-auditado** |
| `codex-delegate.sh` | entra | `agentes-ia/construccion` → **delegar-generacion** |
| `codex-handler.sh` | entra | `agentes-ia/construccion` → **delegar-generacion** |
| `claude-cuenta.sh` | entra | `agentes-ia/coste` → **cuentas-del-asistente** |
| `mantener-sesiones-claude.sh` | entra | `agentes-ia/coste` → **cuentas-del-asistente** |
| `reap-claude-orphans.sh` | entra | `agentes-ia/coste` → **cuentas-del-asistente** |
| `semble-doctor.sh` | entra | `agentes-ia/coste` → **codigo-al-modelo** |
| `repomix-pack.sh` | entra | `agentes-ia/coste` → **codigo-al-modelo** |
| `cc-history.sh` | entra | `agentes-ia/coste` → **medir-contexto** (pueblo ya existente, ampliado) |
| `multi-review.py` | entra | `agentes-ia/evaluacion` → **revision-cruzada** |
| `dedupe-daily-autocapture.py` | entra | `agentes-ia/memoria` → **diario-sin-duplicados** |
| `mandar-a-terminales.py` | entra | `agentes-ia/herramientas` → **ordenes-entre-ventanas** |
| `google-chat-dm.py` | entra | `automatizacion` → **aviso-por-chat** |
| `google-chat-oauth-notify.js` | entra | `automatizacion` → **aviso-por-chat** |
| `domain-suggester.py` | entra | `web/construccion-de-sitios` → **dominios-libres** |
| `wp-mcp-sync.py` | entra | `web/construccion-de-sitios` → **elementor-mcp** |
| `wp-mcp-stdio-bridge.sh` | entra | `web/construccion-de-sitios` → **elementor-mcp** |
| `setup-mac.sh` | **borrada** | Configuracion personal de un Mac concreto: instala un monitor y un actualizador, programa su agente de arranque y termina en pasos manuales de sus Ajustes. No es un oficio. |
| `install-modifier-swap.sh` | **borrada** | Intercambia dos teclas modificadoras en un teclado externo concreto. Preferencia personal de una maquina. |
| `actualizacion-nocturna-mac.sh` | **borrada** | Despierta un ordenador de sobremesa a las 03:00 y activa sus actualizaciones automaticas. Mantenimiento de una maquina personal, con `sudo`. Su unica idea transferible —no actualizar sin copia verificada— ya vive en el nicho de infraestructura. |
| `auto_resume.ps1` | **borrada** | PowerShell de Windows: envia teclas al editor a una hora fija. Depende de infraestructura que aqui no existe, y su hueco —teclear en la ventana interactiva— lo cubre mejor `ordenes-entre-ventanas`, que ademas sabe no escribirse a si mismo. |
| `install-open-interpreter-macos` | **borrada** | Instalador personal de un interprete agentico de terceros, atado a una clave de un proveedor externo. Su hueco —un agente que ejecuta en la maquina— ya tiene dueno publico en `openclaw`, con adopcion incomparable. |
| `clean-gone-branches.sh` | **borrada** | Borra ramas locales cuyo remoto desaparecio. Es un `for-each-ref` con un `awk`: conocimiento que un modelo bueno ya tiene (regla de admision 1). Y no tiene dueno — no hay pais de control de versiones en los 21 nichos, y crear uno para 30 lineas es el nivel de relleno que la taxonomia prohibe (regla 3). |

## 2. Los 10 pueblos nuevos

| Pueblo | Padre | Que aporta que no estaba |
|---|---|---|
| `cuentas-del-asistente` | `agentes-ia/coste` | De **que** cuenta sale la cuota, que ninguna caduque, y matar los restos que llenan la memoria |
| `codigo-al-modelo` | `agentes-ia/coste` | Como se le da codigo a un modelo: fragmento por intencion, o repositorio entero solo si no puede abrir ficheros |
| `medir-contexto` *(ampliado)* | `agentes-ia/coste` | Tercera lectura de las transcripciones: los comandos que se ejecutaron de verdad |
| `plan-auditado` | `agentes-ia/construccion` | Valida el plan como contrato y exige rastro de lo que dice estar hecho |
| `delegar-generacion` | `agentes-ia/construccion` | Un modelo redacta el encargo, otro teclea; el prompt se ve antes de correr |
| `revision-cruzada` | `agentes-ia/evaluacion` | Tres familias de modelos a la vez; el desacuerdo es la senal y sale por codigo de salida |
| `diario-sin-duplicados` | `agentes-ia/memoria` | Limpieza destructiva que **prueba** antes de escribir que no destruyo lo escrito a mano |
| `ordenes-entre-ventanas` | `agentes-ia/herramientas` | Las ordenes que solo existen dentro de la interfaz interactiva, y el registro de lo que NO funciona |
| `aviso-por-chat` | `automatizacion` | Aviso en el chat donde el equipo ya esta, por cuenta de servicio o por permiso de usuario |
| `dominios-libres` | `web/construccion-de-sitios` | Disponibilidad de dominio con tres fuentes publicas y un tercer estado: *incierto* |
| `elementor-mcp` | `web/construccion-de-sitios` | Controles nativos del maquetador como herramientas, tambien con PHP viejo en el servidor |

Ningun pais nuevo: los 17 ficheros caben en paises que ya existian. Un pais con un solo hijo es
fuga pura, y aqui no hacia falta ninguno.

## 3. Las que costo decidir — y por que

Esto es lo que hace falta para revisarme.

**`clean-gone-branches.sh` (borrada).** La mas discutible de las seis. No esta muerta, no es
personal, no depende de nada raro y hace lo que promete con `--dry-run` por defecto. Se cae por dos
reglas distintas y ninguna sola habria bastado: es conocimiento que un modelo bueno ya tiene (dos
comandos nativos), y **no tiene padre** en el mapa — no hay nicho ni pais de control de versiones, y
fabricar uno para un guion de 30 lineas es exactamente el nivel de relleno que la taxonomia prohibe.
Si algun dia entra un pais de control de versiones, este guion es candidato legitimo a volver.

**`repomix-pack.sh` (entra, pero incomoda).** Empaqueta un repositorio entero en un documento: es lo
contrario de la tesis de este proyecto. Entra porque su hueco existe y es real —un modelo que **no
puede abrir ficheros**— y porque emparejado con la busqueda semantica en el mismo pueblo, la regla
de eleccion queda escrita: si el que lee puede abrir ficheros, fragmento; si no, paquete. Suelto y
sin esa frase habria sido una invitacion a volcar el repositorio por comodidad.

**`multi-review.py` (entra, con reserva).** Necesita una clave de un enrutador de modelos. Pasa el
coste cero porque los modelos que usa son de capa gratuita y no piden tarjeta, pero es la unica
herramienta de esta tanda que depende de darse de alta en algo. Ademas trae identificadores de
modelo escritos a mano que envejecen en semanas. Se admite porque el mecanismo —tres familias que no
comparten entrenamiento, y el **desacuerdo** como senal, no la opinion— sobrevive al cambio de
modelos; el pueblo lo dice explicitamente para que nadie confunda la lista con la idea.

**`mandar-a-terminales.py` (entra).** Muy atado a un sistema operativo y a un editor, y por eso casi
se va. Lo salva que su valor no es el guion sino el registro de **lo que no funciona, comprobado**:
escribir al dispositivo de terminal va a su salida y no a la entrada del proceso, el mecanismo del
sistema para inyectar teclas esta denegado, y el arbol de accesibilidad del editor no dice que
terminal tiene el foco. Eso es una tarde de trabajo que no hay que repetir.

**`aviso-por-chat` frente a `ntfy` (no es duplicado).** `ntfy` ya tiene pueblo y tambien notifica.
Se separan porque el destinatario es distinto: `ntfy` avisa al movil de quien se suscribe a su
servicio; esto llega a la herramienta de trabajo donde el equipo ya esta, sin pedirle que instale
nada. Queda dicho en el resumen del pueblo nuevo, que es donde tiene que estar.

**`elementor-mcp` frente a `wp-remoto` (no es duplicado).** Ambos entran al mismo tipo de sitio por
la misma conexion. `wp-remoto` da consola y SQL; esto expone los **controles nativos** del maquetador
como herramientas, que es la diferencia entre editar por la puerta buena y escribir a mano la
estructura interna serializada. Son dos capas del mismo sitio, no dos formas de lo mismo.

**`cc-history.sh` (entra, sin linea de catalogo propia).** Son dos lineas de envoltorio. Habria sido
un pueblo caro por lo que aporta, asi que se suma a `medir-contexto`, que ya leia esas mismas
transcripciones para otras dos cosas. El resumen de ese pueblo se reescribio para que las cubra a
las tres — no se le colgo un fichero por debajo sin decirlo arriba, que es como un resumen empieza a
mentir.

## 4. Limpieza de datos

Un unico hallazgo: `mantener-sesiones-claude.sh` citaba por su nombre a la persona que dio la orden.
**Limpiado** — la cita se atribuye ahora a la casa. Barrido del resto de los 23 (nombres, correos,
dominios de cliente, IP, claves, tokens): sin mas resultados.

## 5. Verificacion — obligatoria y pegada

```
$ python3 -m cosmos generar galaxia --config galaxia.toml
COSMOS  generar  verde

$ python3 -m cosmos validar galaxia --config galaxia.toml
COSMOS  verde  0 errores

$ python3 -m cosmos medir galaxia --config galaxia.toml
  Entrada base .... 1.128 tokens
  Peor nicho ...... 1.771 tokens   (ciberseguridad, 26 pueblos)
  Universo ........ 22.103 tokens
  Descarga ........ 92,0 %
  Presupuesto ..... 4.000     OK, quedan 2.229 tokens en el peor caso
```

**Base y peor nicho, identicos a antes de esta tanda** (1.128 y 1.771): los 10 pueblos nuevos no
tocan el catalogo de entrada ni empeoran el peor caso, que sigue siendo `ciberseguridad`. La
descarga sube de **91,1 % a 92,0 %** — mas sistema disponible sin estar cargado, que es el numero
que esta tanda tenia que mover.

**Nota de proceso, para el siguiente**: la primera pasada de `validar` salio **roja** con cuatro
`E19` (*vista plana desincronizada*). No era un fallo del arbol: al crear pueblos hay que ejecutar
`cosmos compilar` antes de `validar`, o el manifiesto de la vista plana no los conoce. Con el
compilado en medio, verde a la primera.

### Ningun fichero de `cosecha/` queda sin pueblo

```
$ for f in cosecha/*; do b=$(basename "$f"); [ "$b" = "__pycache__" ] && continue; \
    grep -rqF "$b" galaxia/ || echo "SIN CLASIFICAR: $b"; done
--- SIN CLASIFICAR ---
--- fin (vacio = todo clasificado) ---
```

Salida vacia: **los 73 ficheros que quedan en `cosecha/` estan en el mapa**. Era el objetivo del
encargo y es la unica comprobacion que lo demuestra.
