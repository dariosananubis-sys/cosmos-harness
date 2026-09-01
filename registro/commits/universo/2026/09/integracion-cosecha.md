# Integracion de la cosecha propia y relleno de nichos flacos — tanda 3

Fecha: 2026-09-01 · Arbol: `galaxia/` · Config: `galaxia.toml` · Continua `montaje-tanda-1.md` y
`montaje-tanda-2.md`, con su misma regla de admision.

**Estado fijado, porque el arbol muta mientras se escribe**: base `b9e46b7`, arbol sin commitear.
Habia **otros dos trabajos en curso sobre el mismo arbol** —uno en `galaxia/estrellas/` y otro
poblando `trading`, que paso de 5 a 22 pueblos mientras corria este—. Todo lo que este parte afirma
esta escrito como **delta propio** (que anadi yo) y no como total del arbol, que cambia cada pocos
minutos y no es mio. Las dos mediciones de §6 llevan su marca de momento.

Dos encargos en uno: meter en el mapa las 79 herramientas propias de `cosecha/`, que estaban en el
repositorio sin estar en el arbol —hoy no las encontraria nadie—, y rellenar los nichos flacos con lo
mejor que los barridos dejaron fuera **por presupuesto**, ahora que el catalogo se sirve por nicho.

## 1. Que quedo montado

| | Antes de esta tanda | Al cerrarla | Delta mio |
|---|---:|---:|---:|
| pueblos | 127 | 172 | **+45** |
| paises | 54 | 55 | +1 (`agentes-ia/coste`) |
| sistemas solares | 21 | 21 | 0 |
| estrellas, mares, oceanos | — | — | 0 (no tocados) |

La columna del medio es el arbol **en el momento en que termine**. Al cerrar el parte ya iba por 189
pueblos y 56 paises: la diferencia es la tanda de `trading`, que no es mia. El delta de la derecha si
lo es, y es el que hay que leer.

**+20 pueblos de herramienta propia** (42 de los 79 ficheros de `cosecha/`) y **+25 pueblos
publicos** rescatados de los barridos.

### Reparto por nicho

| Nicho | Antes | Ahora | Que entro |
|---|---:|---:|---|
| `ciberseguridad` | 26 | 26 | **nada, a proposito**: es el peor nicho y el techo del presupuesto |
| `web` | 10 | 13 | propias: `wp-remoto`, `wp-app-password`, `catalogo-woocommerce` |
| `agentes-ia` | 6 | 13 | propias: `quota-oficial`, `medir-contexto`, `auditar-gasto`, `lanzadores-de-modelo`, `captura-recortada`, `mcp-call`, `alcance-y-excepcion` |
| `automatizacion` | 7 | 10 | propia: `correo-smtp` · publicas: `node-red`, `rpaframework` |
| `infraestructura` | 7 | 9 | propias: `contenedor-efimero`, `acceso-remoto` |
| `documentos` | 8 | 9 | publica: `diagrams` |
| `rendimiento` | 3 | 8 | publicas: `hyperfine`, `sanitizers`, `mimalloc`, `bpftrace`, `py-spy` |
| `embebidos` | 4 | 8 | publicas: `micropython`, `freertos`, `probe-rs`, `mosquitto` |
| `blockchain` | 4 | 8 | publicas: `viem`, `anchor`, `ponder`, `mythril` |
| `visibilidad` | 5 | 7 | propias: `search-console`, `bing-webmaster` |
| `juegos` | 4 | 7 | publicas: `raylib`, `tiled`, `miniaudio` |
| `cientifico` | 4 | 7 | publicas: `dask`, `hydra`, `reprozip` |
| `saas` | 4 | 6 | propias: `panel-auth-cookie`, `validadores-frontera` |
| `moviles` | 4 | 6 | publicas: `expo`, `rxdb` |
| `cumplimiento` | 4 | 6 | propias: `paginas-legales`, `cookies-declaradas` |
| `modelos-locales` | 4 | 5 | publica: `lm-evaluation-harness` |
| `extraccion` · `trading` | 7 · 5 | 7 · 5 | nada: no estaban flacos y sus barridos ya se vaciaron |
| `ingenieria-datos` · `audiovisual` · `analitica` | 4 · 3 · 4 | 4 · 4 · 4 | `audiovisual` gana la propia `reel-a-texto`; los otros dos, nada — ver §5.3 |

