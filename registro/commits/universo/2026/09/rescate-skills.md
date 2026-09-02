# Rescate de skills — 9 con mecanismo real, de 64 miradas

Fecha: 2026-09-02 · Escrito en `galaxia/pueblos/` (9 pueblos nuevos) y en este `registro/`.
Origen, en solo lectura: `Arnes-Dario/.claude/skills/` y `vh-ref/skills` + `vh-ref/packs/*/skills/`.

## 0. El hueco que se cierra, y su tamaño real

El encargo decía «de las 51 skills de un arnés y las 56 del otro solo se reutilizaron 3». Contadas
una a una, ese 51+56 son **64 skills distintas**: 39 nombres están en los dos árboles (es el mismo
material empaquetado dos veces). Sobre esas 64:

```
  64  skills distintas (47 vivas en Arnes-Dario + 56 en vh-ref, 39 compartidas)
  12  traen guiones dentro de su carpeta          18,8 %
   3  su mecanismo existe pero vive fuera de la skill (tools/ y hooks/ del arnés)
  49  son prosa: instrucciones de cómo hacer algo bien, sin nada que ejecutar
```

**El criterio 1 de `spec/UNIVERSO.md` era la respuesta correcta para 49 de 64.** Pero la mitad de las
15 restantes nunca se miró, y ahí había mecanismo de verdad: un guardarraíl que deniega escrituras,
un gate que no deja aprobar lo que no se pudo medir, tres contratos puros que salen con código 1.

## 1. Las 9 rescatadas

Todas traen el guion **dentro del directorio del pueblo**, así que `cosmos compilar` las exporta
enteras. Esto corrige de paso el patrón de `web-fidelidad-elementor`, que referencia una skill que
solo existe si el arnés está instalado en esa máquina.

| Pueblo | Oficio | Mecanismo, y qué se ejercitó el 2026-09-02 |
|---|---|---|
| `auditor-de-skills` | `ciberseguridad/analisis/cadena-de-suministro` | 1.066 líneas sin dependencias. Escanea el paquete de una skill: guiones peligrosos, inyección de instrucciones en el `SKILL.md`, salidas de la carpeta. Verdicto en el código de salida (0/1/2). Corrido contra dos skills reales. |
| `playbook-obligatorio` | `agentes-ia` | Reescrito genérico. `PreToolUse` que **deniega** (código 2) hasta que el playbook se ha leído en esta sesión; la marca lleva su SHA-256 y va por `session_id`; `PreCompact` la borra. `autotest`: 8/8, incluida la meta-prueba de verla denegar. |
| `gate-de-salida-web` | `web/calidad-de-sitio` | Reescrito genérico. Seis capas y una regla: `no_medido` no cuenta como aprobado. Ejercitado contra dos sitios locales: caso igual → PASA (rc 0); un `h1` de más y una franja movida → FALLA con las bandas de píxeles; sin `--referencia` → FALLA por `no_medido`. |
| `punto-de-restauracion-web` | `web/construccion-de-sitios` | Reescrito genérico. Guarda y devuelve `_elementor_data` por wp-cli, con los dos gotchas que lo hacen funcionar: vaciar el CSS generado y `wp_slash` al escribir. `autotest` con un `wp` doblado: 9/9. |
| `extractor-de-curso` | `extraccion/fuentes-web` | 537 líneas. Vuelca un aula virtual a Markdown con la sesión ya iniciada; solo lectura por diseño. Trae el gotcha de que Chrome 136+ ignora `--remote-debugging-port` sobre el perfil por defecto. |
| `despliegue-reanudable` | `infraestructura` | 780 líneas, sin red. Fases como DAG: la sonda manda sobre el registro, solo se reintenta lo idempotente. Comprobado: un ciclo da `PLAN INVÁLIDO`; un `gate` sin sonda da `gate_without_probe`. |
| `contrato-de-publicacion` | `infraestructura` | 516 líneas. Ocho puertas obligatorias, permiso caducable de un solo uso, y revisión exacta de 40/64 hex — un `latest` sale `revision_not_exact`. Comprobado: quitando `backup_verified`, deniega. |
| `manifiesto-de-evidencias` | `cumplimiento` | 405 líneas. Liga cada prueba a la versión publicada por su hash y exige atestación humana donde toca. Comprobado: tocar un artefacto sin actualizar el manifiesto da `artifact_digest_mismatch`. |
| `consola-interactiva-tmux` | `automatizacion` | 84 líneas de bash. Conduce vim, un REPL o un rebase interactivo por `send-keys`/`capture-pane`. Ejercitado contra un REPL de Python: `print(6*7)` → `42`. |

