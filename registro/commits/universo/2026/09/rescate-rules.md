---
cosmos: lluvia
nombre: rescate-rules
moja: []
resumen: 14 lecciones con cicatriz rescatadas de dos harness reales; un mar nuevo, 5 aguas y 3 estrellas tocadas.
---

# Rescate de las rules: conocimiento con cicatriz

**Fecha:** 2026-09-02 · **Origen:** 22 rules de un harness de agencia y la policy de un segundo
harness, ambos leídos en **solo lectura** (`git status --porcelain` de los dos repos de origen = 0
líneas al terminar). · **Escribe:** `galaxia/agua/`, `galaxia/estrellas/` y este parte.

COSMOS se había traído 73 herramientas y 5 piezas de código de esos harness, pero **escribió sus 5
mares de cero**. Lo que faltaba no era doctrina: era el material que no se puede inventar — reglas
que existen porque algo salió mal una vez, con su fecha, su síntoma y su número.

Al leerlas se comprobó que **COSMOS ya había rescatado por su cuenta una parte importante** (test
que afirma lo medido, disparador de producción, valor mostrado ≠ valor conocido, bandera
trivalente, badge desde el estado autoritativo, contención de CPU antes de tocar código, «lo
desplegado y lo commiteado nunca divergen», presente en el árbol ≠ visible). Eso se dejó como
estaba: la regla de este rescate era **mejorar o referenciar, nunca duplicar** (E17).

---

## 1. Lo rescatado — 14 lecciones, con su origen y su cicatriz

### Mar nuevo: `revision` (4 lecciones)

**Por qué un mar nuevo y no uno de los cinco.** Las cinco aguas existentes no tienen sitio para
esto: `criterio` es *no escribir de más*, `pruebas` moja **solo ficheros de test** (`**/test/**`,
`*_test.*`…) y estas lecciones aplican revisando código normal, `resistencia` es *fallar ruidoso*,
y `accesibilidad`/`custodia` son de otro dominio. El océano `verificar` fija la **política** («nada
se declara hecho sin verlo funcionar y fallar»); lo que faltaba es la **mecánica de demostrar una
afirmación sobre trabajo ya hecho**. `moja` acotado a ficheros de código: se paga solo ahí.

| # | Lección | De dónde | Cicatriz que trae |
|---|---|---|---|
| 1 | Quien la escribe no la aprueba; el revisor entra dando por hecho que está mal y solo la da por buena tras contar qué intentó | `revisor-adversarial.md` (premisa invertida) | Verificarlo con tus propios comandos es revisarse a uno mismo: uno mide lo que espera encontrar |
| 2 | Lo arreglado tras una revisión no está revisado; los revisores se encadenan sobre el árbol ya corregido, nunca en paralelo | `revisor-adversarial.md` §15 | **El primero firmó 11/11 y dejó 9 avisos; el único defecto grave apareció dentro del código escrito para atenderlos** |
| 3 | Una salida publicada sin la llamada exacta que la produjo no se puede volver a ejecutar | `revisor-adversarial.md` §2 | **La firma tenía 5 parámetros y el dato viajaba en el 3.º: la tabla salía bien y leerla llevaba a la conclusión contraria** |
| 4 | Un fallo genérico en algo con auditoría suele ser un contrato de campos, no los datos; buscar por texto no distingue «no existe» de «se llama de otra forma» | `revisor-adversarial.md` §5 y §10 | **7 campos que una parte escribía y otra no admitía impedían abrir cualquier posición, y el mensaje no nombraba ninguno** |

### `mar-criterio` (+2)

| # | Lección | De dónde | Cicatriz |
|---|---|---|---|
| 5 | Antes de empezar se escribe la lista de ficheros que el encargo puede tocar; lo que caiga fuera para y pide permiso, no se amplía solo | `harness-sdd.md` (`boundary[]`, ADR-0050) | **Un ayudante editó un fichero de semilla que nadie le había pedido; deshacerlo costó más que el propio encargo** |
| 6 | Mover o partir código no es reescribirlo: el modelo borra el bloque y lo teclea de memoria, y se pierden líneas sin un solo rojo | `development.md` §6 (migraciones ≠ patches) | Se traslada con la herramienta que conserva historial y se comprueba que el conteo cuadra |

### `mar-pruebas` (+2)