**El peor nicho no se ha movido**: sigue siendo `ciberseguridad` con 26 pueblos. Como E16 se evalua
contra el peor nicho, engordar los otros veinte no ha costado ni un token de veredicto. Ningun nicho
al que haya tocado pasa de 13; el techo de ~25 herramientas por nicho queda intacto y con margen.

### El pais nuevo, y por que solo uno

`agentes-ia/coste` agrupa cinco pueblos que responden a la misma pregunta —cuanto cuesta esta sesion
y como baja—: `quota-oficial`, `medir-contexto`, `auditar-gasto`, `lanzadores-de-modelo` y
`captura-recortada`. Es el unico nivel intermedio creado: un pais se paga en la entrada de **todos**
los nichos (su linea sale siempre en el catalogo), asi que cada uno tiene que agrupar de verdad. Los
otros 44 pueblos colgaron de paises que ya existian o directamente de su sistema solar, que la spec
permite y que evita el nivel de relleno.

## 2. La cosecha: 20 pueblos, 42 ficheros de 79

| Pueblo | Padre | Ficheros de `cosecha/` |
|---|---|---|
| `panel-auth-cookie` | `saas` | `docker-secret-cookie-auth.js` |
| `validadores-frontera` | `saas` | `input-validators.js`, `nif-cif-validator.js` |
| `contenedor-efimero` | `infraestructura` | `docker-ephemeral-runner.js`, `docker-wait-with-timeout.js`, `docker-job-log-markers.js`, `docker-orphan-container-cleanup.js`, `pg-secret-file-connection.js` |
| `acceso-remoto` | `infraestructura/servidores` | `acceso-remoto-watchdog.sh` |
| `wp-remoto` | `web/construccion-de-sitios` | `wp-ssh.sh`, `wp_sql.py`, `wpcli-remote.sh` |
| `wp-app-password` | `web/construccion-de-sitios` | `bootstrap-app-pass.py`, `save-app-pass.py`, `wp-rest-base.js` |
| `catalogo-woocommerce` | `web/comercio-electronico` | `woocommerce-verificar-catalogo.py` |
| `quota-oficial` | `agentes-ia/coste` | `quota-oficial.py`, `quota-peak.py` |
| `medir-contexto` | `agentes-ia/coste` | `medir-contexto-claude.py`, `barrido-transcripts.py` |
| `auditar-gasto` | `agentes-ia/coste` | `auditar-gasto.py` |
| `lanzadores-de-modelo` | `agentes-ia/coste` | `claude-code/` (8 ficheros), `modelos-fijar.py` |
| `captura-recortada` | `agentes-ia/coste` | `captura-ventana.py`, `foto-cuadrar.py` |
| `mcp-call` | `agentes-ia/herramientas` | `mcp-call.py` |
| `alcance-y-excepcion` | `agentes-ia` | `alcance.py`, `excepcion-codigo.py` |
| `search-console` | `visibilidad` | `gsc-search-console.py`, `gsc-service-account-token.js`, `log.py` |
| `bing-webmaster` | `visibilidad` | `bing-webmaster.py` |
| `paginas-legales` | `cumplimiento` | `legales-crear-paginas.py`, `legales-lssi.py`, `legales-texto.py` |
| `cookies-declaradas` | `cumplimiento` | `cookies_catalogo.py`, `legales-bloque-cookies.py`, `legales-bloque-rest.py`, `legales-cookies-complianz.py`, `legales-purga-servicios-complianz.py` |
| `correo-smtp` | `automatizacion` | `enviar-correo-smtp.py` |
| `reel-a-texto` | `audiovisual/video` | `analyze-reel.sh`, `extract_frames.py`, `ig-dl.sh` |

Criterio de agrupacion: **un pueblo por trabajo, no por fichero**. Los cinco ficheros del contenedor
efimero son un solo mecanismo con cinco piezas; separarlos habria dado cinco lineas de catalogo para
una sola decision. Al reves tambien: `paginas-legales` y `cookies-declaradas` salen del mismo
directorio y son dos trabajos distintos —lo que la web tiene que decir, y que terceros carga de
verdad—, asi que son dos pueblos.