Reescritos genéricos (3): el mecanismo valía y el envoltorio era del negocio. Se sacaron el
identificador de cliente, el anfitrión de la agencia, las rutas de una máquina concreta y el trámite
al que servían. Ninguno de los nueve contiene un dominio real, una credencial ni un nombre de cliente
(comprobado con grep).

## 2. Las descartadas, por motivo

**Prosa sin mecanismo (49).** Son buenas instrucciones y no entran: es lo que un modelo capaz ya
hace. Entre ellas `accessibility`, `api-design`, `code-review`, `testing`, `writing-plans`,
`executing-plans`, `dispatching-parallel-agents`, `source-driven-development`, `taste-skill`,
`anthropic-frontend-design`, `audit-context-building`, `database-schema-designer`,
`privacy-compliance`, `schema-markup`, las cuatro de `vh-ref/skills`
(`adversarial-verification`, `context-efficient-work`, `memory-retrieval`, `project-isolation`) y
toda la familia de WordPress (`wordpress-plugin-development`, `wp-editor-live`, `header-footer`,
`web-builder-isolated`, `tienda-woocommerce`…). Caso aparte: **`ruta-reutilizable` está vacía** —
solo tiene un `__pycache__` huérfano, sin `SKILL.md` ni fuente.

**Mecanismo real, pero atado al negocio y no rescatable con honestidad (6).**

- `webs-calidad-top` — 7 guiones, y el mejor argumento en su contra lo escribió el propio arnés:
  «`audit.sh` no tiene ni un `exit`», «`verifica-todo.sh` suma a su código de salida solo 2 de sus 6
  capas», «`compara-pagina.sh` no devuelve nada». Un guion que siempre sale 0 no es un gate. Su
  sucesor —el que sí decide— es lo que se rescató como `gate-de-salida-web`.
- `cuadrilla` — reparte un encargo entre sesiones, con adversario y montaje. Real, pero es el
  conductor de **un demonio concreto** que ya está en la galaxia como `openclaw`, y su otro canal ya
  está como `ordenes-entre-ventanas`. Lo reutilizable de verdad es el protocolo, no la herramienta.
- `browserclaw` — mecanismo bueno (perfil persistente, árbol de accesibilidad, guardarraíl de
  dinero) atado a una aplicación concreta. `agent-browser` ya cubre el hueco de navegador.
- `insti-deberes`, `gmail-send`, `google-chat-send` — el primero es de una persona; los otros dos
  están cubiertos por `correo-smtp` y `aviso-por-chat`.

**Ya cubierta por algo público que está en la galaxia (6).** `cyber-neo` (`scan_secrets.py` y
`check_lockfiles.py` pierden contra `trufflehog`, `osv-scanner` y `trivy`), `static-analysis-semgrep`
y `static-analysis-codeql` (`semgrep`), `defuddle` (`trafilatura`, `markitdown`),
`hierarchical-agent-memory` (aquí es prosa; su repo compite con `claude-mem` y `mem0`, que ya están),
`recall` (indexa el histórico de tres asistentes con FTS5 y sin API — pierde el hueco contra
`claude-mem`, que ya lo ocupa en `agentes-ia/memoria`, y ese nicho estaba a 52 tokens de convertirse
en el peor).

## 3. Duplicados evitados, uno a uno

- `codex-delegate` → ya es **`delegar-generacion`**. No se duplica.
- `agent-browser` → ya está, y es correcto: se comprobó su ficha antes de tocar nada.
- `web-diff-visual.py` (comparador de píxeles por franjas) → **no se creó como pueblo aparte**; es la
  capa C6 dentro de `gate-de-salida-web`, para no repetir lo que ya dice `web-fidelidad-elementor`.
- `web-contrato.py` / `alcance.py` → ya es **`alcance-y-excepcion`**.
- `multi-review.py` → ya es **`revision-cruzada`**.
- `claude-seo-ai` y `seo-wordpress-autonomo` → ya está **`claude-seo-ai`**.
- `mandar-a-terminales.py` → ya es **`ordenes-entre-ventanas`**.

## 4. Presupuesto

El coste real de las nueve incorporaciones, medido quitándolas y volviéndolas a poner:

```
  sin las 9 ...... peor con agua 3.836   (quedan 164)
  con las 9 ...... peor con agua 3.881   (quedan 119)
  coste propio ... 45 tokens
```

