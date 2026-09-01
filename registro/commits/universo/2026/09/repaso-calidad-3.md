# Repaso de calidad — tercera pasada: los 52 pueblos que la segunda no leyó a fondo

Fecha: 2026-09-01 · Árbol: `galaxia/pueblos/` · Premisa invertida (*«los que nadie miró son los que
están mal»*) · Escrito solo en `galaxia/pueblos/**` (6 ficheros) y `registro/`.

**Estado del árbol al auditar** (el informe caduca si no se fija): `HEAD 5f89852` ·
`git status --porcelain` = 22 entradas, de las cuales **16 son de otra ventana trabajando a la vez**
(ver §7). Las afirmaciones se referencian por nombre de pueblo, nunca por `fichero:línea`.

## Veredicto de una línea

**52 leídos enteros · 6 mejorados · 0 devueltos · 0 repos muertos.** La segunda pasada acertó al
declarar que estos nichos «tenían buena pinta por `tail`», pero se le escaparon **cuatro cosas que
solo salen leyendo el cuerpo y ejecutando lo que promete**: un comando de instalación que no existe,
un desinfectante que calla en la máquina de la casa, una medición de rendimiento que mide lo
contrario de lo que dice, y dos umbrales de dinero escritos como «un umbral» en vez de con el número.

Las tres primeras se cazaron **ejecutando**, no leyendo. Ese es el aprendizaje transferible de esta
pasada: en fichas ya buenas, lo que queda no se ve releyendo — se ve corriendo el comando.

## 1. Cómo se midió (invocaciones copiables, no impresiones)

**Vida de los 49 repos con URL de GitHub** (3 pueblos son herramienta propia de la cosecha), contra
la API autenticada, hoy. El token sale del llavero y **no se escribió ni se imprimió en ningún
sitio**:

```bash
export GH_TOKEN=$(security find-internet-password -s github.com -w)
curl -s -H "Authorization: Bearer $GH_TOKEN" "https://api.github.com/repos/OWNER/REPO" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['full_name'],d['stargazers_count'],d['pushed_at'],d['archived'])"
```

Se pidió `full_name` **a propósito**: la API sigue las redirecciones de organización, así que una
ficha con la URL vieja pasaría una verificación de estrellas y fechas sin que nadie se entere. Los
cinco pueblos que declaran cambio de organización —`treeverse/dvc`, `hydra-ecosystem/hydra`,
`otter-sec/anchor`, `react/react-native`, `ConsenSysDiligence/mythril`— **devuelven ese mismo
`full_name`**: son la ruta canónica de hoy, no un alias. Ninguna ficha del lote apunta a una
redirección disfrazada.

Resultado: **49/49 sin desviación** en estrellas (drift máximo: 1 estrella, ruido de minutos),
**49/49 sin desviación** en fecha de push, **0 archivados**.

**El contrato de `spec/PUEBLO.md`, medido a máquina** sobre las 52: 52/52 con referencia,
52/52 con bloque de código, 49/52 con comando de instalación (las 3 excepciones son correctas y
explicadas: `sanitizers` son banderas del compilador, `aviso-por-chat` y `correo-smtp` son guiones
de la cosecha), 52/52 con comparación que nombra al rival, 52/52 con apartado de avisos.

**Lo que se ejecutó de verdad**, que es lo que produjo los hallazgos: instalación real de un binario
publicado, compilación y ejecución de tres programas de prueba con desinfectantes, resolución de 12
fórmulas de Homebrew y 15 paquetes de PyPI, y lectura del README y del `pyproject.toml` reales por
`raw.githubusercontent.com`.

**Verificación final**: `python3 -m cosmos validar` → **verde, 0 errores** (E17 incluido) y
`python3 -m cosmos medir` → **3.143 / 4.000 en el peor caso con agua, quedan 857**. Medido en una
copia aislada del árbol para separar mis cambios de los de la otra ventana (§7); en el árbol vivo hay
un `E19` que no es mío y se explica ahí. **Ninguno de mis cambios toca un `resumen`**
(`git diff | grep -c "^[-+]resumen"` = 0), así que el presupuesto no se mueve por esta pasada: el
cuerpo no entra en el contexto de entrada.

