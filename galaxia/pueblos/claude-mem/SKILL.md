---
cosmos: pueblo
nombre: claude-mem
padre: agentes-ia/memoria
resumen: Comprime y recupera lo hablado en sesiones anteriores del propio asistente de consola.
---

https://github.com/thedotmack/claude-mem · Apache-2.0 · 92.812★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
npx claude-mem install          # registra los enganches y levanta el worker
chmod +x scripts/patch-claude-mem-hooks.sh && scripts/patch-claude-mem-hooks.sh
```

Comprime y recupera lo hablado en sesiones anteriores **del propio asistente de consola**, que es
donde de verdad se pierde el hilo entre ventanas. Mecanismo propio de compresión y recuperación por
enganches, no un fichero de notas: no añade herramientas MCP, así que no cobra contexto en cada
sesión.

Gana a `mem0ai/mem0` (64.500★) en este hueco concreto por estar atado a este asistente: captura por
los enganches del propio CLI en vez de exigir que el agente llame a una API de memoria. `mem0` es el
genérico, para agentes propios sobre el SDK.

Se acompaña de `scripts/patch-claude-mem-hooks.sh`, que corrige tres fallos documentados: los enganches
de `SessionStart` que fallan con «Failed with non-blocking status code» cuando el worker tarda; el SDK
embebido que emite `--setting-sources ""` sin valor y hace que `--permission-mode` se coma el
siguiente argumento y rompa todo con «exited with code 1»; y el puerto del health-check desalineado
con `CLAUDE_MEM_WORKER_PORT`. No es un pueblo aparte: es el parche de este y vive con él.

Ojo: `npm install -g claude-mem` **no instala el plugin** — solo la librería, sin enganches ni worker,
y parece instalado. La vía es `npx claude-mem install`. Y el parche hay que reaplicarlo tras cada
actualización del plugin.
