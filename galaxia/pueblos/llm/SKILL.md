---
cosmos: pueblo
nombre: llm
padre: modelos-locales/servir
resumen: Llama al modelo desde la tuberia de la terminal y guarda cada peticion y respuesta en SQLite.
---

https://github.com/simonw/llm · Apache-2.0 · 12.439★ · último push 2026-08-22 (comprobado por API de
GitHub el 2026-09-01)

```bash
brew install llm
llm install llm-ollama llm-mlx        # complementos para modelos locales
llm models default qwen3:4b-q4_K_M    # el que ya sirve ollama
```

```bash
# lo que hace que exista: es un filtro de shell mas
cat informe.md | llm -s "Resume en tres vinetas, en castellano" > resumen.md
git diff | llm -s "Escribe el mensaje de commit en formato convencional"

# la conversacion continua y queda registrada
llm -c "y ahora en una sola linea"

# y el registro es una base de datos, no un scroll de terminal
llm logs -n 5
llm logs --json | jq '.[] | {modelo: .model, cuando: .datetime_utc}'
sqlite3 "$(llm logs path)" "select model, count(*) from responses group by 1"
```

Gana a `ollama run` y a llamar por `curl` al puerto local, que es la alternativa real y ya está
montada, en dos cosas concretas. Una: **todo queda guardado en SQLite** —prompt, respuesta, modelo,
fecha— así que se puede volver a una respuesta de hace un mes, comparar dos modelos sobre lo mismo o
contar cuánto se usó cada uno; con `ollama run` eso se pierde al cerrar la terminal. Y dos: es un
filtro de shell de verdad, con entrada estándar y salida estándar, lo que le deja encadenarse con
`grep`, `jq` y el resto de la máquina.

Frontera con sus vecinos: `ollama` **sirve** el modelo, esto lo **usa** desde la línea de comandos, y
`lm-evaluation-harness` lo **puntúa**. No compiten.

En 8 GB no añade coste: es una envoltura de Python de unos pocos megas; quien ocupa la memoria es el
modelo que haya detrás, con las reglas de siempre —4 bits, hasta 7B con margen justo.

Y lo que no hace bien:

- **El registro guarda los prompts enteros, en claro, en `~/.config/io.datasette.llm/logs.db`.** Si en
  una sesión entra un dato de cliente, ahí queda: ese fichero no se sincroniza ni se comparte, y se
  vacía con `llm logs --truncate` cuando toque.
- **La mayoría de complementos son de proveedores de pago.** Los de este pueblo son los locales
  (`llm-ollama`, `llm-mlx`, `llm-gguf`); instalar uno de pasarela y poner una clave es gasto, y no se
  hace sin orden.
- **`llm -c` continúa la última conversación, sea cual sea.** Si en medio se lanzó otra cosa, el
  contexto que se arrastra no es el que uno cree — para no dudar, `llm -c --cid <ID>`.
- No orquesta ni tiene herramientas: para un agente con herramientas y memoria, eso es otro oficio.
