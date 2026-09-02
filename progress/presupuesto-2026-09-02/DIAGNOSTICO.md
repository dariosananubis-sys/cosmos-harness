# El verde del presupuesto es falso, por segunda vez y por la misma razón

**Estado del árbol al escribir esto:** `8479933` · `python3 -m cosmos validar` verde ·
`git status --porcelain | wc -l` = 1 (este directorio).

## Síntoma

`python3 -m cosmos medir` dice **3.929 / 4.000, OK, quedan 71 tokens**. Con el
tokenizador real dice **4.244 / 4.000, ROJO, excede en 244**.

```bash
python3 -m venv /tmp/calib && /tmp/calib/bin/pip install -q tiktoken
/tmp/calib/bin/python -m cosmos medir --metodo exacto | grep Presupuesto
```

## Causa raíz

**El contador aproximado se calibró con el corpus equivocado — otra vez.** No es un fallo
del factor: es un fallo de con qué se midió el factor.

Error del contador ya calibrado, por tipo de nodo (n = 302 cuerpos de más de 200 caracteres):

| Nivel | n | Error medio | Peor |
|---|---:|---:|---:|
| mar | 6 | **1,144x** | 1,181x |
| pais | 7 | 1,115x | 1,216x |
| rio | 15 | 1,088x | 1,246x |
| estrella | 21 | 1,088x | 1,185x |
| oceano | 5 | 1,034x | 1,076x |
| pueblo | 247 | **1,011x** | 1,125x |

`FACTOR_CALIBRACION = 1.204` salió de un corpus donde **247 de 302 muestras son fichas de
pueblo**, y las fichas tokenizan bien: llevan URLs, nombres propios e inglés, que es lo que
`cl100k_base` conoce mejor. La prosa española densa —los mares— tokeniza un 14 % peor, y
los mares son justo lo que se paga en cada sesión.

En cifras: el agua sale 1.346 con el aproximado y **1.545 real**. Ahí están 199 de los 244
tokens de exceso. El resto (88) es el catálogo, que ya tiene su propio factor y aun así se
queda corto.

### Qué NO es

- **No es que falte recalibrar el número.** Subir `FACTOR_CALIBRACION` arreglaría los mares
  y rompería las 247 fichas, que hoy están bien medidas.
- **No es que el tokenizador sea otro.** `cl100k_base` es la referencia declarada en
  `docs/CALIBRACION.md` y no ha cambiado.
- **No es un crecimiento del árbol.** El exceso ya existía antes del trabajo de hoy: el
  agente del núcleo lo midió en 4.323 antes de tocar nada, y hoy está en 4.244 — o sea, el
  trabajo de hoy **bajó** el rojo en 79 tokens sin haberlo buscado.

## Fix

Dos mitades, y solo la primera es mía.

**1. Que el medidor deje de mentir (fallo, se arregla).** Un tercer factor para la prosa
que no es ficha ni texto generado —mares, océanos, estrellas, ríos, países—, calibrado con
ese corpus y no con el de las fichas. Es la misma corrección que F01 aplicó al índice y al
catálogo, aplicada al bloque que quedó fuera.

**2. Que el árbol quepa (decisión, no la tomo yo).** Con el medidor honesto el árbol está
en rojo por 244 tokens, y las tres salidas cuestan cosas distintas:

| Salida | Qué cuesta | Qué se pierde |
|---|---|---|
| Recortar los mares | `criterio` (481) y `pruebas` (378) son el 55 % del agua | Contenido normativo que se escribió a propósito |
| Subir el presupuesto a 4.500 | Nada técnico | El 4.000 dejó de ser un límite y pasa a ser lo que salga |
| Cambiar la definición del peor caso | Reescribir `NUCLEO.md` §3 | El techo deja de ser el techo de una sesión real |

La primera es la única que no afloja el listón, y por eso es la que recomiendo — pero
recortar contenido bueno es decisión de quien lo escribió.

## Cómo diagnosticarlo rápido la próxima vez

1. **Un verde del contador aproximado no es un verde.** Antes de creerse cualquier cifra de
   presupuesto: `/tmp/calib/bin/python -m cosmos medir --metodo exacto`. Si no coincide con
   el aproximado en el veredicto, el veredicto es el del exacto.
2. **Si un factor de calibración falla, mira el corpus antes que el número.** La pregunta no
   es «¿cuánto hay que subirlo?» sino «¿con qué se midió?». Dos veces seguidas ha sido lo
   segundo: F01 (prosa vs generado) y esto (fichas vs prosa española).
3. El desglose que lo enseña en un comando:
   ```bash
   /tmp/calib/bin/python -m cosmos medir --metodo exacto --json | \
     python3 -c "import sys,json; d=json.load(sys.stdin)['peor']; print(d['detalle_agua'])"
   python3 -m cosmos medir --json | \
     python3 -c "import sys,json; d=json.load(sys.stdin)['peor']; print(d['detalle_agua'])"
   ```
   Si las dos listas se separan más de un 5 %, el factor no vale para ese contenido.
