---
cosmos: rio
nombre: configurar
moja: []
momento: mantenimiento
invoca: python3 -m cosmos configurar
resumen: El alta de la maquina: oficios, herramientas, credenciales, grado de autonomia y modelos.
---

Lo primero al instalar COSMOS en una máquina, y todo fuera del repositorio (`~/.cosmos/`, 700/600).
Pregunta qué oficios se usan de verdad y qué herramientas de cada uno, escribe el fichero de
credenciales con las variables que esas herramientas piden —vacías, con la pista de dónde se saca
cada una— y lo abre en el editor. `--comprobar` lo lee y se lo queda; `--llavero` lo pasa al
llavero de macOS y vacía el texto.

Tres caras más, de máquina y no de proyecto, porque el runtime solo acepta el modo desde los
ajustes de usuario:

- `--autonomia auto|libre|manual`: cómo arranca el runtime. `auto` no pregunta y deja un
  clasificador detrás; `libre` no comprueba nada (`bypassPermissions`) y acepta el diálogo de
  responsabilidad para que una máquina nueva no se pare; `manual` deshace y devuelve el fichero
  byte a byte. Sin valor, dice el grado vigente. Es lo que hace verdadera la promesa del océano
  `autonomia`: G01 avisa en cada arranque si la carta promete libertad y la máquina pregunta.
- `--modelos instalar|estado|quitar`: el vigilante que repone en el selector del runtime los
  modelos de la cuenta, cada vez que el CLI pisa su fichero (agente de launchd en macOS y hook
  de arranque de sesión), más los atajos `maxcode` y `ultracode`. La lista de modelos vive en
  `puente/modelos.py`; que la cuenta acepte cada id no se comprueba sin red y se dice.
- `--lanzador`: `cosmos` en el PATH (`~/.local/bin/cosmos`, apuntando a este clon).

`--seco` enseña lo que haría. Todo lo que escribe fuera de `~/.cosmos/` guarda los bytes del
fichero anterior y se deshace con el mismo verbo; lo que alguien cambió a mano después no se toca
y se dice. `cosmos estado --maquina` cuenta qué falta.