**Comprobado**: 56 de los 79 ficheros de `cosecha/` estan citados por ruta literal en algun nodo del
arbol (42 como contenido de un pueblo, 14 nombrados en el cuerpo del pueblo que les gano el hueco).
Verificable con `for f in $(ls cosecha); do grep -rqF "cosecha/$f" galaxia/ || echo "$f"; done`.

## 3. Que descarte de la cosecha, y por que

**23 ficheros no entran ni se citan.** Ninguno por mala calidad: por no tener hueco propio.

### A. Dependencia de un servicio o modelo de pago — criterio 3 (4)

`codex-delegate.sh`, `codex-handler.sh` y `multi-review.py` delegan la generacion o la revision de
codigo a modelos de terceros. Aqui funcionan porque hay suscripciones ya pagadas detras; para
cualquier otro, entrar en el catalogo significaria "instala esto y paga aquello". La regla de
admision no admite matices ahi. `install-open-interpreter-macos` cae por lo mismo: instala un
intermediario que pide clave de un proveedor.

### B. Envoltorio de una herramienta que no esta en el arbol (5)

`repomix-pack.sh`, `semble-doctor.sh`, `cc-history.sh`, `patch-claude-mem-hooks.sh` (este si citado,
en el cuerpo de `claude-mem`) y `audit-harness.sh`. Un envoltorio no es un hueco: si la herramienta
de dentro mereciera entrar, entraria ella. `audit-harness.sh` ademas valida el esquema de un formato
de plan que este arbol no tiene.

### C. Ajuste de la maquina de trabajo, no del oficio (6)

`setup-mac.sh`, `actualizacion-nocturna-mac.sh`, `install-modifier-swap.sh`, `auto_resume.ps1`,
`clean-gone-branches.sh`, `reap-claude-orphans.sh`. Utiles, de una linea y sin decision detras. Meter
en un catalogo permanente lo que se resuelve con un alias es exactamente la basura buena contra la
que avisa la regla de admision.

### D. Operacion de varias cuentas del asistente (3)

`claude-cuenta.sh`, `mantener-sesiones-claude.sh`, `mandar-a-terminales.py`. Es intendencia del
arnes, no un oficio: nadie contrata "tener tres cuentas vivas". `mandar-a-terminales.py` ademas trae
un hallazgo negativo valioso (el interfaz de inyeccion en terminal esta denegado en este sistema
operativo, asi que hay que ir por la via de automatizacion del escritorio) que ya cubre `hammerspoon`.

### E. Demasiado estrecho para una linea de catalogo (5)

`domain-suggester.py` (sugerir dominios libres), `dedupe-daily-autocapture.py` (deduplicar capturas
por huella perceptual), `google-chat-dm.py` y `google-chat-oauth-notify.js` (avisar por un chat
corporativo concreto: `ntfy` ya cubre "que me llegue el aviso"), y la pareja `wp-mcp-sync.py` +
`wp-mcp-stdio-bridge.sh`, atada a un servidor de herramientas de terceros para un maquetador
concreto.

## 4. Duplicados evitados — propia contra publica

La seccion que pedia el encargo. Cada linea es un pueblo que **no** existe, con el ganador escrito y
la razon. En todos los casos la perdedora queda **nombrada en el cuerpo del pueblo ganador**, para
que nadie la busque dos veces.