| # | Lección | De dónde | Cicatriz |
|---|---|---|---|
| 7 | Se dobla el borde más externo que resuelva el caso; teclear a mano una estructura de más de 3 claves para contentar a un doble avisa de que se dobló demasiado adentro | `development.md` §7 | Doblar la función interna abortó el pipeline por no cumplir sus claves obligatorias; doblando solo la fuente de datos, el código real arma el objeto válido por construcción |
| 8 | El intérprete se nombra entero | `development.md` §4 y `revisor-adversarial.md` §7 | **518 pruebas en verde se convirtieron en 194 con 39 caídas por dependencias ausentes, solo por coger el intérprete del sistema** |

### `mar-resistencia` (+1)

| # | Lección | De dónde | Cicatriz |
|---|---|---|---|
| 9 | Un código de salida cero no prueba que algo corriera; se comprueba que el programa existe antes de creerle a su código | `development.md` §3 | **`; echo EXIT=$?` detrás de un binario inexistente reporta éxito: una suite que jamás arrancó pasa por aprobada** |

### `oceano-descender` (+1) — la única global

| # | Lección | De dónde | Cicatriz |
|---|---|---|---|
| 10 | Lo que devuelve un encargo delegado es el camino de un fichero y dos líneas | `CLAUDE.md` (anti-teléfono-descompuesto) + `contexto-y-compactacion.md` | **Tres mil líneas de respuesta las paga enteras quien delegó, y un contexto lleno de material de paso razona entre un 20 % y un 40 % peor** |

Va al océano y no a un mar porque delegar no depende del path que se esté tocando: es cómo trabaja
un agente, no una propiedad del fichero. Cuesta 55 tokens de entrada base, asumidos a conciencia.

### Estrellas (+4) — lecciones que solo son ciertas en su nicho, y además **gratis** en el presupuesto

El peor nicho es `ciberseguridad`; una línea en la estrella de otro oficio no mueve el peor caso.
Se aprovechó para colocar ahí lo que de verdad pertenece a un oficio:

| # | Lección | Estrella | De dónde y cicatriz |
|---|---|---|---|
| 11 | Un informe sobre algo que sigue cambiando caduca en minutos: en cabecera la revisión y la huella; dentro, se apunta al símbolo, nunca al número de línea | `documentos` | `informes-casos-raros.md` §6 — **dos informes del mismo día se contradecían y nadie sabía cuál valía** |
| 12 | Un diagnóstico que costó varios pasos se escribe una vez, y lo que ahorra no es el arreglo: es el síntoma, qué resultó no ser la causa, y por dónde entrar directo | `documentos` | `informes-casos-raros.md` (formato mínimo del informe) |
| 13 | Un enlace que existe no es un enlace que llega: se comprueba el código de respuesta | `web` | `revisor-adversarial.md` («un enlace que existe no es un enlace que funciona: exigir el 200») |
| 14 | Una guarda que comprueba el nombre del broker no guarda nada: se comparan los objetos por identidad cada ciclo y se sustituye uno adrede para verla saltar | `trading` | `revisor-adversarial.md` §11 — **una guarda que nunca se ha visto fallar es decorativa**; el escenario original era broker, ledger y gate |

---

## 2. Descartado por ser del negocio, no del oficio

No entra nada que no se pueda separar de su cliente, su buzón o su subvención:

- `correo-solo-buzon-dario.md`, `correo-infra-watcher.md` — qué buzón se puede abrir y de quién.
- `nunca-pagar-sin-orden.md` — el mecanismo genérico («lo irreversible se prepara y se pide el sí
  para esa acción concreta») **ya está** en `oceano-irreversible`; el resto es política de una
  persona sobre su tarjeta.
- `informe-seo-kitdigital.md`, `informe-seo-kitdigital-operativa.md`, `marcar-web-hecha-drive.md` —
  una subvención concreta, sus plantillas, sus destinatarios y su hoja de cálculo.
- `<producto>-backend.md`, `<producto>-deploy.md`, `elementor-multicliente.md`, `seo-wordpress.md`,
  `seo-2026.md` — un producto, un CMS y un panel concretos. Se rescató de ellas lo genérico (13).
- `mac2.md` — dos máquinas concretas con su RAM y su clave SSH.
- `specialist-learning-privacy.md` — el contrato de un producto propio.
- `godmode-triage.md` — sus 4 tablas nombran comandos y reglas de marca de la agencia.

Y descartado por **ya estar dicho en COSMOS** (E17 lo habría cazado): test que afirma lo medido,
disparador de producción, valor mostrado ≠ conocido, bandera trivalente, badge autoritativo,
contención de CPU antes de tocar código, desplegado = commiteado, DOM ≠ visible, buscar antes de
crear, tocar lo justo, hallazgo con reproducción copiable (`estrella ciberseguridad`), y el
«sé breve» de las dos policies — que en COSMOS no es una exhortación sino la forma del árbol.