## 2. Los 6 mejorados, con la evidencia que lo justifica

### `libresprite` — el peor del lote, y el único con un fallo duro

Dos hallazgos, los dos medidos:

1. **El comando de instalación no existe.** La ficha decía `brew install --cask libresprite`.

   ```
   $ brew info --cask libresprite
   Error: Cask 'libresprite' is unavailable: No Cask with this name exists.
   ```

   Esto rompe el criterio 1 del universo («se ejecuta») y la regla 3 de `spec/PUEBLO.md` («el comando
   se puede copiar y pegar»). Un agente que invocara esta skill se estrellaba en la primera línea.

2. **La señal de vida estaba mirando al sitio equivocado.** La ficha decía «dos meses y medio sin
   movimiento» a partir del último push. Mirando las **versiones**, que es lo que de verdad se
   instala: la última estable es la **v1.1 de 2023-12-03** y la v1.2 (2025-03-02) sigue marcada como
   prelanzamiento. Casi dos años sin binario estable, con el código moviéndose. Eso refuerza —con un
   dato, no con una opinión— lo que la propia ficha ya sospechaba: que se quedó en el Aseprite de 2016.

**Fix**: instalación real (descarga del `.dmg` de la v1.2, montaje, copia y **quitar la cuarentena**,
porque el `.app` viene con firma ad hoc y Gatekeeper lo bloquea sin decir por qué —
`codesign -dv` → `Signature=adhoc`, comprobado montando el disco), y la señal de vida reescrita
sobre versiones en vez de commits.

### `sanitizers` — el falso verde más caro que encontré, y estaba en la máquina de la casa

La ficha prometía que `-fsanitize=address` detecta «desbordamiento, uso después de liberar, **fuga**».
En este Mac (arm64, Apple clang 21) la tercera **no es cierta, y calla**:

```bash
printf '#include <stdlib.h>\nint main(void){char*p=malloc(1234);p[0]=1;return 0;}\n' > fuga.c
clang -fsanitize=address -g -O1 fuga.c -o fuga && ./fuga; echo "EXIT=$?"
#   EXIT=0                          <- ni una palabra sobre los 1234 bytes perdidos
ASAN_OPTIONS=detect_leaks=1 ./fuga
#   ==19097==AddressSanitizer: detect_leaks is not supported on this platform.   (aborta, 134)
clang -fsanitize=leak -g fuga.c -o fuga
#   clang: error: unsupported option '-fsanitize=leak' for target 'arm64-apple-darwin23.2.0'
```

O sea: de los tres modos de fallo, en macOS el de fuga es el único que **sale con 0 y sin decir
nada** — el patrón exacto que este árbol persigue. «Pasé la suite con ASan y no hay fugas» era, en
esta máquina, una frase vacía. Comprobé también el lado bueno para no dejar la ficha coja: una
carrera de dos hilos sobre la misma variable **sí** la reporta `-fsanitize=thread`, a la primera y
con fichero y línea. Las dos cosas están ahora en el cuerpo, con el comando reproducible.

### `hyperfine` — la ficha medía en caliente creyendo medir en frío

Es justo el defecto que el encargo señala para este nicho, y estaba **en el propio ejemplo de la
ficha**: `--warmup 3 --prepare 'sync'`. Dos problemas encadenados:

- `--warmup` y `--prepare` para enfriar se contradicen en la misma línea.
- `sync` **no enfría nada** en macOS: vacía escrituras pendientes, no la caché de lectura. La receta
  de caché fría del README oficial es de Linux (`echo 3 | sudo tee /proc/sys/vm/drop_caches`) y ese
  fichero aquí no existe. Lo que sí la tira es `sudo purge` (`/usr/sbin/purge`, presente en el
  sistema, comprobado).

Segundo aviso, verificado en el README real por `raw.githubusercontent.com`: por debajo de **5 ms**
el número es en buena parte el error de una resta — hyperfine ejecuta a través de `/bin/sh` y
**resta una estimación calibrada** del arranque del intérprete. Para eso está `-N` / `--shell=none`.