| Herramienta propia | Publica ya montada | Gana | Por que |
|---|---|---|---|
| `navegador_seguro.py` | `agent-browser` | **publica** | La propia es politica de uso de la publica —no reutilizar sesion ajena, comprobar direccion y ancho antes de fiarse de una medicion—, no otra herramienta. La leccion se queda en el cuerpo del ganador |
| `cdp-client.py` | `agent-browser` | **publica** | Cliente del mismo protocolo escrito a mano sin dependencias. Solo gana si algun dia hace falta el protocolo sin la herramienta; hoy no |
| `pagespeed-accessibility.py` | `lighthouse` | **publica** | El servicio alojado que envuelve la propia **es** el mismo motor corriendo en casa ajena, con cuota y sin control de version. Salvo que haga falta la medicion de campo del buscador, se corre en local |
| `gsheet_sa.py`, `gsheets.py` | `gspread` | **publica** | Mismo trabajo, mismo proveedor, mismo protocolo. La publica tiene mantenimiento detras; las propias eran dos rutas de autenticacion del mismo cliente |
| `gdoc-read.py` | — | **ninguna** | Leer un documento de texto a plano no da para pueblo, y `gspread` cubre la hoja de calculo, que es de donde salen los datos de verdad |
| `backup-rsync-configs.sh` | `restic` | **publica** | Sincronizacion en modo solo anadir, sin cifrado, sin deduplicacion y sin comando de verificacion. Se conserva su unica idea buena: los permisos se aplican DESPUES de copiar, porque copiar los reescribe |
| `telegram-bridge.py` | `openclaw` | **publica** | Mismo hueco resuelto para un solo canal; la publica ya atiende consola, chat y trabajos programados |
| `patch-claude-mem-hooks.sh` | `claude-mem` | **publica** | No compite: es su parche. Vive citado dentro del cuerpo de la publica, que es donde se busca |
| `bws-token-set.sh`, `bws-secret-get.js`, `gh-token-set.sh` | `sops` | **publica** | Las propias son clientes de un gestor alojado concreto, con su cuenta y su plan. La publica cifra los valores del fichero y no depende de ningun servicio |
| `docker-secret-cookie-auth.js` | `casdoor` | **propia** | No es el mismo hueco y por eso entran las dos, con la frontera escrita: la propia para un panel de uno o dos administradores, donde montar un servidor de identidad es desproporcionado; la publica en cuanto haya usuarios, roles o inicio de sesion unico |
| `gsc-search-console.py` | el servidor de herramientas publico de la consola de busqueda | **propia** | La publica ya estaba descartada en el cuerpo de `serpbear` por ser de terceros; ademas un servidor de herramientas se paga en cada sesion. La propia hace el trozo accionable —alta, verificacion, envio del mapa, inspeccion de URL— sin instalar nada |
| `input-validators.js` | `coraza`, `libsodium` | **propia** | Capas distintas: la publica filtra la peticion desde fuera y hace la criptografia; la propia decide si el dato entra al dominio. Y `ciberseguridad` esta en el techo del presupuesto, asi que no cabria ahi de todos modos |
| `nif-cif-validator.js` | `gobl` | **propia** | Complementaria, no rival: la publica modela y emite la factura, la propia valida el identificador fiscal que la factura lleva dentro. Si entra mal, la factura sale mal y ya emitida |
| `wp-ssh.sh` | `wordpress-skills` | **propia** | Las skills oficiales explican como se **extiende** el gestor; la propia es como se le **habla** desde fuera sin abrir el navegador |
| `analyze-reel.sh` | `ffmpeg`, `whisper-cpp` | **propia, y las llama** | No sustituye a ninguna: la pregunta real casi nunca es "convierte este video" sino "dime que dice y que se ve", y esa respuesta son dos artefactos. El aporte es el orden y el muestreo |

### Duplicados publica contra publica evitados en esta tanda

`ldtk` (vs `tiled`) · `soloud` (vs `miniaudio`) · `entt` y `flecs` (el hueco de entidad-componente ya
lo cubre `bevy` de fabrica) · `tic-80` (vs `godot` y `phaser`, y ademas nicho ya con siete) ·
`openocd` y `stlink` (vs `probe-rs`) · `home-assistant` (es el lado del concentrador, aplicacion de
servidor completa, no firmware) · `radiolib` (radio de largo alcance, demasiado estrecho) ·
`aderyn` y `halmos` (vs `slither`; el segundo ademas lleva trece meses parado) · `graph-node` (vs
`ponder`) · `ethers` (vs `viem`) · `julia` (ya citado y fuera en el cuerpo de `scipy`: cambiar de
lenguaje es una decision de proyecto, no una herramienta) · `numpy` (sustrato, no eleccion) · `ray`
(vs `dask`) · `jemalloc` (vs `mimalloc`) · `flamegraph` y `async-profiler` (vs `samply` y `py-spy`) ·
`llvm` (infraestructura de compilador, no herramienta de este nicho) · `huginn`, `kestra`, `bullmq`
(el hueco de cola y de flujo ya lo tienen `celery`, `n8n` y `windmill`) · `capacitor`, `ionic`,
`detox`, `mobsf`, `nativescript` (decisiones de la tanda 2 que siguen vigentes) · `structurizr`,
`wiki-js`, `trilium`, `docusaurus`, `mdbook` (vs `mkdocs-material`, `mermaid`, `d2` y `diagrams`).