Cuarenta y cinco tokens, y son enteros de `auditor-de-skills`: es el único pueblo que cae en el peor
oficio. Los otros ocho se repartieron a propósito entre oficios pequeños y **no cuestan nada al peor
caso**. Ninguno convierte otro oficio en el peor: `ciberseguridad` sigue arriba con 2.483 y
`agentes-ia` queda segundo con 2.431.

Aviso sobre el margen: el encargo hablaba de ~650 tokens y hoy son 119. **De esa diferencia, 45 son
míos.** El resto es el commit `cf7e10a` de otra parte del proyecto (08:23 de hoy).

> **Corregido el 2026-09-02 (F12).** Este párrafo decía que `cf7e10a` «cambió cómo se mide el agua
> condicional: pasó de 961 a 1.398 tokens **sin que se añadiera un solo nodo**». Las tres cosas eran
> falsas, y en la dirección que más engaña: hacían pensar que el margen se estrechó por un cambio de
> método y no por haber gastado presupuesto. Medido sobre los dos árboles, cada uno con su código:
>
> ```
> $ git archive cf7e10a^ | tar -x -C /tmp/pre  && cd /tmp/pre  && python3 -m cosmos medir | grep Agua
>   Agua condicional  961 tokens   (5 aguas por paths:, fuera de la entrada)
> $ ls /tmp/pre/galaxia/agua/mar-*.md | wc -l                       # 5
> $ git archive cf7e10a  | tar -x -C /tmp/post && ls /tmp/post/galaxia/agua/mar-*.md | wc -l   # 6
> ```
>
> `cf7e10a` **añadió** `mar-revision` (236 tok) y engordó otros tres (`criterio` 295→421,
> `pruebas` 358→473, `resistencia` 100→161). Con el método viejo —la suma de toda el agua— ese
> árbol da **1.499**, así que el contenido subió **+538**; el cambio de método bajó el número
> **−101**, hasta los 1.398 publicados. Es decir: la medida bajó, y lo que subió fue el contenido
> que el propio commit metió. Su mensaje de commit ya lo decía bien («Medido: 1.499 -> 1.398») y
> este parte lo copió al revés.
>
> Y el cambio de método era ademas incorrecto: se revirtió el 2026-09-02 al volver a la definición
> normativa de `NUCLEO.md` §3 (F06), así que hoy el agua se vuelve a medir como la suma de toda.
>
> Lección para los partes siguientes, del propio `GOAL.md` §1 («un número copiado a mano envejece en
> silencio»): **un parte cita el bloque de `cosmos medir` con el hash del commit al que corresponde
> en la misma línea**, no un número suelto de memoria.

Se dice aquí porque leer los 119 como consecuencia de este rescate sería falso.

Cadena de verificación, en verde:

```
python3 -m cosmos generar    →  verde
python3 -m cosmos compilar   →  los guiones viajan dentro de cada skill compilada
python3 -m cosmos validar    →  COSMOS verde, 0 errores
python3 -m cosmos medir      →  3.881 / 4.000, OK
python3 -m cosmos estado     →  247 pueblos, mayor 27, menor 7
```

## 5. El juicio honesto sobre esos dos arneses

**De 64 skills, 12 traían algo que ejecutar y 3 más lo tenían fuera de sí mismas. Quince.** Las otras
49 son documentos que le explican a un modelo cómo hacer bien un trabajo que ya sabe hacer, y que se
pagan en cada sesión a cambio de eso.

Tres cosas que este recuento enseña y que no se veían desde dentro:

1. **La duplicación estaba en el propio catálogo.** 39 de 64 nombres estaban empaquetados dos veces.
   Contar carpetas daba 103 skills donde había 64.
2. **El mecanismo bueno no vivía en las skills, vivía en `tools/` y en `.claude/hooks/`.** Lo mejor
   que se ha rescatado hoy —el guardarraíl que deniega la escritura— era un enganche, no una skill;
   la skill era la prosa que lo acompañaba. Un catálogo que solo mira las skills no lo encuentra.
   Y COSMOS ya lo intuía: su `cosecha/` había minado `tools/`, pero no los enganches.
3. **Los guiones que sí existían fallaban por el final, no por el principio.** Los siete de
   `webs-calidad-top` miden bien y **no devuelven código de salida**. Medir sin decidir es la forma
   más cara de no tener un gate: se paga el trabajo entero y se sigue aprobando a ojo. Es la misma
   lección que la regla del `no_medido`, y por eso es la que se ha rescatado.

Nueve de sesenta y cuatro no es un fracaso del rescate: es la medida de esos arneses.
