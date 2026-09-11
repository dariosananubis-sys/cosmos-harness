---
cosmos: pueblo
nombre: context-mode
padre: agentes-ia/memoria
resumen: La salida de la herramienta no entra: se ejecuta aparte, entra lo que imprime y el resto queda indexado.
---

https://github.com/mksglu/context-mode · Elastic-2.0 — no es una licencia OSI, y por eso la API de GitHub la devuelve como `NOASSERTION` · 21.835★ · último push 2026-09-09 (comprobado 2026-09-10, v1.0.169)

```bash
# Pide Node >= 22.5.0 y compila better-sqlite3, que es módulo nativo. Compruébalo primero:
node --version

# Vía MCP: las 11 herramientas, sin enganches y sin bloque de reglas en cada sesión.
claude mcp add context-mode -- npx -y context-mode
```

El plugin completo —enganches, órdenes de barra y línea de estado— se instala desde el mercado, y
es el que cobra contexto (ver los avisos del final):

```
/plugin marketplace add mksglu/context-mode
/plugin install context-mode@context-mode
```

El mecanismo, que es lo único que hay que entender: en vez de leer los ficheros al contexto, el
agente **escribe un guion que los lee** y solo entra lo que ese guion imprime.

```js
// 47 lecturas de fichero (~700 KB de contexto) pasan a un stdout de una línea.
// El `\\n` va con dos barras a propósito: el código viaja dentro de un acento grave, así que una
// sola la consumiría la plantilla y llegaría un salto de línea real que parte la cadena.
ctx_execute("javascript", `
  const fs = require('fs');
  const lineas = fs.readdirSync('src')
    .filter(f => f.endsWith('.ts'))
    .reduce((n, f) => n + fs.readFileSync('src/' + f, 'utf8').split('\\n').length, 0);
  console.log('lineas de TypeScript en src/:', lineas);
`);
```

El guion llega a la caja como `script.js` y Node lo trata como CommonJS, así que `require` está
disponible; el ejemplo del README de la herramienta usa `fs` sin declararlo y por eso no corre tal
cual.

Lo demás es consecuencia de eso: lo que no se imprime se indexa en SQLite con FTS5 y se recupera
por BM25 (`ctx_search`), así que la salida cruda sigue disponible sin haber pasado nunca por el
contexto. `ctx_fetch_and_index` hace lo mismo con una página web, y los enganches capturan
ediciones, órdenes de git y decisiones para que sobrevivan a una compactación.

Frontera con `claude-mem`, su vecino: aquel comprime **lo que ya se dijo**, y este evita que la
salida de la herramienta **llegue a decirse**. Son las dos mitades del mismo problema y no compiten;
si hay que elegir una en un arnés de consola, `claude-mem` no cobra contexto por sesión y este sí.

Ojo, y esto es lo que decide si entra o no en un arnés concreto: **el plugin completo inyecta 1.151
tokens de reglas en cada `SessionStart`** (medido sobre `hooks/routing-block.mjs` de la v1.0.169),
más unos 550 de guías que va soltando por `Bash`, `Read`, `Grep` y `mcp__` durante la sesión. En
COSMOS eso no cabe: `cosmos medir` da 3.772 de 4.000 en el peor caso con agua, o sea 31 tokens de
margen, y el gasto además caería en la línea `no_medido` del medidor, que es justo la fuga que
`spec/MEDIDOR.md` §41 existe para cazar. La vía MCP de arriba se salta el bloque de reglas, pero sus
11 definiciones de herramienta se siguen pagando en esa misma línea que nadie mide.

Tres límites más, por orden de probabilidad de morder:

- Registra **nueve enganches `PreToolUse`**, y uno tiene el matcher `mcp__`: dispara un proceso de
  Node en cada llamada a cualquier otro servidor MCP que tengas montado.
- Bloquea `curl`, `wget` y `WebFetch` a propósito, sustituyéndolos por un error. Si algo tuyo
  depende de ellos, deja de funcionar sin avisar de que fue este plugin.
- El bloque que inyecta es una lista de reglas en mayúsculas («MANDATORY», «BLOCKED», «Do NOT
  retry»): funciona mientras el modelo la recuerde. Es exhortación, no estructura.

Y un aviso de crédito, no de mecanismo: el README abre con una fila de logotipos de Microsoft,
Google, Meta y una docena más bajo el rótulo «Used across teams at», pero todos esos enlaces apuntan
a `#`. No hay nada que comprobar detrás. Las estrellas y el ritmo de commits sí son reales y están
citados arriba con su fecha; esa fila, no.
