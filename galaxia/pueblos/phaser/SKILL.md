---
cosmos: pueblo
nombre: phaser
padre: juegos
resumen: Motor 2D que corre en el navegador al abrir un HTML, sin instalar ni pisar una tienda.
---

https://github.com/phaserjs/phaser · MIT · 40.246★ · último push 2026-08-21 (comprobado por API de GitHub el 2026-09-01).

```bash
npm install phaser
```

```html
<!-- index.html: abre en el navegador y ya corre -->
<script src="https://cdn.jsdelivr.net/npm/phaser@3/dist/phaser.min.js"></script>
<script>
new Phaser.Game({
  type: Phaser.AUTO,
  width: 800, height: 450,
  physics: { default: 'arcade', arcade: { gravity: { y: 300 } } },
  scene: {
    preload() { this.load.image('caja', 'assets/caja.png'); },
    create()  { this.caja = this.physics.add.image(400, 100, 'caja').setBounce(0.7)
                                .setCollideWorldBounds(true); },
    update()  { /* logica por fotograma */ }
  }
});
</script>
```

Es el que encaja con el perfil de agencia web: el minijuego embebido en una pagina de cliente, sin
la friccion de las tiendas. Gana a `godot` exportado a web en su hueco concreto: la exportacion de
Godot arrastra el motor entero en WebAssembly —decenas de megas y un arranque perceptible—, mientras
que aqui el juego es la propia pagina. Frente a `pixijs/pixijs`, que es solo el pintor 2D, este trae
ademas fisicas, escenas, entradas y gestion de activos.

Y lo que no hace bien: es 2D. Para 3D hay que salir de aqui. No hay editor visual —los mapas se
dibujan en `tiled` y se cargan por complemento—, y el rendimiento en moviles depende del navegador
del aparato, no de ti.

Coste cero real: MIT, sin regalias ni umbral de ingresos, a diferencia de Unity y Unreal. El editor
comercial del mismo equipo (Phaser Editor) es de pago; el motor no lo necesita.