**Fix**: el ejemplo partido en dos casos declarados (caliente y frío) con el comando correcto de cada
uno, y los dos avisos en el cuerpo. Es la diferencia entre un número que decide y uno que adorna.

### `godot` — el umbral que decide, con el número

La ficha decía que Unreal cobra «un 5 % de regalías por encima de **un umbral** de ingresos brutos».
El umbral es el número, y el encargo lo pedía. Verificado en texto del propio Epic
(`raw.githubusercontent.com/EpicGames/Signup/master/README.md`, leído hoy):

> *«a 5% royalty only kicks in when your title earns over $1 million USD»*

**Fix**: el millón entra en la ficha, y con la lectura completa —que decide en los **dos** sentidos:
por debajo Unreal también sale gratis, así que elegir Godot por precio para un proyecto que no va a
facturar un millón es contarse un cuento y la comparación honesta pasa a ser por herramientas. Por
encima, cada 100.000 dólares son 5.000 que no se pagan, y para entonces cambiar de motor cuesta el
proyecto entero. No lo verifiqué en `unrealengine.com` porque devuelve 403 a `curl` y la
documentación de Epic se pinta con JavaScript: la fuente citada es la que sí se pudo leer.

### `fastlane` — el dinero era el problema pequeño; el problema era el calendario

La ficha decía «cuota anual en Apple, alta única en Google» sin cifras y sin plazos. Leído hoy en las
páginas de los dos fabricantes:

- Apple (`developer.apple.com/support/compare-memberships`): *«Enrollment is 99 USD (or in local
  currency where available) per membership year»* y —esto es lo que rompe una fecha— *«Companies and
  educational institutions **must provide a D-U-N-S Number** (available for free) registered to their
  legal entity during the enrollment process»*. Es gratis, pero lo emite un tercero y tiene sus
  propios días: no se saca la víspera del lanzamiento.
- Google (`support.google.com/googleplay/android-developer/answer/6112435`): *«There is a **US$25
  one-time registration fee**»*, y las cuentas **personales** creadas después del 13 de noviembre de
  2023 tienen que pasar un periodo de pruebas cerradas obligatorio y verificar un aparato Android
  real antes de poder publicar.

**Fix**: los dos números, los dos trámites, y la conclusión que es el aporte real — **124 USD el
primer año es calderilla al lado de las horas; lo que rompe un compromiso con el cliente es el plazo,
y ni el D-U-N-S ni el periodo de pruebas se aceleran pagando.** No escribí cuánto dura ese periodo:
Google lo mueve y su página de ayuda no lo dice, así que la ficha manda a mirarlo antes de dar fecha
en vez de inventar semanas.

### `expo` — las dos cifras, y nada más

Cambio quirúrgico: donde decía «cuota anual en Apple y alta única en Google» ahora dice 99 USD/año y
25 USD una vez, con puntero a `fastlane` para el calendario. No repetí allí el bloque entero: es el
mismo hecho dicho dos veces y sólo haría más lento encontrar lo demás.

## 3. Los 3 mejores del lote

1. **`mosquitto`** — el mejor aviso de seguridad del árbol que he leído: no dice «configúralo bien»,
   dice **qué línea concreta del tutorial de todo el mundo abre el aparato a internet**
   (`allow_anonymous`, y `listener` sin IP escuchando en todas las interfaces). Es el falso verde
   contado desde el fichero de configuración, no desde la teoría.
2. **`reprozip`** — cuatro limitaciones, y las cuatro son de **naturaleza**, no de comodidad: sólo
   traza en Linux (`ptrace`), no captura la red (el `.rpz` muere el día que muera el URL), no captura
   la GPU, y congela una ejecución, no un proyecto. Con 362 estrellas y siete meses sin push, la
   ficha se gana el sitio explicando **por qué entra como sello puntual y no como flujo diario**. Ese
   es el modelo de admisión honesta.
3. **`hydra`** — *«registrar la semilla no es fijarla»*. Hydra escribe `semilla: 1234` en el YAML y se
   queda tan ancho; sembrar `random`, `numpy` y el marco es trabajo tuyo. Un experimento con la
   semilla registrada y sin sembrar es **exactamente igual de irrepetible, con el agravante de que
   parece lo contrario**. Es la definición de aviso que sólo sabe quien la ha usado.

