---
cosmos: pueblo
nombre: consola-interactiva-tmux
padre: automatizacion
resumen: Conduce vim, un REPL o un rebase interactivo desde un guion: manda teclas y lee la pantalla.
---

Rescatado de la skill `using-tmux-for-interactive-commands`. El guion viaja con el pueblo:
`scripts/tmux-wrapper.sh`, 84 lineas de bash sobre `tmux`. Ejercitado el 2026-09-02 contra un REPL de
Python: `start` devolvio el banner, `send 'print(6*7)' Enter` devolvio `42`.

```bash
brew install tmux        # o: apt install tmux
scripts/tmux-wrapper.sh start   sesion_py python3 -i
scripts/tmux-wrapper.sh send    sesion_py 'print(6*7)' Enter
scripts/tmux-wrapper.sh capture sesion_py
scripts/tmux-wrapper.sh stop    sesion_py
```

El problema que resuelve: un proceso lanzado desde una herramienta de consola no tiene terminal de
verdad, asi que `vim`, `git rebase -i`, `git add -p`, un REPL o cualquier programa a pantalla completa
no se pueden conducir con tuberias. `tmux` da una sesion separada que **sobrevive entre llamadas**, se
teclea con `send-keys` y se mira con `capture-pane`. Cada argumento de `send` es una tecla, asi que
`Enter`, `Escape` o `C-c` se mandan por su nombre.

Gana a `expect`, que es el rival clasico: aquel tiene su propio lenguaje y funciona esperando patrones
de texto, asi que se rompe en cuanto cambia un prompt y depura fatal. Gana a `pexpect` en que no
anade una dependencia de Python. Y gana a los dos en lo mas util para un agente: **puedes mirar la
pantalla en cualquier momento** con `capture`, en vez de programar a ciegas contra una expectativa.

Ojo, cuatro cosas. `capture-pane` devuelve **lo que se ve**, no el historico: lo que se salio por
arriba se ha ido (`tmux capture-pane -S -1000` si lo necesitas). Las esperas son fijas —0,3 s al
arrancar, 0,2 s al enviar—, asi que con un comando lento capturas antes de tiempo y crees que no ha
respondido: vuelve a `capture` en vez de reenviar la orden. Los nombres de sesion son globales de la
maquina, asi que dos trabajos con el mismo nombre se pisan. Y `stop` mata la sesion sin preguntar,
tambien si dentro habia algo a medias.
