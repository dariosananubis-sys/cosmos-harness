---
cosmos: pueblo
nombre: claude-code-hooks
padre: agentes-ia/instrumentacion
resumen: Veintiun hooks pequenos con banco de latencia: no borrar ni saltar tests, formatear en silencio.
---

https://github.com/karanb192/claude-code-hooks · MIT · 509★ · último push 2026-09-08 (comprobado 2026-09-11; 21 plugins, 1.570 tests propios)

```
/plugin marketplace add karanb192/claude-code-hooks
/plugin install protect-tests@claude-code-hooks
/plugin install format-code@claude-code-hooks
```

Dos de los veintiuno resuelven fallos que un agente cansado encuentra solo:

- **`protect-tests`** (`PreToolUse`, matcher `Bash|Edit|MultiEdit|Write`; el `Bash` es lo
  imprescindible, porque el borrado llega por shell): deniega borrar un test (`rm`, `git rm`),
  renombrarlo a `.disabled`/`.bak`/`.skip` o meterle un marcador de salto (`@pytest.mark.skip`,
  `it.skip`, `#[ignore]`, `xit`…). Escribir tests nuevos y refactorizarlos sigue permitido. Es la
  autocertificación que G03 de COSMOS persigue, un piso más abajo: llegar al verde borrando la prueba.
- **`format-code`** (`PostToolUse` sobre `Write|Edit`): `ruff --fix` para Python y `prettier` para
  markdown, YAML y JSON, y **siempre devuelve `{}`**: nunca cuenta al modelo lo que hizo. Un
  formateador que informa es una fuga de contexto en cada edición.

```bash
node bench/run.mjs      # el banco: mediana de 34-38 ms por hook de guarda (Apple M3 Pro), 114 ms el formateador
```

Gana a `disler/claude-code-hooks-mastery` en dos cosas que se pueden comprobar: tiene licencia
(aquel no la tiene) y sus hooks hacen lo que anuncian (el `post_tool_use.py` de aquel solo escribe un
log). Frontera con `alcance-y-excepcion`: aquel acota qué rutas se tocan; este acota qué se hace con
los tests dentro de ellas.

Ojo: `protect-tests` decide por patrones sobre la orden y el texto editado, así que cada sintaxis
nueva de salto es un hueco hasta que alguien lo añade: es la regex que crece que `spec/GUARDARRAILES.md`
señala como antipatrón, y por eso en COSMOS es ficha y no guardarraíl propio. Y el banco publicado
mide latencia, no efecto: nadie ha medido que mejore la calidad de la salida.
