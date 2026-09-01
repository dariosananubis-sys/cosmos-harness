---
cosmos: pueblo
nombre: outlines
padre: modelos-locales/servir
resumen: Obliga a que la salida cumpla un esquema durante la generacion, no despues de generarla.
---

https://github.com/dottxt-ai/outlines · Apache-2.0 · 15.734★ · último push 2026-08-31 (comprobado por
API de GitHub el 2026-09-01)

```bash
pip install "outlines[transformers]"     # tambien: outlines[mlxlm], outlines[llamacpp], outlines[vllm]
```

```python
import outlines
from pydantic import BaseModel
from typing import Literal

class Ficha(BaseModel):
    nombre: str
    categoria: Literal["factura", "albaran", "contrato"]
    importe: float

modelo = outlines.from_transformers(...)          # o outlines.from_mlxlm(...) en Apple Silicon
generar = outlines.Generator(modelo, Ficha)
print(generar("Extrae la ficha de este texto: <TEXTO_DEL_DOCUMENTO>"))
# -> siempre un JSON que valida contra Ficha. No hay rama de "y si no vino JSON"
```

Es un cambio de mecanismo, no un truco de prompt: en cada paso de generación **enmascara los tokens
que romperían el esquema**, así que la salida no puede ser inválida por construcción. Eso elimina de
golpe el bucle de reintentos, el `try/except json.loads` y la rama de recuperación que en un agente
son la mitad del código y la mitad de los fallos.

En 8 GB es exactamente lo que hace viables los modelos que caben: un 3B en 4 bits sin restringir se
inventa la forma cada dos por tres, y restringido acierta la estructura siempre — el modelo solo tiene
que decidir el contenido. La biblioteca en sí no consume nada; el coste es el modelo servido, con las
mismas reglas de siempre.

Gana a `guidance-ai/guidance`, el otro proyecto serio del hueco, en integración: aquí el esquema se
declara con un modelo de Pydantic o una expresión regular y corre igual sobre `transformers`, `mlx-lm`
o `llama.cpp` sin reescribir nada. Y aunque `ollama` acepta hoy un esquema JSON en su petición y
`llama.cpp` tiene su propia gramática, ninguno de los dos cubre lo que sí cubre esto: **expresiones
regulares, gramáticas libres de contexto y tipos de Python arbitrarios**, dentro del mismo guion.

Y lo que no hace bien:

- **Garantiza la forma, no la verdad.** Un JSON perfectamente válido con el importe equivocado sigue
  estando mal, y ahora además parece fiable. Es el falso verde de este pueblo: la validación de esquema
  ya no puede fallar, así que deja de avisar de nada.
- **Necesita acceso a los logits**, así que no funciona contra un servicio que solo devuelva texto: hay
  que servir el modelo desde el propio proceso o por un motor que lo exponga.
- **Un esquema muy restrictivo con un modelo pequeño produce relleno**: si el campo obligatorio no está
  en el texto, el modelo lo rellena igual porque la máscara no le deja callarse. Los campos que puedan
  faltar se declaran `Optional`, a propósito.
- La compilación del autómata de una gramática grande tarda la primera vez; se cachea, pero la primera
  medición no es representativa.
