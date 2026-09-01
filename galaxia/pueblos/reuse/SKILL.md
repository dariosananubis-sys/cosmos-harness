---
cosmos: pueblo
nombre: reuse
padre: cumplimiento/licencias
resumen: Comprueba que cada fichero del repositorio propio dice su licencia y su autoria, no solo el LICENSE.
---

https://github.com/fsfe/reuse-tool · **GPL-3.0-or-later** para la herramienta (leído en su carpeta
`LICENSES/`, que además contiene `Apache-2.0`, `CC-BY-SA-4.0` y `CC0-1.0` para partes distintas del
repositorio; la API de GitHub no clasifica nada porque no hay `LICENSE` en la raíz — comprobado el
2026-09-01) · 583★ · último push 2026-08-22 (misma comprobación). Herramienta oficial de la Free
Software Foundation Europe.

```bash
pipx install reuse        # o: pip install reuse
```

```bash
reuse lint                                    # sale distinto de cero si algo no declara licencia
reuse download MIT                            # deja LICENSES/MIT.txt con el texto exacto
reuse annotate --copyright "<TITULAR>" --license MIT src/*.py
reuse spdx -o proyecto.spdx                   # inventario en formato SPDX del propio repositorio
```

```yaml
# .reuse/dep5 o REUSE.toml para lo que no admite cabecera (imagenes, fuentes, datos)
version = 1
[[annotations]]
path = "assets/**"
SPDX-FileCopyrightText = "<TITULAR>"
SPDX-License-Identifier = "CC-BY-4.0"
```

Sus vecinos miran hacia fuera y este mira hacia dentro, y esa es toda la frontera: `ort` y `fossology`
auditan **las dependencias que entran**; esto audita **lo que sale de aquí**. Es la comprobación que
falta el día que un repositorio se entrega a un cliente o se publica: un `LICENSE` en la raíz no dice
nada del fichero que llegó copiado de un ejemplo, de la fuente tipográfica de la carpeta de recursos ni
del guion que escribió alguien que ya no está.

Gana a poner la cabecera a mano, que es la alternativa: `reuse lint` da código de salida, así que entra
en la puerta de la tubería, y `annotate` escribe las cabeceras en lote respetando el comentario de cada
lenguaje.

**Norma que cubre**: la **especificación REUSE (v3.3)** de la FSFE, construida sobre los identificadores
de licencia **SPDX**. No es una norma legal sino la forma de dejar la autoría y la licencia
demostrables fichero a fichero — que es lo que piden los pliegos y lo que sostiene el inventario de
materiales que exige el **Reglamento europeo de ciberresiliencia**. Territorio: ninguno en concreto.

**Lo que NO comprueba**: no mira las dependencias, no detecta código copiado sin cabecera —si nadie
escribió nada, aquí sale como fichero sin declarar, no como infracción— y **no verifica que la licencia
declarada sea la verdadera**. Comprueba que se declara algo, no que sea cierto.

Ojo: en un repositorio existente, la primera ejecución saca cientos de hallazgos y la tentación es
anotarlo todo en lote con la licencia del proyecto. Eso es exactamente lo contrario de lo que sirve:
`annotate` en masa **firma como propio** lo que quizá no lo sea. Se empieza por lo que se escribió aquí
y lo dudoso se revisa a mano.
