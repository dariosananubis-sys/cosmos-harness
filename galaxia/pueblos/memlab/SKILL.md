---
cosmos: pueblo
nombre: memlab
padre: rendimiento/perfilado
resumen: Unico perfilador de memoria de Node/JS del oficio; memray ya cubre el mismo hueco en Python.
---

https://github.com/facebook/memlab · MIT · 5.033★ · último push 2026-09-02 (comprobado 2026-09-03,
`.../commits/HEAD.atom`). De Meta.

```bash
npm install -g memlab
```

```bash
# demo autocontenida: fuga de memoria de juguete, volcado de heap y analisis del volcado
cat > demo.js <<'EOF'
const v8 = require('v8');
let fuga = [];
setInterval(() => fuga.push(new Array(1e5).fill('x')), 100);   // nunca se libera: fuga de ejemplo
setTimeout(() => { v8.writeHeapSnapshot('demo.heapsnapshot'); process.exit(0); }, 1000);
EOF
node demo.js
memlab view-heap --snapshot demo.heapsnapshot
```

```typescript
// assertion de memoria dentro de un test (Jest/Vitest), sin pasar por el CLI
import {config, takeNodeMinimalHeap} from '@memlab/core';

test('el objeto se libera tras soltar la referencia', async () => {
  config.muteConsole = true;
  let obj: any = {grande: new Array(1e6).fill(0)};
  let heap = await takeNodeMinimalHeap();
  expect(heap.hasObjectWithClassName('Object')).toBe(true);
  obj = null;
  heap = await takeNodeMinimalHeap();
  expect(heap.hasObjectWithClassName('Object')).toBe(false);   // si sigue vivo, algo lo retiene
});
```

Este país prometía «memoria» en su resumen y hasta hoy solo tenía perfiladores de Node para CPU y
tiempo (`clinicjs/node-clinic`, la referencia histórica, lleva sin push desde 2024-09-19 — más de
dos años — y su propio sucesor sugerido, `0x`, tampoco sirve de reemplazo vivo: su último push es de
2025-07-07, más de un año). `memlab` es la alternativa que sigue viva y de mantenedor serio (Meta):
toma volcados de heap V8 (`.heapsnapshot`), los analiza y aísla clústeres de objetos que no deberían
seguir vivos, con traza de qué referencia los retiene desde la raíz de GC. Nació para detectar fugas
en páginas web con Puppeteer, pero el mismo motor de análisis de heap funciona igual sobre un volcado
de cualquier proceso Node — el caso de arriba no abre navegador ninguno.

Frontera con `memray`, su equivalente de este mismo país: aquel es para procesos **Python**
(incluida memoria nativa de extensiones en C); `memlab` es para **Node/JavaScript/Electron** y
también heap de navegadores Chromium — no se solapan, cubren runtimes distintos.

Ojo: el flujo "de serie" (`memlab run` con un escenario Puppeteer) necesita un navegador de verdad y
está pensado para una página web, no para un servidor backend — para un proceso Node puro, la vía es
`view-heap`/`takeNodeMinimalHeap()` de los ejemplos de arriba. Y como todo análisis de heap: un
snapshot es una foto de un instante — una fuga que crece y se libera antes de capturar el volcado no
sale, hay que tomarlo mientras el problema está presente (o comparar dos snapshots, antes/después de
la acción sospechosa).