## 5. Nichos flacos: que entro, y por que hay tres que siguen flacos

### 5.1 El presupuesto cambio, y eso cambia **que** se puede revivir

El catalogo por nicho no perdona todos los rechazos: perdona **los que fueron por presupuesto**. La
tanda 2 rechazo unos 45 nombres asi (§2.A) y son exactamente los que se han revisado. Los rechazados
por solapamiento, por licencia o por estar muertos siguen fuera: el motivo no ha cambiado.

Cuatro pueblos llegue a escribir y **borre** al comprobar que su rechazo no era de presupuesto sino
de criterio, escrito en el cuerpo de otro pueblo:

| Borrado | Donde estaba escrito su rechazo | Motivo, que sigue vigente |
|---|---|---|
| `excel-mcp-server` | cuerpo de `gspread` | Un servidor de herramientas cuesta contexto en **cada** sesion, y eso el catalogo por nicho no lo arregla: los servidores externos no se miden dentro de COSMOS |
| `great-expectations` | cuerpo de `pandera` | "Infraestructura para un equipo, no para un portatil". Es un juicio de encaje, no de presupuesto |
| `llama-cpp` | cuerpo de `ollama` | "Aqui nunca se usa suelto" |
| `localai` | cuerpo de `ollama` | "Se solapa con este" |

Es la comprobacion que evita el peor modo de fallo de una tanda de relleno: reintroducir por otra
puerta lo que ya se habia decidido, y quedarse sin saber cual de los dos partes vale.

### 5.2 Tres bodies que decian una cosa falsa, y se han corregido

Tres pueblos existentes afirmaban en su cuerpo que su rival "queda fuera por presupuesto de
catalogo". Al entrar el rival, esa frase pasaba a ser mentira dentro del propio arbol:

- `zephyr` — decia "se admite uno solo por presupuesto y es este". Ahora entra tambien `freertos`,
  con la frontera escrita en los dos: nucleo minimo o base de codigo existente aqui, pilas incluidas
  y cientos de placas alli.
- `esphome` — decia que el concentrador y el intermediario de mensajeria quedaban fuera por
  presupuesto. Entra el intermediario (`mosquitto`), que es el otro extremo de la conversacion; el
  concentrador sigue fuera, y ahora por su motivo real: es una aplicacion de servidor completa.
- `samply` — citaba el perfilador que se engancha a un proceso vivo "y no admitido por presupuesto".
  Ahora entra como `py-spy`.

### 5.3 Los que se quedan flacos, y por que eso esta bien

**Equilibrar no es igualar.** Tres nichos siguen en 4 y no es por falta de mirada:

- `analitica` (4) — su barrido ya esta vaciado: `duckdb`, `polars` y `great-expectations` estan
  colocados o rechazados en `ingenieria-datos`, que es su sitio. Lo que queda cubre las tres
  preguntas del oficio: publicar (`evidence`, `streamlit`), leer lo que el negocio ya tiene
  (`gspread`) y estimar lo que viene (`statsforecast`).
- `ingenieria-datos` (4) — motor, transformacion y validacion cubiertos con una herramienta cada uno
  y sin candidato que no se solape.
- `trading` (5) y `extraccion` (7) — no estaban flacos y sus barridos se agotaron en la tanda 1.

Si un oficio se resuelve con cuatro herramientas, cuatro es el numero correcto. Lo que no vale es que
este flaco porque nadie leyo su informe, y eso es lo que se ha corregido en los trece que si lo
estaban.

## 6. Verificacion

