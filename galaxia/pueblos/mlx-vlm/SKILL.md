---
cosmos: pueblo
nombre: mlx-vlm
padre: modelos-locales/servir
resumen: Pregunta sobre una imagen o una captura con un modelo que corre entero en el propio portatil.
---

https://github.com/Blaizzy/mlx-vlm · MIT · 5.454★ · último push 2026-09-01 (comprobado por API de
GitHub el 2026-09-01). Solo Apple Silicon: se apoya en el mismo marco que `mlx-lm`.

```bash
pip install mlx-vlm
```

```bash
# describir o interrogar una imagen, sin que salga de la maquina
python -m mlx_vlm.generate \
  --model mlx-community/Qwen2.5-VL-3B-Instruct-4bit \
  --image captura.png \
  --prompt "Que error aparece en pantalla y en que campo del formulario esta" \
  --max-tokens 300
```

```python
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template

modelo, procesador = load("mlx-community/Qwen2.5-VL-3B-Instruct-4bit")
cfg = modelo.config
p = apply_chat_template(procesador, cfg, "Lista los campos y sus valores", num_images=1)
print(generate(modelo, procesador, p, ["captura.png"], max_tokens=400))
```

Cierra el único hueco que le faltaba a este oficio: hasta aquí todo era texto y vectores, y no había
forma de que un modelo local **mirase** algo. El caso real es cotidiano: una captura de un panel que
no se puede compartir, la foto de un albarán, un pantallazo del cliente con un error.

**Con cuantización 4 bits**: un modelo de visión de ~3B ocupa 2-2,5 GB y va con soltura; uno
de 7B en 4 bits ronda los 5 GB y deja el sistema al límite con el editor abierto. Por encima no entra,
igual que en su vecino de texto. Y ojo con lo propio de visión: **la imagen también ocupa** —una
captura de pantalla de retina son miles de tokens visuales—, así que se reescala antes de pasarla, o el
consumo real triplica al del modelo.

Gana a `ollama` para este caso concreto, aunque aquel también sirva modelos con visión: `mlx-vlm` corre
sobre la memoria unificada de Apple sin copia entre procesador y gráfica, que es el mismo motivo por el
que `mlx-lm` gana en Apple Silicon, y llega antes a los modelos nuevos porque `mlx-community` los
convierte el día que salen. Frontera con `PaddleOCR` y con `ocrmypdf`, que están anotados en el nicho
de extracción: aquellos **transcriben** un documento entero y son mejores en eso; esto **responde una
pregunta** sobre una imagen suelta.

Y lo que no hace bien:

- **Un modelo de visión pequeño lee mal el texto pequeño.** Números de una factura, matrículas o un
  identificador largo salen plausibles y cambiados, sin ningún aviso. Para transcribir, OCR de verdad;
  esto es para entender la escena.
- **Solo corren en Apple Silicon.** En cualquier otra máquina no arranca, y no hay alternativa
  dentro de este pueblo; el estándar portable, el que corre en cualquier máquina, es `llama-cpp`.
- **Los nombres de modelo cambian y las conversiones no siempre están al día**: un identificador de
  `mlx-community` que hoy existe puede no tener versión 4 bits mañana, y la descarga es de gigas por la
  red la primera vez.
- Es un proyecto de una persona con mucha tracción, no un producto de una empresa: la API entre
  versiones menores se ha movido más de una vez.