Menciones que se quedaron a un pelo: `esp-idf` («un `build` verde no dice absolutamente nada»),
`snakemake` (`Nothing to be done` con código 0 no es que la tubería funcione, es que no la ha
ejecutado), `tauri` (la otra cara exacta de por qué gana: el motor web del sistema es distinto en
cada usuario), `celery` (`acks_late` sin idempotencia **duplica cobros**) y `ffmpeg` (escribe la
salida y devuelve 0 aunque el fichero sea inservible).

## 4. Los 3 peores del lote (ninguno es basura; son los que menos se ganan el sitio)

1. **`libresprite`** — el único con un fallo duro, ya descrito y corregido. Aun corregido sigue
   siendo el más flojo del nicho: su propia ficha reconoce que los 20 dólares de Aseprite se
   amortizan el primer día en producción diaria, y que existe porque el criterio de coste cero de
   este catálogo es duro. Es admisión por regla, no por mérito.
2. **`viem`** — 3.544 estrellas frente a las 8,7k de `ethers`, que la propia ficha reconoce como
   mayoritario «en proyectos existentes y en la documentación de terceros». Su argumento (tipado
   derivado del ABI) es bueno y real, pero es el único pueblo del lote cuya comparación **pierde en
   el número que él mismo cita**. No lo devuelvo: para proyectos nuevos el argumento aguanta, y el
   hueco tiene que estar ocupado.
3. **`rpaframework`** — 1.555 estrellas, el menos respaldado del lote junto con `ponder` (1.123), y
   con «la mayor parte del ecosistema empujando hacia la plataforma de pago de la misma empresa»,
   como dice la propia ficha. Además su técnica —automatizar por interfaz— es frágil por naturaleza.
   Se sostiene porque la alternativa real (UiPath, Power Automate) es de pago y este catálogo es de
   coste cero. Es el candidato más claro a revisar si aparece algo vivo en su hueco.

## 5. Repos muertos, parados o con la vida mal contada

**Ninguno archivado. Ninguno con la vida falseada.** Los cinco más lentos, todos declarados en su
propia ficha salvo el primero, que es el hallazgo:

| Pueblo | Repo | Push real | Sin push | Cómo lo trataba la ficha |
|---|---|---|---|---|
| `libresprite` | LibreSprite/LibreSprite | 2026-06-15 | 2,5 meses | **Mal, y por eso se corrigió**: el push está vivo, pero **no hay versión estable desde 2023-12-03**. La ficha miraba commits y no versiones. |
| `mythril` | ConsenSysDiligence/mythril | 2026-04-27 | 4 meses | «Cuatro meses sin movimiento: vivo, pero no es de los que publican cada semana.» Correcto. |
| `hyperfine` | sharkdp/hyperfine | 2026-04-30 | 4 meses | «Herramienta madura y estable, no abandonada, pero conviene saberlo.» Correcto. |
| `sanitizers` | google/sanitizers | 2026-05-19 | 3,5 meses | Correcto **y bien explicado**: ese repo es documentación; la implementación viaja en `llvm/llvm-project` (push 2026-09-01), y la ficha lo dice. |
| `reprozip` | VIDA-NYU/reprozip | 2026-02-04 | 7 meses | «El más pequeño y el menos activo de este nicho, y se dice.» Correcto. |

`hammerspoon` (2026-07-08, ~2 meses) también lo declara, con la recomendación acertada de comprobar
compatibilidad tras una actualización mayor de macOS.

## 6. Las 46 que aguantan: qué busqué en cada una y por qué no las toqué

Para no repetir el «0 reescrituras» sin demostrarlo, esto es lo que se buscó y lo que se encontró:

