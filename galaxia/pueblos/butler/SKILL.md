---
cosmos: pueblo
nombre: butler
padre: juegos/motores
resumen: Sube una build a itch.io con parches binarios: solo sube lo que cambio, no el juego entero.
---

https://github.com/itchio/butler · MIT · 980★ · último push 2026-09-03 (comprobado 2026-09-03)

```bash
# el metodo automatizable que documenta itch.io: URL fija de "broth", no expira como la de la web
curl -L "https://broth.itch.zone/butler/darwin-amd64/LATEST/archive/default" -o butler.zip
# en Apple Silicon: https://broth.itch.zone/butler/darwin-arm64/LATEST/archive/default
unzip butler.zip -d butler-bin && chmod +x butler-bin/butler && ./butler-bin/butler -V
```

```bash
butler login
butler push carpeta-de-la-build usuario/mi-juego:canal-windows
butler status usuario/mi-juego:canal-windows      # ver versiones subidas y su tamano de parche
```

Nota de sitio: cuelga de `juegos/motores` y **no es un motor**. Es la herramienta de línea de
comandos para **publicar** la build que produce cualquiera de ellos (`godot`, `bevy`, `phaser`,
`raylib`). El país de distribución que llegó a abrirse para él se retiró el 2026-09-03 por tener un
solo hijo, que es el antipatrón de nivel de relleno de `spec/TAXONOMIA.md`.

Gana a subir el zip a mano por la web de itch.io en lo único que importa para iterar rápido: usa el
protocolo `wharf` para calcular un **parche binario** entre la build anterior y la nueva, así que
publicar una actualización de una build de varios gigas con un cambio pequeño sube solo el delta, no
el paquete entero. Frente a Steamworks SDK (el equivalente para la otra plataforma de distribución),
no compite: son ecosistemas distintos y cada uno solo sirve para el suyo.

Ojo: `butler login` guarda una clave de API con permiso de publicar en la cuenta — tratarla como
credencial, no committearla nunca a un repositorio. Y `butler push` sin revisar el canal
(`:canal-windows`, `:canal-mac`…) sube al canal por defecto si se omite: un `push` sin canal declarado
puede sobrescribir la build equivocada delante de los jugadores.

Ojo de instalación, y es donde falla a la primera: `brew install --cask itch` instala **itch.app** (el
cliente de escritorio), que trae su propio `butler` embebido pero NO lo deja en el `PATH` — la app y el
binario de línea de comandos son artefactos distintos. Y `brew install butler` a secas instala OTRA
herramienta: el `butler` de línea de comandos de Homebrew es un cask de manytricks.com (una app de
organización de tareas), sin relación con itch.io. Tampoco hay tap oficial de Homebrew para este
`butler`; la vía que sí es del proyecto y sí es automatizable es la descarga de `broth.itch.zone` de
arriba.