### `python3 -m cosmos validar galaxia --config galaxia.toml` — literal

```
COSMOS  verde  0 errores
```

### `python3 -m cosmos medir galaxia --config galaxia.toml` — literal, **con solo mi trabajo dentro**

```
COSMOS  medir

  Entrada base .... 1.105 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±desconocido, heurística v1)
  Peor nicho ...... 1.748 tokens   (ciberseguridad, 26 pueblos)
  Universo ........ 16.791 tokens   (estimado, ±desconocido, heurística v1)
  Descarga ........ 89,6 %
  Presupuesto ..... 4.000     OK, quedan 2.252 tokens en el peor caso

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)

  Lo más caro de la entrada evaluada:
    1.  884 tok  catálogo visible
    2.  525 tok  índice de galaxia
    3.  77 tok  oceano/irreversible
```

### El mismo comando al cerrar el parte, ya con la tanda de `trading` dentro — literal

```
COSMOS  medir

  Entrada base .... 1.128 tokens   (índice + océanos + estructura, sin pueblos; estimado, ±desconocido, heurística v1)
  Peor nicho ...... 1.771 tokens   (ciberseguridad, 26 pueblos)
  Universo ........ 19.978 tokens   (estimado, ±desconocido, heurística v1)
  Descarga ........ 91,1 %
  Presupuesto ..... 4.000     OK, quedan 2.229 tokens en el peor caso

  Fuera de COSMOS . no_medido      (system prompt, tools, MCP)
```

Se publican las dos porque de otro modo el parte no se puede reconciliar con el siguiente: los 23
tokens de diferencia en la entrada base son los cinco paises nuevos de `trading`, no mios.

### Lectura de los numeros — solo el delta propio

| | Antes de la tanda | Con mi trabajo dentro | Delta mio |
|---|---:|---:|---:|
| Entrada base | 1.100 | 1.105 | **+5** (el pais nuevo) |
| Peor nicho | 1.743 | 1.748 | **+5** |
| Margen en el peor caso | 2.257 | 2.252 | −5 |
| Universo | 9.320 | 16.791 | +7.471 |
| Descarga | 81,3 % | 89,6 % | **+8,3 pp** |

Esta es la tesis del proyecto medida en una tabla: el sistema disponible casi ha doblado y la entrada
ha subido **cinco tokens**, que son la unica linea de catalogo permanente que he anadido. Los +7.471
tokens de contenido nuevo no se pagan hasta que alguien entra en su nicho, y ningun nicho al que he
tocado se acerca al peor.

### Un rojo intermedio, mio, y como se cerro

Tras escribir los 45 pueblos, `validar` dio **45 errores E19** (vista plana desincronizada: cada
pueblo nuevo "no figura en el manifiesto"). Es el rojo propio y su arreglo esta en la spec: `NUCLEO`
§6 dice que E19 no puede bloquear al comando que la repara. Se ejecuto
`python3 -m cosmos compilar galaxia --config galaxia.toml` (45 `CREAR`, el resto `IGUAL`, salida 0) y
`validar` quedo en verde. Escribe solo artefactos generados bajo `.cosmos/`; no toca el arbol.

### Un rojo que no era mio, y que ya no esta

Al empezar, `validar` daba `E15 indice desincronizado: galaxia/COSMOS.md`. No se toco —regenerarlo
exige `cosmos generar`, que escribe fuera de mi alcance— y a mitad de la tanda desaparecio: otro de
los trabajos en curso regenero el indice. Queda anotado por si vuelve.

**Nota de concurrencia**: `git status` durante la tanda mostraba `cosmos/*.py`, `spec/*.md`,
`galaxia/COSMOS.md` y `PROGRESS.md` modificados por otros trabajos, y al cerrar aparecieron 17
pueblos y 5 paises de `trading` mas 16 estrellas que no son mios. Nada de eso se ha tocado ni se
cuenta como propio. Consecuencia practica para quien lea despues: la vista plana se recompilo con lo
que habia en ese momento, asi que si la tanda de `trading` no vuelve a compilar, E19 saldra roja por
sus pueblos, no por los mios.

## 7. Decisiones dudosas — lo que hay que revisar