- **Comandos de instalación**: resueltas 12 fórmulas y casks de Homebrew (`mimalloc`, `samply`,
  `hyperfine`, `raylib`, `pixi`, `echidna`, `mosquitto`, `fastlane`, `godot`, `tiled`, `ffmpeg`,
  `flutter`, `hammerspoon`, `rust`, `cmake`, `ninja`, `dfu-util`, `gallery-dl`, `yt-dlp`) y 15
  paquetes de PyPI (`esphome`, `mpremote`, `esptool`, `platformio`, `snakemake`, `dvc`, `mythril`,
  `slither-analyzer`, `reprozip`, `reprounzip`, `hydra-core`, `rpaframework`, `mlx-whisper`,
  `celery`, `py-spy`). **Todos existen salvo el cask de `libresprite`.** El caso dudoso
  (`brew install probe-rs/probe-rs/probe-rs`) se comprobó contra la API: el tap
  `probe-rs/homebrew-probe-rs` existe, tiene `probe-rs.rb` y se actualizó en julio de 2026 — la
  fórmula es válida, el error local era sólo que el tap no estaba dado de alta.
- **Afirmaciones de licencia de riesgo**: la de `ffmpeg` es la más cara del lote (dice que el binario
  de Homebrew es GPL y que distribuir un producto cerrado que lo empaquete obliga a liberar código).
  Comprobada contra el binario instalado: `ffmpeg -version` muestra `--enable-gpl --enable-libx264
  --enable-version3`. **La ficha es correcta.**
- **`embebidos`**: los 8 marcan explícitamente que necesitan hardware físico, con el precio de la
  barrera cuando existe (clon de ESP32 «desde unos 3 euros» en `esp-idf`, ST-Link «unos 5 euros» en
  `probe-rs`). `zephyr` va más allá y nombra la salida: `qemu_x86` y `native_sim` cierran en parte el
  falso verde de «compila pero no se ha probado» antes de tener placa. No falta nada que añadir sin
  inventarlo.
- **`blockchain`**: `echidna`, `mythril` y `slither` traen los tres una sección literal **«Qué clase
  de fallo detecta y cuál no»**, que es exactamente lo que pedía el encargo, y las tres se remiten
  entre sí en vez de solaparse. `mythril` además tiene el mejor matiz del nicho: la ejecución
  simbólica no termina, se corta por tiempo, así que «sin hallazgos» puede significar «no llegó» — y
  exige publicar `--execution-timeout` y `--max-depth` en el informe.
- **`cientifico`**: los 7 atacan reproducibilidad desde ángulos distintos y sin duplicarse — `pixi`
  fija paquetes, `hydra` fija la entrada, `dvc` fija el dato, `snakemake` fija el entorno por regla,
  `reprozip` sella la ejecución, `scipy` avisa de la BLAS y los hilos, `dask` del particionado.
  Cinco de los siete traen su propio falso verde nombrado.
- **`automatizacion`**: los 8 tienen la sección «A las tres de la mañana» con el comportamiento real
  ante fallo desatendido, incluidos los tres de la cosecha propia. El mejor es `celery` (`acks_late`
  sin idempotencia duplica cobros; no hay cola muerta de serie con Redis).
- **Números que deciden**: 45 de las 52 traen al menos uno. Las que se quedan en cifras escritas con
  letra (`slither`, «más de noventa detectores»; `snakemake`; `viem`) no piden un número de RAM o de
  tiempo por la naturaleza de lo que hacen, y **no me inventé uno para rellenar la casilla**.

## 7. Lo que NO hice, y por qué (honestidad de alcance)

1. **No commiteé yo, y al final no hizo falta** (actualizado al cerrar). Otra ventana estaba
   trabajando sobre este mismo árbol a la vez: estaba
   reestructurando el nicho `rendimiento` (dos `continentes` nuevos, `rendimiento-velocidad` y
   `rendimiento-calidad`, y el `padre:` de sus pueblos re-apuntado a `rendimiento/velocidad/…`) y
   añadiendo pueblos nuevos (`serena`, `ast-grep`, `difftastic`, `openrewrite`, y durante la propia
   auditoría aparecieron además `eslint` y `ruff`). Commitear mis 6 ficheros arrastraría media
   reestructura suya —`hyperfine` y `sanitizers` llevan en el mismo fichero su cambio de `padre:` y
   mi cambio de cuerpo— y dejaría el árbol en un estado intermedio roto. **No pisé nada de lo suyo**:
   sus líneas de `padre:` siguieron intactas en los dos ficheros. **Desenlace**: mientras se escribía
   este parte, esa ventana cerró su trabajo y commiteó el árbol entero en `ed970d1`
   *(feat(galaxia): 209 herramientas con contrato completo, medidor calibrado)*, arrastrando dentro
   mis 6 ficheros. Comprobado que los seis cambios sobreviven íntegros en esa revisión. Sólo este
   parte queda por commitear, y ese sí es mío solo.