---

## 3. Lo que merecía entrar y **no cupo** (ordenado por lo que más duele)

Quedaban 656 tokens de margen y se gastaron 593. Estas se quedaron fuera, en orden de lo que más
duele dejar:

1. **El mismo comando que falla tres veces con el mismo error no fallará distinto a la cuarta: se
   para y se busca la causa** (`development.md` §1, y también en la policy del segundo harness).
   Estaba escrita y se retiró en el último recorte por 28 tokens. Es la primera candidata a entrar
   si alguien libera espacio.
2. **Citar fuentes: un aviso vago («puede estar desfasado») es peor que las dos opciones honestas —
   o se cita la documentación oficial con enlace al apartado concreto, o se marca la afirmación
   como no verificada** (`citar-fuentes.md`, incidente de 2026-05-27). ~55 tokens.
3. **Anti-convergencia falsa: dos revisiones seguidas que mejoran menos de un 5 % escalan a
   diagnóstico de raíz aunque queden iteraciones de presupuesto** (`harness-sdd.md`). ~40 tokens.
4. **Una evidencia compuesta a mano deja de ser evidencia: la captura sale del propio navegador con
   su barra real, nunca sintética** (`<producto>-deploy.md` §3). ~35 tokens.
5. **Un arreglo no alcanza a lo ya emitido: se dice en tiempo verbal explícito («ya no llevará»,
   no «ya no lleva»)** (`informes-casos-raros.md` §2). ~40 tokens.
6. **Un bloqueo se separa por naturaleza —falta tiempo, falta permiso, falta código por escribir— y
   se atribuye a alguien que exista** (`revisor-adversarial.md` §8). Escrita y retirada; ~55 tokens.
7. **Los datos que se publican salen de la fuente acordada, no de lo que ya ponía el sitio: lo
   heredado llega con errores y se propaga firmado** (`godmode-triage.md`, policy §6). ~35 tokens.
8. **Archivar con razón escrita: un hallazgo que no se ataca se archiva diciendo por qué, no se
   arrastra** (`godmode-triage.md`). ~30 tokens.

Todas caben si en algún momento baja el **catálogo visible** (1.326 tokens, la partida más cara de
la entrada con diferencia) o el **índice de galaxia** (643).

---

## 4. Presupuesto: qué subió y dónde

| | Antes | Después | Δ |
|---|---|---|---|
| Entrada base | 1.609 | 1.664 | +55 (`oceano-descender`) |
| Peor nicho (`ciberseguridad`) | 2.383 | 2.438 | +55 (arrastra la entrada) |
| **Agua condicional** | **961** (5 aguas) | **1.499** (6 aguas) | **+538** |
| Peor con agua | 3.344 | 3.937 | +593 |
| Margen sobre 4.000 | 656 | **63** | −593 |

**Aviso para quien venga detrás:** quedan **63 tokens**. Otro agente está añadiendo pueblos en
paralelo (`galaxia/pueblos/` tiene seis sin trackear al escribir esto); cada pueblo nuevo en
`ciberseguridad` empuja el peor nicho. Antes de añadir cuerpo a un mar o a un océano,
`cosmos medir` y mirar el margen, no la intuición.

## 5. Verificación

```
$ python3 -m cosmos generar && python3 -m cosmos validar && python3 -m cosmos medir
COSMOS  generar  verde
COSMOS  verde  0 errores
COSMOS  medir

  Entrada base .... 1.664 tokens
  Peor nicho ...... 2.438 tokens   (ciberseguridad, 26 pueblos)
  Agua condicional  1.499 tokens   (6 aguas por paths:, fuera de la entrada)
  Peor con agua ... 3.937 tokens
  Universo ........ 148.641 tokens
  Descarga ........ 98,4 %
  Presupuesto ..... 4.000     OK, quedan 63 tokens en el peor caso con agua
```

E17 en verde con las seis aguas y las 21 estrellas comparándose entre sí: ninguna de las 14
lecciones repite una afirmación ya presente. Los dos casos que estuvieron cerca se resolvieron
moviendo la lección a donde de verdad pertenece, no reescribiéndola: el pin del informe salió del
mar nuevo a `estrella documentos`, y la guarda por identidad salió de `mar-pruebas` a
`estrella trading` — donde además es gratis, porque no es el peor nicho.
