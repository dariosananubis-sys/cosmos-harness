---
cosmos: pueblo
nombre: chonkie
padre: modelos-locales/recuperacion
resumen: Trocea el texto para recuperarlo despues, sin arrastrar un marco de orquestacion entero.
---

https://github.com/chonkie-inc/chonkie · MIT · 4.719★ · último push 2026-08-26 (comprobado por API de
GitHub el 2026-09-01).

**Ojo con la URL**: el repositorio vive hoy bajo `feyninc/chonkie` tras un cambio de organización; el
enlace de arriba sigue redirigiendo, pero una cita nueva debería usar el destino real.

```bash
pip install chonkie                    # nucleo minimo
pip install "chonkie[semantic]"        # troceado por significado, necesita un modelo de vectores
```

```python
from chonkie import RecursiveChunker, SemanticChunker

# 1. el caso normal: respeta parrafos y frases antes que el limite de tokens
troceador = RecursiveChunker(chunk_size=512)
trozos = troceador("<TEXTO_DEL_DOCUMENTO>")
print(len(trozos), trozos[0].token_count, trozos[0].text[:80])

# 2. cuando el documento no tiene estructura util: corta donde cambia el tema
semantico = SemanticChunker(embedding_model="all-MiniLM-L6-v2", threshold="auto")
print([t.token_count for t in semantico("<TEXTO_DEL_DOCUMENTO>")])
```

El troceado es la decisión que más manda en la calidad de una búsqueda y la que menos se mira: si el
corte parte una tabla o separa la pregunta de su respuesta, ningún modelo de vectores lo arregla
después. Hasta ahora esto vivía dentro de los marcos de orquestación de agentes, así que trocear un
texto obligaba a instalar el marco entero.

Gana a los divisores de texto de `langchain-ai/langchain` y `run-llama/llama_index`, que son el rival
real y donde está hoy casi todo el mundo, en lo único que importa aquí: **es una biblioteca suelta**
con el núcleo sin dependencias pesadas, así que entra en un guion pequeño sin arrastrar un árbol de
paquetes ni una superficie de suministro. Encaja entre `docling` —que convierte el documento a texto—
y `sentence-transformers`, que lo vectoriza.

En 8 GB: el troceador recursivo no carga ningún modelo y es trivial. El semántico sí carga uno de
vectores, y ahí valen las reglas de su vecino: `all-MiniLM-L6-v2` (~90 MB) es la opción segura.

Y lo que no hace bien:

- **Ningún troceado se valida solo.** El único modo de saber si el tamaño elegido sirve es medir la
  recuperación con preguntas reales; cambiar `chunk_size` a ojo y declararlo mejor es opinión. Trocear
  y medir son dos pasos, y el segundo casi nunca se hace.
- **El semántico es mucho más caro** —vectoriza cada frase antes de decidir el corte— y no siempre
  gana: en un documento bien estructurado, el recursivo da un resultado igual o mejor por una fracción
  del tiempo.
- **No lee ficheros.** Recibe texto ya extraído; PDF, DOCX o HTML son trabajo de `docling` o
  `markitdown`.
- Proyecto joven y con API en movimiento entre versiones menores: fijar la versión en el `requirements`
  y no dejarla suelta.