1. **`mosquitto` revierte a medias una decision de la tanda 2.** Aquella lo dejo fuera en su §3 por
   solaparse con `esphome` ("ya resuelve el cliente de mensajeria y la reconexion") y a la vez lo
   listo en su §A de rechazos por presupuesto. Entra porque esas dos cosas no son el mismo hueco:
   `esphome` es el lado del aparato y esto es el servidor que atiende al otro extremo. Si el criterio
   correcto era el de §3, se borra `pueblos/mosquitto/` y se revierte el parrafo de `esphome`.
2. **`mythril` tiene la misma ambiguedad.** La tanda 2 lo agrupo con `aderyn` como solapamiento
   frente a `slither`+`echidna`, y tambien lo listo por presupuesto. Entra porque hace algo que
   ninguno de los otros puede: trabajar sobre el codigo maquina cuando del contrato ajeno solo hay lo
   desplegado, que es la mitad de los encargos de auditoria. `aderyn` sigue fuera, ese si por
   solapamiento real.
3. **`dask` en `cientifico`, no en datos.** La tanda 2 lo comparo con `polars`+`duckdb` y lo dejo
   fuera. Entra en otro nicho y por otro trabajo: paralelizar calculo numerico, no consultar tablas.
   Su cuerpo lo dice; si aun asi se lee como el mismo hueco, sobra.
4. **`agentes-ia` pasa de 6 a 13, y siete son propias.** Es el nicho que mas crece y todo lo que entra
   es de la casa. Defensa: son las herramientas que hacen barato lo que COSMOS existe para abaratar
   —cuota real, bascula de contexto, fugas de configuracion, modelo por tarea, captura recortada— y
   ninguna tiene equivalente publico montado. Riesgo: si manana se decide que "operar el asistente"
   no es un oficio sino intendencia, este es el bloque que se mueve o se archiva entero.
5. **`ig-dl.sh` dentro de `reel-a-texto`.** Descarga de una red que no deja bajar sin sesion, con
   cascada hasta el raspado. Es doble uso: legitimo para el material propio o del cliente, discutible
   para el ajeno. Entra como pieza de un pueblo de produccion, no como pueblo propio, y sin declarar
   ningun servicio concreto.
6. **`expo` tiene un plan gratuito con limite.** El desarrollo local y el kit son gratis; la
   compilacion y el envio en la nube se pagan pasadas unas pocas al mes. Esta dicho en su cuerpo con
   esas palabras. Si la regla de coste cero se lee estricta —"nada que pueda acabar cobrando"—, no
   deberia estar.
7. **`claude-seo` (16 mil estrellas) sigue fuera de `visibilidad`.** Su barrido lo puso primero y
   propuso decidir entre mantener los dos o migrar el nucleo. No es una decision de relleno: es
   sustituir el auditor que ya esta montado. Queda como propuesta para Dario, no ejecutada.
8. **`log.py` esta citado como dependencia, no como pueblo.** Es lo correcto —una biblioteca interna
   no es una herramienta—, pero significa que un fichero de `cosecha/` vive dentro de un pueblo sin
   ser el pueblo. Si se decide que la cosecha se reorganiza por pueblos, hay que decidir donde vive.

## 8. Ficheros

- **Nuevos**: 45 en `galaxia/pueblos/<nombre>/SKILL.md` y 1 en `galaxia/paises/agentes-ia--coste.md`.
- **Modificados** (cuerpo, para nombrar a la perdedora o corregir un "fuera por presupuesto" que ya
  no es cierto): `agent-browser`, `claude-mem`, `esphome`, `gspread`, `lighthouse`, `openclaw`,
  `restic`, `samply`, `sops`, `zephyr`.
- **Regenerado**: `.cosmos/vista-galaxia/` y `.cosmos/compilado-galaxia.json`, por `cosmos compilar`.
- **No tocados**: `galaxia/estrellas/`, `galaxia/agua/`, `galaxia/sistemas/`, `galaxia/COSMOS.md`,
  `cosmos/`, `tests/`, `ejemplo/`, `cosecha/`, `spec/`.
- **Este parte**: `registro/commits/universo/2026/09/integracion-cosecha.md`.