2. **El `E19` que apareció a mitad no era mío, y se cerró solo.** Durante la auditoría,
   `python3 -m cosmos validar` en el directorio real pasó a dar
   `vista plana desincronizada: serena: no figura en el manifiesto` — un pueblo untracked creado por
   la otra ventana a las 14:09, después de mi comprobación de partida (que estaba verde). **No
   ejecuté `cosmos compilar`** en el árbol real precisamente para no sellar su trabajo a medias en la
   vista plana; la prueba de que mis cambios estaban limpios se hizo en una copia aislada
   (`compilar` + `validar` → verde, 0 errores). Al commitear ella y recompilar, el árbol vivo volvió
   a **verde, 0 errores**, que es como queda.
3. **No verifiqué el umbral de Unreal en su fuente primaria.** `unrealengine.com` devuelve 403 a
   `curl` con cualquier agente, y `dev.epicgames.com` se pinta con JavaScript (19 caracteres de texto
   plano). La cifra que escribí sale del README del propio Epic en GitHub, que es fuente suya pero
   secundaria. Si alguien tiene navegador a mano, conviene confirmarla contra el EULA.
4. **No verifiqué la vida de los repos rivales citados.** Igual que la segunda pasada: sólo los 49
   primarios. Un rival cuyas estrellas o fecha hayan cambiado desde el barrido original queda sin
   detectar — y en este lote hay comparaciones que dependen de ello (`rxdb` descarta WatermelonDB
   por estar parado desde agosto de 2025; `miniaudio` descarta `soloud` por lo mismo desde agosto de
   2024). Ese es el trabajo restante más rentable del árbol entero.
5. **No miré el resto de `analitica`** (`evidence`, `gspread`, `statsforecast`, `streamlit`). La
   segunda pasada los dejó también fuera y no entraban en el reparto de esta. Son 4 fichas y es lo
   único que queda para cobertura 100 %.
6. **No fabriqué ni un aviso.** Los seis cambios salen de algo ejecutado en esta máquina o leído en
   la página del fabricante, y cada uno lleva su invocación o su cita en este parte. Donde hubo
   sospecha sin prueba —la duración del periodo de pruebas de Google, el umbral de Unreal en su
   EULA— está dicho como sospecha, no escrito como hecho.

## 8. Lo que esta pasada le enseña a la siguiente

- **Pedir `full_name` a la API, siempre.** GitHub sigue las redirecciones de organización: una ficha
  con la URL vieja pasa una verificación de estrellas y fechas sin que salte nada. Sólo `full_name`
  distingue «esta es la ruta canónica» de «esto redirige».
- **Mirar `/releases`, no `/commits`.** Un proyecto puede tener push de hace dos meses y no publicar
  binario estable desde hace dos años. Para una herramienta que se instala descargándola, la señal de
  vida es la versión, no el commit.
- **Ejecutar el comando de instalación.** `brew info <x>` y un `curl` a PyPI cuestan segundos y son
  lo único que separa «la ficha parece buena» de «la ficha funciona». Aquí cazaron el único fallo
  duro del lote.
- **Ejercitar el aviso en la máquina que declara el catálogo.** Media docena de líneas de C
  demostraron que un desinfectante de referencia calla en macOS. Ese tipo de falso verde no se ve
  leyendo la ficha ni leyendo el README: se ve corriendo el programa que debería fallar.
- **Cuando una ficha dice «un umbral», falta el número.** Es la señal más barata de detectar en una
  relectura, y casi siempre es la frase donde la comparación deja de decidir.
