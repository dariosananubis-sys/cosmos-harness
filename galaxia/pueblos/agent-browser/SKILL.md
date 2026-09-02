---
cosmos: pueblo
nombre: agent-browser
padre: agentes-ia/herramientas
resumen: Navegador real por protocolo de depuracion desde consola: navega, rellena, captura y verifica barato.
---

https://github.com/vercel-labs/agent-browser · Apache-2.0 · 41.682★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
npm install -g agent-browser     # o: brew install agent-browser
agent-browser --session qa-web open https://example.com
agent-browser --session qa-web set viewport 390 844
agent-browser --session qa-web eval "document.querySelectorAll('h1').length"
agent-browser --session qa-web screenshot /tmp/movil.png
agent-browser --session qa-web close
```

Gana a `microsoft/playwright-mcp` (36.695★) por una cifra concreta: ese servidor expone **71
herramientas que se pagan en cada sesión**, se usen o no, mientras que esto se invoca por consola y
cuesta **cero herramientas permanentes**. Gana a `browser-use/browser-use` (111.924★, más popular) en
coste por tarea: aquel conduce la página con un modelo, es más autónomo y mucho más caro; se reserva
para lo que no se puede describir con selectores.

De la cosecha propia compiten dos y pierden las dos, pero dejan su lección: `scripts/navegador_seguro.py`
(nunca reutiliza sesión ajena y comprueba dirección y ancho antes de fiarse de una medición) es
**política de uso de esta herramienta**, no otra herramienta; y `scripts/cdp-client.py`, cliente del
mismo protocolo escrito a mano sin dependencias, sirve solo si algún día hay que hablar CDP sin esto.

Ojo, dos falsos verdes: una sesión con nombre reutilizada por otro trabajo puede estar en otra URL, y
el informe sale entero y es mentira — de ahí `--session` estable por tarea y comprobar la URL antes de
medir. Y «presente en el DOM» no es «visible»: exigir `offsetParent` y dimensiones > 0. En una máquina
de 8 GB, tres sesiones simultáneas es el techo; `close --all` mata las de otros trabajos.
