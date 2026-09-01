---
cosmos: pueblo
nombre: ollama
padre: modelos-locales/servir
resumen: Gestor que descarga, versiona y sirve modelos con API compatible, sin compilar nada a mano.
---

https://github.com/ollama/ollama · MIT · 179.880★ · último push 2026-09-01 (comprobado 2026-09-01)

```bash
brew install ollama
ollama serve &                       # API compatible OpenAI en http://localhost:11434
ollama pull qwen3:4b-q4_K_M          # el tag decide si cabe: elegirlo a mano
ollama run qwen3:4b-q4_K_M "Resume este parrafo en una linea"
curl http://localhost:11434/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"qwen3:4b-q4_K_M","messages":[{"role":"user","content":"hola"}]}'
```

**En 8 GB**: mismas reglas que el motor que lleva debajo — un 7B en `Q4_K_M` ronda 4-4,5 GB y cabe con
margen justo; un 13B en Q4 ronda 7-8 GB y **no es recomendable** con el sistema abierto encima. La
ventaja propia aquí es la gestión de memoria: descarga el modelo de la RAM tras un rato de inactividad
(`keep_alive`), así que entre usos no compite con el resto de la máquina.

Gana a `mudler/LocalAI` (48.802★) y a `vllm-project/vllm` (90.680★) en este entorno: el primero se
solapa con esto añadiendo backends que aquí no se usan, y el segundo está pensado para GPU dedicada,
que esta máquina no tiene. Por debajo lleva `ggml-org/llama.cpp` (126.621★), que define el formato
GGUF y es el estándar de facto; no entra como pueblo propio porque aquí nunca se usa suelto.

Ojo, el punto flojo real: el catálogo invita a bajar cosas que **no caben**, y `ollama run modelo` sin
tag elige por su cuenta. Hay que escribir el `:Xb-qN` a mano. Un modelo que no entra no falla limpio:
se arrastra intercambiando a disco y parece «lento», no «no cabe». Y `ollama serve` escucha en un
puerto local sin autenticación — no exponerlo fuera de la máquina.
